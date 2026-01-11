import pygame as pg
import pytmx

pg.init()
WIDTH = 1500
HEIGHT = 1000
TILE_SCALE = 4
FPS = 90


class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()
        self.load_animations()
        self.current_animation = self.idle_animation_left
        self.image = self.current_animation[0]
        self.current_image = 0
        self.rect = self.image.get_rect()
        self.rect.center = (200, 300)
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 1
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE
        self.timer = pg.time.get_ticks()
        self.interval = 50
        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000
        self.mask = pg.mask.from_surface(self.image)
        self.facing_right = True

    def load_animations(self):
        tile_size = 128
        tile_scale = 0.5

        self.idle_animation_right = []
        num_images = 6
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Idle.png")
        for i in range(num_images):
            x = i * tile_size +48
            y = 64


            rect = pg.Rect(x, y, tile_size/4, tile_size/2)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.run_animation_right = []
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Run.png")
        num_images = 8
        for i in range(num_images):
            x = i * tile_size +40  # Начальная координата X изображения в спрайтшите
            y = 64  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size/4, tile_size/2)  # Прямоугольник, который определяет область изображения
            image = spritesheet.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.run_animation_right.append(image)  # Добавляем изображение в список
        self.run_animation_left = [pg.transform.flip(image, True, False) for image in self.run_animation_right]
        self.jump_animation_right = []
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Jump.png")
        num_images = 11
        for i in range(num_images):
            x = i * tile_size +48  # Начальная координата X изображения в спрайтшите
            y = 64  # Начальная координата Y изображения в спрайтшите
            rect = pg.Rect(x, y, tile_size/4, tile_size/2)  # Прямоугольник, который определяет область изображения
            image = spritesheet.subsurface(rect)  # Вырезаем изображение из спрайтшита
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.jump_animation_right.append(image)  # Добавляем изображение в список
        self.jump_animation_left = [pg.transform.flip(image, True, False) for image in self.jump_animation_right]


    def animate(self):
        self.current_image += 1
        if self.current_image >= len(self.current_animation):
            self.current_image = 0
        if pg.time.get_ticks() - self.timer > self.interval:
            self.image = self.current_animation[self.current_image]
            self.mask = pg.mask.from_surface(self.image)   # ← обновляем маску
            self.timer = pg.time.get_ticks()

    def update(self, platforms):
        keys = pg.key.get_pressed()

        # 1. Запоминаем желаемые скорости
        if keys[pg.K_a]:
            self.velocity_x = -18
            self.current_animation = self.run_animation_left
            self.facing_right = False
        elif keys[pg.K_d]:
            self.velocity_x = 18
            self.current_animation = self.run_animation_right
            self.facing_right = True
        else:
            self.velocity_x = 0
            if not self.is_jumping:
                if self.current_animation == self.run_animation_left:
                    self.current_animation = self.idle_animation_left
                elif self.current_animation == self.run_animation_right:
                    self.current_animation = self.idle_animation_right

        if keys[pg.K_SPACE] and not self.is_jumping:
            self.velocity_y = -12
            self.is_jumping = True
        if self.is_jumping:
            if self.facing_right:
                self.current_animation = self.jump_animation_right
            else:
                self.current_animation = self.jump_animation_left
        elif self.velocity_x != 0:
            if self.facing_right:
                self.current_animation = self.run_animation_right
            else:
                self.current_animation = self.run_animation_left
        else:
            if self.facing_right:
                self.current_animation = self.idle_animation_right
            else:
                self.current_animation = self.idle_animation_left

        # 2. Гравитация
        self.velocity_y += self.gravity
        if self.velocity_y > 10:  # ограничим макс. скорость падения
            self.velocity_y = 10

        # 3. Горизонтальное перемещение
        future_x = self.rect.x + self.velocity_x
        future_rect = self.rect.copy()
        future_rect.x = future_x

        # 3а. Карта по краям
        if future_rect.left < 0:
            future_rect.left = 0
            self.velocity_x = 0
        if future_rect.right > self.map_width:
            future_rect.right = self.map_width
            self.velocity_x = 0

        # 3б. Столкновения с тайлами
        for p in platforms:
            if future_rect.colliderect(p.rect):
                if self.velocity_x > 0:  # идём вправо
                    future_rect.right = p.rect.left
                elif self.velocity_x < 0:  # идём влево
                    future_rect.left = p.rect.right
                self.velocity_x = 0
        self.rect.x = future_rect.x

        # 4. Вертикальное перемещение
        future_y = self.rect.y + self.velocity_y
        future_rect = self.rect.copy()
        future_rect.y = future_y

        on_ground = False
        for p in platforms:
            if future_rect.colliderect(p.rect):
                if self.velocity_y > 0:  # падаем
                    future_rect.bottom = p.rect.top
                    self.velocity_y = 0
                    on_ground = True
                elif self.velocity_y < 0:  # прыгаем вверх, ударились головой
                    future_rect.top = p.rect.bottom
                    self.velocity_y = 0
        self.rect.y = future_rect.y

        # 5. Приземлились
        if on_ground:
            self.is_jumping = False
            if self.current_animation in (self.jump_animation_left, self.jump_animation_right):
                self.current_animation = self.idle_animation_left if self.velocity_x <= 0 else self.idle_animation_right
        self.animate()

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
        self.rect = self.image.get_rect(topleft=(x * TILE_SCALE, y * TILE_SCALE))
        self.mask = pg.mask.from_surface(self.image)


