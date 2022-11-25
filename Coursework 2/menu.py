from tkinter import *
from pacman import *

class Menu():
    '''Menu class for showing menu'''
    def __init__(self, root, game, pacman, ghosts_group, start_game, resume_game):      # gets all the required variables from display class 
        self.root = root    
        self.game = game
        self.pacman = pacman
        self.ghosts_group = ghosts_group
        self.pellets_group = self.game.pellets_group
        self.start_game = start_game
        self.resume_game = resume_game

    def show_menu(self):
        '''Creates a menu and shows different available options'''
        self.menu_frame = LabelFrame(self.root, bd=0)       # create the frame
        self.menu_frame.place(x=100, y=100, width=250, height=300)

        pos = 30        # variable for positioning the buttons

        if self.check_game_save() and not self.game.start:      # check if a game was saved, if it was, option for continue button

            continue_button = Button(self.menu_frame, text="Continue", command=self.load_game, font=("Menlo", 15))
            continue_button.place(x=50, y=20, height=40, width=150)

            pos = 55        # increment the positioning variable to make space for the first button

        elif self.game.start and self.game.paused:      # check if the game is currently paused
            resume_button = Button(self.menu_frame, text="Resume", command=self.resume_game, font=("Menlo", 15))
            resume_button.place(x=50, y=20, height=40, width=150)

            pos = 55
        
        new_button = Button(self.menu_frame, text="New Game", command=self.start_game, font=("Menlo", 15))      # option to start a new game, the command is from display class
        new_button.place(x=50, y=20+pos, height=40, width=150)

        high_score_button = Button(self.menu_frame, text="Leaderboard", command=self.show_high_score, font=("Menlo", 15))       # option to view the leaderboard
        high_score_button.place(x=50, y=75+pos, height=40, width=150)

        cheat_button = Button(self.menu_frame, text="Enter Code", command=self.enter_code, font=("Menlo", 15))      # option to enter cheat codes
        cheat_button.place(x=50, y=130+pos, height=40, width=150)

        settings_button = Button(self.menu_frame, text="Settings", command=self.show_settings, font=("Menlo", 15))      # option to show settings and change if needed
        settings_button.place(x=50, y=185+pos, height=40, width=150)

    def save_high_score(self):
        '''Saves a new high score after the end of a game'''
        with open("HighScore.txt") as f:
            high_score_list = f.read().split("\n")          # reads from high score text file, splits the paragraph by newline
            for high_score in high_score_list:

                index = high_score_list.index(high_score)       # splits each line into name and highscore
                high_score = high_score.split()
                high_score_val = int(high_score[1])

                if self.game.score > high_score_val:        # checking if current score is greater

                    self.game.player = self.game.player.strip()

                    high_score_list = high_score_list[0:index] + [self.game.player + ": " + str(self.game.score)] + high_score_list[index:]     # insert the current score inbetween the other scores

                    if len(high_score_list) > 5:
                        high_score_list = high_score_list[:5]       # storing only top 5 high scores

                    with open("HighScore.txt", "w") as f:
                        high_score_list = "\n".join(high_score_list)        # write the new highscore list (after turning it to a string) into the file
                        f.write(high_score_list)

                    break

    def show_high_score(self):
        '''Creates a frame showing the top 5 scores'''
        self.high_score_frame = LabelFrame(self.root, bd=0)         # create the frame
        self.high_score_frame.place(x=100, y=100, width=250, height=300)

        with open("HighScore.txt") as f:        # open the high score file in read mode
            high_score_list = f.read().split("\n")
            for index in range(len(high_score_list)):       # for each high score, add the position number before the name and score
                text = str(index+1) + ". " + high_score_list[index]
                row = int(text[0])

                score_info = Label(self.high_score_frame, text=text, font=("Menlo", 15))        # paste the text onto a score lablel
                score_info.place(x=50, y=20+(40*(row-1)), height=40, width=150)

        back_button = Button(self.high_score_frame, text="Back", command=self.high_score_frame.destroy, font=("Menlo", 15))     # back button to go back to menu
        back_button.place(x=50, y=240, height=40, width=150)

    def save_game(self):
        '''Saves the game onto a file after the player has closed the window'''
        temp_pellets = self.pellets_group.pellets.keys()            # for saving game, necessary info are pacman lives, game score, number of normal and power pellets remaining
        temp_pellets = [str(coord) for coord in temp_pellets]       # taking the positions of the pellets and joining them into a string
        temp_pellets = ":".join(temp_pellets)

        temp_power_pellets = self.pellets_group.power_pellets.keys()        # taking the positions of the power pellets and joining them into a string
        temp_power_pellets = [str(coord) for coord in temp_power_pellets]
        temp_power_pellets = ":".join(temp_power_pellets)

        game_details = [                # list containing game info to be written to file after converting to string
            str(self.pacman.lives),
            str(self.game.score),
            temp_pellets,
            temp_power_pellets
        ]
        game_details = "\n".join(game_details)      # join the list to string using newline char

        with open("GameSave.txt", "w") as f:        # write to file
            f.write(game_details)

    def check_game_save(self):
        '''Checks if there is an existing save file for the game'''
        with open("GameSave.txt") as f:
            data = f.read()         # checking if there is a game that was saved earlier
            if data == "":
                return False
            return True

    def load_game(self):
        '''Loads the game contents from the save file'''
        with open("GameSave.txt") as f:         # reads from the save file
            data = f.read().split("\n")

            self.pacman.lives = int(data[0])         # convert the strings into required integer forms
            self.game.score = int(data[1])

            temp_pellets = data[2].split(":")           # split the pellets and power pellets info to list
            temp_power_pellets = data[3].split(":")

            self.pellets_group.pellets = {}             # create empty dictionaries which are used to store the earlier pellets
            self.pellets_group.power_pellets = {}

            if temp_pellets != ['']:            # check if the pellets are not empty (otherwise an error is thrown)
                for pellet in temp_pellets: 
                    pellet = pellet[1:-1].split(',')        # split the row and column values and create a pellet at the position

                    row = int(pellet[0])
                    col = int(pellet[1])
                    self.pellets_group.pellets[(row, col)] = Pellet(row, col)

            if temp_power_pellets != ['']:          # check if the pellets are not empty (otherwise an error is thrown)
                for power_pellet in temp_power_pellets:
                    power_pellet = power_pellet[1:-1].split(',')            # split the row and column values and create a pellet at the position

                    row = int(power_pellet[0])
                    col = int(power_pellet[1])
                    self.pellets_group.power_pellets[(row, col)] = PowerPellet(row, col)

            self.start_game()           # start the game after loading from the save file

    def enter_code(self):
        '''Creates a frame to enter Cheat Codes'''
        self.codes_frame = LabelFrame(self.root, bd=0)              # create frame for cheat codes
        self.codes_frame.place(x=100, y=100, width=250, height=300)

        self.code_entry = Entry(self.codes_frame, bg="white", fg="black", font=("Menlo", 14), justify=CENTER)       # entry frame with focus set to enter the code
        self.code_entry.place(x=25, y=40, height=35, width=200)
        self.code_entry.focus_set()

        submit_button = Button(self.codes_frame, text="Submit Code", command=self.submit_code, font=("Menlo", 13))      # submit button to submit the code for checking
        submit_button.place(x=60, y=100, height=40, width=130)

        self.code_info = Label(self.codes_frame, text="", font=("Menlo", 12))       # code info label that tells if the code is valid or not
        self.code_info.place(x=30, y=150, width=180, height=40)

        back_button = Button(self.codes_frame, text="Back", command=self.codes_frame.destroy, font=("Menlo", 15))       # back button to return to menu
        back_button.place(x=90, y=200, height=40, width=75)

    def submit_code(self):
        '''Submits the entered Cheat Code and validates it'''
        code = self.code_entry.get().strip()
        if code in self.game.codes:             # check if the code is part of valid codes

            if self.game.codes[code] == True:           # check if the code has been entered already
                self.code_info["text"] = "Code entered already"

            else:
                if code == "MORELIVES":
                    self.code_info["text"] = "Added 2 more lives"       # add text info to inform the player what the code has activated
                    self.pacman.lives += 2

                elif code == "SCARYPACMAN":
                    self.code_info["text"] = "Ghosts stay frightened \nfor 15s"
                    self.ghosts_group.time["FRIGHTENED"] = 15

                elif code == "PELLETMASTER":
                    self.code_info["text"] = "Pacman earns 2x points\nfrom pellets"         # add text info to inform the player what the code has activated
                    self.pellets_group.points["Pellet"] = 20
                    self.pellets_group.points["PowerPellet"] = 100

                elif code == "EASYMODE":
                    self.code_info["text"] = "Ghosts' speeds have been\nreduced by half"
                    self.ghosts_group.speed = 2

                self.game.codes[code] = True            # change the code value to true in the dictionary containing all the codes
        else:
            text = "Invalid Code"           # if the code is not valid, give the appropriate message
            self.code_info["text"] = text

    def show_settings(self):
        '''Creates a frame to allow the player to change the controls of pacman'''
        self.settings_frame = LabelFrame(self.root, bd=0)           # create the frame to show the settings
        self.settings_frame.place(x=100, y=100, width=250, height=300)

        self.name_entry = Entry(self.settings_frame, bg="white", fg="black", font=("Menlo", 14), justify=CENTER)        # name entry to change name if need be
        self.name_entry.place(x=50, y=20, height=35, width=150)
        self.name_entry.insert(0, self.game.player)
        self.name_entry.focus_set()

        up_label = Label(self.settings_frame, text="Move Up: ", font=("Menlo", 11), anchor="w")         # Informs that the adjacent key controls move up
        up_label.place(x=40, y=70, height=20, width=100)
        self.up_val = Label(self.settings_frame, text=self.pacman.key_up, font=("Menlo", 11), bg="white", fg="black")       # Selecting these labels lets you change the key binding to any key of your choice
        self.up_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Up"))
        self.up_val.place(x=150, y=70, height=20, width=50)

        left_label = Label(self.settings_frame, text="Move Left: ", font=("Menlo", 11), anchor="w")      # Informs that the adjacent key controls move left
        left_label.place(x=40, y=100, height=20, width=100)
        self.left_val = Label(self.settings_frame, text=self.pacman.key_left, font=("Menlo", 11), bg="white", fg="black")
        self.left_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Left"))
        self.left_val.place(x=150, y=100, height=20, width=50)

        down_label = Label(self.settings_frame, text="Move Down: ", font=("Menlo", 11), anchor="w")      # Informs that the adjacent key controls move down
        down_label.place(x=40, y=130, height=20, width=100)
        self.down_val = Label(self.settings_frame, text=self.pacman.key_down, font=("Menlo", 11), bg="white", fg="black")       # Selecting these labels lets you change the key binding to any key of your choice
        self.down_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Down"))
        self.down_val.place(x=150, y=130, height=20, width=50)

        right_label = Label(self.settings_frame, text="Move Right: ", font=("Menlo", 11), anchor="w")        # Informs that the adjacent key controls move right
        right_label.place(x=40, y=160, height=20, width=100)
        self.right_val = Label(self.settings_frame, text=self.pacman.key_right, font=("Menlo", 11), bg="white", fg="black")
        self.right_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Right"))
        self.right_val.place(x=150, y=160, height=20, width=50)

        pause_label = Label(self.settings_frame, text="Pause Game: ", font=("Menlo", 11), anchor="w")        # Informs that the adjacent key controls pause key
        pause_label.place(x=40, y=190, height=20, width=105)
        self.pause_val = Label(self.settings_frame, text=self.pacman.key_pause, font=("Menlo", 11), bg="white", fg="black")
        self.pause_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Pause"))
        self.pause_val.place(x=150, y=190, height=20, width=50)

        boss_key_label = Label(self.settings_frame, text="Boss Key: ", font=("Menlo", 11), anchor="w")       # Informs that the adjacent key controls boss key
        boss_key_label.place(x=40, y=220, height=20, width=105)
        self.boss_key_val = Label(self.settings_frame, text=self.pacman.key_boss, font=("Menlo", 11), bg="white", fg="black")       # Selecting these labels lets you change the key binding to any key of your choice
        self.boss_key_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Boss_key"))
        self.boss_key_val.place(x=150, y=220, height=20, width=50)

        save_button = Button(self.settings_frame, text="Save", command=self.save_settings, font=("Menlo", 13))          # save button which saves the changes
        save_button.place(x=40, y=250, height=30, width=75)

        back_button = Button(self.settings_frame, text="Back", command=self.settings_frame.destroy, font=("Menlo", 13))     # back button to go back to menu
        back_button.place(x=130, y=250, height=30, width=75)

    def select_key_label(self, event, key):
        '''Selects the controls to be changed'''
        self.up_val["bg"] = "white"             # returns all other label backgrounds to white
        self.left_val["bg"] = "white"
        self.down_val["bg"] = "white"
        self.right_val["bg"] = "white"
        self.pause_val["bg"] = "white"
        self.boss_key_val["bg"] = "white"
                                                        # sets the clicked label to focus which allows the player to change the key binding
        if key == "Up":         
            self.up_val.focus_set()
            self.up_val["bg"] = "lightblue"
            self.up_val.bind("<Key>", lambda event: self.set_key(event, key))
        elif key == "Left":
            self.left_val.focus_set()
            self.left_val["bg"] = "lightblue"
            self.left_val.bind("<Key>", lambda event: self.set_key(event, key))
        elif key == "Down":
            self.down_val.focus_set()
            self.down_val["bg"] = "lightblue"
            self.down_val.bind("<Key>", lambda event: self.set_key(event, key))
        elif key == "Right":
            self.right_val.focus_set()
            self.right_val["bg"] = "lightblue"
            self.right_val.bind("<Key>", lambda event: self.set_key(event, key))
        elif key == "Pause":
            self.pause_val.focus_set()
            self.pause_val["bg"] = "lightblue"
            self.pause_val.bind("<Key>", lambda event: self.set_key(event, key))
        elif key == "Boss_key":
            self.boss_key_val.focus_set()
            self.boss_key_val["bg"] = "lightblue"
            self.boss_key_val.bind("<Key>", lambda event: self.set_key(event, key))

    def set_key(self, event, key):
        '''Sets the new controls of pacman'''                   
        if key == "Up":                                 # Sets the text of the label to the name of the key which is pressed, to let players know the key
            self.up_val["text"] = event.keysym
        elif key == "Left":
            self.left_val["text"] = event.keysym
        elif key == "Down":
            self.down_val["text"] = event.keysym
        elif key == "Right":
            self.right_val["text"] = event.keysym
        elif key == "Pause":
            self.pause_val["text"] = event.keysym
        elif key == "Boss_key":
            self.boss_key_val["text"] = event.keysym

    def save_settings(self):
        '''Saves the new controls into a settings file'''
        if self.game.player != self.name_entry.get().strip():           # deletes the save file info if the player has changed their name (different player, so new game)
            f = open("GameSave.txt", "w")
            f.close()

        self.game.player = self.name_entry.get().strip()            # saves the current settings to a file and also changes it in the game
        self.pacman.key_up = self.up_val["text"]
        self.pacman.key_left = self.left_val["text"]
        self.pacman.key_down = self.down_val["text"]
        self.pacman.key_right = self.right_val["text"]
        self.pacman.key_pause = self.pause_val["text"]
        self.pacman.key_boss = self.boss_key_val["text"]

        self.settings_frame.destroy()
        self.menu_frame.destroy()
        self.show_menu()

        with open("Settings.txt", "w") as f:        # writing the new settings into the file
            text = [
                self.game.player,
                self.pacman.key_up,
                self.pacman.key_left,
                self.pacman.key_down,
                self.pacman.key_right,
                self.pacman.key_pause,
                self.pacman.key_boss
            ]

            text = "\n".join(text)
            f.write(text)

    def load_settings(self):
        '''Loads the current controls of pacman'''
        with open("Settings.txt") as f:
            data = f.read().split("\n")             # loading the current settings and returning them

            return data[0].strip(), data[1].strip(), data[2].strip(), data[3].strip(), data[4].strip(), data[5].strip(), data[6].strip()