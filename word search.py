import random
def wordsList():
    return ["happy", "cheerful", "chipper", "effervescent", "jaunty", "jolly"]

def addWords(alist):
    word = str(input("Enter a word: "))
    while word != "":
        alist.append(word)
        word = str(input("Enter a word: "))

words = wordsList()
addWords(words)
words_copy = words.copy()

def displayWords():
    for word in words:
        print(word)

row = int(input("Enter grid row size: "))
col = int(input("Enter grid column size: "))
grid = [[0 for i in range(col)] for j in range(row)]

def displayGrid():
    for row in grid:
        for letter in row:
            print(letter, end=" ")
        print()

def FindDirection(word, row, col):

    direction = random.randint(0,3)

    if direction == 0:
        #print("placing", word, "from left to right")
        min = 0 #Minimum column index for 1st letter placement.
        max = col - len(word) #Maximum column index for 1st letter placement.
    elif direction == 1:
        #print("placing", word, "from right to left")
        min = len(word) - 1 #Minimum column index for 1st letter placement.
        max = col - 1 #Maximum column index for 1st letter placement.
    elif direction == 2:
        #print("placing", word, "from top to bottom")
        min = 0 #Minimum row index for 1st letter placement.
        max = row - len(word) #Minimum row index for 1st letter placement.
    elif direction == 3:
        #print("placing", word, "from bottom to top")
        min = len(word) - 1 #Minimum row index for 1st letter placement.
        max = row - 1 #Minimum row index for 1st letter placement.

    #print("Word length is ", len(word), " so:") #Min and max depend on length of word.
    #print("min: ", min, " max:", max)

    square = random.randint(min,max) #Random starting point in range chosen.
    #print("Square chosen is ", square)
    if direction < 2:
        row_chosen = random.randint(0, row-1) #Choose random row; doesn't depend on word length.
        col_chosen = square
        #print(" in row ", row) 
    else:
        col_chosen = random.randint(0, col-1) #Choose random column; doesn't depend on word length.
        row_chosen = square
        #print(" in column ", col)

    return row_chosen, col_chosen, direction

def CheckWordWillFit(word, row_chosen, col_chosen, direction):
    
    for charOfWord in range(len(word)):

        if grid[row_chosen][col_chosen] != 0:
            return False
        if direction == 0: 
            col_chosen += 1
        elif direction == 1: 
            col_chosen -= 1
        elif direction == 2:
            row_chosen += 1
        elif direction == 3:
            row_chosen -= 1

    else:
        return True

def PlaceWord(word, row_chosen, col_chosen, direction):

    for charOfWord in range(len(word)):

        grid[row_chosen][col_chosen] = word[charOfWord]
        if direction == 0: 
            col_chosen += 1
        elif direction == 1: 
            col_chosen -= 1
        elif direction == 2:
            row_chosen += 1
        elif direction == 3:
            row_chosen -= 1

def PlaceWords():
    while words_copy != []:
        
        word = words_copy[0]
        if len(word) > row or len(word) > col: 
            words.remove(word)
            words_copy.pop(0)
            continue #If the word is too long for the grid in any direction, don't use it.

        row_chosen, col_chosen, direction = FindDirection(word, row, col)
        #When we've reached this point, we can place the word. This is covered in the next part.
        while not CheckWordWillFit(word, row_chosen, col_chosen, direction):
            row_chosen, col_chosen, direction = FindDirection(word, row, col)

        else:
            PlaceWord(word, row_chosen, col_chosen, direction)

        words_copy.pop(0)

def GridRandomFill(row, col):
    for i in range(row):
        for j in range(col):
            if grid[i][j] == 0:
                ascii_val = random.randint(97,122)
                char = chr(ascii_val)
                grid[i][j] = char

PlaceWords()
GridRandomFill(row, col)
displayGrid()
displayWords()