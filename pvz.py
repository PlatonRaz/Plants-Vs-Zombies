import pygame,sys,random, winsound

pygame.mixer.pre_init(44100,  16, 2, 2048)
pygame.mixer.init()
pygame.init()

pygame.display.set_icon(pygame.image.load("plants/secretsun.png"))
font = pygame.font.Font("SERIO___.TTF",18)



class Sun(pygame.sprite.Sprite):
    score = None
    def __init__(self,anim,x,y,speed):
        super().__init__()
        self.anim = anim
        self.image = anim[0]
        self.speed = speed
        self.rect = self.image.get_rect(center = (x,y))
        self.current_sprite = 0
        self.animation_speed = 0.19

    def update(self):
        if self.current_sprite >= len(self.anim):
            self.current_sprite = 0

        self.rect.y += self.speed
        self.image = self.anim[int(self.current_sprite)]
        self.current_sprite += self.animation_speed

#--------------------------------------------------------------------------------------------------------------------
class Card(pygame.sprite.Sprite):
    obtain = False
    created = False
    stop_enlarging = False
    i = 0
    level = 1
    wallnutcreated = 0
    def __init__(self,image,x,y,recharge,darkened_image):
        super().__init__()
        self.image = image
        self.original_image = image
        self.recharge = recharge
        self.rect = self.image.get_rect(center = (x,y))
        self.recharge_timer = pygame.time.get_ticks() + self.recharge
        self.recharged = True
        self.darkened_image = pygame.image.load(darkened_image).convert_alpha()
        self.speed = 1
        
    def enlarge(enlargedcard,enlargedcardx,enlargedcardy):
        global newenlargedcard, newenlargedcardrect

        if Card.stop_enlarging != True:
            if (Card.i % 10) == 0:
                newenlargedcard = pygame.transform.smoothscale(enlargedcard,(64+Card.i,90+Card.i))

            newenlargedcardrect = enlargedcard.get_rect(center = (enlargedcardx,enlargedcardy))
            newenlargedcardrect.x -= 400
            menu.screen.blit(newenlargedcard,(newenlargedcardrect.x,newenlargedcardrect.y))


        if Card.i >= 160:
            menu.screen.blit(newenlargedcard,(newenlargedcardrect.x,newenlargedcardrect.y))
            Card.stop_enlarging = True

        if Card.i == 240:
            Card.obtain = False
            Card.created = False
            Card.stop_enlarging = False
            Card.i = 0
            Card.level += 1
            for p in plant_group:
                p.kill()

            Wave.victory = False
            Wave.stop_spawning = False
            Wave.normal_wave_counter = 0
            Wave.boss_wave_counter = 0

            game()

        Card.i += 1

    def start_recharge(self):
        if pygame.time.get_ticks() >= self.recharge_timer:
            self.recharged = True
            self.image = self.original_image

    def bowling_move(self):
        self.rect.x -= self.speed

 
        

