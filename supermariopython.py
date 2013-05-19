"""
Scott Hongsdusit
Super Mario Bros.
"""

import pygame, sys, pyganim
from pygame.locals import *

# set up pygame
pygame.init()
mainClock = pygame.time.Clock()

# set up the window
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Super Mario Python!')

# set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKYBLUE = (100, 171, 255)
MARIOFONT = pygame.font.Font('mario.ttf', 18)

# variables
global platforms
global enemies
x = 100
y = 384
velocityX = 0 
velocityY = 0
maxVelocityLeft = -3 #max velocity while walking
maxVelocityRight = 4
maxVelocityLR = -7 #max velocity while running
maxVelocityRR = 8
maxVelocityFall = 6
accX = 0 
accY = 0
gravity = 1
onGround = True
collideTop = 0
collideLeft = 0
collideRight = 0
collideBot = 0
moveLeft = False
moveRight = False
running = False
jump = False
flip = False
time = 0
deadTime = 0
levelTime = 0
dead = True
score = 0
coins = 0
levelTimer = 400
startLevel = True
lowTime = False
menu = True
lives = 3
livesScreen = False
livesScreenTime = 0
gameOver = False

#text and menu image
marioText = MARIOFONT.render('MARIO            WORLD   TIME', True, WHITE)
levelText = MARIOFONT.render('1-1', True, WHITE)
menuImg = pygame.image.load('data\sprites\menu.jpg')
menuImg = pygame.transform.scale(menuImg, (640, 480))

#Create sprite animations and hitbox for mario
player = pygame.Rect(x, y, 26, 32)
marioWalk = pyganim.PygAnimation([('data\sprites\mario1.png', 0.1),
                                  ('data\sprites\mario2.png', 0.1),
                                  ('data\sprites\mario3.png', 0.1),
                                  ('data\sprites\mario4.png', 0.1)])
scoreCoin = pyganim.PygAnimation([('data\sprites\scoreCoin1.png', 0.5),
                                  ('data\sprites\scoreCoin2.png', 0.13),
                                  ('data\sprites\scoreCoin3.png', 0.13)])
pyganim.PygAnimation.scale(scoreCoin, (10, 18))
scoreCoin.play()
                                  
marioWalk1 = pygame.image.load('data\sprites\mario1.png')
marioJump = pygame.image.load('data\sprites\marioJUMP.png')
marioDead = pygame.image.load('data\sprites\marioDEAD.png')
marioJ = pygame.transform.scale(marioJump, (28, 32))
marioS = pygame.transform.scale(marioWalk1, (28, 32))
marioD = pygame.transform.scale(marioDead, (30, 28))
marioF = pygame.transform.flip(marioS, 1, 0)
marioJL = pygame.transform.flip(marioJ, 1, 0)
pyganim.PygAnimation.scale(marioWalk, (28, 32))
marioWalk.play()

#camera stuff
camera = pygame.Rect(0, 0, 640, 480)

#setup sound
jumpSound = pygame. mixer.Sound('data\sounds\jump.ogg')
bump = pygame.mixer.Sound('bump.ogg')
coin = pygame.mixer.Sound('data\sounds\coin.ogg')
stomp = pygame.mixer.Sound('data\sounds\stomp.wav')
marioDie = pygame.mixer.Sound('data\sounds\mariodie.wav')
speedUp = pygame.mixer.Sound('fastTheme.ogg')
gameOverSound = pygame.mixer.Sound('data\sounds\gameover.wav')
pygame.mixer.music.load('data\sounds\maintheme.ogg')
musicPlaying = True

