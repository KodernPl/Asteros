
# implementation of Spaceship - program template for RiceRocks
import pygame
from pygame.locals import *
import math
import random

pygame.init()
pygame.mixer.init()


 
# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
INITIAL_SCORE = score
INITIAL_LIVES = lives
time = 0
started = False
rock_group = set([])
missile_group = set([])
explosion_group = set([])
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])

debris_image = pygame.image.load("Content\\debris2_blue.png")

# background image
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = pygame.image.load("Content/back.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = pygame.image.load("Content/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image1 = pygame.image.load("Content/ship1.png")
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image2 = pygame.image.load("Content/ship2.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = pygame.image.load("Content/shot2.png")

# asteroid images 
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image1 = pygame.image.load("Content/asteroid1.png")
asteroid_image2 = pygame.image.load("Content/asteroid2.png")
asteroid_image3= pygame.image.load("Content/asteroid3.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = pygame.image.load("Content/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg

missile_sound = 0
ship_thrust_sound = 0
explosion_sound =0
#missile_sound =  pygame.mixer.music.load("Content/explosion.mp3")
#ship_thrust_sound =  pygame.mixer.music.load("Content/thrust.mp3")
#explosion_sound = pygame.mixer.music.load("Content/explosion.mp3")

soundtrack = pygame.mixer.music.load("Content/soundtrack.mp3")
pygame.mixer.music.set_volume(.5)
pygame.mixer.music.play(-1,0.0)



# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image1, image2, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image1 = image1
        self.image2 = image2
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.blit(rot_center(self.image2,-self.angle*57.3), (self.pos[0]-self.image_size[0]/2,self.pos[1]-self.image_size[1]/2),(0,0,self.image_size[0],self.image_size[1]))
            
        else:
            canvas.blit(rot_center(self.image1,-self.angle*57.3), (self.pos[0]-self.image_size[0]/2,self.pos[1]-self.image_size[1]/2),(0,0,self.image_size[0],self.image_size[1]))
 
    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        #if on:
        #    ship_thrust_sound.rewind()
        #    ship_thrust_sound.play()
        #else:
        #    ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        global a_missile, missile_group
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        self.lifespan;
        #if sound:
            #sound.rewind()
            #sound.play()
   
    def draw(self, canvas):
        if self.animated:
            canvas.blit(rot_center(self.image,self.angle*57.3), (self.pos[0]-self.image_size[0]/2,self.pos[1]-self.image_size[1]/2),(0+self.age*self.image_size[0],0,self.image_size[0],self.image_size[1]))
        else:
         
            canvas.blit(rot_center(self.image,self.angle*57.3) ,(self.pos[0]-self.image_size[0]/2,self.pos[1]-self.image_size[1]/2),(0,0,self.image_size[0],self.image_size[1]))
    
         

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # update age
        self.age += 1
        if self.age >= self.lifespan:
            self.age = 0
            return False
        return True
    
    def collide(self, other_object):
        radius_sum = self.get_radius() + other_object.get_radius()
        if (radius_sum > dist(self.pos, other_object.get_position() )):
            return True 
        return False
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius

# helper  
def group_collide(group_set, other_object_sprite):
    global explosion_group
    for idx in set(group_set):
        
        if idx.collide(other_object_sprite):
            group_set.remove(idx)
            explosion_pos = [idx.pos[0],idx.pos[1]]
            explosion_vel = [0,0]
            explosion_avel = 0
            a_explosion = Sprite(explosion_pos, explosion_vel, 0, explosion_avel, explosion_image, explosion_info)
            explosion_group.add(a_explosion)
            return True
    return False

def group_group_collide(group1, group2):
    for idx in set(group1):
        if group_collide(group2, idx):
            group1.remove(idx)
            return True
    return False
        
def process_sprite_group(rock_group, canvas):
    for idx in set(rock_group):
        idx.draw(canvas)
        if idx.update()==False:
            rock_group.remove(idx)
    
       
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started,lives, score, INITIAL_LIVES, INITIAL_SCORE
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = INITIAL_LIVES
        score = INITIAL_SCORE
        #soundtrack.rewind()
        #soundtrack.play()

def draw(canvas):
    global time, started, rock_group, lives, score, explosion_group
 
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.blit(nebula_image,(0,0))
    canvas.blit(debris_image, (wtime-WIDTH,50))
    canvas.blit(debris_image, (wtime,50))

    ## draw UI
    font = pygame.font.SysFont('Calibri', 22, True, False)
    text = font.render("Lives",True,WHITE)
    canvas.blit(text, [50, 50])
    text = font.render("Score",True,WHITE)
    canvas.blit(text, [680, 50])
    text = font.render(str(lives),True,WHITE)
    canvas.blit(text, [50, 80])
    text = font.render(str(score),True,WHITE)
    canvas.blit(text, [680, 80])



    #text = font.render(str(timer2),True,WHITE)
    #canvas.blit(text, [680, 90])

    #text = font.render(str(timer3),True,WHITE)
    #canvas.blit(text, [680, 100])
    
    ## draw ship and sprites
    my_ship.draw(canvas)

    ## update ship and sprites
    my_ship.update()
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    
    if group_collide(rock_group, my_ship):
        lives-= 1
        if lives <=0:
            explosion_pos = [my_ship.pos[0],my_ship.pos[1]]
            explosion_vel = [0,0]
            explosion_avel = 0
            a_explosion = Sprite(explosion_pos, explosion_vel, 0, explosion_avel, explosion_image, explosion_info)
            explosion_group.add(a_explosion)
            started = False
            for idx in set(rock_group):
                rock_group.remove(idx)
                   
    
    if group_group_collide(missile_group, rock_group):
        score+= 1
    # draw splash screen if not started
    if not started:
        size = splash_info.get_size()
        canvas.blit(splash_image, ((WIDTH / 2) - size[0]/2, (HEIGHT / 2)- size[1]/2))

# timer handler that spawns a rock    
def rock_spawner():
    
    global rock_group, started
    spawned = False
    if started:
        while spawned != True:
            rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
            rock_vel = [random.random() * 1.9 - .3, random.random() * 1.9 - .3]
            rock_avel = random.random() * .2 - .1
            randomize = random.randrange(0, 3)
            if(randomize==0):
                a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image1, asteroid_info)
            elif(randomize==1):
                a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image2, asteroid_info)
            else:
                a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image3, asteroid_info)
            if a_rock.collide(my_ship) == False:
                rock_group.add(a_rock) if len(rock_group)<12 else rock_group.pop() 
                spawned == True
                break

