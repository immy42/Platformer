#Import external libraries
import pygame
import PIL
import json
import math
import os
import random
#Initiate pygame window
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

#Establish object lists
Platforms = []
Enemies = []
Pictures = []
Enemies = []
Active_Enemies = []
PlayerProjectiles = []

#Globals -------------------------------------------------------------------------------

#Control config
RightButton = pygame.K_RIGHT
LeftButton = pygame.K_LEFT
JumpButton = pygame.K_z
DebugButton = pygame.K_d
ShootButton = pygame.K_x

global camera
camera = "centered"

global sprites
sprites = {
    "platform":r"sprites\platform.png",
    "background":r"sprites\background.png",
    "player_idle":[r"sprites\player_idle.png",r"sprites\player_idle_blink.png"],
    "player_run": [r"sprites\player_run_1.png", r"sprites\player_run_2.png", r"sprites\player_run_3.png",r"sprites\player_run_4.png", r"sprites\player_run_3.png"],
    "player_hurt":[r"sprites\player_hurt.png",r"sprites\player_hurt_2.png"],
    "player_air":r"sprites\player_air.png",
    "enemy1_idle":r"sprites\enemy1_idle.png",
    "enemy1_change":[r"sprites\enemy1_atk_0.png",r"sprites\enemy1_atk_1.png",r"sprites\enemy1_atk_2.png",r"sprites\enemy1_atk_3.png"],
    "enemy1_atk":r"sprites\enemy1_atk_3.png",
    "ray":r"sprites\ray.png",
    "player_hp":[r"sprites\player_health.png", r"sprites\player_health_loss.png"],
    "player_bullet":r"sprites\player_bullet.png"
}

#Globals -------------------------------------------------------------------------------

#Functions -----------------------------------------------------------------------------
#See documentation

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
    stageL = len(os.listdir(r"data\rooms")) #stageL(ength)
    with open(r"data\start\stage.json") as json_file:
        JF = json.load(json_file)
    json_file.close()
    loadStage(JF,[stageX,stageY])
    stageX+=1
    LE = JF["exit"]#last exit
    for i in range(0,stageL):
        while True:
            #Traversable Logic
            LE = JF["exit"]
            with open(r"data\\rooms\\"+random.choice(os.listdir(r"data\rooms"))) as json_file:
                JF = json.load(json_file)
            json_file.close()
            if LE == "R" and JF["entrance"] == "L":
                stageX += 1
                loadStage(JF, [stageX, stageY])
                break
            if LE == "D" and JF["entrance"] == "U":
                stageY += 1
                loadStage(JF, [stageX, stageY])
                break


def draw_ray(xy,mask,offsetX,offsetY,Type): #debug func
    x = xy[0]
    y = xy[1]
    Xx = x
    Yy = y
    Mx = mask[0]
    My = mask[1]
    while True:
        if x != Xx+offsetX:
            if offsetX > 0:
                x += 1
            else:
                x -= 1
        if y != Yy+offsetY:
            if offsetY > 0:
                y += 1
            else:
                y -= 1
        View.draw(sprites["ray"], x, y)
        if x == Xx + offsetX and y == Yy + offsetX:
            break