class Platform():
    
    def __init__(self, x, y, pic, scaleX, scaleY, fallThrough, animated):
        self.image = pygame.image.load('data\sprites\%s' % (pic))
        if not animated:
            self.floor = pygame.transform.scale(self.image, (scaleX, scaleY))
        else:
            self.aniBlock = pyganim.PygAnimation([('data\sprites\platform-q.png', 0.5),
                                                  ('data\sprites\platform-q2.png', 0.13),
                                                  ('data\sprites\platform-q3.png', 0.13)])
            pyganim.PygAnimation.scale(self.aniBlock, (scaleX, scaleY))
            self.aniBlock.play()
        self.x = x
        self.y = y
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.fallThrough = fallThrough
        self.animated = animated
        self.hit = False
        
    def update(self, cameraX, cameraY):
        if self.animated and self.hit:
            windowSurface.blit(self.hitImage, (self.x-cameraX, self.y-cameraY))
        elif not self.animated:
            windowSurface.blit(self.floor, (self.x-cameraX, self.y-cameraY))
        else:
            self.aniBlock.blit(windowSurface, (self.x-cameraX, self.y-cameraY))
            
    def rect(self, cameraX, cameraY):
        return pygame.Rect(self.x-cameraX, self.y-cameraY, self.scaleX, self.scaleY)
    
    def hitCheck(self, cameraX, cameraY):
        self.hitPic = pygame.image.load("data\sprites\Qhit.png")
        self.hitImage = pygame.transform.scale(self.hitPic, (self.scaleX, self.scaleY))
        if not self.hit:        
            coin.play()
        windowSurface.blit(self.hitImage, (self.x-cameraX, self.y-cameraY))
        self.hit = True
        
class Enemy():
    
    def __init__(self, x, y, pic, scaleX, scaleY, deadX, deadY, frames, aniSpeed):
        self.pic = pic
        self.image1 = [('data\sprites\%s%s.png' % (pic, str(num)), aniSpeed) for num in range(frames)]
        self.image = pyganim.PygAnimation(self.image1)
        pyganim.PygAnimation.scale(self.image, (scaleX, scaleY))
        self.image.play()
        self.imageD = pygame.image.load('data\sprites\%sDEAD.png' % (pic))
        self.imageDEAD = pygame.transform.scale(self.imageD, (deadX, deadY))
        self.x = x
        self.y = y
        self.scaleX = scaleX
        self.scaleY = scaleY
        self.dead = False
        self.onGround = True
        self.enemyMove = -1
        self.collide = 0
        self.remove = False
        self.current = False
        self.shellMove = False
        
    def rect(self, cameraX, cameraY):
        return pygame.Rect(self.x-cameraX, self.y-cameraY, self.scaleX, self.scaleY)
        
    def update(self, cameraX, cameraY):
        if not self.dead:
            self.image.blit(windowSurface, (self.x-cameraX, self.y-cameraY))
        else:
            windowSurface.blit(self.imageDEAD, (self.x-cameraX, self.y-cameraY+16))
        
        
