import heapq
import time
import os
import copy
import math
import sys

# Matrix tile graphics.
wall = 'm'
visited = '*'
unvisited = ' '

# Element containing a priority, a location of where this priority is determined from, and its origin.
class PrioLocFrom(object):
    def __init__(self, prio, location, origin, steps_origin):
        self.prio = prio
        self.location = location
        self.origin = origin
        self.steps_origin = steps_origin

    def __eq__(self, other):
        return self.location == other.location

    def __lt__(self, other):
        return self.prio < other.prio

    def __gt__(self, other):
        return self.prio > other.prio

# PriorityQueueHeapSet
class PrioSet(object):
    def __init__(self):
        self.heap = []

    def add(self, entry):
        if entry in self.heap: # Replace entry in queue only if origin location is closer to the start.
            index = self.heap.index(entry)

            if self.heap[index].steps_origin > entry.steps_origin:
                self.heap[index] = entry
        else: # Entry doesn't exist in the queue, just add.
            heapq.heappush(self.heap, entry)

    def pop(self):
        entry = heapq.heappop(self.heap)
        return entry

    def __len__(self):
        return len(self.heap)

# Create a matrix of unvisited nodes for the given size.
def createMatrix(width, height):
    return [[(unvisited, 100, (-1, -1)) for y in range(height)] for x in range(width)]

# Find a path between the start and goal locations using a heuristic function 
# to determine path selection.
def findPath(o_matrix, start, goal, heuristic, n=1000, debug=False, mode="dfs"):
    matrix = copy.deepcopy(o_matrix)
    current_loc = start
    steps_origin = 0
    came_from = start
    ps = PrioSet()

    while current_loc != goal and n > 0:
        if debug:
            print("Iteration: %i" % n)
            print("Current loc: %s, goal: %s\n" % (current_loc, goal))
            print("Current tile type:  %s" % matrix[current_loc[1]][current_loc[0]])
        # Expend the tile being currently checked.
        #matrix[current_loc[1]][current_loc[0]] = 1
        matrix[current_loc[1]][current_loc[0]] = (visited, steps_origin, came_from)
        
        # Reduce the number of iterations for the pathfinding.
        n -= 1
        
        # Get neighbours to the current tile.
        neighbours = [ (x,y) for x in range(current_loc[0]-1, current_loc[0]+2) for y in range(current_loc[1]-1,current_loc[1]+2)]
        if debug:
            print("Neighbours: %s" % neighbours)

        # Remove self from neighbours.
        del neighbours[4]
        
        # Ignore invalid neighbour positions. 
        # Invalid = Out of bounds locations (eg (-1,1)), already visited locations (1), or walls (3).
        valid_neighbours = [ ne for ne in neighbours if not any(x < 0 or x >= len(matrix) for x in ne) and matrix[ne[1]][ne[0]][0] != visited and matrix[ne[1]][ne[0]][0] != wall ]
        if debug:
            print("Valid neighbours: %s" % valid_neighbours)

        # Calculate heuristic for each neighbour.
        if mode == "a*":
            # Use this calculation for A*.
            neighbour_distances = [ (steps_origin+1+heuristic(ne, goal), ne, current_loc, steps_origin+1) for ne in valid_neighbours ]
        elif mode == "dfs":
            # Use this calculation for DFS.
            neighbour_distances = [ (heuristic(ne, goal), ne, current_loc, steps_origin+1) for ne in valid_neighbours ]

        if debug:
            print("Distances: %s" % neighbour_distances)

        # Add neighbours and associated heuristic to heap with lowest distance floating to top.
        for nd in neighbour_distances:
            ps.add(PrioLocFrom(nd[0], nd[1], nd[2], nd[3]))
        
        # No more locations to try out and goal not reached.
        if len(ps) == 0:
            print("No path found from start: %s, to goal location: %s" % (start, goal))
            return

        # Pick next location. Discard heuristic.
        entry = ps.pop()
        current_loc = entry.location
        steps_origin = entry.steps_origin
        came_from = entry.origin

        #if debug:
        #printMatrix(matrix)
        #time.sleep(0.5)
        #os.system('clear')

    # Display goal location as a G.
    matrix[goal[1]][goal[0]] = ('G', steps_origin, came_from)

    print(n)

    animate_path(o_matrix, matrix, start, goal)
    return matrix

def animate_path(o_matrix, matrix, start, goal):
    print("PATH")
    current_loc = goal
    print(o_matrix[current_loc[1]][current_loc[0]][0])

    while current_loc != start:
        o_matrix[current_loc[1]][current_loc[0]] = matrix[current_loc[1]][current_loc[0]]
        current_loc = matrix[current_loc[1]][current_loc[0]][2]
        #printMatrix(o_matrix)
        #time.sleep(0.5)
        #os.system('clear')
    
    #os.system('clear')
    entry = matrix[current_loc[1]][current_loc[0]]
    o_matrix[current_loc[1]][current_loc[0]] = (visited, entry[1], entry[2])
    printMatrix(o_matrix)
    #time.sleep(0.5)

# Straight distance between start and goal.
def birdDistance(start, goal):
    return math.sqrt((start[0] - goal[0])**2+(start[1] - goal[1])**2)

# Prints out a given matrix, separates matrix values using whitespace.
def printMatrix(matrix):
    for y in range(len(matrix)):
        line = ""
        for x in range(len(matrix[y])):
            line += str(matrix[y][x][0]) + ' '
        print(line)


# Generate maze from matrix.
def generateMaze(matrix):
    # Fill matrix with walls, except for starting point.
    # Add starting point to queue of non visited areas.
    # While unexplored tiles exist:
        # if next tile == wall:
            # Break down wall
            # Add neighbouring unvisited walls to queue.

if __name__ == '__main__':
    mode = "a*" # Default computation.
    if (len(sys.argv) == 2):
        if sys.argv[1] in ["dfs", "a*", "maze"]:
            mode = sys.argv[1]
        else:
            print("usage: python main.py HEURISTIC\nheuristics: dfs, a*\ncommands: help")
            sys.exit(0)

    matrix = createMatrix(10,10)

    for x in range(8):
        matrix[6][x] = (wall, 100, (-1,-1))

    for x in range(2):
        matrix[9-x][8] = (wall, 100, (-1,-1))
    
    for x in range(8):
        matrix[8][1+x] = (wall, 100, (-1,-1))

    if mode == "maze":
        matrix = generateMaze(matrix)
        printMatrix(matrix)
    else:
        path = findPath(matrix, (4,0), (4,9), birdDistance, mode=mode)