## initialize stuff
pygame.display.set_caption("Asteros")
frame = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
frame.fill((0, 0, 0))
frame.blit(nebula_image, (0, 0))
# Used to manage how fast the screen updates
clock = pygame.time.Clock()


# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image1,ship_image2, ship_info)
a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, .1, asteroid_image1, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)

timer = 0
timer2 = 0
timer3 = 0
while True:
        if(started == False):
            imer = 0
            timer2 = 0
            timer3 = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            #Changes the moving variables only when the key is being pressed
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_LEFT:
                    my_ship.decrement_angle_vel()
                if event.key == pygame.K_RIGHT:
                    my_ship.increment_angle_vel()
                if event.key == pygame.K_SPACE:
                    my_ship.shoot()
                if event.key == pygame.K_UP:
                    my_ship.set_thrust(True)


            #Stops moving the image once the key isn't being pressed
            elif event.type == pygame.KEYUP:
                
                if event.key == pygame.K_LEFT:
                    my_ship.increment_angle_vel()
                if event.key == pygame.K_RIGHT:
                    my_ship.decrement_angle_vel()
                if event.key == pygame.K_UP:
                    my_ship.set_thrust(False)
            
        draw(frame)
        pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            click(pos)
        timer +=1
        if(timer%(160 - timer2)==0 and started):
            rock_spawner()
            timer2+=3
            
            if(timer2>=140):
                timer2=140;
        pygame.display.flip()
        clock.tick(60)
pygame.quit()