level = """
......................c..........................................................................................................................................................................................................................
...........................................v..................................................v..................................c..............v...............................c................v..............................................
...........c.....................b.............................c...................b.................................c..................b............................c.................b.........................q..c...........................
..........................................................................................1............................................................................................................==........................................
..........................?............................................................++++++++++...++++?................?...........+++....+??+......................................................===........................................
.....................................................................................................................................................................................................====........................................
......................................................................................1.............................................................................................................=====........................................
...................................................................................................................................................................................................======.............w..........................
....................?...+?+?+........................f.........f....................+?+.................+......++.....?..?..?.....+..........++......=..=..........==..=...........++?+...........=======........................................
............................................d.......................................................................................................==..==........===..==........................========........................................
j................................s.....................j..................................................j........................................===..===.j....====..===.....s.............s..=========...j....................................
...............]....h...1...p.................1.[..........11.....]...h.......p...................[......11...........2.]...h.......p..11.11......====p.====....=====..====ph......p....11.....==========...................h....................
---------------------------------------------------------------------------..-----------------....-------------------------------------------------------------------..-------------------------------------------------------------------------------
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..~~~~~~~~~~~~~~~~~....~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

def buildLevel(level):
    platX = 0
    platY = 0
    global platforms
    global enemies
    platforms = []
    enemies = []
    for row in level.split("\n"):
        for col in row:
            if col == "-":
                platforms.append( Platform(platX, platY, "floor.png", 32, 32, False, False) )
            if col == "~":
                platforms.append( Platform(platX, platY, "floor.png", 32, 32, True, False) )
            if col == "+":
                platforms.append( Platform(platX, platY, "brick1.png", 32, 32, False, False) )
            if col == "=":
                platforms.append( Platform(platX, platY, "pyramid.png", 32, 32, False, False) )
            if col == "?":
                platforms.append( Platform(platX, platY, "platform-q.png", 32, 32, False, True) )
            if col == "h":
                platforms.append( Platform(platX, platY, "hill.png", 96, 38, True, False) )
            if col == "j":
                platforms.append( Platform(platX, platY, "bighill.png", 160, 70, True, False) )
            if col == "s":
                platforms.append( Platform(platX, platY, "smallpipe.png", 64, 64, False, False) )
            if col == "d":
                platforms.append( Platform(platX, platY, "medpipe.png", 64, 96, False, False) )
            if col == "f":
                platforms.append( Platform(platX, platY, "bigpipe.png", 64, 128, False, False) )
            if col == "c":
                platforms.append( Platform(platX, platY, "smallcloud.png", 64, 48, True, False) )
            if col == "v":
                platforms.append( Platform(platX, platY, "medcloud.png", 96, 48, True, False) )
            if col == "b":
                platforms.append( Platform(platX, platY, "bigcloud.png", 128, 48, True, False) )
            if col == "p":
                platforms.append( Platform(platX, platY, "smallbush.png", 64, 32, True, False) )
            if col == "[":
                platforms.append( Platform(platX, platY, "medbush.png", 96, 32, True, False) )
            if col == "]":
                platforms.append( Platform(platX, platY, "bigbush.png", 128, 32, True, False) )
            if col == "q":
                platforms.append( Platform(platX-16, platY-16, "flag05.png", 48, 336, False, False) )
            if col == "w":
                platforms.append( Platform(platX, platY, "smallcastle.png", 160, 160, True, False) )
            if col == "1":
                enemies.append( Enemy(platX+5, platY, "goomba", 32, 32, 32, 16, 2, 0.1) )
            if col == "2":
                enemies.append( Enemy(platX-5, platY-16, "koopa", 32, 48, 32, 28, 2, 0.2) )
            platX += 32
        platX = 0
        platY += 32

buildLevel(level)

while True:
        
    if livesScreen and pygame.time.get_ticks() - livesScreenTime >= 4000 and not menu:
        if not gameOver:
            livesScreen = False
            camera.x = 0
            camera.y = 0
            player.x = 100
            player.y = 384
            dead = False
            levelTimer = 400
            startLevel = True
            pygame.mixer.music.load('data\sounds\maintheme.ogg')
            pygame.mixer.music.play(-1, 0.0)
            if flip:
                marioWalk.flip(1, 0)
            buildLevel(level)
        else:
            menu = True
            gameOver = False
            lives = 3
            coins = 0
            score = 0
        
    if not menu:
        windowSurface.fill(SKYBLUE)
        
        collideTop = 0
        collideLeft = 0
        collideRight = 0
        collideBot = 0
        for platform in platforms:
            if platform.x - camera.x >= -400 and platform.x - camera.x <= WINDOWWIDTH:
                platform.update(camera.x, camera.y)
                if not platform.fallThrough:
                    if player.colliderect(platform.rect(camera.x, camera.y)) and not dead:
                        if velocityY >= 0 and (player.y < platform.y):
                            player.bottom = platform.rect(camera.x, camera.y).top + 1
                            collideTop += 1
                        elif velocityY < 0 and (player.y >= platform.y + platform.scaleY-5):
                            player.top = platform.rect(camera.x, camera.y).bottom + 2
                            collideBot += 1
                            if platform.animated:
                                if not platform.hit:
                                    coins += 1
                                    score += 200
                                platform.hitCheck(camera.x, camera.y) # ?-blocks turn to already hit animation
                        elif velocityX < 0 and (player.y >= platform.y):
                            player.left = platform.rect(camera.x, camera.y).right + 5
                            collideLeft += 1
                        elif velocityX > 0 and (player.y >= platform.y):
                            player.right = platform.rect(camera.x, camera.y).left - 5
                            collideRight += 1
        
        for enemy in enemies:
            enemy.collide = 0
            enemy.current = True
            if enemy.dead and pygame.time.get_ticks() - time > 500:
                if not enemy.pic == "koopa" or not (enemy.x - camera.x >= -400 and enemy.x - camera.x <= WINDOWWIDTH):
                    enemy.remove = True
            if enemy.x - camera.x >= -400 and enemy.x - camera.x <= WINDOWWIDTH and not enemy.remove:
                enemy.update(camera.x, camera.y)
                if not enemy.onGround and not enemy.dead:
                    enemy.y += 3
                elif not enemy.dead or (enemy.pic == "koopa"):
                    enemy.x += enemy.enemyMove
                for platform in platforms:
                    if platform.x - camera.x >= -400 and platform.x - camera.x <= WINDOWWIDTH:
                        if not platform.fallThrough:
                            if enemy.rect(camera.x, camera.y).colliderect(platform.rect(camera.x, camera.y)):
                                if enemy.y < platform.y:
                                    enemy.collide += 1
                                elif enemy.enemyMove < 0:
                                    enemy.enemyMove = 1
                                else:
                                    enemy.enemyMove = -1
                if enemy.collide > 0:
                    enemy.onGround = True
                else:
                    enemy.onGround = False
                for enemy1 in enemies:
                    if enemy1.x - camera.x >= -400 and enemy1.x - camera.x <= WINDOWWIDTH and not enemy1.remove and not enemy1.current:
                        if enemy.rect(camera.x, camera.y).colliderect(enemy1.rect(camera.x, camera.y)):
                                if enemy1.pic == "koopa" and enemy1.dead:
                                    enemy.enemyMove = 0
                                    if not enemy.dead:
                                        time = pygame.time.get_ticks()
                                        score += 100
                                    enemy.dead = True
                                if enemy.enemyMove < 0:
                                    enemy.enemyMove = 1
                                else:
                                    enemy.enemyMove = -1
                if player.colliderect(enemy.rect(camera.x, camera.y)) and ( (enemy.pic == "koopa") or (not enemy.dead and not dead) ):
                    if player.x < enemy.x and enemy.pic == "koopa" and enemy.dead:
                        enemy.enemyMove = 5
                    elif player.x > enemy.x and enemy.pic == "koopa" and enemy.dead:
                        enemy.enemyMove = -5                    
                    elif player.y < enemy.y - 10:
                        enemy.enemyMove = 0
                        stomp.play()
                        velocityY = -9
                        enemy.dead = True
                        time = pygame.time.get_ticks()
                        score += 100
                    if player.y >= enemy.y - 2:
                        if not enemy.dead:
                            dead = True
                            onGround = False
                            moveLeft = False
                            moveRight = False
                            running = False
                            jump = False
                            velocityY = -50
                            velocityX = 0
                            lives -= 1
                            marioDie.play()
                            pygame.mixer.music.stop()
                            deadTime = pygame.time.get_ticks()
            enemy.current = False
                    
    if collideTop > 0:
        onGround = True
    else:
        onGround = False
    if collideBot > 0:
        onGround = False
        velocityY = 0
        bump.play()
        jumpSound.stop()
    if collideLeft > 0:
        velocityX = 0
    if collideRight > 0:
        velocityX = 0
        
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == K_RETURN and menu:
            menu = False
            livesScreen = True
            livesScreenTime = pygame.time.get_ticks()
        if not dead and not menu:
            if event.type == KEYDOWN:
                if event.key == ord('x'):
                    running = True
                if (event.key == K_UP or event.key == K_SPACE or event.key == ord('z')) and onGround:              
                    jump = True
                    jumpSound.play()  
                    onGround = False
                if event.key == K_LEFT:
                    moveLeft = True
                    moveRight = False
                    flip = True
                    marioWalk.flip(1, 0)
                elif event.key == K_RIGHT:
                    moveRight = True
                    moveLeft = False
                    flip = False
            if event.type == KEYUP:
                if (event.key == K_UP or event.key == K_SPACE or event.key == ord('z')):
                    jump = False
                if event.key == ord('x'):
                    running = False
                if event.key == K_LEFT:
                    moveLeft = False
                    marioWalk.flip(1, 0)
                elif event.key == K_RIGHT:
                    moveRight = False
                
    # movement of mario
    if jump:
        velocityY = -17
        jump = False
    if velocityY < maxVelocityFall:
        velocityY += gravity
    if not onGround or dead:
        player.y += velocityY
    if onGround: #stop velocity when on the ground
        velocityY = 0
    if moveLeft:
        if not running and player.x > 0:
            accX = -.7
            player.x += velocityX
            if velocityX > maxVelocityLeft:
                velocityX += accX
        elif player.x > 0:
            accX = -1.5
            player.x += velocityX
            if velocityX > maxVelocityLR:
                velocityX += accX
    elif moveRight:
        if not running:
            accX = .7
            if player.x < 300:
                player.x += velocityX
            if velocityX < maxVelocityRight:
                velocityX += accX
        else:
            accX = 1.5
            if player.x < 300:
                player.x += velocityX
            if velocityX < maxVelocityRR:
                velocityX += accX
                
    if velocityX < 0: # friction while running
        velocityX = velocityX + .5
    if velocityX > 0:
        velocityX = velocityX - .5
        
    if (velocityX < .3 or velocityX > -.3) and not moveLeft and not moveRight:
        velocityX = 0
        
    if player.x > 299:
        camera.x += velocityX
        
    if player.y > 480 and not dead:
        dead = True
        onGround = False
        moveLeft = False
        moveRight = False
        running = False
        jump = False
        velocityX = 0
        lives -= 1
        marioDie.play()
        pygame.mixer.music.stop()
        deadTime = pygame.time.get_ticks()
    
    # Drawing sprites for each direction and action
    if not dead:
        if not onGround:
            if not flip:
                windowSurface.blit(marioJ, player)
            else:
                windowSurface.blit(marioJL, player)
        elif moveLeft:
            if not jump:
                marioWalk.blit(windowSurface, player)
        elif moveRight:
            if not jump:
                marioWalk.blit(windowSurface, player)
        elif not moveLeft and not moveRight and onGround:
            if not flip:
                windowSurface.blit(marioS, player)
            else:
                windowSurface.blit(marioF, player)
    else:
        windowSurface.blit(marioD, player)
        
    if dead and pygame.time.get_ticks() - deadTime > 5000 and not menu and not livesScreen:
        livesScreen = True
        livesScreenTime = pygame.time.get_ticks()
   
    if levelTimer <= 100 and not lowTime:
        lowTime = True
        pygame.mixer.music.load('fastTheme.mp3')
        pygame.mixer.music.play(-1, 0.0)
        speedUp.play()
    
    if levelTimer == 0 and not dead:
        dead = True
        onGround = False
        moveLeft = False
        moveRight = False
        running = False
        jump = False
        velocityY = -10
        velocityX = 0
        marioDie.play()
        pygame.mixer.music.stop()
        deadTime = pygame.time.get_ticks()
                
    if (pygame.time.get_ticks() - levelTime > 400 or startLevel == True) and levelTimer > 0 and not livesScreen and not menu:
        levelTime = pygame.time.get_ticks()
        levelTimer -= 1
        startLevel = False
     
    if livesScreen and not menu:
        windowSurface.fill(BLACK)
        if lives > 0:
            livesText = MARIOFONT.render("x  %s" % str(lives), True, WHITE)
            worldText = MARIOFONT.render("WORLD 1-1", True, WHITE)
            windowSurface.blit(livesText, (310, 240))
            windowSurface.blit(worldText, (240, 170))
            windowSurface.blit(marioS, (255, 230))
        else:
            if not gameOver:
                gameOverSound.play()
            gameOverText = MARIOFONT.render("GAME OVER", True, WHITE)
            windowSurface.blit(gameOverText, (240, 170))
            gameOver = True
     
    if menu:       
        windowSurface.blit(menuImg, (0, 0))
    else:
        scoreText = MARIOFONT.render(str(score).zfill(6), True, WHITE)
        coinText = MARIOFONT.render('x%s' % str(coins).zfill(2), True, WHITE)        
        timeText = MARIOFONT.render(str(levelTimer).zfill(3), True, WHITE)
        windowSurface.blit(marioText, (50, 15))
        windowSurface.blit(scoreText, (50, 32))
        windowSurface.blit(coinText, (230, 32))
        windowSurface.blit(levelText, (370, 32))
        windowSurface.blit(timeText, (520, 32))
        scoreCoin.blit(windowSurface, (215 ,30))
    pygame.display.update()
    mainClock.tick(60) # Feel free to experiment with any FPS setting.