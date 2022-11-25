import random
from math import sqrt

class Game():
    '''Game class to create necessary data and other objects'''
    def __init__(self, map):
        self.grid = []
        self.paused = False
        x, y = self.create_grid(map)

        self.score = 0
        self.nodes_group = Nodes_group()
        self.pellets_group = Pellets_group()

        self.nodes_group.create_nodes(self.grid, x, y)
        self.nodes_group.connect_nodes_row_wise(x, y, self.grid)
        self.nodes_group.connect_nodes_col_wise(x, y, self.grid)

        self.pellets_group.create_pellets(self.grid, x, y)

        self.pacman = Pacman(23, 13)
        self.ghosts_group = Ghosts_group("SCATTER")

        self.pacman.speed = 4
        self.ghosts_group.speed = 4
        self.ghosts_group.died_speed = 16

        self.codes = {
            "MORELIVES" : False,
            "SCARYPACMAN" : False,
            "PELLETMASTER" : False,
            "EASYMODE" : False
        }

    def create_grid(self, map):
        '''Creates a 2d matrix using the map text file'''
        file = open(map)
        temp_grid = file.read().split('\n')
        for row in temp_grid:
            row = row.split()
            self.grid.append(row)
        file.close()

        return (len(self.grid), len(row))

    def spawn(self):
        '''Spawns the ghosts in the ghost house and pacman near the bottom'''
        self.pacman.row_pixel, self.pacman.col_pixel = 23*16, 13*16+8
        self.pacman.direction = -2
        self.ghosts_group.state = "SCATTER"
        for ghost in self.ghosts_group.ghosts:
            ghost.died = False
            ghost.new_spawned = False
            if ghost.name == "Blinky":
                ghost.row_pixel, ghost.col_pixel = 11*16, 14*16
                ghost.direction = -2
            elif ghost.name == "Pinky":
                ghost.row_pixel, ghost.col_pixel = 14*16, 14*16
                ghost.direction = -1
            elif ghost.name == "Inky":
                ghost.row_pixel, ghost.col_pixel = 13*16, 15*16
                ghost.direction = 1
            elif ghost.name == "Clyde":
                ghost.row_pixel, ghost.col_pixel = 13*16, 12*16
                ghost.direction = 1
            ghost.image.itemconfig(ghost.container, image = ghost.pictures[ghost.direction])

class Pacman():
    '''Pacman class for controlling pacman'''
    def __init__(self, row, col):

        self.stopped = False
        self.alive = True
        self.lives = 3

        self.position = row, col
        self.row_pixel = self.position[0]*16
        self.col_pixel = self.position[1]*16

        self.keys = {
            None : 'Up', 
            None : 'Left', 
            None : 'Down', 
            None : 'Right'
        }
        
        self.directions = {"Up": -1, "Left": -2, "Down": 1, "Right": 2}
        self.direction = self.directions["Left"]

    def calculate_available_directions(self, direction, nodes_group):
        '''Returns a list containing valid directions pacman can take'''
        available_directions = []
        available_directions.append(direction * -1)

        if (self.col_pixel+8, self.row_pixel+8) in nodes_group.nodes_coord:
            neighbours = nodes_group.nodes[self.position].neighbours

            for neighbour in neighbours:
                if (neighbours[neighbour] is not None):
                    available_directions.append(self.directions[neighbour])

        return list(set(available_directions))

    def next_direction(self, direction, nodes_group):
        '''Changes the direction of pacman using the direction parameter'''
        available_directions = self.calculate_available_directions(self.direction, nodes_group)
        if direction in available_directions:

            self.stopped = False
            self.direction = direction

        elif (self.col_pixel+8, self.row_pixel+8) in nodes_group.nodes_coord:
            self.stopped = True

    def get_position(self, row_pixel, col_pixel):
        '''Returns the position of pacman using his coordinates'''
        row = (row_pixel)//16 
        col = (col_pixel)//16 

        if self.direction == -1:
            row = (row_pixel+15)//16
        elif self.direction == -2:
            col = (col_pixel+15)//16

        return row, col

