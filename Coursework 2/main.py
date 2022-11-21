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
        self.root.resizable(False, False)

        self.game = game

        self.pacman = Pacman(23, 13)
        self.ghosts_group = Ghosts_group("SCATTER")

        self.blinky = self.ghosts_group.ghosts[0]
        self.pinky = self.ghosts_group.ghosts[1]
        self.inky = self.ghosts_group.ghosts[2]
        self.clyde = self.ghosts_group.ghosts[3]

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
        self.time = 0
        self.change = False

        self.display()
        self.counter()
        self.update_ghost_state("SCATTER")
        self.update_screen()
        self.root.mainloop()

    def counter(self):
        if self.game.paused != True:
            self.time += 1
            print(self.time)
            self.root.after(1000, self.counter)
        
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

        self.pacman.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.pacman.circle.place(x=col_pac*16, y=row_pac*16, height=16, width=16)
        oval = self.pacman.circle.create_oval(0, 0, 15, 15, fill="yellow")
        
        for ghost in self.ghosts_group.ghosts:

            row, col = ghost.position

            ghost.circle = Canvas(self.root, bg="black", highlightthickness=0)
            ghost.circle.place(x=col*16, y=row*16, height=16, width=16)

            colour = self.ghosts_group.colour[ghost.name]
            oval = ghost.circle.create_oval(0, 0, 15, 15, fill=colour)
            ghost.oval = oval

        self.score_label = Label(self.root, text="Score: ", font=("Menlo", 20))
        self.score_label.place(x=10, y=31*16, width=80)
        self.score_val = Label(self.root, text=str(self.pacman.score), font=("Menlo", 20))
        self.score_val.place(x=80, y=31*16)

    def update_screen(self):
        
        self.update_pellets(self.t)
        self.update_pacman(self.pacman.direction)
        self.update_ghosts()
        self.update_ghost_state(self.ghosts_group.state)

        if not self.game.paused:
            self.root.after(50, self.update_screen)

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
                row_pixel += 2

            elif direction == -1:
                row_pixel -= 2

            elif direction == 2:
                col_pixel += 2

                if col_pixel > 28*16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= 2

                if col_pixel < -16:
                    col_pixel = 28*16

            self.pacman.circle.place(x=col_pixel, y=row_pixel)
            self.pacman.row_pixel, self.pacman.col_pixel = row_pixel, col_pixel
            self.pacman.position = self.pacman.get_position(row_pixel, col_pixel, self.pacman.direction)
            self.update_score()

    def update_ghosts(self):

        for ghost in self.ghosts_group.ghosts:
            if ghost.position in self.nodes_group.nodes:
                
                if (ghost.col_pixel+8, ghost.row_pixel+8) in self.nodes_group.nodes_coord:
                    ghost.next_direction_ghost(self.nodes_group, ghost.target)

            row_pixel, col_pixel = ghost.row_pixel, ghost.col_pixel
            direction = ghost.direction

            if direction == 1: 
                row_pixel += 2

            elif direction == -1:
                row_pixel -= 2

            elif direction == 2:
                col_pixel += 2

                if col_pixel > 28*16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= 2

                if col_pixel < -16:
                    col_pixel = 28*16

            ghost.circle.place(x=col_pixel, y=row_pixel)
            ghost.row_pixel, ghost.col_pixel = row_pixel, col_pixel
            ghost.position = ghost.get_position(row_pixel, col_pixel, ghost.direction)

    def update_ghost_state(self, state):

        if state != "FRIGHTENED":
            if state == "SCATTER":
                self.ghosts_group.scatter(self.ghosts_group.ghosts, self.change)
                new_state = "CHASE"

            elif state == "CHASE":
                self.ghosts_group.chase(self.ghosts_group.ghosts, self.pacman.position, self.pacman.direction, self.blinky.position, self.change)
                new_state = "SCATTER"

            self.prev_state = state
            self.ghosts_group.state = state
            self.change = False

            if self.time == self.ghosts_group.time[state]:
                self.ghosts_group.state = new_state
                self.time = 0
                self.change = True
                print(self.time, "hey")

        else:

            if self.change == True:
                self.prev_time = self.time 
                self.time = 0

            self.ghosts_group.frightened(self.ghosts_group.ghosts, self.nodes_group, self.change)

            self.change = False
            self.ghosts_group.state = state

            if self.time == self.ghosts_group.time[state]:
                self.ghosts_group.state = self.prev_state
                self.time = self.prev_time
                self.change = True

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

            self.change = True
            self.update_ghost_state("FRIGHTENED")

        self.score_val["text"] = str(self.pacman.score)

    def inputs(self, event):
        if event.keysym in self.pacman_keys:
            if (self.pacman.col_pixel+8, self.pacman.row_pixel+8) in self.nodes_group.nodes_coord or self.pacman.directions[event.keysym.upper()] == self.pacman.direction*-1:
                self.pacman.next_direction(event.keysym, self.nodes_group)

        if event.keysym == "space":
            self.game.paused = not self.game.paused
            if self.game.paused != True:
                self.update_screen() 
                self.update_ghost_state(self.ghosts_group.state)


if __name__ == "__main__":
    game = Game("map.txt")
    dfisplay = Display(450, 576, game)