#--------------------------------------------------------------------------------------------------------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self,picture_path,speed,pos_x,pos_y,bullet_type):
        super().__init__()
        self.bullet_type = bullet_type
        self.image = pygame.image.load(picture_path).convert_alpha()
        self.rect = self.image.get_rect(center = (pos_x,pos_y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed

        if self.rect.x >= menu.screen_width - 50:
            self.kill()
#--------------------------------------------------------------------------------------------------------------------
class Lawnmower(pygame.sprite.Sprite):
    def __init__(self,picture_path,speed,pos_x,pos_y):
        super().__init__()
        self.image = pygame.image.load(picture_path).convert_alpha()
        self.rect = self.image.get_rect(center = (pos_x,pos_y))
        self.speed = speed
        self.touched = False

        self.next_engine_rumble = pygame.time.get_ticks() + 100


    def update(self):
        if self.touched:
            self.rect.x += self.speed
            if pygame.time.get_ticks() >= self.next_engine_rumble:
                pygame.mixer.Sound("sfx/lawnmower.wav").play()
                self.next_engine_rumble = pygame.time.get_ticks() + 9000


        if self.rect.x >= 900:
            self.kill()
#--------------------------------------------------------------------------------------------------------------------
class Zombie(pygame.sprite.Sprite):
    over = False
    killed = 0
    spawned = 0
    def __init__(self,anim,anim_speed,zombie_type,health):
        super().__init__()

        #Sprite Animation--------------------------------------------------------------
        self.anim = anim
        self.current_sprite = 0
        self.animation_speed = anim_speed
        self.image = self.anim[self.current_sprite]

        #Sprite Variables---------------------------------------------------------------
        self.rect = self.image.get_rect(center = (1200,random.choice([110,220,335,450,560])))
        self.hitbox = pygame.Rect(self.rect.x+10, self.rect.y+60,40,40)
        self.speed = 1
        self.health = health
        self.eating = False
        self.type = zombie_type
        self.died = False
        self.start_ticks = None
        self.seconds = None
        self.reset_anim = True
        self.exploded = False
        #Timings
        self.chomp_speed = 1000
        self.next_chomp = pygame.time.get_ticks() + self.chomp_speed
        self.next_groan = pygame.time.get_ticks() + random.choice([50000,25000,30000])

        if Card.level == 9:
            self.speed = 3
            self.frame_speed = 70

        elif Card.level == 8 or Card.level == 7:
            self.frame_speed = 70
            self.speed = 1

        elif Card.level == 6 or Card.level == 5:           
            self.speed = 1
            self.frame_speed = 80
        else:
            self.frame_speed = 90
            self.speed = 1

        self.next_move = pygame.time.get_ticks() + self.frame_speed


    def die_animation(self):
        if self.exploded:
            self.anim = zombie_boom_anim
        else:
            self.anim = zombie_anim_death

        if self.reset_anim == True:
            pygame.mixer.Sound("sfx/limbs_pop.wav").play()
            Zombie.killed += 1
            self.animation_speed = 0.19
            self.rect.x -= 70
            self.rect.y -= 30
            self.current_sprite = 0
            self.start_ticks = pygame.time.get_ticks()



        self.died = True

        self.reset_anim = False



    def update(self):
        if pygame.time.get_ticks() >= self.next_groan:
            pygame.mixer.Sound(random.choice(["sfx/groan.wav","sfx/groan2.wav","sfx/groan3.wav","sfx/groan4.wav","sfx/groan5.wav","sfx/groan6.wav"])).play()
            self.next_groan = pygame.time.get_ticks() + random.choice([50000,25000,30000])

        if self.health <= 0: 
            self.died = True
            self.die_animation()

            
        if self.died == True:
            
            self.seconds = (pygame.time.get_ticks()-self.start_ticks)/1000
            if self.seconds > 2.4 and self.seconds < 2.414 and self.exploded == False:
                pygame.mixer.Sound(random.choice(["sfx/zombie_falling_1.wav","sfx/zombie_falling_2.wav"])).play()

            if self.exploded:
                if self.seconds > 1.44:
                    self.kill()
            else:
                if self.seconds > 3:
                    self.kill()
                
        if Card.level != 9:
            self.hitbox = pygame.Rect(self.rect.x+10, self.rect.y+30,10,30)
        else:
            self.hitbox = pygame.Rect(self.rect.x+10, self.rect.y+30,40,65)


        if pygame.time.get_ticks() >= self.next_move and self.died == False:
            self.next_move = pygame.time.get_ticks() + self.frame_speed
            self.rect.x -= self.speed

        

        if self.current_sprite >= len(self.anim)-1:
            self.current_sprite = 0

        if self.rect.x <= 180 and Zombie.over == False:
            pygame.mixer.Sound("sfx/gameover.wav").play()
            pygame.mixer.music.stop()
            Zombie.over = True

        if self.eating == True and self.health > 0 and self.died == False:
            if pygame.time.get_ticks() >= self.next_chomp:
                pygame.mixer.Sound("sfx/chomp.wav").play()
                self.next_chomp = pygame.time.get_ticks() + self.chomp_speed

            if self.type == "normal":
                self.anim = zombie_anim_attack

            elif self.type == "conehead":
                self.anim = cone_zombie_anim_attack

            elif self.type == "buckethead":
                self.anim = bucket_zombie_anim_attack
                
            if self.current_sprite >= len(self.anim)-1:
                self.current_sprite = 0


            self.image = self.anim[int(self.current_sprite)]
        

        if self.died:
            self.image = self.anim[int(self.current_sprite)]

        
        if self.eating == False and self.health > 0 and self.died == False:
            if self.type == "normal":
                self.anim = zombie_anim_0
            elif self.type == "conehead":
                self.anim = cone_zombie_anim_0
            elif self.type == "buckethead":
                self.anim = bucket_zombie_anim_0

            if self.current_sprite >= len(self.anim)-1:
                self.current_sprite = 0
                
            self.image = self.anim[int(self.current_sprite)]

        for z in zombie_group:
            if z.died == False:
                zomb_hit_normal = pygame.sprite.spritecollideany(z,bullet_normal_group)
                zomb_hit_ice = pygame.sprite.spritecollideany(z,bullet_ice_group)

                if zomb_hit_normal is not None:
                    pygame.mixer.Sound(random.choice(["sfx/splat.wav","sfx/splat2.wav","sfx/splat3.wav"])).play()
                    bullet_normal_group.remove(zomb_hit_normal)
                    self.health -= 1

             


                if zomb_hit_ice is not None:
                    pygame.mixer.Sound(random.choice(["sfx/splat.wav","sfx/splat2.wav","sfx/splat3.wav"])).play()
                    bullet_ice_group.remove(zomb_hit_ice)
                    self.health -= 1
                    self.frame_speed = 260
                    self.anim_speed = 0.09


                

        for dead_boi in dead_zombie_group:
            zombie_group.remove(dead_boi)


   

        dead_zombie_group.empty() 



        
        self.current_sprite += self.animation_speed







        self.eating = False

    

class Wave(pygame.sprite.Sprite):
    normal_wave_counter = 0
    harder_wave_counter = 0
    boss_wave_counter = 0
    total_counter = 0
    victory = False
    game_victory = False
    stop_spawning = False

    i = 0
    def __init__(self):
        super().__init__()
        self.stop_spawning = False
        self.flagmeter_anim = []
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter1.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter1.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter2.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter2.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter3.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter3.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter4.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter4.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter5.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter5.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter6.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter6.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter7.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter7.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter8.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter8.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter9.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter9.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter10.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter10.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter11.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter11.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter12.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter12.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))
        self.flagmeter_anim.append(pygame.image.load("Screen/flagmeter13.png"))

        #Rate of zombies to spawn
        if Card.level != 9 and Card.level != 1 and Card.level != 2:
            self.boss_wave = [600,1000,2000,800]
            self.harder_wave = [6000,2000,3000,2000]
            self.normal_wave = [14000,10000,10000,9000,18000]
            self.current_spawn_rate = self.normal_wave[0]

            #Timings of waves
            self.zombiespawntime = pygame.time.get_ticks() + 18001 # Intro
            self.harderspawntime = pygame.time.get_ticks() + 6001 # Mid game
            self.bossspawntime = pygame.time.get_ticks() + 2001 # Boss wave

        elif Card.level == 9:
            self.total_counter = 0
            self.boss_wave = [900,700]
            self.harder_wave = [2000,1000]
            self.normal_wave = [6000,3000,2400]
            self.current_spawn_rate = self.normal_wave[0]

            #Timings of waves
            self.zombiespawntime = pygame.time.get_ticks() + 7000 # Intro
            self.harderspawntime = pygame.time.get_ticks() + 4000 # Mid game
            self.bossspawntime = pygame.time.get_ticks() + 4000 # Boss wave

        elif Card.level == 1 or Card.level == 2:
            self.boss_wave = [2000]
            self.harder_wave = [6000,9000,3000,6000]
            self.normal_wave = [14000,10000,10000,9000,18000]
            self.current_spawn_rate = self.normal_wave[0]

            #Timings of waves
            self.zombiespawntime = pygame.time.get_ticks() + 18001 # Intro
            self.harderspawntime = pygame.time.get_ticks() + 9001 # Mid game
            self.bossspawntime = pygame.time.get_ticks() + 2001 # Boss wave

        

    def update(self):
        menu.screen.blit(self.flagmeter_anim[self.total_counter], (870,600))

        if self.total_counter >= 24 and Card.level == 9:
            Wave.stop_spawning = True
          

        if self.boss_wave_counter >= 4: 
            Wave.stop_spawning = True

        if Wave.stop_spawning == False:
            if self.normal_wave_counter <= 8: # Begining waves
                if pygame.time.get_ticks() >= self.zombiespawntime:
    
                    self.current_spawn_rate = random.choice(self.normal_wave)
                    self.normal_wave_counter += 1
                    if self.normal_wave_counter == 1:
                        pygame.mixer.Sound("sfx/zombiesarecoming.wav").play()

                    if Card.level != 9:
                        self.total_counter += 1
                    else:
                        self.total_counter += 2
                    self.zombiespawntime = pygame.time.get_ticks() + 18001

                    SPAWNZOMBIES = pygame.USEREVENT + 1
                    pygame.time.set_timer(SPAWNZOMBIES,self.current_spawn_rate)

            if self.harder_wave_counter <= 12 and self.normal_wave_counter >= 8: # Mid game
                if pygame.time.get_ticks() >= self.harderspawntime:
                
                    self.current_spawn_rate = random.choice(self.harder_wave)
                    self.harder_wave_counter += 1

                    if Card.level != 9:
                        self.total_counter += 1
                    else:
                        self.total_counter +=2

                    self.harderspawntime = pygame.time.get_ticks() + 9001

                    SPAWNZOMBIES = pygame.USEREVENT + 1
                    pygame.time.set_timer(SPAWNZOMBIES,self.current_spawn_rate)                

            if self.boss_wave_counter <= 4 and self.harder_wave_counter >= 12:
                if pygame.time.get_ticks() >= self.bossspawntime:
                   
                    self.current_spawn_rate = random.choice(self.boss_wave)
                    self.boss_wave_counter += 1

                    if Card.level != 9:
                        self.total_counter += 1
                    else:
                        self.total_counter +=2

                    self.bossspawntime = pygame.time.get_ticks() + 2001 

                    SPAWNZOMBIES = pygame.USEREVENT + 1
                    pygame.time.set_timer(SPAWNZOMBIES,self.current_spawn_rate)

        elif Wave.stop_spawning == True and len(zombie_group) == 0:

            if Card.level == 8 or Card.level == 9:
                Wave.game_victory = True
                return
            Wave.victory = True

       