class Ghost():
    '''Ghost class creates the individual ghosts'''
    def __init__(self, name, target, row, col):
        self.name = name

        self.target = target

        self.position = row, col
        self.row_pixel = self.position[0]*16
        self.col_pixel = self.position[1]*16

        self.directions = {"Up": -1, "Left": -2, "Down": 1, "Right": 2}
        self.direction = self.directions["Left"]

        self.pictures = {-1: None, -2: None, 1: None, 2: None}

        self.died = False
        self.new_spawned = False
        self.in_home = False

    def calculate_available_directions_ghost(self, direction, nodes_group):
        '''Returns a list containing valid directions the ghost can take'''
        available_directions = []

        if self.died != True and self.position == (11, 14):
            if direction == -1:
                return [-2]
            return [direction]

        if self.died != True and self.position == (14, 14):
            return [-1]

        if self.died == True and self.position == self.target:
            self.died = False
            self.new_spawned = True
            if self.name == "Blinky":
                self.target = (0, 25)
            elif self.name == "Pinky":
                self.target = (0, 3)
            elif self.name == "Inky":
                self.target = (30, 27)
            elif self.name == "Clyde":
                self.target = (30, 0)
            return [direction*(-1)]

        if self.position in nodes_group.nodes:
            neighbours = nodes_group.nodes[self.position].neighbours

            for neighbour in neighbours:
                if (neighbours[neighbour] is not None) and (self.directions[neighbour] != direction*-1):
                    available_directions.append(self.directions[neighbour])

        else: available_directions.append(direction)

        return list(set(available_directions))

    def pinky_target(self, target, direction):
        '''Returns pinky's target, which is 4 tiles ahead of pacman'''
        x, y = target
        if direction == -1:
            x -= 4
            y -= 4
        elif direction == -2:
            y -= 4
        elif direction == 1:
            x += 4
        elif direction == 2:
            y += 4

        return x, y

    def inky_target(self, target, direction, blinky_position):
        '''Returns inky's target, which is determind by both pacman and blinky to ambush pacman from the front'''
        x1, y1 = target
        x2, y2 = blinky_position

        if direction == -1:
            x1 -= 2
            y1 -= 2
        elif direction == -2:
            y1 -= 2
        elif direction == 1:
            x1 += 2
        elif direction == 2:
            y1 += 2

        x = 2*x1 - x2
        y = 2*y1 - y2

        return x, y

    def clyde_target(self, target):
        '''Returns clyde's target which is similar to blinky, but clyde goes to scatter mode when he gets close to pacman'''
        x1, y1 = self.position
        x2, y2 = target
        distance = sqrt((x1-x2)**2 + (y1-y2)**2)
        if distance < 8:
            return (30, 0)
        else:
            return target

    def calculate_target_distance(self, direction, target):
        '''Returns the distance between the ghost and it's target'''
        x1, y1 = self.position
        if direction == -1:
            x1 -= 1
        elif direction == -2:
            y1 -= 1
        elif direction == 1:
            x1 += 1
        elif direction == 2:
            y1 += 1

        x2, y2 = target

        return sqrt((x1-x2)**2 + (y1-y2)**2)

    def next_direction_ghost(self, nodes_group, target):
        '''Determines the ghost's direction by choosing the tile closest to its target'''
        available_directions = self.calculate_available_directions_ghost(self.direction, nodes_group)

        distance = self.calculate_target_distance(available_directions[0], target)

        self.direction = available_directions[0]
        for direction in available_directions:
            temp_distance = self.calculate_target_distance(direction, target)
            if temp_distance < distance:
                distance = temp_distance
                self.direction = direction

    def get_position(self, row_pixel, col_pixel, direction):
        '''Returns the position of the ghost using its coordinates'''
        row = (row_pixel)//16 
        col = (col_pixel)//16 

        if direction == -1:
            row = (row_pixel+15)//16
        elif direction == -2:
            col = (col_pixel+15)//16

        return row, col

