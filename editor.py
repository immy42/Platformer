import pygame
import PIL
import time
import json
pygame.init()
windowIcon = pygame.image.load(r"sprites\icon.png")
pygame.display.set_icon(windowIcon)
pygame.display.set_caption('Mega Man')
xRes = 256
yRes = 224
window = pygame.display.set_mode((xRes, yRes))
roomX = 256
roomY = 224
preLoadRadius = 32
clock = pygame.time.Clock()

Framerate = 60
bgColour = (255,255,255)

Pictures = []

#Globals -------------------------------------------------------------------------------

RightButton = pygame.K_RIGHT
LeftButton = pygame.K_LEFT
UpButton = pygame.K_UP
DownButton = pygame.K_DOWN
EnterButton = pygame.K_RETURN
MenuButton = pygame.K_ESCAPE
S_Button = pygame.K_s
R_Button = pygame.K_r
L_Button = pygame.K_l

global camera
camera = "locked"

global sprites
sprites = {
    "menu":[r"sprites\menu.png",r"sprites\highlightG.png",r"sprites\highlightR.png"],
    "picker":r"sprites\picker.png",
    "dropped":[r"sprites\picker_dropped1.png",r"sprites\picker_dropped2.png",r"sprites\picker_dropped3.png",r"sprites\picker_dropped4.png",r"sprites\picker_dropped5.png"],
    "platform":r"sprites\platform.png",
    "background":r"sprites\background.png",
    "player_idle":[r"sprites\player_idle.png",r"sprites\player_idle_blink.png"],
    }

global Platforms
Platforms = []

global SaveData
SaveData = {"platforms":[]}

#Globals -------------------------------------------------------------------------------

#Functions -----------------------------------------------------------------------------

def get_img_size(img):
    from PIL import Image
    img = Image.open(img)
    return img.size

def loadStage(level_data):
    global Platforms
    Platforms = []
    for i in range(0,len(level_data["platforms"])):
        platform(level_data["platforms"][i][0],level_data["platforms"][i][1])
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
        if camera == "locked":
            self.xview = 0,256
            self.yview = 0,224
            self.followObj.x = self.followObj.Xx
            self.followObj.y = self.followObj.Yy

class picker:

    def __init__(self):
        camera = "locked"
        self.Moved = 0
        self.GridX = 16
        self.GridY = 16
        self.image = sprites["picker"]
        self.maskWidth = 4
        self.maskHeight = 8
        self.anim_counter = 0
        self.anim_counter_max = 120
        self.Hspeed = 0
        self.Vspeed = 0
        self.x = 0#xRes / 2 - round(get_img_size(self.image)[0] / 2)  # Position on screen (X)
        self.y = 0#yRes / 2 - round(get_img_size(self.image)[1] / 2)  # Position on screen (Y)
        self.Xx = self.x  # Position in level (X)
        self.Yy = self.y  # Position in level (Y)
        self.status = "idle"
        self.last_status = self.status
        self.dir = 1
        self.cooldown = 8
        self.img_index = 0
        self.MenuCreated = 0
        #self.origin = self.Xx + round(get_img_size(self.image)[0] / 2), self.Yy + round(get_img_size(self.image)[1] / 2)  # CollisionPoint
        self.origin = self.Xx,self.Yy

    def update(self): #Each frame
        #self.origin = self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2) #CollisionPoint
        self.origin = self.Xx, self.Yy

        #H Movement -
        if self.Moved == 0: #add cooldown
            if key_pressed[RightButton]:
                self.Xx += self.GridX
                self.Moved = self.cooldown
            if key_pressed[LeftButton]:
                self.Xx -= self.GridX
                self.Moved = self.cooldown
            if key_pressed[UpButton]:
                self.Yy -= self.GridY
                self.Moved = self.cooldown
            if key_pressed[DownButton]:
                self.Yy += self.GridY
                self.Moved = self.cooldown
            if key_pressed[EnterButton]:
                self.status = "drop"
                self.Moved = self.cooldown
            if key_pressed[MenuButton]:
                if self.MenuCreated == 0:
                    global Menu
                    Menu = menu()
                    self.MenuCreated = 1
                else:
                    del Menu
                    self.MenuCreated = 0
                self.Moved = self.cooldown
        else:
            self.Moved -= 1
        #Movement =

        #Animations -------------------------------
        self.anim_counter += 1
        if self.anim_counter > self.anim_counter_max:
            self.anim_counter = 0
        if self.last_status != self.status:
            self.anim_counter = 0
            self.img_index = 0
        if self.status == "idle":
            self.image = sprites["picker"]
        if self.status == "drop":
            self.anim_counter_max = 2 #Animation speed (frames per sprite)
            if self.anim_counter == 0:
                if self.image in sprites["dropped"]:
                    self.img_index += 1
                if self.img_index == 5: #Animation end (1 frame past last sprite frame)6
                    platform(self.Xx,self.Yy)
                    self.status = "idle"
                try:
                    self.image = sprites["dropped"][self.img_index]
                except:
                    pass
        #Animations -------------------------------

        #final stuff
        view.draw(self.image,self.x,self.y)
        self.last_status = self.status
        
        try:
            Menu.update()
        except:
            pass
            #menu doesnt exist

class platform:

    def __init__(self,x,y):
        Platforms.append(self)
        self.image = sprites["platform"]
        self.x = x
        self.y = y
        global SaveData
        SaveData["platforms"].append([self.x,self.y])

    def __del__(self):
        pass
        #delete obj
    
    def update(self):
        view.draw(self.image,self.x,self.y)

class menu:

    def __init__(self):
        self.image = sprites["menu"][0]
        self.x = 0
        self.y = 0
        self.hasSaved = 0
        self.hasReset = 0
        self.hasLoaded = 0
        self.Dels = 0

    def __del__(self):
        for i in range(0,self.Dels):
            del Pictures[len(Pictures)-1]
        #delete obj

    def update(self):
        view.draw(self.image,self.x,self.y)
        global Platforms

        if key_pressed[S_Button] and self.hasSaved == 0:
            global SaveData
            self.hasSaved = 1
            with open('data\exported.json', 'w') as f:
                f.write(json.dumps(SaveData))
            f.close()
            picture(sprites["menu"][1], 16, 32, "front")
            self.Dels += 1

        if key_pressed[R_Button] and self.hasReset == 0:
            for each in Platforms:
                del each
            Platforms = []
            SaveData["platforms"] = []
            self.hasReset = 1
            picture(sprites["menu"][1], 16, 48, "front")
            self.Dels += 1

        if key_pressed[L_Button] and self.hasLoaded < 1:
            try:
                self.hasLoaded = 1
                with open(r"data\to_import.json") as json_file:
                    print("opened")
                    JF = json.load(json_file)
                json_file.close()
                loadStage(JF)
                picture(sprites["menu"][1], 16, 64, "front")
                self.Dels += 1
            except:
                picture(sprites["menu"][2], 16, 64, "front")
                #file doesnt exist
                self.Dels += 1

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

picker = picker()
bg = background()
view = view(picker)

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
        if each.layer == "back":
            each.update()
    view.update()
    for each in Platforms:
        each.update()
    picker.update()
    for each in Pictures:
        if each.layer == "front":
            each.update()

    #Update Objs [END]#

    ########################################################## MAIN
    pygame.display.flip()
    pygame.display.update()

pygame.quit()
