import pygame
import PIL
import json
import math
import os
import random
pygame.init()
windowIcon = pygame.image.load(r"sprites\icon.png")
pygame.display.set_icon(windowIcon)
pygame.display.set_caption('Mega Man')
xRes = 256
yRes = 224
window = pygame.display.set_mode((xRes, yRes))
roomX = 512
roomY = 448
preLoadRadius = 32
clock = pygame.time.Clock()

Framerate = 60
bgColour = (255,255,255)

Platforms = []
Pictures = []

#Globals -------------------------------------------------------------------------------

RightButton = pygame.K_RIGHT
LeftButton = pygame.K_LEFT
JumpButton = pygame.K_z
DebugButton = pygame.K_d

global camera
camera = "centered"

global sprites
sprites = {
    "platform":r"sprites\platform.png",
    "background":r"sprites\background.png",
    "player_idle":[r"sprites\player_idle.png",r"sprites\player_idle_blink.png"],
    "player_run":[r"sprites\player_run_1.png",r"sprites\player_run_2.png",r"sprites\player_run_3.png",r"sprites\player_run_4.png",r"sprites\player_run_3.png"],
    "player_air":r"sprites\player_air.png"
           }


global platforms
platforms = []

#Globals -------------------------------------------------------------------------------

#Functions -----------------------------------------------------------------------------

def get_img_size(img):
    from PIL import Image
    img = Image.open(img)
    return img.size

def setGrid(x,y):
    a = [],[]
    for i in range(0,x):
        a[0].append([])
    for i in range(0,y):
        a[1].append([])
    return a

def loadStage(level_data,pos):
    oX = pos[0]*256 #offsetX
    oY = pos[1]*224 #offsetY
    for i in range(0,len(level_data["platforms"])): #read platform positions from file
        ii = level_data["platforms"][i][0] #get xPos of platform
        iii = level_data["platforms"][i][1] #get yPos of platform
        ii += oX #add offset based on the imported level's position within the larger stage's Xgrid
        iii += oY#add offset based on the imported level's position within the larger stage's Ygrid
        platform(ii,iii) #create imported platform

def generateStage(w,h):
    StageGrid = setGrid(w, h)
    stageX = 0
    stageY = 0
    stageL = len(os.listdir(r"data\rooms"))
    with open(r"data\start\stage.json") as json_file:
        JF = json.load(json_file)
    json_file.close()
    loadStage(JF,[stageX,stageY])
    stageX+=1
    for i in range(0,stageL):
        with open(r"data\\rooms\\"+random.choice(os.listdir(r"data\rooms"))) as json_file:
            JF = json.load(json_file)
        json_file.close()
        loadStage(JF, [stageX, stageY])
        stageX += 1

def place_meeting(xy,mask,offsetX,offsetY,Type):
    x = xy[0]
    y = xy[1]
    Mx = mask[0]
    My = mask[1]
    if Type == "platform":
        for each in Platforms:
            if offsetX == 0:
                if offsetY > 0:
                    if x >= each.x - (get_img_size(each.image)[0]) / 2 and x < each.x + (get_img_size(each.image)[0]) + (get_img_size(each.image)[0] - 1) and each.y == y + offsetY:  # meeting platform at x,(y + offsetY):
                        return True
                if offsetY < 0:
                    if x >= each.x - (get_img_size(each.image)[0]) / 2 and x < each.x + (get_img_size(each.image)[0]) + (get_img_size(each.image)[0] - 1) and each.y == y + offsetY:  # TO EDIT meeting platform at x,(y + offsetY):
                        return True
        return False

#Functions -----------------------------------------------------------------------------