class NPC1(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super().__init__()
        self.is_speaking = False
        self.load_animations()
        self.current_animation = self.idle_animation_left
        self.image = self.current_animation[0]
        self.current_image = 0
        self.rect = self.image.get_rect()
        self.rect.center = (5350, 800)
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE
        self.timer = pg.time.get_ticks()
        self.interval = 50
        self.facing_right = False
    def load_animations(self):
        tile_size = 128
        tile_scale = 0.5

        self.idle_animation_right = []
        num_images = 8
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_2/Idle.png")
        for i in range(num_images):
            x = i * tile_size +48
            y = 64


            rect = pg.Rect(x, y, tile_size/4, tile_size/2)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

    def animate(self):
        self.current_image += 1
        if self.current_image >= len(self.current_animation):
            self.current_image = 0
        if pg.time.get_ticks() - self.timer > self.interval:
            self.image = self.current_animation[self.current_image]
            self.mask = pg.mask.from_surface(self.image)  # ← обновляем маску
            self.timer = pg.time.get_ticks()

    def update(self, platforms):





        self.animate()


    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.hint_rect = pg.Rect(self.rect.left, self.rect.top, 1000, 200)
        # self.hint_rect.bottomright= (5350, 750)
        pg.draw.rect(self.screen, pg.Color("white"), self.hint_rect)
        print(self.hint_rect.center)



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
        self.player = Player(self.map_pixel_width, self.map_pixel_height)
        self.npc1 = NPC1(self.map_pixel_width, self.map_pixel_height)
        self.all_sprites.add(self.npc1)
        self.camera_x = self.player.rect.x
        self.camera_y = self.player.rect.y
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

        self.run()

    def draw(self):
        f = pg.font.SysFont(None, 50)
        text = f.render(f"координата игрока {self.player.rect.center}", True, pg.Color("red"))
        text_rect = text.get_rect()
        self.screen.fill(pg.Color("grey"))

        # pg.draw.rect(self.screen, pg.Color("blue"), self.player.rect.move(-int(self.camera_x), -int(self.camera_y)))
        self.screen.blit(self.player.image, self.player.rect.move(-int(self.camera_x), -int(self.camera_y)))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))
        self.screen.blit(text, text_rect)
        if self.npc1.rect.x - self.player.rect.x < 100 and self.npc1.rect.y == self.player.rect.y  :
            self.hint_rect = pg.Rect(5250, 600, 200, 100)

            pg.draw.rect(self.screen, pg.Color("white"),self.hint_rect.move(-self.camera_x, -self.camera_y), border_radius= 30)


            font = pg.font.SysFont('Arial', 25)
            text = font.render('Привет, тебе\n надо тут выжить', True, (0, 100, 0))
            text_rect = text.get_rect()
            text_rect.center = self.hint_rect.center
            self.screen.blit(text,text_rect.move(-self.camera_x, -self.camera_y) )




        pg.display.flip()
    def update(self):
        self.player.update(self.platforms)
        self.npc1.update(self.platforms)
        self.camera_x = max(0, min(self.player.rect.x - WIDTH // 2, self.map_pixel_width - WIDTH))
        self.camera_y = max(0, min(self.player.rect.y - HEIGHT // 2, self.map_pixel_height - HEIGHT))



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
        quit()


if __name__ == "__main__":
    game = Game()