#----------------------------------
class Plant(pygame.sprite.Sprite):
    drag = False
    win = False
    def __init__(self,anim,health,x,y,plant_type,anim_speed):
        super().__init__()
        #Sprite Variables--------------------------------------------------------------------------------------------------------------------
        self.x = x
        self.y = y
        self.placed = False
        self.type = plant_type
        self.health = health
        self.grown = False
        self.exploded = False
        self.cherry_exploded = 0
        self.eating = False
        self.digest = False
        self.roll = None
        self.pos = None
        self.bowl_collided = False
        self.direction_list = None
        self.direction = None
        self.deflect_wall = False
        #Sprite Animations--------------------------------------------------------------------------------------------------------------------

        self.anim = anim
        self.current_sprite = 0
        self.animation_speed = anim_speed
        self.image = self.anim[self.current_sprite]
        self.rect = self.image.get_rect(center = (self.x,self.y))
        self.angle = 0
        if self.type == "cherrybomb": 
            self.hitbox = pygame.Rect(self.rect.x + 30, self.rect.y-130,20,190)


            
        #Sprite Timings--------------------------------------------------------------------------------------------------------------------
        self.next_shot = pygame.time.get_ticks() + 2500
        self.next_sun_created = pygame.time.get_ticks() + 4500
        self.grow_potato = pygame.time.get_ticks() + 17000
        self.zombie_digested = pygame.time.get_ticks() + 10000
        self.repeater_pea_next_shot = pygame.time.get_ticks() + 1250
        self.next_bowl = pygame.time.get_ticks() + 1250
        self.next_shot_sound = pygame.time.get_ticks() + 500


        self.start_ticks = None
        self.seconds = None
    
    def create_sun(self):
        sun = Sun(sun_anim,self.rect.x+10,self.rect.y+10,0)
        sun_group.add(sun)

    def shoot(self):
        if len(zombie_group) != 0 or Zombie.over == True:
            if pygame.time.get_ticks() >= self.next_shot_sound:
                pygame.mixer.Sound(random.choice(["sfx/peafire.wav","sfx/peafire.wav","sfx/peafire2.wav"])).play()
                self.next_shot_sound = pygame.time.get_ticks() + 500

            if self.type == "peashooter" or self.type == "repeaterpea":
                bullet = Bullet("Bullets/PeaNormal/PeaNormal_0.png",5,self.rect.x+50,self.rect.y+10,"normal")
                bullet_normal_group.add(bullet)


            if self.type == "icepeashooter" and self.placed == True:
                bullet = Bullet("Bullets/PeaIce/PeaIce_0.png",5,self.rect.x+50,self.rect.y+10,"ice")
                bullet_ice_group.add(bullet)



    def grow(self):
        plant.image = pygame.image.load("plants/PotatoMine/PotatoMine/PotatoMine_0.png")
        plant.rect = plant.image.get_rect(center=(self.rect.x+30,self.rect.y+50))
        plant.grown = True
        plant.anim = potatomine_anim_1

    def explode(self):
        pygame.mixer.Sound("sfx/cherrybomb.wav").play()
        p.current_sprite = 0
        self.anim = potatomine_anim_2

        if p.type == "potatomine":
            p.rect = plant.image.get_rect(center=(self.rect.x,self.rect.y))

        self.exploded = True
        self.start_ticks = pygame.time.get_ticks()


    def update(self):
            
        if self.health <= 0:
            self.kill()


        if pygame.time.get_ticks() >= self.next_shot:
            if self.placed == True and self.type == "peashooter" or self.type == "icepeashooter":
                self.shoot()
                self.next_shot = pygame.time.get_ticks() + random.choice([2500,2300])

        if pygame.time.get_ticks() >= self.repeater_pea_next_shot:
            if self.placed == True and self.type == "repeaterpea":
                self.shoot()
                self.repeater_pea_next_shot = pygame.time.get_ticks() + random.choice([1250,1300])

        if pygame.time.get_ticks() >= self.next_sun_created:
            if self.placed == True and self.type == "sunflower":
                self.create_sun()
                self.next_sun_created = pygame.time.get_ticks() + random.choice([15000,16000,15500])

        if self.digest == True and self.type == "chomper":
            if pygame.time.get_ticks() >= self.zombie_digested:
                if self.placed == True:
                    self.digest = False
                    self.eating = False
                    self.anim = chomper_anim_0
                    self.animation_speed = 0.2

        if self.health <= 900 and self.type == "walnut":
            self.anim = wallnut_anim_1
        if self.health <= 300 and self.type == "walnut":
            self.anim = wallnut_anim_2


            


        if self.placed != False:
            self.current_sprite += self.animation_speed

            self.image = self.anim[int(self.current_sprite)]

            if self.type == "cherrybomb" and self.cherry_exploded == 0:
                if self.current_sprite >= len(self.anim)-1:
                    self.explode()
                    self.cherry_exploded = 1
        
            if self.type == "chomper" and self.eating == True:
                self.anim = chomper_anim_1
                if self.current_sprite >= len(self.anim)-1:
                    self.anim = chomper_anim_0
                    self.eating = False
                    self.digest = True
                    self.zombie_digested = pygame.time.get_ticks() + 9000


            if self.type == "chomper" and self.digest == True and self.eating == False:
                self.anim = chomper_anim_2
                self.animation_speed = 0.12
                    
            if self.current_sprite >= len(self.anim)-1:
                self.current_sprite = 0

        if self.type == "cherrybomb": 
            self.hitbox = pygame.Rect(self.rect.x-40, self.rect.y-130,200,250)

        

    def bowl(self):
        if self.placed == True:
            self.rect.x += 3

        if self.rect.x >= menu.screen_width:
            self.kill()

    def spin(self):
        if self.placed == True:
            self.rotated_image = pygame.transform.rotate(self.image, self.angle)
            menu.screen.blit(self.rotated_image,self.rect)



            self.angle -= 3 

    def alter_direction(self):
        self.direction_list = ["up","down"]

        if random.choice(self.direction_list) == "up":
            self.direction = "up"


        elif random.choice(self.direction_list) == "down":
            self.direction = "down"


    def deflect(self):

        if self.deflect_wall != True:
            if self.direction == "up":
                self.rect.y -= random.choice([3,2,3,4])
            else:
                self.rect.y += random.choice([3,2,3,4])

    def deflect_of_wall(self):
        self.deflect_wall = True

        if self.direction == "up":
            self.rect.y += random.choice([3,2,3,4])
        else:
            self.rect.y -= random.choice([3,2,3,4])
####################################

class Tiles(pygame.sprite.Sprite):
    def __init__(self,a,b,occupied):
        super().__init__()
        self.a = a
        self.b = b
        self.occupied = occupied
        self.rect = pygame.Rect(self.a,self.b,18,30)
        self.image = pygame.image.load("Bullets/PeaNormal/PeaNormal_0.png")


# Sprite Groups--------------------------------------------------------------------------------------------------------------------
sun_group = pygame.sprite.Group()

card_group = pygame.sprite.Group()

plant_group = pygame.sprite.Group()

bullet_normal_group = pygame.sprite.Group()

bullet_ice_group = pygame.sprite.Group()

zombie_group = pygame.sprite.Group()

dead_zombie_group = pygame.sprite.Group()

lawnmower_group = pygame.sprite.Group()

tile_group = pygame.sprite.Group()




  


# Pygame Events--------------------------------------------------------------------------------------------------------------------
SPAWNSUN = pygame.USEREVENT + 0
pygame.time.set_timer(SPAWNSUN,23000)

