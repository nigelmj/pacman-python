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

        self.blinky = Ghost("Blinky", (0, 25), 1, 23)
        self.pinky = Ghost("Pinky", (0, 3), 1, 7)
        self.inky = Ghost("Inky", (30, 27), 29, 23)
        self.clyde = Ghost("Clyde", (30, 0), 29, 7)

        self.ghost_group = [self.blinky, self.pinky, self.inky, self.clyde]

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
        row_bli, col_bli = self.blinky.position
        row_pin, col_pin = self.pinky.position
        row_ink, col_ink = self.inky.position
        row_cly, col_cly = self.clyde.position

        self.pacman.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.pacman.circle.place(x=col_pac*16, y=row_pac*16, height=16, width=16)
        oval = self.pacman.circle.create_oval(0, 0, 15, 15, fill="yellow")
        
        self.blinky.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.blinky.circle.place(x=col_bli*16, y=row_bli*16, height=16, width=16)
        oval = self.blinky.circle.create_oval(0, 0, 15, 15, fill="red")

        self.pinky.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.pinky.circle.place(x=col_pin*16, y=row_pin*16, height=16, width=16)
        oval = self.pinky.circle.create_oval(0, 0, 15, 15, fill="pink")

        self.inky.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.inky.circle.place(x=col_ink*16, y=row_ink*16, height=16, width=16)
        oval = self.inky.circle.create_oval(0, 0, 15, 15, fill="lightblue")

        self.clyde.circle = Canvas(self.root, bg="black", highlightthickness=0)
        self.clyde.circle.place(x=col_cly*16, y=row_cly*16, height=16, width=16)
        oval = self.clyde.circle.create_oval(0, 0, 15, 15, fill="orange")

        self.score_label = Label(self.root, text="Score: ", font=("Menlo", 20))
        self.score_label.place(x=10, y=31*16, width=80)
        self.score_val = Label(self.root, text=str(self.pacman.score), font=("Menlo", 20))
        self.score_val.place(x=80, y=31*16)
    
    def update_screen(self):
        
        self.update_pellets(self.t)
        self.update_pacman(self.pacman.direction)
        self.update_ghosts()

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

    def update_ghosts(self):

        for ghost in self.ghost_group:
            if ghost.position in self.nodes_group.nodes:
                if (ghost.col_pixel+8, ghost.row_pixel+8) in self.nodes_group.nodes_coord:
                    ghost.next_direction(self.nodes_group, ghost.target)

            row_pixel, col_pixel = ghost.row_pixel, ghost.col_pixel
            direction = ghost.direction

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

            ghost.circle.place(x=col_pixel, y=row_pixel)
            ghost.row_pixel, ghost.col_pixel = row_pixel, col_pixel
            ghost.position = ghost.get_position(row_pixel, col_pixel, ghost.direction)
            ghost.next_target(self.pacman.position, self.pacman.direction, self.blinky.position)
    
    def update_ghost_state(self):
        for ghost in self.ghost_group:
            pass
    
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