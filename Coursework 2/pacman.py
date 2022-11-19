from math import sqrt

class Game():
    def __init__(self, map):
        self.grid = []
        self.paused = False
        x, y = self.create_grid(map)

        self.nodes_group = Nodes_group()
        self.pellets_group = Pellets_group()

        self.nodes_group.create_nodes(self.grid, x, y)
        self.nodes_group.connect_nodes_row_wise(x, y, self.grid)
        self.nodes_group.connect_nodes_col_wise(x, y, self.grid)

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
        self.row_pixel = self.position[0]*16
        self.col_pixel = self.position[1]*16
        
        self.directions = {"UP": -1, "LEFT": -2, "DOWN": 1, "RIGHT": 2}
        self.direction = self.directions["LEFT"]

    def calculate_available_directions(self, direction, nodes_group):
        available_directions = []
        available_directions.append(direction * -1)

        if self.position in nodes_group.nodes:
            neighbours = nodes_group.nodes[self.position].neighbours

            for neighbour in neighbours:
                if (neighbours[neighbour] is not None):
                    available_directions.append(self.directions[neighbour])

        return list(set(available_directions))

    def next_direction(self, arrow_key, nodes_group):
        arrow_key = arrow_key.upper()
        available_directions = self.calculate_available_directions(self.direction, nodes_group)

        if self.directions[arrow_key] in available_directions:
            self.direction = self.directions[arrow_key]
            self.stopped = False

        elif self.position in nodes_group.nodes:
            self.stopped = True

    def get_position(self, row_pixel, col_pixel, direction):
        
        row = (row_pixel)//16 
        col = (col_pixel)//16 

        if direction == -1:
            row = (row_pixel+14)//16
        elif direction == -2:
            col = (col_pixel+14)//16

        return row, col

class Ghost():
    def __init__(self, target, row, col):
        self.target = target
        self.state = self.scatter(self.target)

        self.position = row, col
        self.row_pixel = self.position[0]*16
        self.col_pixel = self.position[1]*16

        self.directions = {"UP": -1, "LEFT": -2, "DOWN": 1, "RIGHT": 2}
        self.direction = self.directions["LEFT"]

    def scatter(self, target):
        self.time = 7
        
    def chase(self, target):
        self.time = 20

    def calculate_available_directions(self, direction, nodes_group):
        available_directions = []

        if self.position in nodes_group.nodes:
            neighbours = nodes_group.nodes[self.position].neighbours

            for neighbour in neighbours:
                if (neighbours[neighbour] is not None) and (self.directions[neighbour] != direction*-1):
                    available_directions.append(self.directions[neighbour])

        else: available_directions.append(direction)

        return list(set(available_directions))

    def calculate_target_distance(self, position, direction, target):
        x1, y1 = position
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

    def next_direction(self, nodes_group, target):

        available_directions = self.calculate_available_directions(self.direction, nodes_group)

        distance = self.calculate_target_distance(self.position, available_directions[0], target)
        self.direction = available_directions[0]
        for direction in available_directions:
            temp_distance = self.calculate_target_distance(self.position, direction, target)
            if temp_distance < distance:
                self.direction = direction

    def get_position(self, row_pixel, col_pixel, direction):
        
        row = (row_pixel)//16 
        col = (col_pixel)//16 

        if direction == -1:
            row = (row_pixel+14)//16
        elif direction == -2:
            col = (col_pixel+14)//16

        return row, col

