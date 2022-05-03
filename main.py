import pygame
import PIL

pygame.init()
windowIcon = pygame.image.load(r"sprites\icon.png")
pygame.display.set_icon(windowIcon)
pygame.display.set_caption('Mega Man')
xRes = 256
yRes = 224
window = pygame.display.set_mode((xRes, yRes))
roomX = 512
roomY = 448
clock = pygame.time.Clock()

Framerate = 1
bgColour = (255,255,255)

Platforms = []

#Globals -------------------------------------------------------------------------------

RightButton = pygame.K_RIGHT
LeftButton = pygame.K_LEFT

global camera
camera = "centered"

global sprites
sprites = {
    "platform":r"sprites\platform.png",
    "background":r"sprites\background.png",
    "player_idle":r"sprites\player_idle.png",
    "player_idle_blink":r"sprites\player_idle_blink.png"
           }

global platforms
platforms = []

#Globals -------------------------------------------------------------------------------

#Functions -----------------------------------------------------------------------------

def get_img_size(img):
    from PIL import Image
    img = Image.open(img)
    return img.size

def place_meeting(xy,offsetX,offsetY,Type):
    x = xy[0]
    y = xy[1]
    if Type == "platform":
        for each in Platforms:
            if offsetX == 0:
                if offsetY > 0:
                    if x >= each.x and x < each.x+(get_img_size(each.image)[0]) + (get_img_size(each.image)[0]-1) and each.y == y+offsetY: #meeting platform at x,(y + offsetY)
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
        #if x >= self.xview[0] and x <= self.xview[1] and y >= self.yview[0] and y <= self.yview[1] and
        #^ This can be added before img in the line below to only draw sprites in view, only useful if there are constraints to how many images are visible
        if img != self.followObj.image:
            windowXPos = x-self.xview[0]
            windowYPos = y-self.yview[0]
            img = pygame.image.load(img).convert_alpha() #Load Sprite
            window.blit(img,(windowXPos,windowYPos)) #Draw Sprite
        if img == self.followObj.image:
            img = pygame.image.load(img).convert_alpha() #Load Sprite
            window.blit(img,(x,y)) #Draw Sprite

    def update(self):
        if camera == "centered":
            self.followObj.x = xRes/2-(get_img_size(self.followObj.image)[0]/2) #Position on screen (X)
            self.followObj.y = yRes/2-(get_img_size(self.followObj.image)[1])+1 #Position on screen (Y)
        self.xview = self.followObj.origin[0]-(xRes/2),self.followObj.origin[0]+(xRes/2)
        self.yview = self.followObj.origin[1]-(yRes/2),self.followObj.origin[1]+(yRes/2)

        
class player:

    def __init__(self):
        camera == "centered"
        self.image = sprites["player_idle"]
        self.maskWidth = 4
        self.maskHeight = 8
        self.anim_counter = 0
        self.anim_counter_max = 120
        self.x = xRes/2-round(get_img_size(self.image)[0]/2) #Position on screen (X)
        self.y = yRes/2-round(get_img_size(self.image)[1]/2) #Position on screen (Y)
        self.Xx = self.x #Position in level (X)
        self.Yy = self.y #Position in level (Y)
        self.status = "idle"
        self.origin = self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2) #CollisionPoint

    def update(self): #Each frame
        self.origin = self.Xx+round(get_img_size(self.image)[0]/2),self.Yy+round(get_img_size(self.image)[1]/2) #CollisionPoint
        
        #Physics ----------------------------------
        
        #Gravity -
        if place_meeting(self.origin,0,1,"platform") == True: #If player on platform
            #On platform
            pass
        else:
            self.Yy += 2
            pass
        #Gravity =
        
        #H Movement -
        if key_pressed[RightButton]:
            player.Xx += 2
        if key_pressed[LeftButton]:
            player.Xx -= 2
        #H Movement =
            
        #Physics ----------------------------------
            
        #Animations -------------------------------
        self.anim_counter += 1
        if self.anim_counter > self.anim_counter_max:
            self.anim_counter = 0
        if self.status == "idle":
            self.anim_counter_max = 120
            if self.anim_counter >= 110:
                self.image = sprites["player_idle_blink"]
            else:
                self.image = sprites["player_idle"]
        #Animations -------------------------------
        view.draw(self.image,self.x,self.y)

class platform:

    def __init__(self,x,y):
        Platforms.append(self)
        self.image = sprites["platform"]
        self.x = x
        self.y = y

    def update(self):
        view.draw(self.image,self.x,self.y)

class background:

    def __init__(self):
        self.image = sprites["background"]
        self.x = 0
        self.y = 0

    def update(self):
        view.draw(self.image,self.x,self.y)
    
#Objects -------------------------------------------------------------------------------
        
player = player()
bg = background()
view = view(player)
platform(128,113)
platform(112,113)

#Objects -------------------------------------------------------------------------------

run = True
while run:
    
    window.fill((bgColour))
    #clock.tick(Framerate)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        key_pressed = pygame.key.get_pressed()

    ########################################################## Debug

    print("[",str(view.xview[0]),"] Left")
    print("[",str(view.xview[1]),"] Right")
    print("[",str(view.yview[0]),"] Top")
    print("[",str(view.yview[1]),"] Bottom")

    ########################################################## Debug

    ########################################################## MAIN

    #Update Objs [START]#
    
    bg.update()
    view.update()
    for each in Platforms:
        each.update()
    player.update()

    #Update Objs [END]#
    
    ########################################################## MAIN
    pygame.display.flip()
    pygame.display.update()
    
pygame.quit()
exit()