def draw_mask(xy,mask,offsetX,offsetY,Type): #debug func
    x = xy[0] #player pos X
    y = xy[1] #player pos Y
    Mx = mask[0] #mask width
    My = mask[1] #mask height
    Xx = x-Mx # drawing x pos
    Yy = y #drawing y pos
    while True:
        View.draw(sprites["ray"], Xx, Yy)
        if Xx != x+Mx: #if havent drawn complete width on this line yet
            Xx += 1 #extend line (draw next ray x+1)
        else:
            if Yy != y-My: #if entire height of mask hasnt been reached yet
                Xx = x-Mx #xpos of next ray reset to playerX-width of mask
                Yy -= 1 #next rays to be drawn at y-1 creating a thicker mask drawn
            else:
                break


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
    if Type == "player":
        each = Player
        if offsetX == 0:
            if offsetY == 0:
                if each.y <= y and each.y >= y - My - (get_img_size(each.image)[1]) and each.x >= x - (Mx * 2) and each.x + (get_img_size(each.image)[0]) <= x + (Mx * 2):
                    return True
        return False
    if Type == "enemy":
        for each in Active_Enemies:
            if offsetX == 0:
                if offsetY > 0:
                    if x >= each.x - (get_img_size(each.image)[0]) / 2 and x < each.x + (get_img_size(each.image)[0]) + (get_img_size(each.image)[0] - 1) and each.y == y + offsetY:  # meeting platform at x,(y + offsetY):
                        return True
                if offsetY < 0:
                    if x >= each.x - (get_img_size(each.image)[0]) / 2 and x < each.x + (get_img_size(each.image)[0]) + (get_img_size(each.image)[0] - 1) and each.y == y + offsetY:  # TO EDIT meeting platform at x,(y + offsetY):
                        return True
                if offsetY == 0:
                    #if each.x >= x-Mx and each.x+(get_img_size(each.image)[0]) <= x+Mx and each.y <= y and each.y >= y-My:
                    if each.y <= y and each.y >= y-My-(get_img_size(each.image)[1]) and each.x >= x-(Mx*2) and each.x+(get_img_size(each.image)[0]) <= x+(Mx*2):
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
        if (x >= self.xview[0]-preLoadRadius and x <= self.xview[1]+preLoadRadius and y >= self.yview[0]-preLoadRadius and y <= self.yview[1]+preLoadRadius) or img == self.followObj.image or img in sprites["player_hp"]:
        #^ This can be added before img in the line below to only draw sprites in view, only useful if there are constraints to how many images are visible (e.g ram usage)
            if img != self.followObj.image and img not in sprites["player_hp"]:
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
        self.maskWidth = 8
        self.maskHeight = 16
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
        self.MaxGrav = 3.5
        self.Falling = 0
        self.Jumping = 0
        self.CanJump = 0
        self.JumpSpeedC = 0
        self.status = "idle"
        self.last_status = self.status
        self.dir = 1
        self.img_index = 0
        self.hp = 24
        self.hpN = 0
        self.anim_loops = 0
        self.max_anim_loops = 0
        self.CanHurt = 1
        self.Freeze = 0
        self.Shooting = 0
        self.ShotFrame = 0
        self.MaxShotFrame = 10
        self.origin = [self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2)] #CollisionPoint

    def update(self): #Each frame
        self.origin = [self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2)] #CollisionPoint

        if self.Shooting == 0:
            sprites["player_idle"] = [r"sprites\player_idle.png", r"sprites\player_idle_blink.png"]
            sprites["player_run"] = [r"sprites\player_run_1.png", r"sprites\player_run_2.png", r"sprites\player_run_3.png",r"sprites\player_run_4.png", r"sprites\player_run_3.png"]
            sprites["player_air"] = r"sprites\player_air.png"
        else:
            sprites["player_idle"] = [r"sprites\player_shoot.png",r"sprites\player_shoot.png"]
            self.ShotFrame += 1
            if self.ShotFrame == self.MaxShotFrame:
                self.Shooting = 0
                self.ShotFrame = 0

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
                self.Vspeed = 0.75
                self.Falling = 1
                self.CanJump = 0
            else:
                if self.MaxGrav > self.Vspeed:
                    self.Vspeed = round(self.Vspeed + self.GForce,2) #Change 2 to ? if gravity is to be more than 9.9 in strength
            if self.Freeze == 0:
                self.status = "air"
        if math.floor(self.Vspeed) > 0:
            for i in range(0,math.floor(self.Vspeed)):
                if place_meeting(self.origin, self.maskXY, 0, 1, "platform") == False:
                    self.Yy += 1
                    self.origin[1] += 1
        #Gravity =

        #Enemies and damage-
        if place_meeting(self.origin,self.maskXY,0,0,"enemy") == True and self.CanHurt == 1: #touching enemy
            self.CanHurt = 0
            self.status = "hurt"
            self.hpN += 4
            self.Freeze = 1
            if self.Jumping == 1:
                self.Jumping = 0
                self.Gravity = 1
                self.JumpSpeed = 2
                self.JumpSpeedC = 0
        #if self.status != "hurt" and self.Freeze == 1:
            #self.Freeze = 0
            #self.Hspeed = 0
            #self.CanHurt = 1
        #Enemies and damage=

        if key_pressed[ShootButton]:
            self.Shooting = 1

        #H Movement -
        if key_pressed[JumpButton] and self.Freeze == 0:
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

        #if self.CanHurt == 1: #DEBUG!!!!!
            #draw_mask(self.origin, self.maskXY, 16, 16, "enemy")

        #if key_pressed[DebugButton]:

            #self.x = xRes / 2 - round(get_img_size(self.image)[0] / 2)  # Position on screen (X)
            #self.y = yRes / 2 - round(get_img_size(self.image)[1] / 2)  # Position on screen (Y)
            #self.Xx = self.x  # Position in level (X)
            #self.Yy = self.y  # Position in level (Y)
            #if self.CanHurt == 1:
                #self.CanHurt = 0
            #else:
                #self.CanHurt = 1

        if self.Freeze == 0:
            if key_pressed[RightButton]:
                self.Hspeed = 1
                self.dir = 1
            if key_pressed[LeftButton]:
                self.Hspeed = -1
                self.dir = -1
        if key_pressed[RightButton] == False and key_pressed[LeftButton] == False and self.status != "hurt":
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
        if self.anim_loops == self.max_anim_loops:
            if self.status == "hurt":
                if self.Falling == 0:
                    self.status = "idle"
                else:
                    self.status = "air"
                self.Hspeed = 0
                self.CanHurt = 1
                self.Freeze = 0
            self.anim_loops = 0
            self.max_anim_loops = "null"
        if self.last_status != self.status:
            self.anim_counter = 0
            self.img_index = 0
        if self.status == "idle":
            self.anim_counter_max = 120 #img speed
            if self.anim_counter >= 110:
                self.image = sprites["player_idle"][1]
            else:
                self.image = sprites["player_idle"][0]
        if self.status == "hurt":
            self.max_anim_loops = 10
            self.Hspeed = self.dir*-1
            self.anim_counter_max = 4
            if self.anim_counter >= 3:
                self.image = sprites["player_hurt"][1]
                self.anim_loops += 1
            else:
                self.image = sprites["player_hurt"][0]
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
        View.draw(self.image,self.x,self.y)
        self.last_status = self.status