class Node():
    def __init__(self, x, y):
        self.position = (x, y)
        self.neighbours = {"UP": None, "LEFT": None, "DOWN": None, "RIGHT": None}

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

    def connect_nodes_row_wise(self, x, y, grid):
        for row in range(x):
            previous_node = None

            for col in range(y):

                if grid[row][col] == 'X':
                    previous_node = None
                    
                elif (row, col) in self.nodes:
 
                    if previous_node is not None:
                        current_node = self.nodes[(row,col)]
                        current_node.neighbours["LEFT"] = previous_node
                        previous_node.neighbours["RIGHT"] = current_node

                    previous_node = self.nodes[(row,col)]

                    if col == 0:
                        self.nodes[(row, col)].neighbours["LEFT"] = self.nodes[(row, 27)]
                        self.nodes[(row, 27)].neighbours["RIGHT"] = self.nodes[(row, col)]

    def connect_nodes_col_wise(self, x, y, grid):
        for col in range(y):
            previous_node = None

            for row in range(x):

                if grid[row][col] == 'X':
                    previous_node = None

                elif (row, col) in self.nodes:

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
        self.pellets_coord = []
        self.power_pellets_coord = []

    def create_pellets(self, grid, x, y):
        for row in range(x):
            for col in range(y):

                if grid[row][col] in "+.":
                    pellet = Pellet(row, col)
                    self.pellets[(row,col)] = pellet

                elif grid[row][col] in "pP":
                    powerpellet = PowerPellet(row, col)
                    self.power_pellets[(row,col)] = powerpellet


#####################

from math import sqrt
from tkinter import *
from PIL import Image, ImageTk
from pacman import *

