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

        self.pacman_speed = 4
        self.ghost_speed = 4

        self.nodes_group = self.game.nodes_group
        self.pellets_group = self.game.pellets_group
        self.pellets_canvas = {}

        image = Image.open("Maze.jpeg")
        bg = image.resize((448,496))
        bg = ImageTk.PhotoImage(bg)

        self.canvas_bg = Canvas(self.root, width=448, height=496)
        self.canvas_bg.place(x=-1, y=-1)
        self.canvas_bg.create_image(0, 0, image=bg, anchor="nw")

        self.game.paused = True
        self.pacman_keys = ["Up", "Down", "Left", "Right"]
        self.root.bind("<Key>", self.inputs)
        self.t = 1
        self.time = 0
        self.change = False

        self.menu()

        self.root.mainloop()

    def menu(self):
        self.menu_frame = LabelFrame(self.root, bd=0)
        self.menu_frame.place(x=130, y=130, width=190, height=250)

        continue_button = Button(self.menu_frame, text="Continue", command=self.load_game, font=("Menlo", 16))
        continue_button.place(x=20, y=20, height=40, width=150)
        
        new_button = Button(self.menu_frame, text="New Game", command=self.start_game, font=("Menlo", 16))
        new_button.place(x=20, y=80, height=40, width=150)

        high_score_button = Button(self.menu_frame, text="High Scores", command=self.menu_frame.destroy, font=("Menlo", 16))
        high_score_button.place(x=20, y=140, height=40, width=150)

        cheat_button = Button(self.menu_frame, text="Enter Code", command=self.menu_frame.destroy, font=("Menlo", 16))
        cheat_button.place(x=20, y=200, height=40, width=150)

    def load_game(self):
        with open("GameSave.txt") as f:
            data = f.read().split("\n")

            self.game.lvl = int(data[0])
            self.pacman.lives = int(data[1])
            self.game.score = int(data[2])

            temp_pellets = data[3].split(":")
            temp_power_pellets = data[4].split(":")

            self.pellets_group.pellets = {}
            self.pellets_group.power_pellets = {}

            for pellet in temp_pellets:
                pellet = pellet[1:-1].split(',')

                row = int(pellet[0])
                col = int(pellet[1])
                self.pellets_group.pellets[(row, col)] = Pellet(row, col)

            for power_pellet in temp_power_pellets:
                power_pellet = power_pellet[1:-1].split(',')

                row = int(power_pellet[0])
                col = int(power_pellet[1])
                self.pellets_group.power_pellets[(row, col)] = PowerPellet(row, col)

            self.start_game()

    def start_game(self):

        self.menu_frame.destroy()
        self.game.paused = False
        self.display()
        self.counter()
        self.update_ghost_state("SCATTER")
        self.update_screen()
        
    def counter(self):
        if self.game.paused != True:
            self.time += 1
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
        oval = self.pacman.circle.create_arc(0, 0, 15, 15, start = 225, extent = 270, fill="yellow")
        
        for ghost in self.ghosts_group.ghosts:

            row, col = ghost.position

            ghost.circle = Canvas(self.root, bg="black", highlightthickness=0)
            ghost.circle.place(x=col*16, y=row*16, height=16, width=16)

            colour = self.ghosts_group.colour[ghost.name]
            oval = ghost.circle.create_oval(0, 0, 15, 15, fill=colour)
            ghost.oval = oval

        self.score_label = Label(self.root, text="Score: ", font=("Menlo", 20))
        self.score_label.place(x=10, y=31*16, width=80)
        self.score_val = Label(self.root, text=str(self.game.score), font=("Menlo", 20))
        self.score_val.place(x=80, y=31*16)

        self.save_button = Button(self.root, text="Save", font=("Menlo", 14), command=self.save_game)
        self.save_button.place(x=150, y = 31*16)

    def update_screen(self):
        
        self.update_pellets(self.t)
        self.update_pacman(self.pacman.direction)
        self.update_ghosts()
        self.update_ghost_state(self.ghosts_group.state)

        if not self.game.paused:
            self.root.after(70, self.update_screen)

    def update_pellets(self, t):
        if t == 2:
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

        self.pacman.next_direction(direction, self.nodes_group)
        if self.pacman.stopped != True:
            row_pixel, col_pixel = self.pacman.row_pixel, self.pacman.col_pixel

            if direction == 1:
                row_pixel += self.pacman_speed

            elif direction == -1:
                row_pixel -= self.pacman_speed

            elif direction == 2:
                col_pixel += self.pacman_speed

                if col_pixel > 28*16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= self.pacman_speed

                if col_pixel < -16:
                    col_pixel = 28*16

            self.pacman.circle.place(x=col_pixel, y=row_pixel)
            self.pacman.row_pixel, self.pacman.col_pixel = row_pixel, col_pixel
            self.pacman.position = self.pacman.get_position(row_pixel, col_pixel)
            self.update_score()
        self.check_game_status()

    def update_ghosts(self):

        for ghost in self.ghosts_group.ghosts:
            if ghost.position in self.nodes_group.nodes:
                
                if (ghost.col_pixel+8, ghost.row_pixel+8) in self.nodes_group.nodes_coord:
                    ghost.next_direction_ghost(self.nodes_group, ghost.target)

            row_pixel, col_pixel = ghost.row_pixel, ghost.col_pixel
            direction = ghost.direction

            if direction == 1: 
                row_pixel += self.ghost_speed

            elif direction == -1:
                row_pixel -= self.ghost_speed

            elif direction == 2:
                col_pixel += self.ghost_speed

                if col_pixel > 28*16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= self.ghost_speed

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

        else:

            if self.change == True:
                self.prev_time = self.time 
                self.time = 0
                self.ghost_eaten = 0

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
            self.game.score += self.pellets_group.pellets[self.pacman.position].points
            self.pellets_group.pellets.pop(self.pacman.position)
            self.pellets_group.pellets_coord.remove(pacman_coord)
            self.pellets_canvas[self.pacman.position][0].destroy()

        elif pacman_coord in self.pellets_group.power_pellets_coord:
            self.game.score += self.pellets_group.power_pellets[self.pacman.position].points
            self.pellets_group.power_pellets.pop(self.pacman.position)
            self.pellets_group.power_pellets_coord.remove(pacman_coord)
            self.pellets_canvas[self.pacman.position][0].destroy()

            self.change = True
            self.update_ghost_state("FRIGHTENED")

        self.score_val["text"] = str(self.game.score)

    def inputs(self, event):
        if event.keysym in self.pacman_keys:
            if self.pacman.position in self.nodes_group.nodes or self.pacman.directions[event.keysym] == self.pacman.direction*-1:
                self.pacman.next_direction(self.pacman.directions[event.keysym], self.nodes_group)

        if event.keysym == "space":
            self.game.paused = not self.game.paused
            if self.game.paused != True:
                self.update_screen() 
                self.update_ghost_state(self.ghosts_group.state)

    def check_game_status(self):
        for ghost in self.ghosts_group.ghosts:

            if ghost.row_pixel == self.pacman.row_pixel and ghost.col_pixel == self.pacman.col_pixel:
                if self.ghosts_group.state != "FRIGHTENED":
                    self.game.paused = True
                    return
                else:
                    self.game.score += 200 * (self.ghost_eaten + 1)
                    self.ghost_eaten += 1

            if abs(ghost.row_pixel-self.pacman.row_pixel)<5 and abs(ghost.col_pixel-self.pacman.col_pixel)<5 and ghost.direction == (self.pacman.direction * -1):
                if self.ghosts_group.state != "FRIGHTENED":
                    self.game.paused = True
                    return
                else:
                    self.game.score += 200 * (self.ghost_eaten + 1)
                    self.ghost_eaten += 1

        if self.pellets_group.pellets == {} and self.pellets_group.power_pellets == {}:
            self.game.paused = True
            self.save_high_score()

    def save_high_score(self):

        with open("HighScore.txt") as f:
            high_score_list = f.read().split()
            high_score = int(high_score_list[0])

            if self.game.score > high_score:
                high_score_list = [str(self.game.score)] + high_score_list

                if len(high_score_list) > 3:
                    high_score_list = high_score_list[:3]

                with open("HighScore.txt", "w") as f:
                    high_score_list = "\n".join(high_score_list)
                    f.write(high_score_list)

    def save_game(self):

        temp_pellets = self.pellets_group.pellets.keys()
        temp_pellets = [str(coord) for coord in temp_pellets]
        temp_pellets = ":".join(temp_pellets)

        temp_power_pellets = self.pellets_group.power_pellets.keys()
        temp_power_pellets = [str(coord) for coord in temp_power_pellets]
        temp_power_pellets = ":".join(temp_power_pellets)

        game_details = [
            str(self.game.lvl),
            str(self.pacman.lives),
            str(self.game.score),
            temp_pellets,
            temp_power_pellets
        ]
        game_details = "\n".join(game_details)

        with open("GameSave.txt", "w") as f:
            f.write(game_details)

if __name__ == "__main__":
    game = Game("map.txt")
    dfisplay = Display(450, 576, game)