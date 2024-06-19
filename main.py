'''
Nigel Martin Jose
Coursework 2
Task: To create a game using Tkinter
My game: Replica of Retro Pacman

Resolution: 1440x900
Ghosts images created using https://www.pixilart.com/
Boss key image from https://unsplash.com/photos/JKUTrJ4vK00
Background map edited from https://pixabay.com/illustrations/pacman-game-video-game-nintendo-4121590/
Pacman and pellets created using canvas shapes
'''
from tkinter import *
import PIL
from PIL import ImageTk
from pacman import *
from menu import *


class Display():
    '''Display class for the main window'''

    def __init__(self, width, height):  # initialize the window , and geometry, title
        self.root = Tk()
        self.root.title("Pacman")
        self.width = str(width)
        self.height = str(height)
        self.root.geometry(self.width + "x" + self.height)
        self.root.resizable(False, False)

        self.game = Game("map.txt")            # create a game object
        self.game.start = False
        self.game.paused = True
        self.game.over = False
        self.game.won = False

        self.pacman = self.game.pacman              # get pacman and the ghost group
        self.ghosts_group = self.game.ghosts_group

        self.blinky = self.ghosts_group.ghosts[0]
        self.pinky = self.ghosts_group.ghosts[1]
        self.inky = self.ghosts_group.ghosts[2]
        self.clyde = self.ghosts_group.ghosts[3]

        self.nodes_group = self.game.nodes_group
        self.pellets_group = self.game.pellets_group
        self.pellets_canvas = {}

        # create image for the background
        image = PIL.Image.open("images/map.jpg")
        self.bg = image.resize((448, 496))
        self.bg = ImageTk.PhotoImage(self.bg)

        self.canvas_bg = Canvas(self.root, width=448, height=496)
        self.canvas_bg.place(x=-1, y=-1)
        self.canvas_bg.create_image(0, 0, image=self.bg, anchor="nw")

        image = image = PIL.Image.open("images/boss_key.jpeg")
        self.boss_key_pic = image.resize((450, 576))
        self.boss_key_pic = ImageTk.PhotoImage(self.boss_key_pic)

        self.menu = Menu(
            self.root,
            self.game,
            self.pacman,
            self.ghosts_group,
            self.start_game,
            self.resume_game)  # create the menu object
        self.menu.show_menu()

        self.game.player, self.pacman.key_up, self.pacman.key_left, self.pacman.key_down, self.pacman.key_right, self.pacman.key_pause, self.pacman.key_boss = self.menu.load_settings()

        self.t = 1          # set the time to 0 and player settings
        self.time = 0
        self.change = False

        self.root.mainloop()
        if self.pacman.lives > 0 and self.game.score > 0 and not self.game.won:
            self.menu.save_game()  # only save if the game is not over yet

    def start_game(self):
        '''Starts the games by calling the necessary update and display functions'''
        self.menu.menu_frame.destroy()          # destroy and the menu frame and start the game
        if self.game.start:

            del self.game
            self.canvas_bg.destroy()
            self.score_val.destroy()

            # delete the previous game and start new if players starts new in
            # between
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

        self.game.start = True          # set variables again as well as player controls
        self.game.over = False
        self.game.won = False

        self.game.player, self.pacman.key_up, self.pacman.key_left, self.pacman.key_down, self.pacman.key_right, self.pacman.key_pause, self.pacman.key_boss = self.menu.load_settings()
        self.pacman.keys = {
            self.pacman.key_up: 'Up',
            self.pacman.key_left: 'Left',
            self.pacman.key_down: 'Down',
            self.pacman.key_right: 'Right'
        }

        self.root.bind("<Key>", self.inputs)        # bind the keys
        self.game.paused = True

        self.display()

        self.timeout_period = 3         # time out variable to let the player get ready
        self.timeout_label = Label(
            self.canvas_bg,
            text="",
            font=(
                "Menlo",
                16,
                "bold"),
            fg="lightblue",
            bg="black")
        self.timeout_label.place(x=13 * 16 - 10, y=17 * 16 - 5)
        self.game.spawn()
        self.update_screen()
        self.timeout()

    def resume_game(self):
        '''Resumes the game after the player paused it'''
        self.menu.menu_frame.destroy()
        # destroys the menu and unpauses the game as well as sets controls if
        # there are changes and binds the keys to inputs
        self.lives_frame.destroy()
        self.display_lives()

        self.pacman.keys = {
            self.pacman.key_up: 'Up',
            self.pacman.key_left: 'Left',
            self.pacman.key_down: 'Down',
            self.pacman.key_right: 'Right'
        }

        self.game.paused = False
        self.timer()
        self.root.bind("<Key>", self.inputs)
        self.update_screen()

    def timer(self):
        '''Creates a timer for changing ghost states'''
        if self.game.paused != True:                # continue timer only if game is not paused
            self.time += 1
            self.root.after(1000, self.timer)

    def display(self):
        '''Displays pellets, creates nodes_coords, images for ghosts and arc for pacman'''
        for indrow, row in enumerate(self.game.grid):
            for indcol, col in enumerate(
                    row):                  # display the pellets

                if self.game.grid[indrow][indcol] in ['+', 'n', 'P', 'G']:
                    self.nodes_group.nodes_coord.append(
                        (indcol * 16 + 8, indrow * 16 + 8))         # add coordinates to nodes group

                if (indrow, indcol) in self.pellets_group.pellets:
                    # create the pellets and the power pellets
                    ele = Canvas(
                        self.canvas_bg,
                        bg="black",
                        highlightthickness=0)
                    ele.place(
                        x=indcol * 16,
                        y=indrow * 16,
                        height=15,
                        width=15)
                    oval = ele.create_oval(5, 5, 8, 8, fill="white")

                    self.pellets_canvas[(indrow, indcol)] = ele, oval
                    self.pellets_group.pellets_coord.append(
                        (indcol * 16 + 8, indrow * 16 + 8))

                elif (indrow, indcol) in self.pellets_group.power_pellets:
                    ele = Canvas(
                        self.canvas_bg,
                        bg="black",
                        highlightthickness=0)
                    ele.place(
                        x=indcol * 16,
                        y=indrow * 16,
                        height=15,
                        width=15)
                    oval = ele.create_oval(2, 2, 11, 11, fill="white")

                    self.pellets_canvas[(indrow, indcol)] = ele, oval
                    self.pellets_group.power_pellets_coord.append(
                        (indcol * 16 + 8, indrow * 16 + 8))

        row_pac, col_pac = self.pacman.position

        self.pacman.circle = Canvas(
            self.canvas_bg,
            bg="black",
            highlightthickness=0)               # create the pacman canvas arc
        self.pacman.circle.place(
            x=col_pac * 16,
            y=row_pac * 16,
            height=16,
            width=16)
        self.pacman.arc = self.pacman.circle.create_arc(
            0, 0, 15, 15, start=225, extent=270, fill="yellow")

        # for each ghost, load its various images and set the canvas
        for ghost in self.ghosts_group.ghosts:

            row, col = ghost.position

            image = PIL.Image.open(f"images/up/{ghost.name}.png")
            ghost.up = image.resize((16, 16))
            ghost.up = ImageTk.PhotoImage(ghost.up)
            ghost.pictures[-1] = ghost.up

            image = PIL.Image.open(f"images/left/{ghost.name}.png")
            ghost.left = image.resize((16, 16))
            ghost.left = ImageTk.PhotoImage(ghost.left)
            ghost.pictures[-2] = ghost.left

            image = PIL.Image.open(f"images/down/{ghost.name}.png")
            ghost.down = image.resize((16, 16))
            ghost.down = ImageTk.PhotoImage(ghost.down)
            ghost.pictures[1] = ghost.down

            image = PIL.Image.open(f"images/right/{ghost.name}.png")
            ghost.right = image.resize((16, 16))
            ghost.right = ImageTk.PhotoImage(ghost.right)
            ghost.pictures[2] = ghost.right

            image = PIL.Image.open("images/frightened_ghost_1.png")
            ghost.fright_picture = image.resize((16, 16))
            ghost.fright_picture = ImageTk.PhotoImage(ghost.fright_picture)

            ghost.image = Canvas(
                self.canvas_bg,
                bg="black",
                highlightthickness=0)
            ghost.image.place(x=col * 16, y=row * 16, height=16, width=16)
            ghost.container = ghost.image.create_image(
                0, 0, image=ghost.left, anchor="nw")

        self.score_label = Label(self.root, text="Score: ", font=("Menlo", 20))
        self.score_label.place(x=10, y=31 * 16, width=80)
        self.score_val = Label(
            self.root, text=str(
                self.game.score), font=(
                "Menlo", 20))
        self.score_val.place(x=80, y=31 * 16)

        self.display_lives()

    def display_lives(self):
        '''Displays the number of lives left'''

        # displays the lives remaining for pacman
        self.lives_frame = LabelFrame(self.root, bd=0)
        self.lives_frame.place(x=150, y=31 * 16, width=300, height=50)
        for life in range(self.pacman.lives):

            self.life_circle = Canvas(self.lives_frame, highlightthickness=0)
            self.life_circle.place(x=260 - (30 * life),
                                   y=5, height=21, width=21)
            self.life_arc = self.life_circle.create_arc(
                0, 0, 20, 20, start=225, extent=270, fill="yellow")

    def update_screen(self):
        '''Updates the screen every 70ms'''
        self.update_pellets(self.t)
        self.update_pacman(self.pacman.direction)  # updates the screen
        self.update_ghosts()
        self.update_ghost_state(self.ghosts_group.state)

        if not self.game.paused:
            self.root.after(70, self.update_screen)

    def update_pellets(self, t):
        '''Creates the blinking effect of the power pellets'''          # updates the blinking of the pellets,
        if t == 2:
            for coord in self.pellets_group.power_pellets:

                power = self.pellets_group.power_pellets[coord]

                ele = self.pellets_canvas[(coord)][0]
                oval = self.pellets_canvas[(coord)][1]

                if power.visible:                                   # if visible, blink, else stay open
                    ele.itemconfig(oval, fill="white")
                else:
                    ele.itemconfig(oval, fill="black")

                self.pellets_group.power_pellets[coord].visible = not power.visible
            self.t = 1
        else:
            self.t += 1

    def update_pacman(self, direction):
        '''Updates the position of pacman'''
        self.pacman.next_direction(
            direction,
            self.nodes_group)             # update position of pacman only if he is not stopped
        if not self.pacman.stopped:
            row_pixel, col_pixel = self.pacman.row_pixel, self.pacman.col_pixel

            if direction == 1:
                row_pixel += self.pacman.speed
                self.pacman.circle.itemconfig(self.pacman.arc, start=315)

            elif direction == -1:
                row_pixel -= self.pacman.speed
                self.pacman.circle.itemconfig(self.pacman.arc, start=135)

            elif direction == 2:
                col_pixel += self.pacman.speed

                if col_pixel > 28 * 16:                   # moves pacman back to the very left of the screen
                    col_pixel = -16
                self.pacman.circle.itemconfig(self.pacman.arc, start=45)

            elif direction == -2:
                col_pixel -= self.pacman.speed

                if col_pixel < -16:                 # moves pacman back to the very left of the screen
                    col_pixel = 28 * 16
                self.pacman.circle.itemconfig(self.pacman.arc, start=225)

            # set the circle and the arc according to the position and
            # direction and update the score
            self.pacman.circle.place(x=col_pixel, y=row_pixel)
            self.pacman.row_pixel, self.pacman.col_pixel = row_pixel, col_pixel
            self.pacman.position = self.pacman.get_position(
                row_pixel, col_pixel)
            self.update_score()

        elif self.pacman.alive == False:
            self.pacman.circle.itemconfig(self.pacman.arc, start=225)
            self.pacman.circle.place(
                x=self.pacman.col_pixel,
                y=self.pacman.row_pixel)

        self.check_game_status()

    def update_ghosts(self):
        '''Updates the position of the ghosts'''
        for ghost in self.ghosts_group.ghosts:
            # updates the options of the ghosts similar to pacman
            if ghost.position in self.nodes_group.nodes:

                if (ghost.col_pixel + 8, ghost.row_pixel +
                        8) in self.nodes_group.nodes_coord:
                    ghost.next_direction_ghost(self.nodes_group, ghost.target)

            row_pixel, col_pixel = ghost.row_pixel, ghost.col_pixel
            direction = ghost.direction

            speed = self.ghosts_group.speed
            if ghost.died and not ghost.in_home:
                speed = self.ghosts_group.died_speed
                # if the ghost is dead, change speed to 16, and position it
                # correctly so it can detect the nodes
                if row_pixel % 16 != 0 or col_pixel % 16 != 0:
                    row_pixel -= row_pixel % 16
                    col_pixel -= col_pixel % 16

            if direction == 1:
                row_pixel += speed

            elif direction == -1:
                row_pixel -= speed

            elif direction == 2:
                col_pixel += speed

                if col_pixel > 28 * 16:
                    col_pixel = -16

            elif direction == -2:
                col_pixel -= speed

                if col_pixel < -16:
                    col_pixel = 28 * 16

            # set image according to the ghost and its direction
            ghost.image.itemconfig(
                ghost.container,
                image=ghost.pictures[direction])

            ghost.image.place(x=col_pixel, y=row_pixel)
            ghost.row_pixel, ghost.col_pixel = row_pixel, col_pixel
            ghost.position = ghost.get_position(
                row_pixel, col_pixel, ghost.direction)

    def update_ghost_state(self, state):
        '''Updates the ghost state by checking the time left on the timer'''
        if state != "FRIGHTENED":
            if state == "SCATTER":
                # update the ghost state according to the timer
                self.ghosts_group.scatter(
                    self.ghosts_group.ghosts, self.change)
                new_state = "CHASE"

            elif state == "CHASE":
                self.ghosts_group.chase(
                    self.ghosts_group.ghosts,
                    self.pacman.position,
                    self.pacman.direction,
                    self.blinky.position,
                    self.change)
                new_state = "SCATTER"           # call opposite functions after timer reaches end

            self.prev_state = state
            self.ghosts_group.state = state
            self.change = False

            if self.time == self.ghosts_group.time[state]:
                self.ghosts_group.state = new_state
                self.time = 0
                self.change = True

        else:           # if state is frightened

            if self.change:         # set variables for initial second
                self.prev_time = self.time
                self.time = 0
                self.ghost_eaten = 0
                self.ghosts_group.state = state
                self.pacman.speed = 8

            self.ghosts_group.frightened(
                self.ghosts_group.ghosts,
                self.nodes_group,
                self.change)       # call the function

            self.change = False

            # at the end of function, go back to prevous state with previous
            # time
            if self.time == self.ghosts_group.time[state]:
                self.ghosts_group.state = self.prev_state
                self.time = self.prev_time
                self.change = True
                self.pacman.speed = 4

    def update_score(self):
        '''Updates the score and initializes frightened state if power pellet is consumed'''
        pacman_coord = self.pacman.col_pixel + 8, self.pacman.row_pixel + 8

        # updates the scores, pellets give you 10 points, power pellets give
        # you 50
        if pacman_coord in self.pellets_group.pellets_coord:
            self.game.score += self.pellets_group.points["Pellet"]
            self.pellets_group.pellets.pop(self.pacman.position)
            self.pellets_group.pellets_coord.remove(pacman_coord)
            self.pellets_canvas[self.pacman.position][0].destroy()

        elif pacman_coord in self.pellets_group.power_pellets_coord:
            self.game.score += self.pellets_group.points["PowerPellet"]
            self.pellets_group.power_pellets.pop(self.pacman.position)
            self.pellets_group.power_pellets_coord.remove(pacman_coord)
            self.pellets_canvas[self.pacman.position][0].destroy()

            self.change = True
            # set state to frightened
            self.update_ghost_state("FRIGHTENED")

        self.score_val["text"] = str(self.game.score)

    def inputs(self, event):
        '''Checks for inputs from player and calls the necessary functions'''
        if event.keysym.lower() in self.pacman.keys:                # check inputs from the player
            key = self.pacman.keys[event.keysym.lower()]
            if self.pacman.position in self.nodes_group.nodes or self.pacman.directions[
                    key] == self.pacman.direction * -1:
                # checks the inputs for moving pacman, only works if pacman in
                # a node or direction is reversed
                self.pacman.next_direction(
                    self.pacman.directions[key], self.nodes_group)

        if event.keysym.lower() == self.pacman.key_pause:
            # pause the game and bring the menu as well as unbind the key to
            # prevent errors
            self.game.paused = not self.game.paused
            if self.game.paused:
                self.menu.show_menu()
                self.root.unbind("<Key>")

        if event.keysym.lower() == self.pacman.key_boss:

            self.game.paused = not self.game.paused
            if self.game.paused != True:                        # quickly bring up fake image for productivity,
                # I don't have to, I'm quite good with tab switcher
                self.boss_key_screen.destroy()
                self.update_screen()  # *insert sunglasses emoji*
                self.timer()

            else:
                # otherwise remove the screen, (key works both ways)
                self.boss_key_screen = Canvas(self.root, width=450, height=576)
                self.boss_key_screen.place(x=0, y=0)
                self.boss_key_screen.create_image(
                    0, 0, image=self.boss_key_pic, anchor="nw")

    def check_game_status(self):
        '''Checks the status of the game after every update'''
        for ghost in self.ghosts_group.ghosts:

            # check if ghost and pacman are in same coordinate
            if ghost.row_pixel == self.pacman.row_pixel and ghost.col_pixel == self.pacman.col_pixel:

                # check if state is frightened or new spawn
                if self.ghosts_group.state != "FRIGHTENED" or ghost.new_spawned:
                    self.pacman.lives -= 1
                    self.pacman.alive = False           # subtract 1 from pacman lives, pause the game

                    self.lives_frame.destroy()
                    self.display_lives()

                    self.game.paused = True
                    self.time = 0

                    if self.pacman.lives > 0:       # if there are more lives, call the timout function to restart game
                        self.timeout_period = 3
                        self.timeout_label = Label(
                            self.canvas_bg, text="", font=(
                                "Menlo", 16, "bold"), fg="lightblue", bg="black")
                        self.timeout_label.place(x=13 * 16 - 8, y=17 * 16 - 5)
                        self.game.spawn()
                        self.update_screen()

                        self.timeout()

                    if self.pacman.lives == 0:      # if there are no lives, end game with game over text
                        self.game.over = True
                        self.game_over_label = Label(
                            self.canvas_bg, text="GAME OVER!", font=(
                                "Menlo", 16, "bold"), fg="lightblue", bg="black")
                        self.game_over_label.place(
                            x=11 * 16 - 10, y=17 * 16 - 5)
                        # open the save file and empty it
                        f = open("gameFiles/save_data.txt", "w")
                        f.close()

                    return
                else:
                    # if state is frightened, add 200 points to the pacman
                    # score (multiplies by how many ghosts he eats)
                    self.game.score += 200 * (self.ghost_eaten + 1)
                    self.ghost_eaten += 1
                    ghost.died = True

            elif abs(ghost.row_pixel - self.pacman.row_pixel) < 5 and abs(ghost.col_pixel - self.pacman.col_pixel) < 5 and ghost.direction == (self.pacman.direction * -1):

                # similar condition to above, only checks for rare cases when
                # pacman and ghost intersect and don't match coordinates
                if self.ghosts_group.state != "FRIGHTENED" or ghost.new_spawned:
                    self.pacman.lives -= 1
                    self.pacman.alive = False

                    self.lives_frame.destroy()
                    self.display_lives()

                    self.game.paused = True
                    self.time = 0

                    if self.pacman.lives > 0:

                        self.timeout_period = 3
                        self.timeout_label = Label(
                            self.canvas_bg, text="", font=(
                                "Menlo", 16, "bold"), fg="lightblue", bg="black")
                        self.timeout_label.place(x=13 * 16 - 10, y=17 * 16 - 5)
                        self.game.spawn()
                        self.update_screen()

                        self.timeout()

                    if self.pacman.lives == 0:
                        self.game.over = True
                        self.game_over_label = Label(
                            self.canvas_bg, text="GAME OVER!", font=(
                                "Menlo", 16, "bold"), fg="lightblue", bg="black")
                        self.game_over_label.place(
                            x=11 * 16 - 8, y=17 * 16 - 5)
                        f = open("gameFiles/save_data.txt", "w")
                        f.close()

                    return
                else:
                    self.game.score += 200 * (self.ghost_eaten + 1)
                    self.ghost_eaten += 1
                    ghost.died = True

        if self.pellets_group.pellets == {} and self.pellets_group.power_pellets == {
        }:     # if all pellets have been eaten, pacman wins
            self.game.paused = True
            self.game.over = True       # call the you won function to show the text
            self.game.won = True
            self.win_label = Label(
                self.canvas_bg, text="YOU WON!", font=(
                    "Menlo", 16, "bold"), fg="lightblue", bg="black")
            self.win_label.place(x=12 * 16 - 8, y=17 * 16 - 5)
            self.you_won()              # YAYYYYY YOU WONNNNN!!!
            self.menu.save_high_score()     # save the high score
            f = open("gameFiles/save_data.txt", "w")
            f.close()

    def timeout(self):
        '''Creates a timout period when a new game is started or pacman loses a life'''
        if self.timeout_period == -1:
            # sets everything to initial conditions to begin playing game
            self.pacman.alive = True
            self.pacman.stopped = False
            self.game.paused = False
            self.timeout_label.destroy()
            self.ghosts_group.state = "SCATTER"
            self.update_screen()                # updates screen and calls timer
            self.timer()

        elif self.timeout_period == 0:
            self.timeout_label["text"] = "READY!"       # text says ready
            self.timeout_period -= 1
            self.root.after(1000, self.timeout)

        else:
            self.timeout_label["text"] = "  " + str(self.timeout_period)
            self.timeout_period -= 1         # text says the time remaining
            self.root.after(1000, self.timeout)

    def you_won(self):
        # keep changing the colour of the text after wining
        if self.win_label["fg"] == "lightblue":
            self.win_label["fg"] = "white"
        else:
            self.win_label["fg"] = "lightblue"
        self.root.after(400, self.you_won)


if __name__ == "__main__":
    display = Display(450, 576)