class Display():
    def __init__(self, width, height, game):
        self.root = Tk()
        self.root.title("Pacman")
        self.width = str(width)
        self.height = str(height)
        self.root.geometry(self.width+"x"+self.height)
        # self.root.resizable(False, False)

        self.game = game

        self.pacman = Pacman(23, 13)
        self.ghost = Ghost(self.pacman.position, 11, 13)

        self.nodes_group = self.game.nodes_group
        self.pellets_group = self.game.pellets_group
        self.pellets_canvas = {}

        image = Image.open("Maze.jpeg")
        bg = image.resize((448,496))
        bg = ImageTk.PhotoImage(bg)

        self.canvas_bg = Canvas(self.root, width=448, height=496)
        self.canvas_bg.place(x=-1, y=-1)
        self.canvas_bg.create_image(0, 0, image=bg, anchor="nw")

        self.pacman_keys = ["Up", "Down", "Left", "Right"]
        self.root.bind("<Key>", self.inputs)
        self.t = 1

        self.display()
        self.update_screen()
        self.root.mainloop()

    def display(self):
        for indrow, row in enumerate(self.game.grid):
            for indcol, col in enumerate(row):
                
                if self.game.grid[indrow][indcol] in ['+', 'n', 'P']:
                    self.nodes_group.nodes_coord.append((indcol*16+8, indrow*16+8))

                if (indrow, indcol) in self.pellets_group.pellets:
                    ele = Canvas(self.root, bg="black", highlightthickness=0)
                    ele.place(x=indcol*16, y=indrow*16, height=15, width=15)
                    oval = ele.create_oval(5, 5, 8, 8, fill="white")

                    self.pellets_canvas[(indrow, indcol)] = ele, oval
                    self.pellets_group.pellets_coord.append((indcol*16+8, indrow*16+8))

                elif (indrow, indcol) in self.pellets_group.power_pellets:
                    ele = Canvas(self.root, bg="black", highlightthickness=0)
                    ele.place(x=indcol*16, y=indrow*16, height=15, width=15)
                    oval = ele.create_oval(2, 2, 11, 11, fill="white")
                    
                    self.pellets_canvas[(indrow, indcol)] = ele, oval
                    self.pellets_group.power_pellets_coord.append((indcol*16+8, indrow*16+8))

        row_pac, col_pac = self.pacman.position
        row_gho, col_gho = self.ghost.position

        self.pacman.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.pacman.circle.place(x=col_pac*16, y=row_pac*16, height=16, width=16)
        oval = self.pacman.circle.create_oval(0, 0, 15, 15, fill="yellow")
        
        self.ghost.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.ghost.circle.place(x=col_gho*16, y=row_gho*16, height=16, width=16)
        oval = self.ghost.circle.create_oval(0, 0, 15, 15, fill="red")

        self.score_label = Label(self.root, text="Score: ", font=("Menlo", 20))
        self.score_label.place(x=10, y=31*16, width=80)
        self.score_val = Label(self.root, text=str(self.pacman.score), font=("Menlo", 20))
        self.score_val.place(x=80, y=31*16)
    
    def update_screen(self):
        
        self.update_pellets(self.t)
        self.update_pacman(self.pacman.direction)
        self.update_ghost()

        if not self.game.paused:
            self.root.after(75, self.update_screen)

    def update_pellets(self, t):
        if t == 4:
            for coord in self.pellets_group.power_pellets:

                power = self.pellets_group.power_pellets[coord]

                ele = self.pellets_canvas[(coord)][0]
                oval = self.pellets_canvas[(coord)][1]

                if power.visible:
                    ele.itemconfig(oval, fill="white")
                else:
                    ele.itemconfig(oval, fill="black")

                self.pellets_group.power_pellets[coord].visible = not power.visible
            self.t = 1
        else: self.t += 1 

    def update_pacman(self, direction):

        for key in self.pacman.directions:
            if self.pacman.directions[key] == direction:
                direction_name = key
                break

        self.pacman.next_direction(direction_name, self.nodes_group)
        if self.pacman.stopped != True:
            row_pixel, col_pixel = self.pacman.row_pixel, self.pacman.col_pixel

            if direction == 1: 
                row_pixel += 4

            elif direction == -1:
                row_pixel -= 4

            elif direction == 2:
                col_pixel += 4

                if col_pixel > 28*16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= 4

                if col_pixel < -16:
                    col_pixel = 28*16

            self.pacman.circle.place(x=col_pixel, y=row_pixel)
            self.pacman.row_pixel, self.pacman.col_pixel = row_pixel, col_pixel
            self.pacman.position = self.pacman.get_position(row_pixel, col_pixel, self.pacman.direction)
            self.update_score()

    def update_ghost(self):

        if self.ghost.position in self.nodes_group.nodes:
            if (self.ghost.col_pixel+8, self.ghost.row_pixel+8) in self.nodes_group.nodes_coord:
                self.ghost.next_direction(self.nodes_group, self.ghost.target)

        row_pixel, col_pixel = self.ghost.row_pixel, self.ghost.col_pixel
        direction = self.ghost.direction

        if direction == 1: 
            row_pixel += 4

        elif direction == -1:
            row_pixel -= 4

        elif direction == 2:
            col_pixel += 4

            if col_pixel > 28*16:
                col_pixel = -16

        elif direction == -2:
            col_pixel -= 4

            if col_pixel < -16:
                col_pixel = 28*16

        self.ghost.circle.place(x=col_pixel, y=row_pixel)
        self.ghost.row_pixel, self.ghost.col_pixel = row_pixel, col_pixel
        self.ghost.position = self.ghost.get_position(row_pixel, col_pixel, self.ghost.direction)
        self.ghost.target = self.pacman.position
        
    def update_score(self):
        pacman_coord = self.pacman.col_pixel+8, self.pacman.row_pixel+8

        if pacman_coord in self.pellets_group.pellets_coord:
            self.pacman.score += self.pellets_group.pellets[self.pacman.position].points
            self.pellets_group.pellets.pop(self.pacman.position)
            self.pellets_group.pellets_coord.remove(pacman_coord)
            self.pellets_canvas[self.pacman.position][0].destroy()

        elif pacman_coord in self.pellets_group.power_pellets_coord:
            self.pacman.score += self.pellets_group.power_pellets[self.pacman.position].points
            self.pellets_group.power_pellets.pop(self.pacman.position)
            self.pellets_group.power_pellets_coord.remove(pacman_coord)
            self.pellets_canvas[self.pacman.position][0].destroy()

        self.score_val["text"] = str(self.pacman.score)

    def inputs(self, event):
        if event.keysym in self.pacman_keys:
            if (self.pacman.col_pixel+8, self.pacman.row_pixel+8) in self.nodes_group.nodes_coord or self.pacman.directions[event.keysym.upper()] == self.pacman.direction*-1:
                self.pacman.next_direction(event.keysym, self.nodes_group)

        if event.keysym == "space":
            self.game.paused = not self.game.paused
            if self.game.paused == False:
                self.update_screen() 

if __name__ == "__main__":
    game = Game("map.txt")
    dfisplay = Display(450, 576, game)