def bowling_game():
    global walnutcard, offset_x, offset_y, bombwalnutcard

    for c in card_group:
        c.kill()
        
    global screen, font, score, plant, p
    winsound.PlaySound(None, winsound.SND_ASYNC)
    pygame.mixer.music.load("sfx/Loonboon.wav")
    pygame.mixer.music.play(-1)
    Card.level = 9
    Wave.game_victory = False
    Wave.victory = False
    Wave.stop_spawning = False

    zombie_wave = Wave()

    SPAWNZOMBIES = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWNZOMBIES,zombie_wave.current_spawn_rate)

    SPAWNBOWLINGCARD = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWNBOWLINGCARD,2000)
    # Draw tiles for plants--------------------------------------------------------------------------------------------------------------------
    tiles_list = []
    a = 0
    b = 0

    for i in range(15):
        tile = Tiles(325+a,110+b,False)
        tiles_list.append(tile)
        tile_group.add(tile)
        a += 90
        if a >= 200:
            a = 0
            b += 110

    walnutcard = Card(pygame.image.load("cards/card_wallnut_move.png").convert_alpha(),1000,40,11000,"dark_cards/d_walnut.png")
    bombwalnutcard = Card(pygame.image.load("cards/card_wallnut_move.png").convert_alpha(),1000,40,11000,"dark_cards/d_walnut.png")

    menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")
    card_group.add(menubutton)


    background = pygame.image.load("Background/Background_4.jpg").convert_alpha()

    #Timings
    restart_game = 0
    victory_timer = 0
    while True:
        key = pygame.key.get_pressed()

        # Check for in-game events--------------------------------------------------------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if Card.level == 9:

                if Wave.stop_spawning == False:

                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                 
                if Wave.game_victory == False:
                    if event.type == SPAWNBOWLINGCARD:
                        if random.choice(["1","1","1","1","0"]) == "1":   
                            walnutcard = Card(pygame.image.load("cards/card_wallnut_move.png").convert_alpha(),490,40,11000,"dark_cards/d_walnut.png")
                            card_group.add(walnutcard)
                        else:
                            bombwalnutcard = Card(pygame.image.load("cards/card_redwallnut_move.png").convert_alpha(),490,40,50,"dark_cards/d_walnut.png")
                            card_group.add(bombwalnutcard)

                        Card.wallnutcreated += 1
           
            if Wave.game_victory == False:

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for card in card_group:
                        if card.recharge == 11000:
                            x, y = event.pos

                          
                                    
                            if Card.level == 9:
                                if card.rect.collidepoint(x,y):
                                    plant = Plant(wallnut_anim_0,1000,x,y,"walnut",0.2)
                                    Plant.drag = True
                                    offset_x = plant.rect.x - x
                                    offset_y = plant.rect.y - y
                                    card.kill()
                                    plant_group.add(plant)

                                    pygame.mixer.Sound("sfx/seedlift.wav").play()

                        if card.recharge == 50:
                            x, y = event.pos

                            if Card.level == 9:
                                if card.rect.collidepoint(x,y):
                                    plant = Plant(bomb_wallnut_anim,1000,x,y,"bombwalnut",0.2)
                                    Plant.drag = True
                                    offset_x = plant.rect.x - x
                                    offset_y = plant.rect.y - y
                                    card.kill()
                                    plant_group.add(plant)

                                    pygame.mixer.Sound("sfx/seedlift.wav").play()

                        if card == menubutton:
                            x, y = event.pos
                            if menubutton.rect.collidepoint(x,y):
                                pygame.mixer.Sound("sfx/buttonclick.wav").play()
                                menu.paused = True
                            

                elif event.type == pygame.MOUSEBUTTONUP:

                    if Plant.drag == True:
                        Plant.drag = False


                        for tile in tiles_list:
                            if tile.rect.colliderect(plant.rect):
                                if tile.occupied == True:
                                    plant.kill()

                                plant.placed = True
                                pygame.mixer.Sound("sfx/plant.wav").play()
                                plant.rect.center = tile.rect.center




                        if plant.placed == False:
                            plant.kill()

                elif event.type == pygame.MOUSEMOTION:

                    if Plant.drag:
                        x, y = event.pos
                        plant.rect.x = x + offset_x
                        plant.rect.y = y + offset_y


        menu.screen.blit(background,(0,0))
        menu.screen.blit(pygame.image.load("Screen/MoveBackground.png").convert_alpha(),(0,0))
        card_group.draw(menu.screen)


        for p in plant_group:
            if p.placed == False:
                menu.screen.blit(p.image,p.rect)
                
       
        zombie_group.draw(menu.screen)

        if menu.paused == False:
            plant_group.update()
            zombie_group.update()
            card_group.update()
        zombie_wave.update()
            
        for c in card_group:
            if c != menubutton:
                c.bowling_move()

            if c.rect.x <= -c.rect.width:
                c.kill()
                




         
            
            
        for p in plant_group:
            p.bowl()
            p.spin()

        for p in plant_group:
            for z in zombie_group:
                if p.placed and p.type == "walnut" and z.died == False:
                    if p.rect.y - p.rect.width//2 < z.hitbox[1] + z.hitbox[3] and p.rect.y + p.rect.width//2 > z.hitbox[1]:
                        if  p.rect.x + p.rect.width > z.hitbox[0] and p.rect.x - p.rect.width//2 < z.hitbox[0] + z.hitbox[2]:
                            z.health -= 1

                            if pygame.time.get_ticks() >= p.next_bowl:
                                pygame.mixer.Sound("sfx/bowlingimpact.wav").play()
                                p.next_bowl = pygame.time.get_ticks() + 800

                            p.bowl_collided = True
                            p.alter_direction()

                elif p.placed and p.type == "bombwalnut" and z.died == False:
                    if p.rect.y - p.rect.width//2 < z.hitbox[1] + z.hitbox[3] and p.rect.y + p.rect.width//2 > z.hitbox[1]:
                        if  p.rect.x + p.rect.width > z.hitbox[0] and p.rect.x - p.rect.width//2 < z.hitbox[0] + z.hitbox[2]:
                            z.health = -1
                            z.exploded = True
                            if pygame.time.get_ticks() >= p.next_bowl:
                                pygame.mixer.Sound("sfx/bowlingimpact2.wav").play()
                                p.next_bowl = pygame.time.get_ticks() + 800
                                
                            p.kill()

        for p in plant_group:
            if p.bowl_collided:
                p.deflect()
            if p.placed:
                if p.rect.y >= menu.screen_height-30 or p.rect.y <= 10:
                    p.deflect_wall = True

            if p.deflect_wall:
                p.deflect_of_wall()

        if Zombie.over == True:
            restart_game += 1
            gameover = pygame.image.load("gameover1.png").convert_alpha()
            menu.screen.blit(gameover,(menu.screen_width//2-300,menu.screen_height//2-300))

            for z in zombie_group:
                z.speed = 0



            if restart_game > 200:
                for p in plant_group:
                    p.kill()
                for z in zombie_group:
                    z.kill()
                for s in sun_group:
                    s.kill()
                for c in card_group:
                     c.kill()

                Card.level = 1
                Zombie.over = False
                Zombie.killed = 0
                restart_game = 0
                p = Window()
                p.run_menu()
                
        if Wave.game_victory == True:
            for p in plant_group:
                p.kill()                    
            victory_timer += 1
            if victory_timer > 400:
                for p in plant_group:
                    p.kill()
                for z in zombie_group:
                    z.kill()
                for s in sun_group:
                    s.kill()
                for c in card_group:
                    c.kill()


                Card.level = 1
                Zombie.over = False
                Zombie.killed = 0
                restart_game = 0
                p = Window()
                p.run_menu()

        menu.update()
        pygame.display.flip()
        menu.clock.tick(65)
        pygame.display.set_caption(str(int(menu.clock.get_fps())))



def spawn_zombie():
    if Card.level == 1 or Card.level == 2:
        zombie_types = ["normal"]
    elif Card.level == 3:
        zombie_types = ["normal","normal","normal","conehead"]
    elif Card.level == 4:
        zombie_types = ["normal","normal","conehead"]
    elif Card.level == 5:
        zombie_types = ["normal","normal","normal","conehead","buckethead"]
    elif Card.level == 6 or Card.level == 7:
        zombie_types = ["normal","normal","buckethead","normal","normal","conehead","conehead"]
    elif Card.level == 8:
        zombie_types = ["normal","normal","conehead","normal", "conehead", "conehead", "buckethead"]
    elif Card.level == 9:
        zombie_types = ["normal","normal","normal", "conehead", "buckethead"]
    zombie_chosen = random.choice(zombie_types)
    if Card.level != 9:
        if zombie_chosen == "normal":
            zombie = Zombie(zombie_anim_0,0.19,"normal",12)
            zombie_group.add(zombie)
            
        elif zombie_chosen == "conehead":
            cone_zombie = Zombie(cone_zombie_anim_0,0.19,"conehead",15)
            zombie_group.add(cone_zombie)

        elif zombie_chosen == "buckethead":
            bucket_zombie = Zombie(bucket_zombie_anim_0,0.17,"buckethead",19)
            zombie_group.add(bucket_zombie)
    else:
        if zombie_chosen == "normal":
            zombie = Zombie(zombie_anim_0,0.19,"normal",12)
            zombie_group.add(zombie)
            
        elif zombie_chosen == "conehead":
            cone_zombie = Zombie(cone_zombie_anim_0,0.19,"conehead",100)
            zombie_group.add(cone_zombie)

        elif zombie_chosen == "buckethead":
            bucket_zombie = Zombie(bucket_zombie_anim_0,0.17,"buckethead",150)
            zombie_group.add(bucket_zombie)        

def game():
    global screen, font, score, plant, p, offset_x, offset_y, walnutcard
    w = Window()
    #Load music--------------------------------------------------------------------------------------------------------------------
    winsound.PlaySound(None, winsound.SND_ASYNC)
    pygame.mixer.music.load("sfx/song.wav")
    pygame.mixer.music.play(-1)
    Wave.game_victory = False
    Wave.victory = False
    Wave.stop_spawning = False

    zombie_wave = Wave()

    SPAWNZOMBIES = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWNZOMBIES,zombie_wave.current_spawn_rate)
    
    # Load cards--------------------------------------------------------------------------------------------------------------------
    if Card.level == 1:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")
    
        card_group.add(peacard,shovel,menubutton)

    elif Card.level == 2:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")
        card_group.add(peacard,suncard,shovel,menubutton)

    elif Card.level  == 3:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),270,54,35000,"dark_cards/d_cherrybomb.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")
        card_group.add(peacard,suncard,cherrybombcard,shovel,menubutton)  

    elif Card.level == 4:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),270,54,35000,"dark_cards/d_cherrybomb.png")
        potatominecard = Card(pygame.image.load("cards/card_potatomine.png").convert_alpha(),340,54,35000,"dark_cards/d_potatomine.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")
        card_group.add(peacard,suncard,cherrybombcard,potatominecard,shovel,menubutton)

    elif Card.level == 5:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),270,54,35000,"dark_cards/d_cherrybomb.png")
        potatominecard = Card(pygame.image.load("cards/card_potatomine.png").convert_alpha(),340,54,35000,"dark_cards/d_potatomine.png")
        walnutcard = Card(pygame.image.load("cards/card_wallnut.png").convert_alpha(),410,54,11000,"dark_cards/d_walnut.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")

        card_group.add(peacard,suncard,cherrybombcard,walnutcard,potatominecard,shovel,menubutton)

    elif Card.level == 6:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),270,54,35000,"dark_cards/d_cherrybomb.png")
        potatominecard = Card(pygame.image.load("cards/card_potatomine.png").convert_alpha(),340,54,35000,"dark_cards/d_potatomine.png")
        walnutcard = Card(pygame.image.load("cards/card_wallnut.png").convert_alpha(),410,54,11000,"dark_cards/d_walnut.png")
        icepeashootercard = Card(pygame.image.load("cards/card_snowpea.png").convert_alpha(),480,54,7000,"dark_cards/d_snowpea.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")

        card_group.add(peacard,suncard,cherrybombcard,walnutcard,potatominecard,icepeashootercard,shovel,menubutton)

    elif Card.level == 7:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),270,54,35000,"dark_cards/d_cherrybomb.png")
        potatominecard = Card(pygame.image.load("cards/card_potatomine.png").convert_alpha(),340,54,35000,"dark_cards/d_potatomine.png")
        walnutcard = Card(pygame.image.load("cards/card_wallnut.png").convert_alpha(),410,54,11000,"dark_cards/d_walnut.png")
        icepeashootercard = Card(pygame.image.load("cards/card_snowpea.png").convert_alpha(),480,54,7000,"dark_cards/d_snowpea.png")
        chompercard = Card(pygame.image.load("cards/card_chomper.png").convert_alpha(),550,54,6000,"dark_cards/d_chomper.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")

        card_group.add(peacard,suncard,cherrybombcard,walnutcard,potatominecard,icepeashootercard,chompercard,shovel,menubutton)

    elif Card.level == 8:
        peacard = Card(pygame.image.load("cards/card_peashooter.png").convert_alpha(),130,54,6000,"dark_cards/d_peashooter.png")
        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),200,54,5000,"dark_cards/d_sunflower.png")
        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),270,54,35000,"dark_cards/d_cherrybomb.png")
        potatominecard = Card(pygame.image.load("cards/card_potatomine.png").convert_alpha(),340,54,35000,"dark_cards/d_potatomine.png")
        walnutcard = Card(pygame.image.load("cards/card_wallnut.png").convert_alpha(),410,54,11000,"dark_cards/d_walnut.png")
        icepeashootercard = Card(pygame.image.load("cards/card_snowpea.png").convert_alpha(),480,54,7000,"dark_cards/d_snowpea.png")
        chompercard = Card(pygame.image.load("cards/card_chomper.png").convert_alpha(),550,54,6000,"dark_cards/d_chomper.png")
        repeaterpeacard = Card(pygame.image.load("cards/card_repeaterpea.png").convert_alpha(),620,54,7000,"dark_cards/d_repeaterpea.png")
        shovel = Card(pygame.image.load("Screen/Shovel.jpg").convert_alpha(),720,54,6000,"dark_cards/d_peashooter.png")
        menubutton = Card(pygame.image.load("Screen/menu.png").convert_alpha(),1070,15,6000,"dark_cards/d_peashooter.png")

        card_group.add(peacard,suncard,cherrybombcard,walnutcard,potatominecard,icepeashootercard,chompercard,repeaterpeacard,shovel,menubutton)

   

    # Draw tiles for plants--------------------------------------------------------------------------------------------------------------------
    tiles_list = []
    a = 0
    b = 0

    for i in range(45):
        tile = Tiles(325+a,110+b,False)
        tiles_list.append(tile)
        tile_group.add(tile)
        a += 90
        if a >= 800:
            a = 0
            lawnmower = Lawnmower("lawnmower.png",3,250,150+b)
            lawnmower_group.add(lawnmower)
            b += 110




    #Timings
    restart_game = 0
    victory_timer = 0

    def check_recharge():
        if menu.paused == False:
        
            if peacard.recharged == False:
                peacard.start_recharge()

            if Card.level > 1:
                if suncard.recharged == False:
                    suncard.start_recharge()

            if Card.level > 2:
                if cherrybombcard.recharged == False:
                    cherrybombcard.start_recharge()

            if Card.level > 3:
                if potatominecard.recharged == False:
                    potatominecard.start_recharge()

            if Card.level > 4:
                if walnutcard.recharged == False:
                    walnutcard.start_recharge()

            if Card.level > 5:
                if icepeashootercard.recharged == False:
                    icepeashootercard.start_recharge()

            if Card.level > 6:
                if chompercard.recharged == False:
                    chompercard.start_recharge()

            if Card.level > 7:
                if repeaterpeacard.recharged == False:
                    repeaterpeacard.start_recharge()
                    
    #Reset num of zombies killed / zombie spawned
    if Card.level == 1:
        Sun.score = 1000
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 2:
        Sun.score = 100
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 3:
        Sun.score = 100
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 4:
        Sun.score = 100
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 5:
        Sun.score = 100
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 6:
        Sun.score = 100
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 7:
        Sun.score = 100
        Zombie.killed = 0
        Zombie.spawned = 0
        
    elif Card.level == 8:
        Sun.score = 1000
        Zombie.killed = 0
        Zombie.spawned = 0

    elif Card.level == 9:
        Sun.score = 100 
        Zombie.killed = 0
        Zombie.spawned = 0

    if Card.level <= 8:
        background = pygame.image.load("Background/Background_0.jpg")


    
    while True and menu.paused == False:
        key = pygame.key.get_pressed()

        # Check for in-game events--------------------------------------------------------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SPAWNSUN:
                sun = Sun(sun_anim,random.randint(750,1100),random.randint(-300,-200),1)
                sun_group.add(sun)



            # Amount of zombies in each level----------------------------------------------------------------------------------------------------------
            if Card.level == 1:
                
                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        suncard = Card(pygame.image.load("cards/card_sunflower.png").convert_alpha(),1000,menu.screen_height//2,3000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(suncard)

            elif Card.level == 2:

                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned+= 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        cherrybombcard = Card(pygame.image.load("cards/card_cherrybomb.png").convert_alpha(),1000,menu.screen_height//2,7000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(cherrybombcard)

            elif Card.level == 3:
                
                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        potatominecard = Card(pygame.image.load("cards/card_potatomine.png").convert_alpha(),1000,menu.screen_height//2,7000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(potatominecard)

            elif Card.level == 4:

                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        walnutcard = Card(pygame.image.load("cards/card_wallnut.png").convert_alpha(),1000,menu.screen_height//2,5000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(walnutcard)

            elif Card.level == 5:
                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        icepeashootercard = Card(pygame.image.load("cards/card_snowpea.png").convert_alpha(),1000,menu.screen_height//2,5000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(icepeashootercard)

            elif Card.level == 6:
                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        chompercard = Card(pygame.image.load("cards/card_chomper.png").convert_alpha(),1000,menu.screen_height//2,5000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(chompercard)

            elif Card.level == 7:
                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()

                else:
                    if len(zombie_group) == 0 and Card.created != True:
                        repeaterpeacard = Card(pygame.image.load("cards/card_repeaterpea.png").convert_alpha(),1000,menu.screen_height//2,5000,"dark_cards/d_sunflower.png")
                        Card.created = True
                        card_group.add(repeaterpeacard)

            elif Card.level == 8:
                if Wave.stop_spawning == False:
                    if event.type == SPAWNZOMBIES:
                        Zombie.spawned += 1
                        spawn_zombie()


        
            
    




            # Check what plant card is selected--------------------------------------------------------------------------------------------------------------------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for sun in sun_group:
                    x, y = event.pos
                    if sun.rect.collidepoint(x,y):
                        pygame.mixer.Sound("sfx/suncollect.wav").play()
                        sun.kill()
                        Sun.score += 25



            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for card in card_group:
                    if card.recharged == True:
                        x, y = event.pos
                        if card == menubutton:

                            if menubutton.rect.collidepoint(x,y):
                                pygame.mixer.Sound("sfx/buttonclick.wav").play()
                                menu.paused = True
                                
                        if Card.level >= 1:
                            if card == peacard:
                                if peacard.rect.collidepoint(x,y):
                                    if Sun.score >= 100:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(peashooter_anim,190,x,y,"peashooter",0.2)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == suncard:
                                    if suncard.rect.collidepoint(x,y):
                                        if Card.level == 1:
                                            pygame.mixer.music.stop()
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)
                                            Card.obtain = True



                        if Card.level >= 2:
                            if card == suncard:
                                if suncard.rect.collidepoint(x,y):
                                    if Sun.score >= 50:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(sunflower_anim,150,x,y,"sunflower",0.2)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == cherrybombcard:
                                    if cherrybombcard.rect.collidepoint(x,y):
                                        if Card.level == 2:
                                            pygame.mixer.music.stop()
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)
                                            Card.obtain = True

                        if Card.level >= 3:
                            if card == cherrybombcard:
                                if cherrybombcard.rect.collidepoint(x,y):
                                    if Sun.score >= 150:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(cherrybomb_anim_1,150,x,y,"cherrybomb",0.13)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == potatominecard:
                                    if potatominecard.rect.collidepoint(x,y):
                                        if Card.level == 3:
                                            pygame.mixer.music.stop() 
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)
                                            Card.obtain = True



                        if Card.level >= 4:
                            if card == potatominecard:
                                if potatominecard.rect.collidepoint(x,y):
                                    if Sun.score >= 25:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(potatomine_anim_0,50,x,y,"potatomine",0.09)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == walnutcard:
                                    if walnutcard.rect.collidepoint(x,y):
                                        if Card.level == 4:
                                            pygame.mixer.music.stop()
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)

                                            Card.obtain = True

                        if Card.level >= 5:
                            if card == walnutcard:
                                if walnutcard.rect.collidepoint(x,y):
                                    if Sun.score >= 50:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(wallnut_anim_0,1400,x,y,"walnut",0.2)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == icepeashootercard:
                                    if icepeashootercard.rect.collidepoint(x,y):
                                        if Card.level == 5:
                                            pygame.mixer.music.stop()
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)

                                            Card.obtain = True

                        if Card.level >= 6:
                            if card == icepeashootercard:
                                if icepeashootercard.rect.collidepoint(x,y):
                                    if Sun.score >= 175:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(snowpea_anim,190,x,y,"icepeashooter",0.2)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == chompercard:
                                    if chompercard.rect.collidepoint(x,y):
                                        if Card.level == 6:
                                            pygame.mixer.music.stop()
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)

                                            Card.obtain = True


                        if Card.level >= 7:
                            if card == chompercard:
                                if chompercard.rect.collidepoint(x,y):
                                    if Sun.score >= 150:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(chomper_anim_0,190,x,y,"chomper",0.2)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                            if Zombie.killed > 0 and len(zombie_group) == 0 and Wave.victory == True:
                                if card == repeaterpeacard:
                                    if repeaterpeacard.rect.collidepoint(x,y):
                                        if Card.level == 7:
                                            pygame.mixer.music.stop()
                                            winsound.PlaySound("sfx/Plants Vs Zombies Victory Jingle.wav",winsound.SND_ASYNC)

                                            Card.obtain = True

                        if Card.level >= 8:
                            if card == repeaterpeacard:
                                if repeaterpeacard.rect.collidepoint(x,y):
                                    if Sun.score >= 200:
                                        pygame.mixer.Sound("sfx/seedlift.wav").play()
                                        plant = Plant(repeaterpea_anim,190,x,y,"repeaterpea",0.2)
                                        Plant.drag = True
                                        offset_x = plant.rect.x - x
                                        offset_y = plant.rect.y - y
                                        plant_group.add(plant)

                        if Card.level <= 8:
                            if card == shovel:
                                if shovel.rect.collidepoint(x,y):
                                    plant = Plant(shovel_anim,99999,x,y,"shovel",0.2)
                                    Plant.drag = True
                                    offset_x = plant.rect.x - x
                                    offset_y = plant.rect.y - y
                                    plant_group.add(plant)                            

                                    pygame.mouse.set_visible(False)


            # Check if plants collide with tile--------------------------------------------------------------------------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONUP:
                pygame.mouse.set_visible(True)
                for p in plant_group:
                    for s in plant_group:
                        if s.type == "shovel" and p.type != "shovel":
                            if p.rect.colliderect(s.rect):
                                p.health = 0
                    
                if Plant.drag == True:
                    Plant.drag = False

                    if plant.type != "shovel":
                        for tile in tiles_list:
                            if tile.rect.colliderect(plant.rect):
                                if tile.occupied == True:
                                    plant.kill()

                                plant.placed = True
                                plant.rect.center = tile.rect.center




                                # Take away sun cost from plants--------------------------------------------------------------------------------------------------------------------
                                if tile.occupied == False:
                                    if plant.type == "peashooter":
                                        Sun.score -= 100
                                        peacard.recharged = False
                                        peacard.image = peacard.darkened_image
                                        peacard.recharge_timer = pygame.time.get_ticks() + peacard.recharge

                                    if plant.type == "sunflower":
                                        Sun.score -= 50
                                        suncard.recharged = False
                                        suncard.image = suncard.darkened_image
                                        suncard.recharge_timer = pygame.time.get_ticks() + suncard.recharge

                                    if plant.type == "potatomine":
                                        Sun.score -= 25
                                        potatominecard.recharged = False
                                        potatominecard.image = potatominecard.darkened_image
                                        potatominecard.recharge_timer = pygame.time.get_ticks() + potatominecard.recharge

                                    if plant.type == "icepeashooter":
                                        Sun.score -= 175
                                        icepeashootercard.recharged = False
                                        icepeashootercard.image = icepeashootercard.darkened_image
                                        icepeashootercard.recharge_timer = pygame.time.get_ticks() + icepeashootercard.recharge

                                    if plant.type == "walnut":
                                        Sun.score -= 50
                                        walnutcard.recharged = False
                                        walnutcard.image = walnutcard.darkened_image
                                        walnutcard.recharge_timer = pygame.time.get_ticks() + walnutcard.recharge

                                    if plant.type == "cherrybomb":
                                        Sun.score -= 150
                                        cherrybombcard.recharged = False
                                        cherrybombcard.image = cherrybombcard.darkened_image
                                        cherrybombcard.recharge_timer = pygame.time.get_ticks() + cherrybombcard.recharge

                                    if plant.type == "chomper":
                                        Sun.score -= 150
                                        chompercard.recharged = False
                                        chompercard.image = chompercard.darkened_image
                                        chompercard.recharge_timer = pygame.time.get_ticks() + chompercard.recharge

                                    if plant.type == "repeaterpea":
                                        Sun.score -= 200
                                        repeaterpeacard.recharged = False
                                        repeaterpeacard.image = repeaterpeacard.darkened_image
                                        repeaterpeacard.recharge_timer = pygame.time.get_ticks() + repeaterpeacard.recharge

                                pygame.mixer.Sound("sfx/plant.wav").play()
                                
                                tile.occupied = True



                    if plant.placed == False:
                        plant.kill()






            elif event.type == pygame.MOUSEMOTION:
                if Plant.drag:
                    x, y = event.pos
                    plant.rect.x = x + offset_x
                    plant.rect.y = y + offset_y







        # Render score
        score = font.render(str(Sun.score),False,(0,0,0))






        # Check for collisions between bullets and zombies, courtesy of u/t_trimz--------------------------------------------------------------------------------------------------

        



        # Check for collisions between plants, lawnmowers and zombies, courtesy of Tech With Tim-------------------------------------------------------------------------------------------
        if menu.paused == False:
            for p in plant_group:
                for z in zombie_group:
                    if p.placed and p.type != "cherrybomb" and z.died == False and p.type != "shovel":
                        if p.rect.y - p.rect.width//2 < z.hitbox[1] + z.hitbox[3] and p.rect.y + p.rect.width//2 > z.hitbox[1]:
                            if  p.rect.x + p.rect.width > z.hitbox[0] and p.rect.x - p.rect.width//2 < z.hitbox[0] + z.hitbox[2]:
                                p.health -= 1
                                z.speed = 0
                                z.eating = True

                    if p.placed and p.type == "potatomine" and p.grown == True and p.exploded == False:
                        if p.rect.y - p.rect.width//2 < z.hitbox[1] + z.hitbox[3] and p.rect.y + p.rect.width//2 > z.hitbox[1]:
                            if  p.rect.x + p.rect.width > z.hitbox[0] and p.rect.x - p.rect.width//2 < z.hitbox[0] + z.hitbox[2]:
                                z.health = -1
                                z.exploded = True
                                Zombie.killed += 1
                                p.explode()

                    if p.placed and p.type == "cherrybomb" and p.exploded == True:
                        if z.rect.y - z.rect.width//2 < p.hitbox[1] + p.hitbox[3] and z.rect.y + z.rect.width//2 > p.hitbox[1]:
                            if  z.rect.x + z.rect.width > p.hitbox[0] and z.rect.x - z.rect.width//2 < p.hitbox[0] + p.hitbox[2]:
                                z.health = -1
                                z.exploded = True
                                Zombie.killed += 1

                    if p.placed and p.type == "chomper" and p.eating == False and p.digest == False:
                        if p.rect.y - p.rect.width//2 < z.hitbox[1] + z.hitbox[3] and p.rect.y + p.rect.width//2 > z.hitbox[1]:
                            if  p.rect.x + p.rect.width > z.hitbox[0] and p.rect.x - p.rect.width//2 < z.hitbox[0] + z.hitbox[2]:
                                z.kill()
                                p.eating = True
     
            for l in lawnmower_group:
                for z in zombie_group:
                    if l.rect.y - l.rect.width//2 < z.hitbox[1] + z.hitbox[3] and l.rect.y + l.rect.width//2 > z.hitbox[1]:
                        if  l.rect.x + l.rect.width > z.hitbox[0] and l.rect.x - l.rect.width//2 < z.hitbox[0] + z.hitbox[2]:
                            z.kill()
                            l.touched = True

            for plant in plant_group:
                if plant.placed == True:
                    if pygame.time.get_ticks() >= plant.grow_potato:
                        if plant.grown == False and plant.type == "potatomine" and plant.placed == True:
                            pygame.mixer.Sound("sfx/plantgrow.wav").play()
                            plant.grow()
                            plant.grow_potato = pygame.time.get_ticks() + 17000



            for p in plant_group:
                if p.exploded == True:
                    p.seconds = (pygame.time.get_ticks()-p.start_ticks)/1000
                    if p.seconds > 1:
                        p.health = 0

            for p in plant_group:
                for t in tiles_list:
                    if p.health <= 0:
                        if t.rect.colliderect(p.rect):
                            t.occupied = False

    
    
                






        # Blit sprites to screen--------------------------------------------------------------------------------------------------------------------
        menu.screen.blit(background,(0,0))
        menu.screen.blit(pygame.image.load("Screen/ChooserBackground.png").convert_alpha(),(0,0))
        menu.screen.blit(score,(22,84))
        card_group.draw(menu.screen)
        plant_group.draw(menu.screen)
        bullet_ice_group.draw(menu.screen)
        zombie_group.draw(menu.screen)
        bullet_normal_group.draw(menu.screen)
        lawnmower_group.draw(menu.screen)
        sun_group.draw(menu.screen)

        if Wave.game_victory == True:
            menu.screen.blit(pygame.image.load("Background/victory.png").convert_alpha(),((menu.screen_width//2)-120,(menu.screen_height//2)-120))


     


        # Update Groups--------------------------------------------------------------------------------------------------------------------
        if menu.paused == False:
            sun_group.update()
            plant_group.update()
            bullet_ice_group.update()
            bullet_normal_group.update()
            lawnmower_group.update()
            zombie_group.update()
            card_group.update()

        zombie_wave.update()

        

        # Check for card recharge
        check_recharge()

        if Zombie.over == True:
            restart_game += 1
            gameover = pygame.image.load("gameover1.png").convert_alpha()
            menu.screen.blit(gameover,(menu.screen_width//2-300,menu.screen_height//2-300))

            for z in zombie_group:
                z.speed = 0



            if restart_game > 200:
                for p in plant_group:
                    p.kill()
                for z in zombie_group:
                    z.kill()
                for s in sun_group:
                    s.kill()
                for c in card_group:
                    if c != peacard:
                        c.kill()

                Card.level = 1
                Zombie.over = False
                Zombie.killed = 0
                restart_game = 0
                p = Window()
                p.run_menu()

        if Wave.game_victory == True:
            victory_timer += 1
            if victory_timer > 400:
                for p in plant_group:
                    p.kill()
                for z in zombie_group:
                    z.kill()
                for s in sun_group:
                    s.kill()
                for c in card_group:
                    c.recharged = True
                    if c != peacard:
                        c.kill()

                Card.level = 1
                Zombie.over = False
                Zombie.killed = 0
                restart_game = 0
                p = Window()
                p.run_menu()
                

        if Card.obtain == True:
            if Card.level == 1:
                Card.enlarge(suncard.image,suncard.rect.x,suncard.rect.y)
                suncard.kill()
            elif Card.level == 2:
                Card.enlarge(cherrybombcard.image,cherrybombcard.rect.x,cherrybombcard.rect.y)
                cherrybombcard.kill()
            elif Card.level == 3:
                Card.enlarge(potatominecard.image,potatominecard.rect.x,potatominecard.rect.y)
                potatominecard.kill()
            elif Card.level == 4:
                Card.enlarge(walnutcard.image,walnutcard.rect.x,walnutcard.rect.y)
                walnutcard.kill()
            elif Card.level == 5:
                Card.enlarge(icepeashootercard.image,icepeashootercard.rect.x,icepeashootercard.rect.y)
                icepeashootercard.kill()
            elif Card.level == 6:
                Card.enlarge(chompercard.image,chompercard.rect.x,chompercard.rect.y)
                chompercard.kill()
            elif Card.level == 7:
                Card.enlarge(repeaterpeacard.image,repeaterpeacard.rect.x,repeaterpeacard.rect.y)
                repeaterpeacard.kill()















      

        # Update Game-------------------------------------------------------------------------------------------------------------------
        menu.update()
        pygame.display.flip()
        menu.clock.tick(65)
        pygame.display.set_caption(str(int(menu.clock.get_fps())))

class Window():
    bg1 = pygame.image.load("Background/mainmenu.png")
    bg2 = pygame.image.load("Background/Background_0.jpg")
    paused = False

    def __init__(self):
        self.click = False
        self.game = 0
        self.screen_width = 1129
        self.screen_height = 668
        self.background = self.bg1
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fontsmall = pygame.font.Font("SERIO___.TTF",18)
        self.clock = pygame.time.Clock()
        self.mx, self.my = pygame.mouse.get_pos()
        self.colors = {"red":(255,0,0),"white":(255,255,255),
                       "green":(0,255,0),"yellow":(255,255,0),"orange":(255,160,0)}

    def setup(self):
        self.screen_width = 1129
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.blit(self.background,(0,0))


    def text(self,message,font,color,x,y,length,width):
        text = font.render(message,False,(self.colors[color]))
        button_rect = pygame.Rect(x,y,length,width)


        if button_rect.collidepoint(self.mx,self.my):
            if self.click:
                if message == "play":
                    self.game = 1
                if message == "minigame":
                    self.game = 2
                if message == "cancel" or message == "continue":
                    self.game = 3
                if message == "newgame":
                    self.game = 4
                if message == "help":
                    self.game = 5
                if message == "ok":
                    self.game = 6
                if message == "quit":
                    self.game = 7

    def run_menu(self):
        winsound.PlaySound("sfx/menusong.wav", winsound.SND_ASYNC)
        pygame.mixer.music.stop()

        self.click = False
        self.setup()

        while True:
            self.mx, self.my = pygame.mouse.get_pos()
            self.text("play",self.fontsmall,"red",587,94,451,123)
            self.text("minigame",self.fontsmall,"red",587,225,451,105)
            self.text("help",self.fontsmall,"red",900,500,100,150)
            self.text("quit",self.fontsmall,"red",1000,500,100,150)

            self.click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
         
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                        


            if self.game == 1:
                pygame.mixer.Sound("sfx/buttonclick.wav").play()
                game()

            if self.game == 2:
                pygame.mixer.Sound("sfx/buttonclick.wav").play()
                bowling_game()

            if self.game == 5:
                self.text("ok",self.fontsmall,"red",420,370,300,45)
                self.screen.blit(pygame.image.load("Screen/help.png").convert_alpha(),((menu.screen_width//2)-200,(menu.screen_height//2)-200))
            if self.game == 7:
                pygame.quit()
                sys.exit()
            
            pygame.display.update()
            self.clock.tick(60)

    def run_pause(self):
        self.click = False

        while True and menu.paused == True:
            self.screen.blit(pygame.image.load("Screen/menuchoice.png").convert_alpha(),((menu.screen_width//2)-200,(menu.screen_height//2)-200))

            self.mx, self.my = pygame.mouse.get_pos()
            self.text("cancel",self.fontsmall,"red",420,410,380,30)
            self.text("continue",self.fontsmall,"red",400,360,200,35)
            self.text("newgame",self.fontsmall,"red",625,360,200,35)

            self.click = False

            for p in plant_group:
                p.next_shot = pygame.time.get_ticks() + 2500
                p.next_sun_created = pygame.time.get_ticks() + 4500
                p.grow_potato = pygame.time.get_ticks() + 17000
                p.zombie_digested = pygame.time.get_ticks() + 10000
                p.repeater_pea_next_shot = pygame.time.get_ticks() + 1250
                p.next_bowl = pygame.time.get_ticks() + 1250
                p.next_shot_sound = pygame.time.get_ticks() + 500

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
          
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True


            if self.game == 3:
                pygame.mixer.Sound("sfx/buttonclick.wav").play()
                menu.game = 0
                menu.paused = False

            elif self.game == 4:
                pygame.mixer.Sound("sfx/buttonclick.wav").play()

                for p in plant_group:
                    p.kill()
                for z in zombie_group:
                    z.kill()
                for s in sun_group:
                    s.kill()
                for c in card_group:
                    c.kill()

                Card.level = 1
                Zombie.over = False
                Zombie.killed = 0
                restart_game = 0
                menu.game = 0
                menu.paused = False

                p = Window()
                p.run_menu()


     
            pygame.display.update()
            pygame.display.set_caption(str(int(menu.clock.get_fps())))
            self.clock.tick(60)

    def update(self):
        if menu.paused == True:
            menu.run_pause()
     


menu = Window()

#Boom die zombie animation
zombie_boom_anim = []
for i in range(20):  
    path = f"zombies/NormalZombie/BoomDie/BoomDie_{i}.png"
    zombie_boom_anim.append(pygame.image.load(path).convert_alpha())




#Shovel
shovel_anim = []
shovel_anim.append(pygame.image.load("Screen/useshovel.png").convert_alpha())

#Bomb walnut anim
bomb_wallnut_anim = []
bomb_wallnut_anim.append(pygame.image.load("plants/WallNut/RedWallNutBowling/RedWallNutBowling_0.png").convert_alpha())

#Sun animation
sun_anim = []
for i in range(22):  
    path = f"plants/Sun/Sun_{i}.png"
    sun_anim.append(pygame.image.load(path).convert_alpha())

#Animations Peashooter--------------------------------------------------------------------------------------------------------------------
peashooter_anim = []
for i in range(13):  
    path = f"plants/Peashooter/Peashooter_{i}.png"
    peashooter_anim.append(pygame.image.load(path).convert_alpha())


#Animations Repeater Pea-----------------------------------------------------------------------------------------------------------------
repeaterpea_anim = []
for i in range(15):
    path = f"plants/RepeaterPea/RepeaterPea_{i}.png"
    repeaterpea_anim.append(pygame.image.load(path).convert_alpha())


#Animations Sunflower--------------------------------------------------------------------------------------------------------------------
sunflower_anim = []
for i in range(18):
    path = f"plants/SunFlower/SunFlower_{i}.png"
    sunflower_anim.append(pygame.image.load(path).convert_alpha())


#Animations Snowpea--------------------------------------------------------------------------------------------------------------------
snowpea_anim = []
for i in range(15):
    path = f"plants/SnowPea/SnowPea_{i}.png"
    snowpea_anim.append(pygame.image.load(path).convert_alpha())


#Animations Wallnut--------------------------------------------------------------------------------------------------------------------
wallnut_anim_0 = []
for i in range(16):
    path = f"plants/WallNut/WallNut/WallNut_{i}.png"
    wallnut_anim_0.append(pygame.image.load(path).convert_alpha())


#Animations Wallnut Cracked 1--------------------------------------------------------------------------------------------------------------------
wallnut_anim_1 = []
for i in range(11):
    path = f"plants/WallNut/WallNut_cracked1/WallNut_cracked1_{i}.png"
    wallnut_anim_1.append(pygame.image.load(path).convert_alpha())


#Animations Wallnut Cracked 2--------------------------------------------------------------------------------------------------------------------
wallnut_anim_2 = []
for i in range(15):
    path = f"plants/WallNut/WallNut_cracked2/WallNut_cracked2_{i}.png"
    wallnut_anim_2.append(pygame.image.load(path).convert_alpha())


#Animations Potato Mine Initialising--------------------------------------------------------------------------------------------------------------------
potatomine_anim_0 = [pygame.image.load("plants/PotatoMine/PotatoMineInit/PotatoMineInit_0.png").convert_alpha()]

#Animations Potato Mine Primed--------------------------------------------------------------------------------------------------------------------
potatomine_anim_1 = []
for i in range(8):
    path = f"plants/PotatoMine/PotatoMine/PotatoMine_{i}.png"
    potatomine_anim_1.append(pygame.image.load(path).convert_alpha())

#Animations Potato Mine Explosion--------------------------------------------------------------------------------------------------------------------
potatomine_anim_2 = []
potatomine_anim_2.append(pygame.image.load("plants/PotatoMine/PotatoMineExplode/PotatoMineExplode_0.png").convert_alpha())

#Animations Cherry Bomb Explosion--------------------------------------------------------------------------------------------------------------------
cherrybomb_anim_1 = []
for i in range(7):
    path = f"plants/CherryBomb/CherryBomb_{i}.png"
    cherrybomb_anim_1.append(pygame.image.load(path).convert_alpha())


#Animations Chomper Idle
chomper_anim_0 = []
for i in range(12):
    path = f"plants/Chomper/Chomper/Chomper_{i}.png"
    chomper_anim_0.append(pygame.image.load(path).convert_alpha())


#Animations Chomper Attack
chomper_anim_1 = []
for i in range(9):
    path = f"plants/Chomper/ChomperAttack/ChomperAttack_{i}.png"
    chomper_anim_1.append(pygame.image.load(path).convert_alpha())


#Animations Chomper Digest
chomper_anim_2 = []
for i in range(6):
    path = f"plants/Chomper/ChomperDigest/ChomperDigest_{i}.png"
    chomper_anim_2.append(pygame.image.load(path).convert_alpha())


#Animations Normal Zombie Walking--------------------------------------------------------------------------------------------------------------------
zombie_anim_0 = []
for i in range(21):
    path = f"zombies/NormalZombie/Zombie/Zombie_{i}.png"
    zombie_anim_0.append(pygame.image.load(path).convert_alpha())


#Animations Normal Zombie Attacking
zombie_anim_attack = []
for i in range(21):
    path = f"zombies/NormalZombie/ZombieAttack/ZombieAttack_{i}.png"
    zombie_anim_attack.append(pygame.image.load(path).convert_alpha())


#Animations Normal Zombie Dying
zombie_anim_death = []
for i in range(18):
    path = f"zombies/NormalZombie/ZombieDie/ZombieLostHead_{i}.png"
    zombie_anim_death.append(pygame.image.load(path).convert_alpha())


# Append frames 0 to 8
for i in range(9):
    zombie_anim_death.append(pygame.image.load(f"zombies/NormalZombie/ZombieDie/ZombieDie_{i}.png").convert_alpha())

# Append frame 9 multiple times 
for _ in range(15):
    zombie_anim_death.append(pygame.image.load("zombies/NormalZombie/ZombieDie/ZombieDie_9.png").convert_alpha())

#Animations Cone Zombie Walking
cone_zombie_anim_0 = []

for i in range(21):
    cone_zombie_anim_0.append(pygame.image.load(f"zombies/ConeheadZombie/ConeheadZombie/ConeheadZombie_{i}.png").convert_alpha())


#Animations Cone Zombie Attacking
cone_zombie_anim_attack = []

for i in range(11):
    cone_zombie_anim_attack.append(pygame.image.load(f"zombies/ConeheadZombie/ConeheadZombieAttack/ConeheadZombieAttack_{i}.png").convert_alpha())


#Animations Bucket Zombie Walking
bucket_zombie_anim_0 = []

for i in range(15):
    bucket_zombie_anim_0.append(pygame.image.load(f"zombies/BucketheadZombie/BucketheadZombie/BucketheadZombie_{i}.png").convert_alpha())


#Animations Bucket Zombie Attacking 
bucket_zombie_anim_attack = []

for i in range(11):
    bucket_zombie_anim_attack.append(pygame.image.load(f"zombies/BucketheadZombie/BucketheadZombieAttack/BucketheadZombieAttack_{i}.png").convert_alpha())


menu.run_menu()
