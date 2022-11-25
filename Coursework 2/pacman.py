import random
from math import sqrt


class Game():
    '''Game class to create necessary data and other objects'''

    def __init__(self, map):
        # creating all the required variables like grid, pacman, ghosts, nodes,
        # pellets
        self.grid = []
        self.paused = False
        x, y = self.create_grid(map)

        self.score = 0
        self.nodes_group = Nodes_group()
        self.pellets_group = Pellets_group()

        # connecting the nodes with each other after creating them
        self.nodes_group.create_nodes(self.grid, x, y)
        self.nodes_group.connect_nodes_row_wise(x, y, self.grid)
        self.nodes_group.connect_nodes_col_wise(x, y, self.grid)

        self.pellets_group.create_pellets(self.grid, x, y)

        self.pacman = Pacman(23, 13)
        self.ghosts_group = Ghosts_group("SCATTER")

        # defining the speed of pacman and the ghosts, as well that of a dead
        # ghost
        self.pacman.speed = 4
        self.ghosts_group.speed = 4
        self.ghosts_group.died_speed = 16

        self.codes = {                      # defining the cheat codes
            "MORELIVES": False,
            "SCARYPACMAN": False,
            "PELLETMASTER": False,
            "EASYMODE": False
        }

    def create_grid(self, map):
        '''Creates a 2d matrix using the map text file'''
        file = open(
            map)                            # creates a grid containing the characters from the map text file
        temp_grid = file.read().split('\n')
        for row in temp_grid:
            row = row.split()
            self.grid.append(row)
        file.close()

        return (len(self.grid), len(row))

    def spawn(self):
        '''Spawns the ghosts in the ghost house and pacman near the bottom'''
        self.pacman.row_pixel, self.pacman.col_pixel = 23 * 16, 13 * 16 + \
            8               # setting the coordinates of pacman and the ghosts to inital values
        self.pacman.direction = -2
        # setting the ghost state to SCATTER
        self.ghosts_group.state = "SCATTER"
        for ghost in self.ghosts_group.ghosts:
            # setting died and new_spawn ghost variables to false (only become
            # true after being eaten by pacman)
            ghost.died = False
            ghost.new_spawned = False
            if ghost.name == "Blinky":
                ghost.row_pixel, ghost.col_pixel = 11 * 16, 14 * 16
                ghost.direction = -2
            elif ghost.name == "Pinky":
                ghost.row_pixel, ghost.col_pixel = 14 * 16, 14 * 16
                ghost.direction = -1
            elif ghost.name == "Inky":
                ghost.row_pixel, ghost.col_pixel = 13 * 16, 15 * 16
                ghost.direction = 1
            elif ghost.name == "Clyde":
                ghost.row_pixel, ghost.col_pixel = 13 * 16, 12 * 16
                ghost.direction = 1
            # changing the picture of the ghosts to their directions
            ghost.image.itemconfig(ghost.container,
                                   image=ghost.pictures[ghost.direction])


class Pacman():
    '''Pacman class for controlling pacman'''

    # creates the pacman object at the mentioned row and column
    def __init__(self, row, col):

        self.stopped = False                    # setting initial variables
        self.alive = True
        self.lives = 3

        self.position = row, col
        # setting coordinates by multiplying by 16 (the grid is divided by
        # 16*16px squares which represent each element)
        self.row_pixel = self.position[0] * 16
        self.col_pixel = self.position[1] * 16

        self.keys = {               # setting the controls of pacman
            None: 'Up',
            None: 'Left',
            None: 'Down',
            None: 'Right'
        }

        self.directions = {
            "Up": -1,
            "Left": -2,
            "Down": 1,
            "Right": 2}  # the directions
        self.direction = self.directions["Left"]        # initial direction

    def calculate_available_directions(self, direction, nodes_group):
        '''Returns a list containing valid directions pacman can take'''
        available_directions = []
        # pacman can always travel back, ghosts can't
        available_directions.append(direction * -1)

        if (self.col_pixel + 8, self.row_pixel + 8) in nodes_group.nodes_coord:
            # if pacman's coordinates are inside that of a node, add the
            # remaining directions as well
            neighbours = nodes_group.nodes[self.position].neighbours

            for neighbour in neighbours:
                # add only if there is a neighbour for that node
                if (neighbours[neighbour] is not None):
                    available_directions.append(self.directions[neighbour])

        # returns a list without duplicate elements (set deletes duplicates)
        return list(set(available_directions))

    def next_direction(self, direction, nodes_group):
        '''Changes the direction of pacman using the direction parameter'''
        available_directions = self.calculate_available_directions(
            self.direction, nodes_group)
        # checking if the entered direction is in the available directions
        if direction in available_directions:

            self.stopped = False
            # changing pacman's direction and setting stopped to False
            self.direction = direction

        elif (self.col_pixel + 8, self.row_pixel + 8) in nodes_group.nodes_coord:
            # otherwise if pacman is in a node and the direction is valid, set
            # stopped to True
            self.stopped = True

    def get_position(self, row_pixel, col_pixel):
        '''Returns the position of pacman using his coordinates'''
        row = (
            row_pixel) // 16               # get pacman's position by dividing the coordinates by 16
        col = (col_pixel) // 16

        if self.direction == -1:
            # if he's coming from the top or left, make the necessary changes
            # to get correct position
            row = (row_pixel + 15) // 16
        elif self.direction == -2:
            col = (col_pixel + 15) // 16

        return row, col