#Objects -------------------------------------------------------------------------------
class view:

    def __init__(self,followObj):
        followObj.x = xRes/2-(get_img_size(followObj.image)[0]/2) #Position on screen (X)
        followObj.y = yRes/2-(get_img_size(followObj.image)[1])+1 #Position on screen (Y)
        self.xview = followObj.origin[0]-(xRes/2),followObj.origin[0]+(xRes/2)
        self.yview = followObj.origin[1]-(yRes/2),followObj.origin[1]+(yRes/2)
        self.followObj = followObj

    def draw(self,img,x,y):
        if (x >= self.xview[0]-preLoadRadius and x <= self.xview[1]+preLoadRadius and y >= self.yview[0]-preLoadRadius and y <= self.yview[1]+preLoadRadius) or img == self.followObj.image:
        #^ This can be added before img in the line below to only draw sprites in view, only useful if there are constraints to how many images are visible (e.g ram usage)
            if img != self.followObj.image:
                windowXPos = x-self.xview[0]
                windowYPos = y-self.yview[0]
                img = pygame.image.load(img).convert_alpha() #Load Sprite
                window.blit(img,(windowXPos,windowYPos)) #Draw Sprite
            else:
                if self.followObj.dir == 1:
                    img = pygame.image.load(img).convert_alpha() #Load Sprite
                    window.blit(img,(x,y)) #Draw Sprite
                else:
                    img = pygame.image.load(img).convert_alpha() #Load Sprite
                    img = img.copy()
                    img = pygame.transform.flip(img, True, False)
                    window.blit(img, (x, y))  # Draw Sprite

    def update(self):
        if camera == "centered":
            self.followObj.x = xRes/2-(get_img_size(self.followObj.image)[0]/2) #Position on screen (X)
            self.followObj.y = yRes/2-(get_img_size(self.followObj.image)[1])+1 #Position on screen (Y)
        self.xview = self.followObj.origin[0] - (xRes / 2), self.followObj.origin[0] + (xRes / 2)
        self.yview = self.followObj.origin[1] - (yRes / 2), self.followObj.origin[1] + (yRes / 2)