class player_projectile:

    def __init__(self,x,y,ID):
        PlayerProjectiles.append(self)
        if ID == 1:
            self.image = sprites["player_bullet"]
        self.ID = ID
        self.x = x
        self.y = y
        self.Hspeed = 0

    def update(self):
        if self.ID == 1:
            self.Hspeed = 2
        if Hspeed != 0:
            self.x += Hspeed
        View.draw(self.image, self.x, self.y)
        print(self.x)

class platform:

    def __init__(self,x,y):
        Platforms.append(self)
        self.image = sprites["platform"]
        self.x = x
        self.y = y

    def update(self):
        View.draw(self.image,self.x,self.y)

class enemyOne:

    def __init__(self,x,y):
        Enemies.append(self)
        self.image = sprites["enemy1_idle"]
        self.x = x
        self.y = y
        self.origin = [x-(get_img_size(self.image)[0]/2),y+(get_img_size(self.image)[1])]
        self.status = "idle"
        self.anim_counter = 0
        self.anim_counter_max = 0
        self.img_index = 0

    def update(self):
        View.draw(self.image,self.x,self.y)
        if Player.Xx <= self.x+8 and Player.Xx >= self.x-24 and Player.Yy <= self.y and Player.Yy >= self.y-16:
            if self.status == "idle":
                self.status = "change1"
        else:
            if self.status == "up":
                self.status = "change2"

        self.anim_counter += 1
        if self.anim_counter > self.anim_counter_max:
            self.anim_counter = 0
        if self.status == "idle":
            self.anim_counter_max = 0
            self.image = sprites["enemy1_idle"]
        if self.status == "change1":
            self.anim_counter_max = 7
            self.image = sprites["enemy1_change"][self.img_index]
            if self.anim_counter == 0:
                if self.image in sprites["enemy1_change"]:
                    self.img_index += 1
                else:
                    self.image = sprites["enemy1_change"][0]
                if self.img_index == 3:
                    self.status = "up"
                    self.img_index = 0
        if self.status == "up":
            self.anim_counter_max = 0
            self.image = sprites["enemy1_atk"]
            if self not in Active_Enemies:
                Active_Enemies.append(self)
        else:
            if self in Active_Enemies:
                Active_Enemies.remove(self)
        if self.status == "change2":
            self.anim_counter_max = 7
            self.image = sprites["enemy1_change"][self.img_index]
            if self.anim_counter == 0:
                if self.image in sprites["enemy1_change"]:
                    self.img_index -= 1
                else:
                    self.image = sprites["enemy1_change"][2]
                if self.img_index == -1:
                    self.status = "idle"
                    self.img_index = 0

class picture:

    def __init__(self,img,x,y,layer):
        Pictures.append(self)
        self.image = img
        self.x = x
        self.y = y
        self.layer = layer

    def update(self):
        View.draw(self.image,self.x,self.y)

class healthbar:

    def __init__(self,link):
        self.image = sprites["player_hp"]
        self.imgs = 24
        self.link = link
        self.x = 16
        self.y = 16

    def update(self):
        self.x = 16
        self.y = 16
        self.imgs = self.link.hp
        for i in range(0,self.imgs):
            if self.link.hpN > 0 and i <= self.link.hpN:
                View.draw(self.image[1],self.x,self.y)
            else:
                View.draw(self.image[0], self.x, self.y)
            self.y += 2

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
ran = 0
Lives = 3
generateStage(4,4)
background()
while True:
    if ran == 1:
        for each in Enemies:
            del each
        for each in Platforms:
            del each
        for each in Pictures:
            del each
        for each in PlayerProjectiles:
            del each
        del Player
        del PlayerHB
        del View
    Player = player()
    View = view(Player)
    PlayerHB = healthbar(Player)
    enemyOne(114,163)
    ran = 1
    #Objects -------------------------------------------------------------------------------

    run = True
    while run and Lives > 0:

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
        View.update()
        for each in Platforms:
            each.update()
        Player.update()
        for each in Enemies:
            each.update()
        for each in PlayerProjectiles:
            each.update()
        PlayerHB.update()
        if Player.hpN == Player.hp:
            run = False
            Lives -= 1

        #Update Objs [END]#

        ########################################################## MAIN
        pygame.display.flip()
        pygame.display.update()

print("!!!")
pygame.quit()
exit()