class Ghost():
    '''Ghost class creates the individual ghosts'''

    def __init__(self, name, target, row, col):
        self.name = name            # sets unique name and other required variables

        self.target = target

        self.position = row, col
        self.row_pixel = self.position[0] * 16
        self.col_pixel = self.position[1] * 16

        self.directions = {"Up": -1, "Left": -2, "Down": 1, "Right": 2}
        self.direction = self.directions["Left"]

        self.pictures = {-1: None, -2: None, 1: None, 2: None}

        self.died = False
        self.new_spawned = False
        self.in_home = False

    def calculate_available_directions_ghost(self, direction, nodes_group):
        '''Returns a list containing valid directions the ghost can take'''
        available_directions = []           # calculating the available directions

        if self.died != True and self.position == (11, 14):
            if direction == -1:             # if ghosts left the house facing up, changing their direction to left or right
                return [-2, 2]
            # otherwise, continue in the same direction without entering the
            # ghost house
            return [direction]

        if self.died != True and self.position == (
                14, 14):         # to ensure ghosts in the house exit it after being respawned
            return [-1]

        if self.died and self.position == self.target:
            # if the ghosts reached their target in the house, spawn them again
            # and set new scatter targets accordingly
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
            return [direction * (-1)]

        if self.position in nodes_group.nodes:      # if there in any other node, get all valid directions
            neighbours = nodes_group.nodes[self.position].neighbours

            for neighbour in neighbours:
                if (neighbours[neighbour] is not None) and (
                        self.directions[neighbour] != direction * -1):
                    available_directions.append(self.directions[neighbour])

        else:
            # else just continue in the same direction
            available_directions.append(direction)

        return list(set(available_directions))

    def pinky_target(self, target, direction):
        '''Returns pinky's target, which is 4 tiles ahead of pacman'''
        x, y = target
        if direction == -1:             # pinky's target when pacman is facing up was always 4 tiles to top and right due to a carry bug in the original game
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

        if direction == -1:         # inky tries to get in front of pacman by setting target to a place so that
            x1 -= 2                 # pacman is between inky and blinky
            y1 -= 2
        # uses mid point theorem (that's all i can say, quite hard to explain
        # through comments, but simple to understand)
        elif direction == -2:
            y1 -= 2
        elif direction == 1:
            x1 += 2
        elif direction == 2:        # blinky's target is pacman's exact position
            y1 += 2

        x = 2 * x1 - x2
        y = 2 * y1 - y2

        return x, y

    def clyde_target(self, target):
        '''Returns clyde's target which is similar to blinky, but clyde goes to scatter mode when he gets close to pacman'''
        x1, y1 = self.position
        x2, y2 = target         # target is pacman's position expect when he's less that 8 units from pacman, when clyde goes back to scatter target
        distance = sqrt((x1 - x2)**2 + (y1 - y2)**2)
        if distance < 8:
            return (30, 0)
        else:
            return target

    def calculate_target_distance(self, direction, target):
        '''Returns the distance between the ghost and it's target'''
        x1, y1 = self.position
        if direction == -1:         # calculate the distance between the ghost and its target
            x1 -= 1
        elif direction == -2:
            y1 -= 1
        elif direction == 1:
            x1 += 1
        elif direction == 2:
            y1 += 1

        x2, y2 = target

        return sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def next_direction_ghost(self, nodes_group, target):
        '''Determines the ghost's direction by choosing the tile closest to its target'''
        available_directions = self.calculate_available_directions_ghost(
            self.direction, nodes_group)

        distance = self.calculate_target_distance(
            available_directions[0], target)

        self.direction = available_directions[0]
        # goes through all available directions and checks if the current
        # direction would have shorter path than next direction
        for direction in available_directions:
            temp_distance = self.calculate_target_distance(direction, target)
            if temp_distance < distance:
                distance = temp_distance
                self.direction = direction

    def get_position(self, row_pixel, col_pixel, direction):
        '''Returns the position of the ghost using its coordinates'''
        row = (row_pixel) // 16
        col = (col_pixel) // 16               # same as pacman's get position

        if direction == -1:
            row = (row_pixel + 15) // 16
        elif direction == -2:
            col = (col_pixel + 15) // 16

        return row, col