class player:

    def __init__(self):
        camera == "centered"
        self.image = sprites["player_idle"][0]
        self.maskWidth = 4
        self.maskHeight = 8
        self.maskXY = self.maskWidth,self.maskHeight
        self.anim_counter = 0
        self.anim_counter_max = 120
        self.Hspeed = 0
        self.x = 64#xRes/2-round(get_img_size(self.image)[0]/2) #Position on screen (X)
        self.y = 64#yRes/2-round(get_img_size(self.image)[1]/2) #Position on screen (Y)
        self.Xx = self.x #Position in level (X)
        self.Yy = self.y #Position in level (Y)
        self.Vspeed = 0
        self.JumpSpeed = 0
        self.MaxJumpSpeed = 4
        self.Gravity = 1
        self.GForce = 0.1
        self.MaxGrav = 2
        self.Falling = 0
        self.Jumping = 0
        self.CanJump = 0
        self.JumpSpeedC = 0
        self.status = "idle"
        self.last_status = self.status
        self.dir = 1
        self.img_index = 0
        self.origin = [self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2)] #CollisionPoint

    def update(self): #Each frame
        self.origin = [self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2)] #CollisionPoint

        #Physics --
        #Gravity -
        if place_meeting(self.origin,self.maskXY,0,1,"platform") == True: #If player on platform
            if self.status == "air" and self.Falling == 1:
                self.status = "idle"
                self.Vspeed = 0
                self.Falling = 0
                self.Gravity = 1
                self.Jumping = 0
                self.CanJump = 1
                self.JumpSpeed = 2
                self.JumpSpeedC = 0
        elif self.Gravity == 1:
            if self.Falling == 0:
                self.Vspeed = 1
                self.Falling = 1
                self.CanJump = 0
            else:
                if self.MaxGrav > self.Vspeed:
                    self.Vspeed = round(self.Vspeed + self.GForce,2) #Change 2 to ? if gravity is to be more than 9.9 in strength
            self.status = "air"
        if math.floor(self.Vspeed) > 0:
            for i in range(0,math.floor(self.Vspeed)):
                if place_meeting(self.origin, self.maskXY, 0, 1, "platform") == False:
                    self.Yy += 1
                    self.origin[1] += 1
        #Gravity =

        #H Movement -
        if key_pressed[JumpButton]:
            if self.CanJump == 1:
                self.CanJump = 0
                self.Jumping = 1
                self.status = "air"
                self.Gravity = 0
            if self.CanJump == 0 and self.Jumping == 1:
                self.Yy -= self.JumpSpeed
                if self.JumpSpeed != self.MaxJumpSpeed:
                    self.JumpSpeedC += 0.1
                    if self.JumpSpeedC >= 1:
                        self.JumpSpeedC = 0
                        self.JumpSpeed += 1
                else:
                    self.Jumping = 0
                    self.Gravity = 1
                    self.JumpSpeed = 2
                    self.JumpSpeedC = 0
        else:
            if self.Jumping == 1:
                self.Jumping = 0
                self.Gravity = 1
                self.JumpSpeed = 2
                self.JumpSpeedC = 0

        print(self.JumpSpeedC)
        if key_pressed[DebugButton]:
            self.x = xRes / 2 - round(get_img_size(self.image)[0] / 2)  # Position on screen (X)
            self.y = yRes / 2 - round(get_img_size(self.image)[1] / 2)  # Position on screen (Y)
            self.Xx = self.x  # Position in level (X)
            self.Yy = self.y  # Position in level (Y)
        if key_pressed[RightButton]:
            self.Hspeed = 1
            self.dir = 1
        if key_pressed[LeftButton]:
            self.Hspeed = -1
            self.dir = -1
        if key_pressed[RightButton] == False and key_pressed[LeftButton] == False:
            self.Hspeed = 0
            if self.status == "run":
                self.status = "idle"
        if self.status == "idle" and abs(self.Hspeed) == 1:
            self.status = "run"
        if self.Hspeed != 0:
            self.Xx += self.Hspeed
        #H Movement =

        #Physics ==

        #Animations -------------------------------
        self.anim_counter += 1
        if self.anim_counter > self.anim_counter_max:
            self.anim_counter = 0
        if self.last_status != self.status:
            self.anim_counter = 0
            self.img_index = 0
        if self.status == "idle":
            self.anim_counter_max = 120
            if self.anim_counter >= 110:
                self.image = sprites["player_idle"][1]
            else:
                self.image = sprites["player_idle"][0]
        if self.status == "run":
            self.anim_counter_max = 7
            if self.anim_counter == 0:
                if self.image in sprites["player_run"]:
                    self.img_index += 1
                if self.img_index == 5:
                    self.img_index = 1
                self.image = sprites["player_run"][self.img_index]
        if self.status == "air":
            self.anim_counter_max = 0
            self.image = sprites["player_air"]
        #Animations -------------------------------
        view.draw(self.image,self.x,self.y)
        self.last_status = self.status

class platform:

    def __init__(self,x,y):
        Platforms.append(self)
        self.image = sprites["platform"]
        self.x = x
        self.y = y

    def update(self):
        view.draw(self.image,self.x,self.y)


class picture:

    def __init__(self,img,x,y,layer):
        Pictures.append(self)
        self.image = img
        self.x = x
        self.y = y
        self.layer = layer

    def update(self):
        view.draw(self.image,self.x,self.y)

class background:

    def __init__(self):
        self.image = sprites["background"]
        self.rX = round(roomX/32)
        self.rY = round(roomY/32)
        self.Xx = 0
        self.Yy = 0
        for ii in range(0,self.rY):
            for i in range(0,self.rX):
                picture(self.image,self.Xx+(32*i),self.Yy,"back")
            self.Yy += 32


#Objects -------------------------------------------------------------------------------

player = player()
bg = background()
view = view(player)

generateStage(4,4)

#Objects -------------------------------------------------------------------------------

run = True
while run:

    window.fill((bgColour))
    clock.tick(Framerate)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        key_pressed = pygame.key.get_pressed()

    ########################################################## Debug

    #print(player.img_index)

    ########################################################## Debug

    ########################################################## MAIN

    #Update Objs [START]#
    for each in Pictures:
        each.update()
    view.update()
    for each in Platforms:
        each.update()
    player.update()

    #Update Objs [END]#

    ########################################################## MAIN
    pygame.display.flip()
    pygame.display.update()

pygame.quit()
