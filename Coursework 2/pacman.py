class Game():
    def __init__(self, map, nodes_group, pellets_group):
        self.grid = []
        self.paused = False
        x, y = self.create_grid(map)

        self.nodes_group = Nodes_group()
        self.pellets_group = Pellets_group()

        self.nodes_group.create_nodes(self.grid, x, y)
        self.nodes_group.connect_nodes_row_wise(x, y)
        self.nodes_group.connect_nodes_col_wise(x, y)

        self.pellets_group.create_pellets(self.grid, x, y)

    def create_grid(self, map):
        file = open(map)
        temp_grid = file.read().split('\n')
        for row in temp_grid:
            row = row.split()
            self.grid.append(row)
        file.close()

        return (len(self.grid), len(row))

class Pacman():
    def __init__(self, row, col):

        self.stopped = False
        self.score = 0
        self.alive = True
        self.lives = 3

        self.position = row, col
        self.row_pixel = row*16+44
        self.col_pixel = col*16+5
        
        self.directions = {"UP": -1, "DOWN": 1, "LEFT": -2, "RIGHT": 2}
        self.direction = self.directions["LEFT"]

    def calculate_available_directions(self, direction, nodes_group):
        available_directions = []
        available_directions.append(direction * -1)

        if self.position in nodes_group.nodes:
            neighbours = nodes_group.nodes[self.position].neighbours

            for direction in neighbours:
                if (neighbours[direction] is not None) and (direction not in available_directions):
                    available_directions.append(self.directions[direction])

        return available_directions

    def next_direction(self, arrow_key, nodes_group):
        arrow_key = arrow_key.upper()
        available_directions = self.calculate_available_directions(self.direction, nodes_group)

        if self.directions[arrow_key] in available_directions:
            self.direction = self.directions[arrow_key]
            self.stopped = False

        elif self.position in nodes_group.nodes:
            self.stopped = True

    def get_position(self, row_pixel, col_pixel):
        
        row = (row_pixel+8)//16 
        col = (col_pixel+8)//16 

        return row, col

class Node():
    def __init__(self, x, y):
        self.position = (x, y)
        self.neighbours = {"UP": None, "DOWN": None, "LEFT": None, "RIGHT": None}

class Nodes_group():
    def __init__(self):
        self.nodes = {}
        self.nodes_coord = []

    def create_nodes(self, grid, x, y):
        for row in range(x):
            for col in range(y):

                if grid[row][col] in "+nP":
                    node = Node(row, col)
                    self.nodes[(row,col)] = node

    def connect_nodes_row_wise(self, x, y):
        for row in range(x):
            previous_node = None

            for col in range(y):
                if (row, col) in self.nodes:

                    if previous_node is not None:
                        current_node = self.nodes[(row,col)]
                        current_node.neighbours["LEFT"] = previous_node
                        previous_node.neighbours["RIGHT"] = current_node

                    previous_node = self.nodes[(row,col)]

    def connect_nodes_col_wise(self, x, y):
        for col in range(y):
            previous_node = None

            for row in range(x):
                if (row, col) in self.nodes:

                    if previous_node is not None:
                        current_node = self.nodes[(row,col)]
                        current_node.neighbours["UP"] = previous_node
                        previous_node.neighbours["DOWN"] = current_node

                    previous_node = self.nodes[(row,col)]

class Pellet():
    def __init__(self, x, y):
        self.position = (x, y)
        self.points = 10
        self.consumed = False

class PowerPellet():
    def __init__(self, x, y):
        self.position = (x, y)
        self.points = 50
        self.consumed = False
        self.visible = True
        self.timer = 10

class Pellets_group():
    def __init__(self):
        self.pellets = {}
        self.power_pellets = {}

    def create_pellets(self, grid, x, y):
        for row in range(x):
            for col in range(y):

                if grid[row][col] in "+.":
                    pellet = Pellet(row, col)
                    self.pellets[(row,col)] = pellet

                elif grid[row][col] in "pP":
                    powerpellet = PowerPellet(row, col)
                    self.power_pellets[(row,col)] = powerpellet