class Ghosts_group():
    '''Ghost class for grouping the ghosts'''

    def __init__(self, state):              # groups the ghosts and sets common behaviour

        self.ghosts = [
            Ghost("Blinky", (0, 25), 1, 23),
            Ghost("Pinky", (0, 3), 1, 7),
            Ghost("Inky", (30, 27), 29, 23),
            Ghost("Clyde", (30, 0), 29, 7)
        ]

        self.state = state
        self.time = {
            "SCATTER": 8,
            "CHASE": 20,
            "FRIGHTENED": 10
        }

        self.canvas = {}

    def scatter(self, ghosts, change):
        '''Changes the ghost targets to corners to the map'''
        for ghost in ghosts:
            ghost.image.itemconfig(
                ghost.container, image=ghost.pictures[ghost.direction])    # set the image

            if ghost.name == "Blinky":          # scatter targets are at the corners of the map
                ghost.target = (0, 25)
            elif ghost.name == "Pinky":
                ghost.target = (0, 3)
            elif ghost.name == "Inky":
                ghost.target = (30, 27)
            elif ghost.name == "Clyde":
                ghost.target = (30, 0)

            if change:              # if the state has newly changed, reverse the direction of the ghosts
                ghost.direction *= -1       # as well as died and new_spawned are False
                ghost.died = False
                ghost.died = False
                ghost.new_spawned = False

    def chase(
            self,
            ghosts,
            pacman_position,
            pacman_direction,
            blinky_position,
            change):
        '''Changes the ghost targets to catch pacman'''
        for ghost in ghosts:
            # set the images of the ghosts
            ghost.image.itemconfig(ghost.container,
                                   image=ghost.pictures[ghost.direction])

            if ghost.name == "Blinky":              # set the targets according to their names
                ghost.target = pacman_position
            elif ghost.name == "Pinky":
                ghost.target = ghost.pinky_target(
                    pacman_position, pacman_direction)
            elif ghost.name == "Inky":
                ghost.target = ghost.inky_target(
                    pacman_position, pacman_direction, blinky_position)
            elif ghost.name == "Clyde":
                ghost.target = ghost.clyde_target(pacman_position)

            if change:           # if the state has newly changed, reverse the direction of the ghosts
                ghost.direction *= -1       # as well as died and new_spawned are False
                ghost.died = False
                ghost.new_spawned = False

    def frightened(self, ghosts, nodes_group, change):
        '''Changes the ghost target to frantically pick any direction'''
        for ghost in ghosts:

            if change:           # if the state has newly changed, reverse the direction of the ghosts
                ghost.direction *= -1       # as well as died and new_spawned are False
                ghost.died = False
                ghost.new_spawned = False
                ghost.image.itemconfig(
                    ghost.container, image=ghost.fright_picture)

            if ghost.died or ghost.new_spawned:         # if the ghost died or spawned again, go to died function
                self.died(ghost)

            elif (ghost.col_pixel + 8, ghost.row_pixel + 8) in nodes_group.nodes_coord:
                # check the available directions and randomly generate a new
                # direction and target
                available_directions = ghost.calculate_available_directions_ghost(
                    ghost.direction, nodes_group)
                ghost.image.itemconfig(
                    ghost.container, image=ghost.fright_picture)

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

            else:
                ghost.image.itemconfig(
                    ghost.container, image=ghost.fright_picture)

    def died(self, ghost):
        '''Sends the ghost back to ghost house after it is caught by pacman in frightened mode'''
        if ghost.new_spawned == False:          # if the ghost hasn't spawned, send it to the house
            if ghost.name == "Blinky":
                ghost.target = (14, 12)
            elif ghost.name == "Pinky":
                ghost.target = (14, 15)
            elif ghost.name == "Inky":
                ghost.target = (13, 12)
            elif ghost.name == "Clyde":
                ghost.target = (13, 15)

            if ghost.position == (
                    11, 14):      # if it entered the house, change value to true
                ghost.in_home = True

        else:                               # if the ghost has spawned, change its target to its scatter target
            if ghost.name == "Blinky":
                ghost.target = (0, 25)
            elif ghost.name == "Pinky":
                ghost.target = (0, 3)
            elif ghost.name == "Inky":
                ghost.target = (30, 27)
            elif ghost.name == "Clyde":
                ghost.target = (30, 0)

            if ghost.position == (
                    11, 14):      # if it exited the house, change value to false
                ghost.in_home = False


