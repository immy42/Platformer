import pygame
import PIL
import time

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

Platforms = []
Pictures = []

#Globals -------------------------------------------------------------------------------

RightButton = pygame.K_RIGHT
LeftButton = pygame.K_LEFT
UpButton = pygame.K_UP
DownButton = pygame.K_DOWN
EnterButton = pygame.K_RETURN

global camera
camera = "centered"

global sprites
sprites = {
    "picker":r"sprites\picker.png",
    "platform":r"sprites\platform.png",
    "background":r"sprites\background.png",
    "player_idle":[r"sprites\player_idle.png",r"sprites\player_idle_blink.png"],
           }


global platforms
platforms = []

#Globals -------------------------------------------------------------------------------

#Functions -----------------------------------------------------------------------------

def get_img_size(img):
    from PIL import Image
    img = Image.open(img)
    return img.size

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

class picker:

    def __init__(self):
        camera == "centered"
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
        #self.origin = self.Xx + round(get_img_size(self.image)[0] / 2), self.Yy + round(get_img_size(self.image)[1] / 2)  # CollisionPoint
        self.origin = self.Xx,self.Yy

    def update(self): #Each frame
        #self.origin = self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2) #CollisionPoint
        self.origin = self.Xx, self.Yy

        #Physics --

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
                platform(self.Xx,self.Yy)
                self.Moved = self.cooldown
        else:
            self.Moved -= 1
        #H Movement =

        #Physics ==

        #Animations -------------------------------
        self.anim_counter += 1
        if self.anim_counter > self.anim_counter_max:
            self.anim_counter = 0
        if self.last_status != self.status:
            self.anim_counter = 0
            self.img_index = 0
        #Animations -------------------------------
        view.draw(self.image,self.x+8,self.y+15)
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
        each.update()
    view.update()
    for each in Platforms:
        each.update()
    picker.update()

    #Update Objs [END]#

    ########################################################## MAIN
    pygame.display.flip()
    pygame.display.update()

pygame.quit()
