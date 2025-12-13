from turtledemo.nim import SCREENWIDTH

import pygame as pg
import pytmx

pg.init()
WIDTH = 1500
HEIGHT = 1000
TILE_SCALE = 2

FPS = 60


class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()

        self.load_animations()
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.center = (500, 250)  # Начальное положение персонажа

        # Начальная скорость и гравитация
        self.velocity_x = 1
        self.velocity_y = 5
        self.gravity = 1
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000








    def load_animations(self):
        self.animation_timer = pg.time.get_ticks()
        tile_size = 128
        tile_scale = 1

        self.idle_animation_right = []

        num_images = 2
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Idle.png")

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]



        self.run_animation_right = []
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Run.png")
        num_images = 8
        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = spritesheet.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.run_animation_right.append(image)  # Добавляем изображение в список

        self.run_animation_left = [pg.transform.flip(image, True, False) for image in self.run_animation_right]


        self.jump_animation_right = []
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Jump.png")
        num_images = 11
        for i in range(num_images):
            x = i * tile_size  # Начальная координата X изображения в спрайтшите
            y = 0  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size, tile_size)  # Прямоугольник, который определяет область изображения
            image = spritesheet.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.jump_animation_right.append(image)  # Добавляем изображение в список

        self.jump_animation_left = [pg.transform.flip(image, True, False) for image in self.jump_animation_right]



    def animate(self):
        self.current_image +=1
        if self.current_image > len(self.current_animation) -1:
            self.current_image = 0


        if pg.time.get_ticks() -self.animation_timer > 200//len(self.current_animation):
            self.image = self.current_animation[self.current_image]
            self.animation_timer = pg.time.get_ticks()





    def update(self, platforms):
        self.animate()

        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and not self.is_jumping:
            if self.current_animation != self.jump_animation_left:
                self.current_animation = self.jump_animation_right
                self.current_image = 0
            elif self.current_animation != self.jump_animation_right:
                self.current_animation = self.jump_animation_left
                self.current_image = 0
            self.jump()

        if keys[pg.K_a]:
            if self.current_animation != self.run_animation_left:
                self.current_animation = self.run_animation_left
                self.current_image = 0

            self.velocity_x = -1
        elif keys[pg.K_d]:
            if self.current_animation != self.run_animation_right:
                self.current_animation = self.run_animation_right
                self.current_image = 0
                self.velocity_x = 0
            self.velocity_x = 1

        else:
            if self.is_jumping:
                if self.current_animation in [self.jump_animation_left, self.idle_animation_left]:
                    self.rect.x -= 1
                elif self.current_animation in [self.jump_animation_right, self.idle_animation_right]:
                    self.rect.x += 1
            # if self.current_animation == self.run_animation_right:
            #     self.current_animation = self.idle_animation_right
            #     self.current_image = 0
            # elif self.current_animation == self.run_animation_left:
            #     self.current_animation = self.idle_animation_left
            #     self.current_image = 0
            #
            #
            self.velocity_x = 0

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False
                self.current_image = 0

                if self.current_animation == self.jump_animation_left:
                    self.current_animation = self.idle_animation_left
                if self.current_animation == self.jump_animation_right:
                    self.current_animation = self.idle_animation_right

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
                self.is_jumping = False
                self.current_image = 0

                if self.current_animation == self.jump_animation_left:
                    self.current_animation = self.idle_animation_left
                if self.current_animation == self.jump_animation_right:
                    self.current_animation = self.idle_animation_right
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                print(platform.rect.x)

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

    def jump(self):
        self.velocity_y = -10
        self.is_jumping = True


    def get_damage(self):
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= 1
            self.damage_timer = pg.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Platform, self).__init__()

        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE


class Game:
    def __init__(self):

        self.clock = pg.time.Clock()
        self.is_game = True
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.tmx_map = pytmx.load_pygame("безымянный.tmx")
        self.map_pixel_width = self.tmx_map.width * self.tmx_map.tilewidth * TILE_SCALE
        self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * TILE_SCALE
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        for layer in self.tmx_map:
            for x, y, gid in layer:
                tile = self.tmx_map.get_tile_image_by_gid(gid)

                if tile:
                    platform = Platform(tile, x * self.tmx_map.tilewidth,
                                        y * self.tmx_map.tileheight,
                                        self.tmx_map.tilewidth,
                                        self.tmx_map.tileheight)

                    self.all_sprites.add(platform)
                    self.platforms.add(platform)
        self.camera_x = 0
        self.camera_y = 0
        print(self.map_pixel_width, self.map_pixel_height)
        self.camera_speed = 4

        self.player = Player(self.map_pixel_width, self.map_pixel_height)

        self.run()

    def draw(self):

        self.screen.fill(pg.Color("grey"))
        self.all_sprites.draw(self.screen)
        self.player.draw(self.screen)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))
        pg.display.flip()

    def update(self):
        self.player.update(self.platforms)

        self.camera_x = max(0, min(self.player.rect.x - SCREENWIDTH // 2, self.map_pixel_width - SCREENWIDTH))

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_game = False

    def run(self):
        self.is_game = True
        while self.is_game:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pg.quit()
        quit()


if __name__ == "__main__":
    game = Game()