class Ghosts_group():
    '''Ghost class for grouping the ghosts'''
    def __init__(self, state):

        self.ghosts = [
            Ghost("Blinky", (0, 25), 1, 23), 
            Ghost("Pinky", (0, 3), 1, 7),
            Ghost("Inky", (30, 27), 29, 23),
            Ghost("Clyde", (30, 0), 29, 7)
        ]

        self.state = state
        self.time = {
            "SCATTER" : 8,
            "CHASE" : 20, 
            "FRIGHTENED" : 30
        }

        self.colour = {
            "Blinky" : "red",
            "Pinky" : "pink",
            "Inky" : "lightblue",
            "Clyde" : "orange",
        }

        self.canvas = {}

    def scatter(self, ghosts, change):
        '''Changes the ghost targets to corners to the map'''
        for ghost in ghosts:
            ghost.image.itemconfig(ghost.container, image = ghost.pictures[ghost.direction])

            if ghost.name == "Blinky":
                ghost.target = (0, 25)
            elif ghost.name == "Pinky":
                ghost.target = (0, 3)
            elif ghost.name == "Inky":
                ghost.target = (30, 27)
            elif ghost.name == "Clyde":
                ghost.target = (30, 0)

            if change == True:
                ghost.direction *= -1
                ghost.died = False

            if ghost.position == (14, 14):
                ghost.direction = -1
                ghost.died = False
                ghost.new_spawned = False

    def chase(self, ghosts, pacman_position, pacman_direction, blinky_position, change):
        '''Changes the ghost targets to catch pacman'''
        for ghost in ghosts:
            ghost.image.itemconfig(ghost.container, image = ghost.pictures[ghost.direction])

            if ghost.name == "Blinky":
                ghost.target = pacman_position
            elif ghost.name == "Pinky":
                ghost.target = ghost.pinky_target(pacman_position, pacman_direction)
            elif ghost.name == "Inky":
                ghost.target = ghost.inky_target(pacman_position, pacman_direction, blinky_position)
            elif ghost.name == "Clyde":
                ghost.target = ghost.clyde_target(pacman_position)

            if change == True:
                ghost.direction *= -1
                ghost.died = False
                ghost.new_spawned = False
    
    def frightened(self, ghosts, nodes_group, change):
        '''Changes the ghost target to frantically pick any direction'''
        for ghost in ghosts:

            if change == True:
                ghost.direction *= -1
                ghost.died = False
                ghost.new_spawned = False
                ghost.image.itemconfig(ghost.container, image = ghost.fright_picture)

            if ghost.died or ghost.new_spawned:
                self.died(ghost)

            elif (ghost.col_pixel+8, ghost.row_pixel+8) in nodes_group.nodes_coord:
                available_directions = ghost.calculate_available_directions_ghost(ghost.direction, nodes_group)
                ghost.image.itemconfig(ghost.container, image = ghost.fright_picture)

                ghost.direction = random.choice(available_directions)
                x, y = ghost.position
                
                if ghost.direction == -1:
                    x -= 1
                elif ghost.direction == -2:
                    y -= 1
                elif ghost.direction == 1:
                    x += 1
                elif ghost.direction == 2:
                    y += 1
                
                ghost.target = x, y

            else: ghost.image.itemconfig(ghost.container, image = ghost.fright_picture)

    def died(self, ghost):
        '''Sends the ghost back to ghost house after it is caught by pacman in frightened mode'''
        if ghost.new_spawned == False:
            if ghost.name == "Blinky":
                ghost.target = (14, 12)
            elif ghost.name == "Pinky":
                ghost.target = (14, 15)
            elif ghost.name == "Inky":
                ghost.target = (13, 12)
            elif ghost.name == "Clyde":
                ghost.target = (13, 15)
            
            if ghost.position == (11, 14):
                ghost.in_home = True

        else:
            if ghost.name == "Blinky":
                ghost.target = (0, 25)
            elif ghost.name == "Pinky":
                ghost.target = (0, 3)
            elif ghost.name == "Inky":
                ghost.target = (30, 27)
            elif ghost.name == "Clyde":
                ghost.target = (30, 0)

            if ghost.position == (11, 14):
                ghost.in_home = False

class Node():
    '''Node class to create nodes where pacman and ghosts can change directions'''
    def __init__(self, x, y):

        self.position = (x, y)
        self.neighbours = {"Up": None, "Left": None, "Down": None, "Right": None}

class Nodes_group():
    '''Nodes group class to group the nodes together'''
    def __init__(self):
        self.nodes = {}
        self.nodes_coord = []

    def create_nodes(self, grid, x, y):
        '''Creates the nodes from the grid'''
        for row in range(x):
            for col in range(y):

                if grid[row][col] in "+nPG":
                    node = Node(row, col)
                    self.nodes[(row,col)] = node

    def connect_nodes_row_wise(self, x, y, grid):
        '''Sets the right and left neighbours of each node'''
        for row in range(x):
            previous_node = None

            for col in range(y):

                if grid[row][col] == 'X':
                    previous_node = None
                    
                elif (row, col) in self.nodes:
 
                    if previous_node is not None:
                        current_node = self.nodes[(row,col)]
                        current_node.neighbours["Left"] = previous_node
                        previous_node.neighbours["Right"] = current_node

                    previous_node = self.nodes[(row,col)]

                    if col == 0:
                        self.nodes[(row, col)].neighbours["Left"] = self.nodes[(row, 27)]
                        self.nodes[(row, 27)].neighbours["Right"] = self.nodes[(row, col)]

    def connect_nodes_col_wise(self, x, y, grid):
        '''Sets the top and bottom neighbours of each node'''
        for col in range(y):
            previous_node = None

            for row in range(x):

                if grid[row][col] == 'X':
                    previous_node = None

                elif (row, col) in self.nodes:

                    if previous_node is not None:
                        current_node = self.nodes[(row,col)]
                        current_node.neighbours["Up"] = previous_node
                        previous_node.neighbours["Down"] = current_node

                    previous_node = self.nodes[(row,col)]

class Pellet():
    '''Pellet class to create the normal pellets'''
    def __init__(self, x, y):
        self.position = (x, y)
        self.consumed = False

class PowerPellet():
    '''Power pellet class to create the 4 power pellets'''
    def __init__(self, x, y):
        self.position = (x, y)
        self.consumed = False
        self.visible = True

class Pellets_group():
    '''Pellets group class to group the tiny and power pellets together'''
    def __init__(self):
        self.pellets = {}
        self.power_pellets = {}
        self.pellets_coord = []
        self.power_pellets_coord = []
        self.points = {
            "Pellet" : 10,
            "PowerPellet" : 50
        }

    def create_pellets(self, grid, x, y):
        '''Creates the different pellets from the grid'''
        for row in range(x):
            for col in range(y):

                if grid[row][col] in "+.":
                    self.pellets[(row,col)] = Pellet(row, col)

                elif grid[row][col] in "pP":
                    self.power_pellets[(row,col)] = PowerPellet(row, col)