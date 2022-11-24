from tkinter import *
from pacman import *

class Menu():
    def __init__(self, root, game, pacman, start_game, resume_game):
        self.game = game
        self.pacman = pacman
        self.root = root
        self.pellets_group = self.game.pellets_group
        self.start_game = start_game
        self.resume_game = resume_game

    def show_menu(self):
        self.menu_frame = LabelFrame(self.root, bd=0)
        self.menu_frame.place(x=100, y=100, width=250, height=300)

        pos = 30

        if self.check_game_save() and not self.game.start:

            continue_button = Button(self.menu_frame, text="Continue", command=self.load_game, font=("Menlo", 15))
            continue_button.place(x=50, y=20, height=40, width=150)

            pos = 55

        elif self.game.start and self.game.paused:
            resume_button = Button(self.menu_frame, text="Resume", command=self.resume_game, font=("Menlo", 15))
            resume_button.place(x=50, y=20, height=40, width=150)

            pos = 55
        
        new_button = Button(self.menu_frame, text="New Game", command=self.start_game, font=("Menlo", 15))
        new_button.place(x=50, y=20+pos, height=40, width=150)

        high_score_button = Button(self.menu_frame, text="Leaderboard", command=self.show_high_score, font=("Menlo", 15))
        high_score_button.place(x=50, y=75+pos, height=40, width=150)

        cheat_button = Button(self.menu_frame, text="Enter Code", command=self.enter_code, font=("Menlo", 15))
        cheat_button.place(x=50, y=130+pos, height=40, width=150)

        settings_button = Button(self.menu_frame, text="Settings", command=self.show_settings, font=("Menlo", 15))
        settings_button.place(x=50, y=185+pos, height=40, width=150)

    def save_high_score(self):

        with open("HighScore.txt") as f:
            high_score_list = f.read().split("\n")
            for high_score in high_score_list:

                index = high_score_list.index(high_score)
                high_score = high_score.split()
                high_score_val = int(high_score[1])

                if self.game.score > high_score_val:

                    self.game.player = self.game.player.strip()

                    high_score_list = high_score_list[0:index] + [self.game.player + ": " + str(self.game.score)] + high_score_list[index:]

                    if len(high_score_list) > 5:
                        high_score_list = high_score_list[:5]

                    with open("HighScore.txt", "w") as f:
                        high_score_list = "\n".join(high_score_list)
                        f.write(high_score_list)

                    break

    def show_high_score(self):

        self.high_score_frame = LabelFrame(self.root, bd=0)
        self.high_score_frame.place(x=100, y=100, width=250, height=300)

        with open("HighScore.txt") as f:
            high_score_list = f.read().split("\n")
            for index in range(len(high_score_list)):
                text = str(index+1) + ". " + high_score_list[index]
                row = int(text[0])

                score_info = Label(self.high_score_frame, text=text, font=("Menlo", 15))
                score_info.place(x=50, y=20+(40*(row-1)), height=40, width=150)

        back_button = Button(self.high_score_frame, text="Back", command=self.high_score_frame.destroy, font=("Menlo", 15))
        back_button.place(x=50, y=240, height=40, width=150)

    def save_game(self):

        temp_pellets = self.pellets_group.pellets.keys()
        temp_pellets = [str(coord) for coord in temp_pellets]
        temp_pellets = ":".join(temp_pellets)

        temp_power_pellets = self.pellets_group.power_pellets.keys()
        temp_power_pellets = [str(coord) for coord in temp_power_pellets]
        temp_power_pellets = ":".join(temp_power_pellets)

        game_details = [
            str(self.pacman.lives),
            str(self.game.score),
            temp_pellets,
            temp_power_pellets
        ]
        game_details = "\n".join(game_details)

        with open("GameSave.txt", "w") as f:
            f.write(game_details)

    def check_game_save(self):
        with open("GameSave.txt") as f:
            data = f.read()
            if data == "":
                return False
            return True

    def load_game(self):
        with open("GameSave.txt") as f:
            data = f.read().split("\n")

            self.pacman.lives = int(data[0])
            self.game.score = int(data[1])

            temp_pellets = data[2].split(":")
            temp_power_pellets = data[3].split(":")

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

    def enter_code(self):
        self.codes_frame = LabelFrame(self.root, bd=0)
        self.codes_frame.place(x=100, y=100, width=250, height=300)

        self.code_entry = Entry(self.codes_frame, bg="white", fg="black", font=("Menlo", 14), justify=CENTER)
        self.code_entry.place(x=25, y=20, height=35, width=200)

        submit_button = Button(self.codes_frame, text="Submit Code", command=self.submit_code, font=("Menlo", 13))
        submit_button.place(x=60, y=70, height=40, width=130)

    def submit_code(self):
        
        pass

    def show_settings(self):
        self.settings_frame = LabelFrame(self.root, bd=0)
        self.settings_frame.place(x=100, y=100, width=250, height=300)

        self.name_entry = Entry(self.settings_frame, bg="white", fg="black", font=("Menlo", 14), justify=CENTER)
        self.name_entry.place(x=50, y=20, height=35, width=150)
        self.name_entry.insert(0, self.game.player)

        up_label = Label(self.settings_frame, text="Move Up: ", font=("Menlo", 11), anchor="w")
        up_label.place(x=40, y=85, height=20, width=100)
        self.up_val = Label(self.settings_frame, text=self.pacman.key_up, font=("Menlo", 11), bg="white")
        self.up_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Up"))
        self.up_val.place(x=150, y=85, height=20, width=50)

        left_label = Label(self.settings_frame, text="Move Left: ", font=("Menlo", 11), anchor="w")
        left_label.place(x=40, y=115, height=20, width=100)
        self.left_val = Label(self.settings_frame, text=self.pacman.key_left, font=("Menlo", 11), bg="white")
        self.left_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Left"))
        self.left_val.place(x=150, y=115, height=20, width=50)

        down_label = Label(self.settings_frame, text="Move Down: ", font=("Menlo", 11), anchor="w")
        down_label.place(x=40, y=145, height=20, width=100)
        self.down_val = Label(self.settings_frame, text=self.pacman.key_down, font=("Menlo", 11), bg="white")
        self.down_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Down"))
        self.down_val.place(x=150, y=145, height=20, width=50)

        right_label = Label(self.settings_frame, text="Move Right: ", font=("Menlo", 11), anchor="w")
        right_label.place(x=40, y=175, height=20, width=100)
        self.right_val = Label(self.settings_frame, text=self.pacman.key_right, font=("Menlo", 11), bg="white")
        self.right_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Right"))
        self.right_val.place(x=150, y=175, height=20, width=50)

        pause_label = Label(self.settings_frame, text="Pause Game: ", font=("Menlo", 11), anchor="w")
        pause_label.place(x=40, y=205, height=20, width=105)
        self.pause_val = Label(self.settings_frame, text=self.pacman.key_pause, font=("Menlo", 11), bg="white")
        self.pause_val.bind("<Button-1>", lambda event: self.select_key_label(event, "Pause"))
        self.pause_val.place(x=150, y=205, height=20, width=50)

        save_button = Button(self.settings_frame, text="Save", command=self.save_settings, font=("Menlo", 15))
        save_button.place(x=40, y=240, height=40, width=75)

        back_button = Button(self.settings_frame, text="Back", command=self.settings_frame.destroy, font=("Menlo", 15))
        back_button.place(x=130, y=240, height=40, width=75)

    def select_key_label(self, event, key):

        self.up_val["bg"] = "white"
        self.left_val["bg"] = "white"
        self.down_val["bg"] = "white"
        self.right_val["bg"] = "white"
        self.pause_val["bg"] = "white"

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

    def set_key(self, event, key):

        if key == "Up":
            self.up_val["text"] = event.keysym
        elif key == "Left":
            self.left_val["text"] = event.keysym
        elif key == "Down":
            self.down_val["text"] = event.keysym
        elif key == "Right":
            self.right_val["text"] = event.keysym
        elif key == "Pause":
            self.pause_val["text"] = event.keysym

    def save_settings(self):
        if self.game.player != self.name_entry.get().strip():
            f = open("GameSave.txt", "w")
            f.close()

        self.game.player = self.name_entry.get().strip()
        self.pacman.key_up = self.up_val["text"]
        self.pacman.key_left = self.left_val["text"]
        self.pacman.key_down = self.down_val["text"]
        self.pacman.key_right = self.right_val["text"]
        self.pacman.key_pause = self.pause_val["text"]

        self.settings_frame.destroy()
        self.menu_frame.destroy()
        self.show_menu()

        with open("Settings.txt", "w") as f:
            text = [
                self.game.player,
                self.pacman.key_up,
                self.pacman.key_left,
                self.pacman.key_down,
                self.pacman.key_right,
                self.pacman.key_pause
            ]

            text = "\n".join(text)
            f.write(text)

    def load_settings(self):
        with open("Settings.txt") as f:
            data = f.read().split("\n")

            return data[0].strip(), data[1].strip(), data[2].strip(), data[3].strip(), data[4].strip(), data[5].strip()