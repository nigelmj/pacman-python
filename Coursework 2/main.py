from tkinter import *
import PIL
from PIL import ImageTk
from pacman import *
from menu import *

class Display():
    def __init__(self, width, height):
        self.root = Tk()
        self.root.title("Pacman")
        self.width = str(width)
        self.height = str(height)
        self.root.geometry(self.width+"x"+self.height)
        self.root.resizable(False, False)

        self.game = Game("map.txt")
        self.game.start = False
        self.game.paused = True
        self.game.over = False

        self.pacman = self.game.pacman
        self.ghosts_group = self.game.ghosts_group

        self.blinky = self.ghosts_group.ghosts[0]
        self.pinky = self.ghosts_group.ghosts[1]
        self.inky = self.ghosts_group.ghosts[2]
        self.clyde = self.ghosts_group.ghosts[3]

        self.nodes_group = self.game.nodes_group
        self.pellets_group = self.game.pellets_group
        self.pellets_canvas = {}

        image = PIL.Image.open("Images/Map.jpg")
        self.bg = image.resize((448,496))
        self.bg = ImageTk.PhotoImage(self.bg)

        self.canvas_bg = Canvas(self.root, width=448, height=496)
        self.canvas_bg.place(x=-1, y=-1)
        self.canvas_bg.create_image(0, 0, image=self.bg, anchor="nw")

        self.menu = Menu(self.root, self.game, self.pacman, self.start_game, self.resume_game)
        self.menu.show_menu()

        self.game.player, self.pacman.key_up, self.pacman.key_left, self.pacman.key_down, self.pacman.key_right, self.pacman.key_pause = self.menu.load_settings()

        self.t = 1
        self.time = 0
        self.change = False

        self.root.mainloop()
        if self.pacman.lives > 0 and self.game.score > 0: self.menu.save_game()

    def start_game(self):

        self.menu.menu_frame.destroy()
        if self.game.start:

            del self.game
            self.canvas_bg.destroy()
            self.score_val.destroy()

            self.game = Game("map.txt")

            self.pacman = self.game.pacman
            self.ghosts_group = self.game.ghosts_group

            self.blinky = self.ghosts_group.ghosts[0]
            self.pinky = self.ghosts_group.ghosts[1]
            self.inky = self.ghosts_group.ghosts[2]
            self.clyde = self.ghosts_group.ghosts[3]

            self.nodes_group = self.game.nodes_group
            self.pellets_group = self.game.pellets_group
            self.pellets_canvas = {}

            self.canvas_bg = Canvas(self.root, width=448, height=496)
            self.canvas_bg.place(x=-1, y=-1)
            self.canvas_bg.create_image(0, 0, image=self.bg, anchor="nw")

            self.t = 1
            self.time = 0
            self.change = False

        self.game.start = True

        self.pacman.keys = {
            self.pacman.key_up : 'Up', 
            self.pacman.key_left : 'Left', 
            self.pacman.key_down : 'Down', 
            self.pacman.key_right : 'Right'
        }

        self.root.bind("<Key>", self.inputs)
        self.game.paused = False
        self.counter()
        self.display()
        self.update_screen()
        self.update_ghost_state("SCATTER")
    
    def resume_game(self):
        self.menu.menu_frame.destroy()

        self.pacman.keys = {
            self.pacman.key_up : 'Up', 
            self.pacman.key_left : 'Left', 
            self.pacman.key_down : 'Down', 
            self.pacman.key_right : 'Right'
        }

        self.game.paused = False
        self.counter()
        self.root.bind("<Key>", self.inputs)
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
                    ele = Canvas(self.canvas_bg, bg="black", highlightthickness=0)
                    ele.place(x=indcol*16, y=indrow*16, height=15, width=15)
                    oval = ele.create_oval(5, 5, 8, 8, fill="white")

                    self.pellets_canvas[(indrow, indcol)] = ele, oval
                    self.pellets_group.pellets_coord.append((indcol*16+8, indrow*16+8))

                elif (indrow, indcol) in self.pellets_group.power_pellets:
                    ele = Canvas(self.canvas_bg, bg="black", highlightthickness=0)
                    ele.place(x=indcol*16, y=indrow*16, height=15, width=15)
                    oval = ele.create_oval(2, 2, 11, 11, fill="white")
                    
                    self.pellets_canvas[(indrow, indcol)] = ele, oval
                    self.pellets_group.power_pellets_coord.append((indcol*16+8, indrow*16+8))

        row_pac, col_pac = self.pacman.position

        self.pacman.circle = Canvas(self.canvas_bg, bg="black", highlightthickness=0)
        self.pacman.circle.place(x=col_pac*16, y=row_pac*16, height=16, width=16)
        self.pacman.arc = self.pacman.circle.create_arc(0, 0, 15, 15, start = 225, extent = 270, fill="yellow")
        
        for ghost in self.ghosts_group.ghosts:

            row, col = ghost.position

            image = PIL.Image.open(f"Images/Up/Up_{ghost.name}.png")
            ghost.up = image.resize((16, 16))
            ghost.up = ImageTk.PhotoImage(ghost.up)
            ghost.pictures[-1] = ghost.up

            image = PIL.Image.open(f"Images/Left/Left_{ghost.name}.png")
            ghost.left = image.resize((16, 16))
            ghost.left = ImageTk.PhotoImage(ghost.left)
            ghost.pictures[-2] = ghost.left

            image = PIL.Image.open(f"Images/Down/Down_{ghost.name}.png")
            ghost.down = image.resize((16, 16))
            ghost.down = ImageTk.PhotoImage(ghost.down)
            ghost.pictures[1] = ghost.down

            image = PIL.Image.open(f"Images/Right/Right_{ghost.name}.png")
            ghost.right = image.resize((16, 16))
            ghost.right = ImageTk.PhotoImage(ghost.right)
            ghost.pictures[2] = ghost.right

            image = PIL.Image.open("Images/ghost_fright.png")
            ghost.fright_picture = image.resize((16, 16))
            ghost.fright_picture = ImageTk.PhotoImage(ghost.fright_picture)

            ghost.image = Canvas(self.canvas_bg, bg="black", highlightthickness=0)
            ghost.image.place(x=col*16, y=row*16, height=16, width=16)
            ghost.container = ghost.image.create_image(0, 0, image=ghost.left, anchor="nw")

        self.score_label = Label(self.root, text="Score: ", font=("Menlo", 20))
        self.score_label.place(x=10, y=31*16, width=80)
        self.score_val = Label(self.root, text=str(self.game.score), font=("Menlo", 20))
        self.score_val.place(x=80, y=31*16)

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
                row_pixel += self.pacman.speed
                self.pacman.circle.itemconfig(self.pacman.arc, start=315)

            elif direction == -1:
                row_pixel -= self.pacman.speed
                self.pacman.circle.itemconfig(self.pacman.arc, start=135)

            elif direction == 2:
                col_pixel += self.pacman.speed

                if col_pixel > 28*16:
                    col_pixel = -16
                self.pacman.circle.itemconfig(self.pacman.arc, start=45)

            elif direction == -2:
                col_pixel -= self.pacman.speed

                if col_pixel < -16:
                    col_pixel = 28*16
                self.pacman.circle.itemconfig(self.pacman.arc, start=225)

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
                row_pixel += self.ghosts_group.speed

            elif direction == -1:
                row_pixel -= self.ghosts_group.speed

            elif direction == 2:
                col_pixel += self.ghosts_group.speed

                if col_pixel > 28*16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= self.ghosts_group.speed

                if col_pixel < -16:
                    col_pixel = 28*16

            ghost.image.itemconfig(ghost.container, image = ghost.pictures[direction])

            ghost.image.place(x=col_pixel, y=row_pixel)
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
                self.ghosts_group.state = state
                self.pacman.speed = 8

            self.ghosts_group.frightened(self.ghosts_group.ghosts, self.nodes_group, self.change)

            self.change = False

            if self.time == self.ghosts_group.time[state]:
                self.ghosts_group.state = self.prev_state
                self.time = self.prev_time
                self.change = True
                self.pacman.speed = 4

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
        if event.keysym in self.pacman.keys:
            key = self.pacman.keys[event.keysym]
            if self.pacman.position in self.nodes_group.nodes or self.pacman.directions[key] == self.pacman.direction*-1:
                self.pacman.next_direction(self.pacman.directions[key], self.nodes_group)

        if event.keysym == self.pacman.key_pause:
            self.game.paused = not self.game.paused
            if self.game.paused != True:
                self.update_screen() 
                self.update_ghost_state(self.ghosts_group.state)
            else:
                self.menu.show_menu()
                self.root.unbind("<Key>")

    def check_game_status(self):
        for ghost in self.ghosts_group.ghosts:

            if ghost.row_pixel == self.pacman.row_pixel and ghost.col_pixel == self.pacman.col_pixel:
                if self.ghosts_group.state != "FRIGHTENED":
                    self.pacman.lives -= 1

                    if self.pacman.lives == 0:
                        self.game.paused = True 
                        self.game.over = True
                        f = open("GameSave.txt", "w")
                        f.close()

                    return
                else:
                    self.game.score += 200 * (self.ghost_eaten + 1)
                    self.ghost_eaten += 1

            elif abs(ghost.row_pixel-self.pacman.row_pixel)<5 and abs(ghost.col_pixel-self.pacman.col_pixel)<5 and ghost.direction == (self.pacman.direction * -1):
                if self.ghosts_group.state != "FRIGHTENED":
                    self.pacman.lives -= 1

                    if self.pacman.lives == 0:
                        self.game.paused = True 
                        self.game.over = True
                        f = open("GameSave.txt", "w")
                        f.close()

                    return
                else:
                    self.game.score += 200 * (self.ghost_eaten + 1)
                    self.ghost_eaten += 1

        if self.pellets_group.pellets == {} and self.pellets_group.power_pellets == {}:
            self.game.paused = True
            self.game.over = True
            self.menu.save_high_score()

if __name__ == "__main__":
    dfisplay = Display(450, 576)