class Node():
    '''Node class to create nodes where pacman and ghosts can change directions'''

    def __init__(self, x, y):       # create nodes

        self.position = (x, y)
        self.neighbours = {
            "Up": None,
            "Left": None,
            "Down": None,
            "Right": None}


class Nodes_group():
    '''Nodes group class to group the nodes together'''

    def __init__(self):         # create a group to make it easier to join the nodes
        self.nodes = {}
        self.nodes_coord = []

    def create_nodes(self, grid, x, y):
        '''Creates the nodes from the grid'''
        for row in range(x):
            for col in range(y):            # create the nodes from the grid

                if grid[row][col] in "+nPG":
                    node = Node(row, col)
                    self.nodes[(row, col)] = node

    def connect_nodes_row_wise(self, x, y, grid):
        '''Sets the right and left neighbours of each node'''
        for row in range(x):
            # goes through each row and sets the inital previous node as none
            previous_node = None

            for col in range(y):

                # check if the current element is X (represents a wall)
                if grid[row][col] == 'X':
                    previous_node = None            # the previous node to none

                elif (row, col) in self.nodes:

                    if previous_node is not None:           # if there is a previous node, connect it with current one
                        current_node = self.nodes[(row, col)]
                        current_node.neighbours["Left"] = previous_node
                        previous_node.neighbours["Right"] = current_node

                    # set the previous node as the current one
                    previous_node = self.nodes[(row, col)]

                    if col == 0:
                        self.nodes[(row, col)].neighbours["Left"] = self.nodes[(
                            row, 27)]       # connect the two portals
                        self.nodes[(row, 27)].neighbours["Right"] = self.nodes[(
                            row, col)]

    def connect_nodes_col_wise(self, x, y, grid):
        '''Sets the top and bottom neighbours of each node'''
        for col in range(
                y):            # goes through each column and checks similary to above function
            previous_node = None

            for row in range(x):

                if grid[row][col] == 'X':
                    previous_node = None

                elif (row, col) in self.nodes:

                    if previous_node is not None:
                        current_node = self.nodes[(row, col)]
                        current_node.neighbours["Up"] = previous_node
                        previous_node.neighbours["Down"] = current_node

                    previous_node = self.nodes[(row, col)]


class Pellet():
    '''Pellet class to create the normal pellets'''

    def __init__(self, x, y):           # creates a pellet
        self.position = (x, y)
        self.consumed = False


class PowerPellet():
    '''Power pellet class to create the 4 power pellets'''

    def __init__(self, x, y):
        # creates a power pellet, visible variable to allow for blinking
        # function
        self.position = (x, y)
        self.consumed = False
        self.visible = True


class Pellets_group():
    '''Pellets group class to group the tiny and power pellets together'''

    def __init__(self):
        # sets required variables, pellet positions, coordinates, points
        self.pellets = {}
        self.power_pellets = {}
        self.pellets_coord = []
        self.power_pellets_coord = []
        self.points = {
            "Pellet": 10,
            "PowerPellet": 50
        }

    def create_pellets(self, grid, x, y):       # creates the pellets from the grid
        '''Creates the different pellets from the grid'''
        for row in range(x):
            for col in range(y):

                if grid[row][col] in "+.":
                    self.pellets[(row, col)] = Pellet(row, col)

                elif grid[row][col] in "pP":
                    self.power_pellets[(row, col)] = PowerPellet(row, col)
