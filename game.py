########################################################
#
#    Programming 1 2020-2021
#    Coursework 02 - MOBA Trainer
#    Created by Andrei Hutu
#
########################################################

#    Recommended resolution - 1920x1080
#    Scaling - 100% (Windows - Display Settings)
#
#    Cheat codes:
#    Immortality:     Shift-F1
#    No Cooldowns:    Shift-F2
#    Super Speed:    Shift-F3

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from tkinter import Tk, Canvas, Frame, Button, Label
from tkinter import Entry, PhotoImage, filedialog, messagebox
import random
import math
import time
import re
import pickle

#############################
#
#    NAVIGATION METHODS
#
#############################


def toMenu():
    """Go to Main Menu Frame."""
    hideFrames()
    canvas.focus_set()
    menuFrame.pack()


def startGame():
    """Set up initial state of game and enter the game loop."""
    global score, noCheats, pause, bossOn, gameOver, immortal, cooldownsOff
    global q, enemies, obstacles, cooldowns, speed, delay,  startTime
    # Set up game state variables
    score = 0
    noCheats = True
    pause = False
    gameOver = False
    bossOn = False
    immortal = False
    cooldownsOff = False
    startTime = time.time()
    cooldowns = [[True, 0, 1, qBox, qText], [True, 0, 5, wBox, wText],
                 [True, 0, 5, eBox, eText]]
    speed = [8, 2, 25, 15]
    delay = 30
    # Set up enemy and obstacles lists
    enemies = []
    obstacles = []
    # Move player and other game elements to starting positions
    canvas.coords(dest, startPos)
    canvas.coords(player[0], startPos)
    canvas.coords(player[1], width//2-playerSize//2, height//2-playerSize//2)
    canvas.coords(q[0], -100, -100, -90, -90)
    canvas.coords(q[1], -100, -100)
    q[2] = [-95, -95, -95, -95]
    canvas.coords(w[0], -200, -200, -100, -100)
    canvas.coords(w[1], -200, -200)
    # Clear displayed text
    canvas.itemconfig(scoreText, text="Score: 0")
    canvas.itemconfig(cheatText1, text="")
    canvas.itemconfig(cheatText2, text="")
    canvas.itemconfig(cheatText3, text="")
    # Show canvas and enter game loop
    hideFrames()
    canvas.pack()
    gameLoop()


def toSave():
    """Let user create a save file."""
    try:
        savefilename = filedialog.asksaveasfilename(
                                  initialdir="saves",
                                  title="Create save file",
                                  defaultextension=".sav",
                                  filetypes=(("Save files", "*.sav"),
                                             ("all files", "*.*")))
        savefile = open(savefilename, "wb")
        # Prepare values for saving
        gameTime = pauseTime - startTime
        posP = [canvas.coords(player[i]) for i in range(0, 2)]
        posD = canvas.coords(dest)
        posQ = [canvas.coords(q[0]), canvas.coords(q[1]), q[2]]
        posW = [canvas.coords(w[0]), canvas.coords(w[1])]
        posE = [[canvas.coords(enemy[0]),
                 canvas.coords(enemy[1])]
                for enemy in enemies]
        posO = [[canvas.coords(obst[0]),
                 canvas.coords(obst[1]),
                 obst[2],
                 obst[3]]
                for obst in obstacles]
        saveVars = [score, bossOn, noCheats, gameTime, pauseTime,
                    posP, posD, posQ, posW, posE, posO,
                    cooldowns, speed, delay]
        # Save to file
        pickle.dump(saveVars, savefile)
        messagebox.showinfo(title="Success", message="Game saved")
    except:
        pass


def toLoad():
    """Let user select a save file to load."""
    global score, gameOver, pause, bossOn, noCheats, startTime
    global player, dest, q, w, enemies, obstacles, cooldowns, speed
    global delay, immortal, cooldownsOff
    try:
        savefilename = filedialog.askopenfilename(
                                  initialdir="saves",
                                  title="Select save file",
                                  filetypes=(("Save files", "*.sav"),
                                             ("all files", "*.*")))
        savefile = open(savefilename, "rb")
        saveVars = pickle.load(savefile)
        (score, bossOn, noCheats, gameTime, pauseTime,
         posP, posD, posQ, posW, posE, posO,
         cooldowns, speed, delay) = saveVars
        # Delete current game elements if they exist
        for enemy in enemies:
            canvas.delete(enemy[0])
            canvas.delete(enemy[1])
        for obst in obstacles:
            canvas.delete(obst[0])
            canvas.delete(obst[1])
        # Adjust time
        startTime = time.time() - gameTime
        # Set variables and coords according to loaded values
        gameOver = False
        immortal = False
        pause = False
        cooldownsOff = False
        speed[0] = 8
        canvas.coords(dest, posD)
        canvas.coords(player[0], posP[0])
        canvas.coords(player[1], posP[1])
        canvas.coords(q[0], posQ[0])
        canvas.coords(q[1], posQ[1])
        q[2] = posQ[2]
        canvas.coords(w[0], posW[0])
        canvas.coords(w[1], posW[1])
        window.after(200, removeW)
        # Create new enemies
        enemies = []
        for i in range(len(posE)):
            enemies.append([canvas.create_oval(posE[i][0], fill="red"),
                            canvas.create_image(posE[i][1],
                            image=enemyImg, anchor="nw")])
        # Create new obstacles
        obstacles = []
        for i in range(len(posO)):
            obstacles.append([canvas.create_oval(posO[i][0],
                                                 fill="orange"),
                              canvas.create_image(posO[i][1],
                                                  image=obstImg,
                                                  anchor="nw"),
                              posO[i][2],
                              posO[i][3]])
        # Change displayed text
        canvas.itemconfig(scoreText, text="Score: " + str(score))
        canvas.itemconfig(cheatText1, text="")
        canvas.itemconfig(cheatText2, text="")
        canvas.itemconfig(cheatText3, text="")
        # Adjust ability cooldowns
        elapsedTime = time.time()-pauseTime
        for ability in cooldowns:
                ability[1] += elapsedTime
        hideFrames()
        canvas.pack()
        gameLoop()
    except FileNotFoundError:
        pass
    except:
        messagebox.showerror(title="Error",
                             message="Cannot load file. Try another!")


def toLeaders():
    """Go to Leader Board Frame."""
    readLeaders()
    hideFrames()
    leaderBoardFrame.pack()


def toSettings():
    """Go to Settings Frame."""
    hideFrames()
    settingsFrame.pack()


def toMenuExit():
    """Clear game elements and go to Main Menu Frame."""
    global pause, gameOver
    pause = False
    gameOver = True
    for enemy in enemies:
        canvas.delete(enemy[0])
        canvas.delete(enemy[1])
    for obst in obstacles:
        canvas.delete(obst[0])
        canvas.delete(obst[1])
    toMenu()


def toExit():
    """Exit program."""
    window.destroy()


def toBoss():
    """Go to Boss Key Frame."""
    hideFrames()
    bossFrame.pack()


def toPause():
    """Go to Pause Frame."""
    hideFrames()
    pauseFrame.pack()


def toGameOver():
    """Clear game elements and go to Game Over Frame."""
    hideFrames()
    for enemy in enemies:
        canvas.delete(enemy[0])
        canvas.delete(enemy[1])
    for obst in obstacles:
        canvas.delete(obst[0])
        canvas.delete(obst[1])
    # Check score against leader board
    readLeaders()
    if (noCheats and (len(leaderData) < 5 or
       score > int(leaderData[len(leaderData)-1][1]))):
        # Add score to leader board
        toAddScore()
    else:
        # Display score and go straight to game over screen
        score3.configure(text="Final Score: "+str(score))
        gameOverFrame.pack()


def toAddScore():
    """Go to Add Score to Leader Board Frame."""
    global pause
    pause = True
    hideFrames()
    addScoreFrame.pack()


def hideFrames():
    """Hide all frames."""
    canvas.pack_forget()
    menuFrame.pack_forget()
    pauseFrame.pack_forget()
    gameOverFrame.pack_forget()
    leaderBoardFrame.pack_forget()
    addScoreFrame.pack_forget()
    bossFrame.pack_forget()
    settingsFrame.pack_forget()


def setWindowDimensions(w, h):
    """Returns root widget with width=w and height=h, centered on screen."""
    window = Tk()
    window.title("MOBA Trainer")
    window.resizable(False, False)
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    return window


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#############################
#
#        EVENT METHODS
#
#############################

# Universal Event Methods

def anykeyPress(event):
    """Checks pressed key and calls binding-specific methods."""
    key = event.char.upper()
    global changingBind, bind
    # During gameplay
    if not gameOver and not pause and not bossOn:
        if key == bind[0]:
            qAbility(event)
        elif key == bind[1]:
            wAbility(event)
        elif key == bind[2]:
            eAbility(event)
        elif key == bind[3]:
            bossPress(event)
    # In menus
    elif gameOver and not pause and True not in changingBind:
        if key == bind[3]:
            bossPress(event)
    # During binding change
    else:
        if changingBind[0]:
            bind[0] = key
        if changingBind[1]:
            bind[1] = key
        if changingBind[2]:
            bind[2] = key
        if changingBind[3]:
            bind[3] = key
        clearChange()
        updateConfig()


def pausePress(event):
    """Pauses and unpauses game."""
    if not gameOver and not bossOn:
        global pause, startTime
        pause = not pause
        if pause:
            global pauseTime
            pauseTime = time.time()
            toPause()
        else:
            # Readjust game time
            elapsedTime = time.time() - pauseTime
            startTime += elapsedTime
            for ability in cooldowns:
                ability[1] += elapsedTime
            hideFrames()
            canvas.pack()
            gameLoop()


def bossPress(event):
    """Enter and leave Boss Key mode."""
    global bossOn
    bossOn = not bossOn
    # During gameplay
    if not gameOver and not pause:
        global startTime
        if bossOn:
            global bossTime
            bossTime = time.time()
            toBoss()
        else:
            elapsedTime = time.time() - bossTime
            startTime += elapsedTime
            for ability in cooldowns:
                ability[1] += elapsedTime
            hideFrames()
            canvas.pack()
            gameLoop()
    # In pause screen
    elif not gameOver and pause:
        if bossOn:
            toBoss()
        else:
            toPause()
    # In other menus
    else:
        if bossOn:
            toBoss()
        else:
            toMenu()


# Cheat Code Event Methods

def immortalSwitch(event):
    """Switch Immortal Mode On/Off."""
    if not gameOver and not pause and not bossOn:
        global immortal, noCheats
        immortal = not immortal
        noCheats = False
        if immortal:
            canvas.itemconfig(cheatText1, text="Immortal")
        else:
            canvas.itemconfig(cheatText1, text="")


def cooldownsSwitch(event):
    """Switch No Cooldowns Mode On/Off."""
    if not gameOver and not pause and not bossOn:
        global cooldownsOff, noCheats
        cooldownsOff = not cooldownsOff
        noCheats = False
        if cooldownsOff:
            canvas.itemconfig(cheatText2, text="No Cooldowns")
        else:
            canvas.itemconfig(cheatText2, text="")


def speedSwitch(event):
    """Switch Super Speed Mode On/Off."""
    if not gameOver and not pause and not bossOn:
        global noCheats, speed
        noCheats = False
        if speed[0] == 8:
            speed[0] = 20
            canvas.itemconfig(cheatText3, text="Super Speed")
        else:
            speed[0] = 8
            canvas.itemconfig(cheatText3, text="")


# Ability Event Methods

def qAbility(event):
    """Fire Ability 1 (default Q)."""
    if not gameOver and not pause and not bossOn:
        global q, cooldowns
        x = event.x
        y = event.y
        if cooldownsOff or cooldowns[0][0]:
            cooldowns[0][1] = time.time()
            posP = canvas.coords(player[0])
            # Move Q on player center
            canvas.coords(q[0], posP[0]+15, posP[1]+15, posP[0]+35, posP[1]+35)
            canvas.coords(q[1], posP[0]+15, posP[1]+15)
            centerQ = [(posP[2]+posP[0])/2, (posP[3]+posP[1])/2]
            # Calculate trajectory
            slopeY = y - centerQ[1]
            slopeX = x - centerQ[0]
            slope = math.atan2(slopeY, slopeX)
            tempY = math.sin(slope)
            tempX = math.cos(slope)
            q[2] = [centerQ[0]+tempX*435,
                    centerQ[1]+tempY*435,
                    centerQ[0]+tempX*435,
                    centerQ[1]+tempY*435]
            # Move Q to player edge
            canvas.move(q[0], tempX*35, tempY*35)
            canvas.move(q[1], tempX*35, tempY*35)


def wAbility(event):
    """Place Ability 2 (default W)."""
    if not gameOver and not pause and not bossOn:
        global cooldowns
        x = event.x
        y = event.y
        if cooldownsOff or (cooldowns[1][0] and not offScreen(x, y)):
            cooldowns[1][1] = time.time()
            # Move W to cursor
            canvas.coords(w[0], x-50, y-50, x+50, y+50)
            canvas.coords(w[1], x-50, y-50)
            # Remove W after 1 sec
            window.after(1000, removeW)


def eAbility(event):
    """Use Ability 3 (default 3)."""
    if not gameOver and not pause and not bossOn:
        global cooldowns
        x = event.x
        y = event.y
        if cooldownsOff or cooldowns[2][0]:
            cooldowns[2][1] = time.time()
            movIncr = move(canvas.coords(player[0]), [x, y, x, y], 400)
            # Move player to cursor or max distance
            canvas.move(player[0], movIncr[1], movIncr[2])
            canvas.move(player[1], movIncr[1], movIncr[2])
            # Move player destination to cursor
            canvas.coords(dest, x-5, y-5, x+5, y+5)


# Movement Event Methods

def moveDest(event):
    """Move player destination to cursor."""
    x = event.x
    y = event.y
    canvas.coords(dest, x-5, y-5, x+5, y+5)
    canvas.itemconfig(dest, fill="white")
    window.after(100, removeDest)


def dragDest(event):
    """Drag player destination while holding right-click."""
    x = event.x
    y = event.y
    if not offScreen(x, y):
        canvas.coords(dest, x-5, y-5, x+5, y+5)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#############################
#
#    GAMEPLAY METHODS
#
#############################

def gameLoop():
    """Main Gameplay Loop."""
    global gameOver
    # Check cooldowns and update icons
    checkCooldown()
    # Move player towards its destination
    movePlayer()
    # Move ability 1 (default Q) towards its destination
    moveQ()
    # Move enemies and objects and check collisions
    gameOver = moveEnemy() or moveObst()
    # Add new enemies and objects
    addEnemy()
    addObst()
    canvas.pack()
    if not pause and not bossOn:
        if gameOver:
            # Player hit -> Game Over
            window.after(1000, toGameOver)
        else:
            # Go to next frame
            window.after(delay, gameLoop)


# Ability Methods

def checkCooldown():
    """Check ability cooldowns and update ability icons."""
    global cooldowns
    currTime = time.time()
    # Loop through abilities
    for i in range(len(cooldowns)):
        if cooldownsOff or currTime - cooldowns[i][1] >= cooldowns[i][2]:
            # Can use
            cooldowns[i][0] = True
            canvas.itemconfig(cooldowns[i][3], fill="white")
            canvas.itemconfig(cooldowns[i][4], fill="green", text=bind[i])
        else:
            # Cannot use
            cooldowns[i][0] = False
            canvas.itemconfig(cooldowns[i][3], fill="black")
            canvas.itemconfig(cooldowns[i][4], fill="red", text=bind[i])


def moveQ():
    """Move Ability 1 (default Q) towards its destination."""
    global q
    movIncr = move(canvas.coords(q[0]), q[2], speed[2])
    if (movIncr[0] == 1 and
       (abs(movIncr[1]) > 0.00001 or abs(movIncr[2]) > 0.00001)):
        # Continue moving
        canvas.move(q[0], movIncr[1], movIncr[2])
        canvas.move(q[1], movIncr[1], movIncr[2])
    else:
        # Remove Ability 1 (default Q)
        canvas.coords(q[0], -100, -100, -90, -90)
        canvas.coords(q[1], -100, -100)
        q[2] = [-95, -95, -95, -95]


def removeW():
    """Remove Ability 2 (default W)."""
    canvas.coords(w[0], -200, -200, -100, -100)
    canvas.coords(w[1], -200, -200)


# Movement and Collision Methods

# Universal
def overlapping(posA, posB):
    """Check overlap of 2 spheres and return result."""
    centerA = [(posA[2]+posA[0])/2, (posA[3]+posA[1])/2]
    centerB = [(posB[2]+posB[0])/2, (posB[3]+posB[1])/2]
    minDist = (posA[2]-posA[0]+posB[2]-posB[0])/2
    if math.dist(centerA, centerB) < minDist:
        return True
    return False


def offScreen(x, y):
    """Check if x and y are offscreen and return result."""
    if(x < 0 or x > width or y < 0 or y > height):
        return True
    return False


def move(posA, posB, speed):
    """Calculate trajectory of A towards B and
       return [keepMoving, x_increment, y_increment]."""
    centerA = [posA[2]+posA[0], posA[3]+posA[1]]
    centerB = [posB[2]+posB[0], posB[3]+posB[1]]
    if centerA[0] != centerB[0] or centerA[1] != centerB[1]:
        # Calculate trajectory
        slopeY = (centerB[1] - centerA[1])/2
        slopeX = (centerB[0] - centerA[0])/2
        slope = math.atan2(slopeY, slopeX)
        y = math.sin(slope) * speed
        x = math.cos(slope) * speed
        # Check overshooting
        return [1, min([slopeX, x], key=abs),  min([slopeY, y], key=abs)]
    return [0, 0, 0]


# Player
def movePlayer():
    """Move player towards its destinations."""
    movIncr = move(canvas.coords(player[0]), canvas.coords(dest), speed[0])
    if movIncr[0] == 1:
        canvas.move(player[0], movIncr[1], movIncr[2])
        canvas.move(player[1], movIncr[1], movIncr[2])


def removeDest():
    """Make destination invisible."""
    canvas.itemconfig(dest, fill="")


# Enemy
def addEnemy():
    """Add new enemy if necessary."""
    global enemies
    limit = 2 + score//2
    elapsedTime = time.time() - startTime
    # Check limit
    if len(enemies) < limit and int(elapsedTime) % 2 == 0:
        # Create random spawn
        posSpwn = random.randint(0, 99)
        sideSpwn = random.randint(0, 3)
        if sideSpwn == 0:
            temp = posSpwn/100*width
            enemies.append([canvas.create_oval(temp, -100,
                                               temp+50, -50,
                                               fill="red"),
                            canvas.create_image(temp, -100, image=enemyImg,
                                                anchor="nw")])
        elif sideSpwn == 1:
            temp = posSpwn/100*height
            enemies.append([canvas.create_oval(width+50, temp,
                                               width+100, temp+50,
                                               fill="red"),
                            canvas.create_image(width+50, temp,
                                                image=enemyImg,
                                                anchor="nw")])
        elif sideSpwn == 2:
            temp = posSpwn/100*width
            enemies.append([canvas.create_oval(temp, height+50,
                                               temp+50, height+100,
                                               fill="red"),
                            canvas.create_image(temp, height+50,
                                                image=enemyImg,
                                                anchor="nw")])
        else:
            temp = posSpwn/100*height
            enemies.append([canvas.create_oval(-100, temp,
                                               -50, temp+50,
                                               fill="red"),
                            canvas.create_image(-100, temp,
                                                image=enemyImg,
                                                anchor="nw")])


def moveEnemy():
    """Move enemies towards player and try to add new enemies."""
    global q, score
    for enemy in enemies:
        movIncr = move(canvas.coords(enemy[0]),
                       canvas.coords(player[0]),
                       speed[1])
        # Move
        if movIncr[0] == 1:
            canvas.move(enemy[0], movIncr[1], movIncr[2])
            canvas.move(enemy[1], movIncr[1], movIncr[2])
        # Check collision with Ability 1
        if overlapping(canvas.coords(enemy[0]), canvas.coords(q[0])):
            # Update Score
            score += 1
            txt = "Score: " + str(score)
            canvas.itemconfigure(scoreText, text=txt)
            # Remove Ability 1
            canvas.coords(q[0], -100, -100, -90, -90)
            canvas.coords(q[1], -100, -100)
            q[2] = [-95, -95, -95, -95]
            # Delete enemy
            canvas.delete(enemy[0])
            canvas.delete(enemy[1])
            enemies.remove(enemy)
        # Check collision with Ability 2
        elif overlapping(canvas.coords(enemy[0]), canvas.coords(w[0])):
            # Update Score
            score += 1
            txt = "Score: " + str(score)
            canvas.itemconfigure(scoreText, text=txt)
            # Delete enemy
            canvas.delete(enemy[0])
            canvas.delete(enemy[1])
            enemies.remove(enemy)
        # Check collision with player
        elif (overlapping(canvas.coords(enemy[0]),
              canvas.coords(player[0])) and
              not immortal):
            # End game
            return True
    return False


# Obstacles
def addObst():
    """Add new obstacle if necessary."""
    global obstacles
    interval = max(5 - score//10, 1)
    if score < 10:
        times = 1
    elif score < 60:
        times = 2
    else:
        times = 3
    elapsedTime = time.time() - startTime
    # Check limit formula
    if ((int(elapsedTime)+1) % interval == 0 and
       elapsedTime-math.floor(elapsedTime) < times * delay / 1000):
        # Create random spawn
        posSpwn = random.randint(0, 99)
        sideSpwn = random.randint(0, 3)
        if sideSpwn == 0:
            temp = posSpwn/100*width
            newObst = canvas.create_oval(temp, -100,
                                         temp+30, -70,
                                         fill="orange")
            newImg = canvas.create_image(temp, -100,
                                         image=obstImg,
                                         anchor="nw")
        elif sideSpwn == 1:
            temp = posSpwn/100*height
            newObst = canvas.create_oval(width+70, temp,
                                         width+100, temp+30,
                                         fill="orange")
            newImg = canvas.create_image(width+70, temp,
                                         image=obstImg,
                                         anchor="nw")
        elif sideSpwn == 2:
            temp = posSpwn/100*width
            newObst = canvas.create_oval(temp, height+70,
                                         temp+30, height+100,
                                         fill="orange")
            newImg = canvas.create_image(temp, height+70,
                                         image=obstImg,
                                         anchor="nw")
        else:
            temp = posSpwn/100*height
            newObst = canvas.create_oval(-100, temp,
                                         -70, temp+30,
                                         fill="orange")
            newImg = canvas.create_image(-100, temp,
                                         image=obstImg,
                                         anchor="nw")
        movIncr = move(canvas.coords(newObst),
                       canvas.coords(player[0]),
                       speed[3])
        obstacles.append([newObst, newImg, movIncr[1], movIncr[2]])


def moveObst():
    """Move obstacles forward."""
    for obst in obstacles:
        canvas.move(obst[0], obst[2], obst[3])
        canvas.move(obst[1], obst[2], obst[3])
        posObst = canvas.coords(obst[0])
        # Check collision with player
        if overlapping(posObst, canvas.coords(player[0])) and not immortal:
            # End game
            return True
        # Check obstable offscreen
        if (posObst[0] < -100 or posObst[2] > width+100 or
           posObst[1] < -100 or posObst[3] > height+100):
            canvas.delete(obst[0])
            canvas.delete(obst[1])
            # Delete obstacle
            obstacles.remove(obst)
    return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#############################
#
#    SETTINGS METHODS
#
#############################

def readConfig():
    """Read settings file."""
    global bind
    try:
        # Get binds
        f = open("settings.txt", "r")
        lines = f.read().strip('\n').split('\n')
        for line in lines:
            bind.append(line[0])
        f.close()
    except:
        # If file corrupted, restore defaults
        f = open("settings.txt", "w")
        f.write("Q\nW\nE\nB")
        f.close()
        bind = ["Q", "W", "E", "B"]


def updateConfig():
    """Update settings file."""
    f = open("settings.txt", "w")
    txt = "\n".join([elem for elem in bind])
    f.write(txt)
    f.close()
    # Change settings menu labels
    bind1.configure(text="Ability 1: "+bind[0])
    bind2.configure(text="Ability 2: "+bind[1])
    bind3.configure(text="Ability 3: "+bind[2])
    bind4.configure(text="Boss Key: "+bind[3])


def changeAb1():
    """Change ability 1 binding to next key pressed."""
    global changingBind
    clearChange()
    changingBind[0] = True
    change1.configure(bg="brown", activebackground="brown",
                      text="Press new binding...", command=clearChange)


def changeAb2():
    """Change ability 2 binding to next key pressed."""
    global changingBind
    clearChange()
    changingBind[1] = True
    change2.configure(bg="brown", activebackground="brown",
                      text="Press new binding...", command=clearChange)


def changeAb3():
    """Change ability 3 binding to next key pressed."""
    global changingBind
    clearChange()
    changingBind[2] = True
    change3.configure(bg="brown", activebackground="brown",
                      text="Press new binding...", command=clearChange)


def changeAb4():
    """Change ability 4 binding to next key pressed."""
    global changingBind
    clearChange()
    changingBind[3] = True
    change4.configure(bg="brown", activebackground="brown",
                      text="Press new binding...", command=clearChange)


def clearChange():
    """Stop waiting for next key press."""
    global changingBind
    changingBind = [False, False, False, False]
    change1.configure(bg="black", activebackground="black",
                      text="Change binding", command=changeAb1)
    change2.configure(bg="black", activebackground="black",
                      text="Change binding", command=changeAb2)
    change3.configure(bg="black", activebackground="black",
                      text="Change binding", command=changeAb3)
    change4.configure(bg="black", activebackground="black",
                      text="Change binding", command=changeAb4)


def restoreDefaults():
    """Restore default key bindings."""
    global bind
    bind = ["Q", "W", "E", "B"]
    clearChange()
    updateConfig()


def backSettings():
    """Back out of Settings Frame."""
    clearChange()
    if gameOver:
        toMenu()
    else:
        toPause()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#############################
#
#    LEADER BOARDS METHODS
#
#############################

def readLeaders():
    """Read Leader Board file."""
    global leaderData
    try:
        # Get leaders
        f = open("leaderboard.txt", "r")
        lines = f.read().strip('\n').split('\n')
        leaderData = []
        for line in lines:
            leaderData.append(line.split(' '))
        # Sort leaders
        leaderData = sorted(leaderData, key=lambda x: int(x[1]), reverse=True)
        f.close()
        # Update leader board frame labels
        for i in range(5):
            if i < len(leaderData) and leaderData[i][0] != '':
                txt = (str(i+1) +
                       "		" +
                       leaderData[i][0] +
                       "		" +
                       leaderData[i][1])
            else:
                txt = ""
            leaderLabels[i].configure(text=txt)
    except:
        # Clear file
        f = open("leaderboard.txt", "w")
        f.close()
        leaderData = []
        # Clear leader board frame labels
        for i in range(5):
            leaderLabels[i].configure(text="")
    # Update leaders
    f = open("leaderboard.txt", "w")
    for i in range(min(len(leaderData), 5)):
        f.write(leaderData[i][0]+" "+leaderData[i][1]+"\n")
    f.close()


def enterName():
    """Get initials from nameEntry and save to leader board."""
    global pause
    pause = False
    name = nameEntry.get().upper()
    newName = re.search(r'[A-Z]{3}', name)
    if not newName:
        # Invalid name
        txt = "AAA"
    else:
        txt = newName.group(0)
    with open("leaderboard.txt", "a") as f:
        f.write(txt+" "+str(score)+"\n")
    toLeaders()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#############################
#
#    SETTING UP FRAMES
#
#############################

# Creating root widget
width = 1600
height = 900
window = setWindowDimensions(width, height)

# Creating root binds
window.bind("<B3-Motion>", dragDest)
window.bind("<Button-3>", moveDest)
window.bind("<Escape>", pausePress)
window.bind("<Shift-F1>", immortalSwitch)
window.bind("<Shift-F2>", cooldownsSwitch)
window.bind("<Shift-F3>", speedSwitch)
window.bind("<Key>", anykeyPress)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating canvas and its widgets
canvas = Canvas(window, bg="black", width=width, height=height)
scoreText = canvas.create_text(width/2, 30, fill="white",
                               font="Helvetica 20 italic bold",
                               text="Score: 0")
cheatText1 = canvas.create_text(width-100, 30, fill="red",
                                font="Helvetica 20 bold",
                                text="")
cheatText2 = canvas.create_text(width-100, 80, fill="red",
                                font="Helvetica 20 bold",
                                text="")
cheatText3 = canvas.create_text(width-100, 130, fill="red",
                                font="Helvetica 20 bold",
                                text="")
qBox = canvas.create_rectangle(width/2-125, height-85, width/2-45, height-5,
                               fill="white",
                               outline="gray",
                               width=5)
qText = canvas.create_text(width/2-85, height-40, fill="green",
                           font="Helvetica 40 bold",
                           text="Q")
wBox = canvas.create_rectangle(width/2-40, height-85, width/2+40, height-5,
                               fill="white",
                               outline="gray",
                               width=5)
wText = canvas.create_text(width/2, height-40,
                           fill="green",
                           font="Helvetica 40 bold",
                           text="W")
eBox = canvas.create_rectangle(width/2+45, height-85, width/2+125, height-5,
                               fill="white",
                               outline="gray",
                               width=5)
eText = canvas.create_text(width/2+85, height-40,
                           fill="green",
                           font="Helvetica 40 bold",
                           text="E")

# Setting universal variables
playerSize = 50
gameOver = True
pause = False
bossOn = False
startPos = (width//2-playerSize//2, height//2-playerSize//2,
            width//2+playerSize//2, height//2+playerSize//2)

# Check game assets
# Use only shapes if missing
try:
    playerImg = PhotoImage(file="assets/player.png")
except:
    playerImg = PhotoImage()
try:
    enemyImg = PhotoImage(file="assets/enemy.png")
except:
    enemyImg = PhotoImage()
try:
    obstImg = PhotoImage(file="assets/obst.png")
except:
    obstImg = PhotoImage()
try:
    qImg = PhotoImage(file="assets/q.png")
except:
    qImg = PhotoImage()
try:
    wImg = PhotoImage(file="assets/w.png")
except:
    wImg = PhotoImage()
try:
    bossImg = PhotoImage(file="assets/boss.png")
except:
    bossImg = PhotoImage()

# Creating game elements
player = [canvas.create_oval(startPos, fill="green"),
          canvas.create_image(width//2-playerSize//2, height//2-playerSize//2,
                              image=playerImg, anchor='nw')]
dest = canvas.create_oval(startPos)
enemies = []
obstacles = []
leaderData = []
bind = []
changingBind = [False, False, False, False]
q = [canvas.create_oval(-100, -100, -90, -90, fill="blue"),
     canvas.create_image(-100, -100, image=qImg, anchor="nw"),
     [-95, -95, -95, -95]]
w = [canvas.create_oval(-200, -200, -100, -100, fill="purple"),
     canvas.create_image(-200, -200, image=wImg, anchor="nw")]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Menu Frame and its widgets
menuFrame = Frame(window, width=width, height=height, bg="black")
title1 = Label(menuFrame, bg="black", fg="royal blue",
               text="MOBA Trainer", font="Helvetica 80 bold")
title1.place(x=width/3, y=height/3-50, anchor="center")
description = Label(menuFrame, justify="l", bg="black", fg="green",
                    text="Improve your MOBA mechanics by dodging enemies" +
                    "\n" +
                    "and hitting skillshots in this fast-paced game." +
                    "\n" +
                    "Can you top the leader board?",
                    font="Helvetica 20 bold")
description.place(x=width/3, y=height/2-50, anchor="center")
howTo = Label(menuFrame, justify="l", bg="black", fg="green",
              text="How to play:\n\n" +
              "Move and avoid getting hit by right-clicking" +
              "\n" +
              "Aim your abilities by hovering your mouse and"+"\n" +
              "pressing the ability key to kill enemies and score points!" +
              "\n" +
              "Remember to check your available abilities" +
              "\n" +
              "at the bottom of the screen" + "\n" +
              "Ability 1: Shoot projectile" + "\n" +
              "Ability 2: Kill all enemies in targeted area" + "\n" +
              "Ability 3: Blink to nearby location" + "\n" +
              "Esc: Pause game",
              font="Helvetica 20 bold")
howTo.place(x=width/3, y=height/2+200, anchor="center")
bStartGame = Button(menuFrame, width="15", height="3",
                    bg="black", fg="green",
                    activebackground="black", activeforeground="royal blue",
                    bd=4,
                    font="Helvetica 20 bold", text="New Game",
                    command=startGame)
bStartGame.place(x=2*width/3, y=height/4+50, anchor="center")
bLoadGame1 = Button(menuFrame, width="15", height="3",
                    bg="black", fg="green",
                    activebackground="black", activeforeground="royal blue",
                    bd=4,
                    font="Helvetica 20 bold", text="Load Game",
                    command=toLoad)
bLoadGame1.place(x=2*width/3, y=height/4+150, anchor="center")
bLeaderBoard1 = Button(menuFrame, width="15", height="3",
                       bg="black", fg="green",
                       activebackground="black", activeforeground="royal blue",
                       bd=4,
                       font="Helvetica 20 bold", text="Leader Board",
                       command=toLeaders)
bLeaderBoard1.place(x=2*width/3, y=height/4+250, anchor="center")
bSettings1 = Button(menuFrame, width="15", height="3",
                    bg="black", fg="green",
                    activebackground="black", activeforeground="royal blue",
                    bd=4,
                    font="Helvetica 20 bold", text="Settings",
                    command=toSettings)
bSettings1.place(x=2*width/3, y=height/4+350, anchor="center")
bExit = Button(menuFrame, width="15", height="3",
               bg="black", fg="green",
               activebackground="black", activeforeground="red",
               bd=4,
               font="Helvetica 20 bold", text="Exit", command=toExit)
bExit.place(x=2*width/3, y=height/4+450, anchor="center")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Pause Frame and its widgets
pauseFrame = Frame(window, width=width, height=height, bg="black")
title2 = Label(pauseFrame, bg="black", fg="green",
               text="Game Paused", font="Helvetica 80 bold")
title2.place(x=width/2, y=200, anchor="center")
bResume = Button(pauseFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="royal blue",
                 bd=4,
                 font="Helvetica 20 bold", text="Resume Game",
                 command=lambda: pausePress(None))
bResume.place(x=width/2, y=350, anchor="center")
bSaveGame = Button(pauseFrame, width="15", height="3", bg="black", fg="green",
                   activebackground="black", activeforeground="royal blue",
                   bd=4,
                   font="Helvetica 20 bold", text="Save Game",
                   command=toSave)
bSaveGame.place(x=width/2, y=450, anchor="center")
bLoadGame2 = Button(pauseFrame, width="15", height="3",
                    bg="black", fg="green",
                    activebackground="black", activeforeground="royal blue",
                    bd=4,
                    font="Helvetica 20 bold", text="Load Game",
                    command=toLoad)
bLoadGame2.place(x=width/2, y=550, anchor="center")
bSettings2 = Button(pauseFrame, width="15", height="3",
                    bg="black", fg="green",
                    activebackground="black", activeforeground="royal blue",
                    bd=4,
                    font="Helvetica 20 bold", text="Settings",
                    command=toSettings)
bSettings2.place(x=width/2, y=650, anchor="center")
bMenu2 = Button(pauseFrame, width="15", height="3",
                bg="black", fg="green",
                activebackground="black", activeforeground="red",
                bd=4,
                font="Helvetica 20 bold", text="Exit to Main Menu",
                command=toMenuExit)
bMenu2.place(x=width/2, y=750, anchor="center")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Game Over Frame and its widgets
gameOverFrame = Frame(window, width=width, height=height, bg="black")
title3 = Label(gameOverFrame, bg="black", fg="red",
               text="Game Over!", font="Helvetica 80 bold")
title3.place(x=width/2, y=200, anchor="center")
score3 = Label(gameOverFrame, bg="black", fg="green",
               text="", font="Helvetica 20 bold")
score3.place(x=width/2, y=300, anchor="center")
bRestart = Button(gameOverFrame, width="15", height="3",
                  bg="black", fg="green",
                  activebackground="black", activeforeground="royal blue",
                  bd=4,
                  font="Helvetica 20 bold", text="Restart Game",
                  command=startGame)
bRestart.place(x=width/2, y=450, anchor="center")
bLeaderBoard3 = Button(gameOverFrame, width="15", height="3",
                       bg="black", fg="green",
                       activebackground="black", activeforeground="royal blue",
                       bd=4,
                       font="Helvetica 20 bold", text="Leader Board",
                       command=toLeaders)
bLeaderBoard3.place(x=width/2, y=550, anchor="center")
bMenu3 = Button(gameOverFrame, width="15", height="3",
                bg="black", fg="green",
                activebackground="black", activeforeground="red",
                bd=4,
                font="Helvetica 20 bold", text="Exit to Main Menu",
                command=toMenu)
bMenu3.place(x=width/2, y=650, anchor="center")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Leader Board Frame and its widgets
leaderBoardFrame = Frame(window, width=width, height=height, bg="black")
title4 = Label(leaderBoardFrame, bg="black", fg="green",
               text="Leader Board", font="Helvetica 80 bold")
title4.place(x=width/2, y=100, anchor="center")
headings = Label(leaderBoardFrame, bg="black", fg="green",
                 text="RANK                        " +
                 "NAME                        " +
                 "SCORE",
                 font="Helvetica 20 bold")
headings.place(x=width/2, y=225, anchor="center")
leader1 = Label(leaderBoardFrame, bg="black", fg="green",
                text="", font="Helvetica 20 bold")
leader1.place(x=width/2-270, y=300, anchor="nw")
leader2 = Label(leaderBoardFrame, bg="black", fg="green",
                text="", font="Helvetica 20 bold")
leader2.place(x=width/2-270, y=400, anchor="nw")
leader3 = Label(leaderBoardFrame, bg="black", fg="green",
                text="", font="Helvetica 20 bold")
leader3.place(x=width/2-270, y=500, anchor="nw")
leader4 = Label(leaderBoardFrame, bg="black", fg="green",
                text="", font="Helvetica 20 bold")
leader4.place(x=width/2-270, y=600, anchor="nw")
leader5 = Label(leaderBoardFrame, bg="black", fg="green",
                text="", font="Helvetica 20 bold")
leader5.place(x=width/2-270, y=700, anchor="nw")
bMenu4 = Button(leaderBoardFrame, width="15", height="3",
                bg="black", fg="green",
                activebackground="black", activeforeground="red",
                bd=4,
                font="Helvetica 20 bold", text="Exit to Main Menu",
                command=toMenu)
bMenu4.place(x=width/2, y=850, anchor="center")
leaderLabels = [leader1, leader2, leader3, leader4, leader5]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Add Score to Leader Board Frame and its widgets
addScoreFrame = Frame(window, width=width, height=height, bg="black")
title5 = Label(addScoreFrame, bg="black", fg="green",
               text="Enter name", font="Helvetica 80 bold")
title5.place(x=width/2, y=300, anchor="center")
nameEntry = Entry(addScoreFrame, bg="black", fg="green",
                  font="Helvetica 20 bold")
nameEntry.place(x=width/2, y=450, anchor="center")
nameGet = Button(addScoreFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="green",
                 bd=4,
                 font="Helvetica 20 bold", text="OK",
                 command=enterName)
nameGet.place(x=width/2, y=550, anchor="center")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Settings Frame and its widgets
settingsFrame = Frame(window, width=width, height=height, bg="black")
title6 = Label(settingsFrame, bg="black", fg="green",
               text="Settings", font="Helvetica 80 bold")
title6.place(x=width/2, y=100, anchor="center")
bind1 = Label(settingsFrame, bg="black", fg="green",
              text="", font="Helvetica 20 bold")
bind1.place(x=width/2-200, y=250, anchor="nw")
change1 = Button(settingsFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="royal blue",
                 bd=4,
                 font="Helvetica 20 bold", text="Change binding",
                 command=changeAb1)
change1.place(x=width/2+100, y=275, anchor="center")
bind2 = Label(settingsFrame, bg="black", fg="green",
              text="", font="Helvetica 20 bold")
bind2.place(x=width/2-200, y=350, anchor="nw")
change2 = Button(settingsFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="royal blue",
                 bd=4,
                 font="Helvetica 20 bold", text="Change binding",
                 command=changeAb2)
change2.place(x=width/2+100, y=375, anchor="center")
bind3 = Label(settingsFrame, bg="black", fg="green",
              text="", font="Helvetica 20 bold")
bind3.place(x=width/2-200, y=450, anchor="nw")
change3 = Button(settingsFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="royal blue",
                 bd=4,
                 font="Helvetica 20 bold", text="Change binding",
                 command=changeAb3)
change3.place(x=width/2+100, y=475, anchor="center")
bind4 = Label(settingsFrame, bg="black", fg="green",
              text="", font="Helvetica 20 bold")
bind4.place(x=width/2-200, y=550, anchor="nw")
change4 = Button(settingsFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="royal blue",
                 bd=4,
                 font="Helvetica 20 bold", text="Change binding",
                 command=changeAb4)
change4.place(x=width/2+100, y=575, anchor="center")
default = Button(settingsFrame, width="15", height="3",
                 bg="black", fg="green",
                 activebackground="black", activeforeground="royal blue",
                 bd=4,
                 font="Helvetica 20 bold", text="Restore defaults",
                 command=restoreDefaults)
default.place(x=width/2, y=700, anchor="center")
bMenu6 = Button(settingsFrame, width="15", height="3",
                bg="black", fg="green",
                activebackground="black", activeforeground="red",
                bd=4,
                font="Helvetica 20 bold", text="Go back",
                command=backSettings)
bMenu6.place(x=width/2, y=800, anchor="center")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Creating Boss Key Frame and its widgets
bossFrame = Frame(window, width=width, height=height, bg="black")
bossMask = Label(bossFrame, image=bossImg,
                 height=height, width=width, bg="black")
bossMask.place(x=width/2, y=height/2, anchor="center")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#############################
#
#    STARTING PROGRAM
#
#############################

# Read settings.txt (create if it doesn't exist or is corrupted)
readConfig()
updateConfig()
# Read leaderboard.txt (create if it doesn't exist or is corrupted)
readLeaders()
# Open Main Menu Frame
toMenu()
# Start running loop
window.mainloop()
