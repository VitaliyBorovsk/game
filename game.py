import pygame as pg
import pytmx

pg.init()
WIDTH = 1500
HEIGHT = 1000
TILE_SCALE = 3
FPS = 60


class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()

        self.load_animations()
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[0]
        self.animation_index = 0

        # Создаем маску для точной коллизии
        self.mask = pg.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.midbottom = (WIDTH // 2, HEIGHT // 2)

        # Физические параметры
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.max_fall_speed = 20
        self.speed = 8
        self.jump_power = -16
        self.is_jumping = False
        self.is_grounded = False

        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.animation_timer = pg.time.get_ticks()
        self.animation_interval = 80

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000

        self.facing_right = True

    def load_animations(self):
        tile_size = 128
        tile_scale = TILE_SCALE * 0.3

        # Idle animation right
        self.idle_animation_right = []
        num_images = 6
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Idle.png").convert_alpha()

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (int(tile_size * tile_scale), int(tile_size * tile_scale)))
            # Обрезаем прозрачные края
            self.idle_animation_right.append(self.crop_transparent(image))

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        # Run animation right
        self.run_animation_right = []
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Run.png").convert_alpha()
        num_images = 8

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (int(tile_size * tile_scale), int(tile_size * tile_scale)))
            self.run_animation_right.append(self.crop_transparent(image))

        self.run_animation_left = [pg.transform.flip(image, True, False) for image in self.run_animation_right]

        # Jump animation right
        self.jump_animation_right = []
        spritesheet = pg.image.load("craftpix-net-679950-free-raider-sprite-sheets-pixel-art/Raider_1/Jump.png").convert_alpha()
        num_images = 11

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (int(tile_size * tile_scale), int(tile_size * tile_scale)))
            self.jump_animation_right.append(self.crop_transparent(image))

        self.jump_animation_left = [pg.transform.flip(image, True, False) for image in self.jump_animation_right]

    def crop_transparent(self, image):
        """Обрезает прозрачные края у изображения"""
        mask = pg.mask.from_surface(image)
        bounding_rect = mask.get_bounding_rects()

        if bounding_rect:
            # Берем самый большой bounding rect (на случай если несколько несвязных областей)
            max_rect = bounding_rect[0]
            for rect in bounding_rect:
                if rect.width * rect.height > max_rect.width * max_rect.height:
                    max_rect = rect

            # Обрезаем изображение
            cropped_image = image.subsurface(max_rect)
            return cropped_image
        return image

    def animate(self):


        if pg.time.get_ticks() - self.animation_timer > self.animation_interval  :
            self.animation_index += 1
            if self.animation_index >= len(self.current_animation) :
                self.animation_index = 0

            self.image = self.current_animation[self.animation_index]
            self.mask = pg.mask.from_surface(self.image)
            self.animation_timer = pg.time.get_ticks()

    def update(self, platforms):
        keys = pg.key.get_pressed()

        self.velocity_x = 0
        moving = False

        if keys[pg.K_a]:
            self.velocity_x = -self.speed
            self.facing_right = False
            moving = True
        elif keys[pg.K_d]:
            self.velocity_x = self.speed
            self.facing_right = True
            moving = True

        # Обработка прыжка
        if keys[pg.K_SPACE] and self.is_grounded:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.is_grounded = False

        # Применение гравитации
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed


        if self.is_jumping:
            if self.facing_right:
                self.current_animation = self.jump_animation_right

            else:
                self.current_animation = self.jump_animation_left
        elif moving:
            if self.facing_right:
                self.current_animation = self.run_animation_right
            else:
                self.current_animation = self.run_animation_left
        else:
            if self.facing_right:
                self.current_animation = self.idle_animation_right
            else:
                self.current_animation = self.idle_animation_left

        # Обновляем анимацию
        self.animate()
        # Двигаем по горизонтали
        self.rect.x += self.velocity_x

        # Проверка горизонтальных коллизий с использованием масок
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Проверяем точное пересечение масок
                offset_x = platform.rect.x - self.rect.x
                offset_y = platform.rect.y - self.rect.y

                if self.mask.overlap(pg.mask.from_surface(platform.image), (offset_x, offset_y)):
                    if self.velocity_x > 0:  # Движение вправо
                        self.rect.right = platform.rect.left
                    elif self.velocity_x < 0:  # Движение влево
                        self.rect.left = platform.rect.right

        # Двигаем по вертикали
        self.rect.y += self.velocity_y
        self.is_grounded = False

        # Проверка вертикальных коллизий с использованием масок
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                offset_x = platform.rect.x - self.rect.x
                offset_y = platform.rect.y - self.rect.y

                if self.mask.overlap(pg.mask.from_surface(platform.image), (offset_x, offset_y)):
                    if self.velocity_y > 0:  # Падение вниз
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.is_grounded = True
                        self.is_jumping = False
                    elif self.velocity_y < 0:  # Движение вверх
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0

        # Ограничение выхода за границы карты
        self.rect.x = max(0, min(self.rect.x, self.map_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.map_height - self.rect.height))

        # Если игрок падает и достигает нижней границы
        if self.rect.bottom >= self.map_height:
            self.rect.bottom = self.map_height
            self.velocity_y = 0
            self.is_grounded = True
            self.is_jumping = False

    def jump(self):
        self.velocity_y = self.jump_power
        self.is_jumping = True
        self.is_grounded = False

    def get_damage(self):
        current_time = pg.time.get_ticks()
        if current_time - self.damage_timer > self.damage_interval:
            self.hp -= 1
            self.damage_timer = current_time

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

        # Для отладки: рисуем контур маски (закомментировать в финальной версии)
        # outline = self.mask.outline()
        # if outline:
        #     points = [(point[0] + self.rect.x - camera_x, point[1] + self.rect.y - camera_y) for point in outline]
        #     if len(points) > 1:
        #         pg.draw.lines(screen, (255, 0, 0), True, points, 2)


class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Platform, self).__init__()

        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE
        # Создаем маску для платформы
        self.mask = pg.mask.from_surface(self.image)


class Game:
    def __init__(self):
        self.clock = pg.time.Clock()
        self.is_game = True
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Platformer Game")

        # Загрузка карты
        self.tmx_map = pytmx.load_pygame("безымянный.tmx")
        self.map_pixel_width = self.tmx_map.width * self.tmx_map.tilewidth * TILE_SCALE
        self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * TILE_SCALE

        # Создание групп спрайтов
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        # Создание игрока
        self.player = Player(self.map_pixel_width, self.map_pixel_height)

        # Инициализация камеры
        self.camera_x = 0
        self.camera_y = 0

        # Загрузка платформ из TMX карты
        for layer in self.tmx_map.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    if gid != 0:
                        tile = self.tmx_map.get_tile_image_by_gid(gid)
                        if tile:
                            platform = Platform(
                                tile,
                                x * self.tmx_map.tilewidth,
                                y * self.tmx_map.tileheight,
                                self.tmx_map.tilewidth,
                                self.tmx_map.tileheight
                            )
                            self.all_sprites.add(platform)
                            self.platforms.add(platform)

        # Инициализируем камеру позицией игрока
        self.camera_x = self.player.rect.centerx - WIDTH // 2
        self.camera_y = self.player.rect.centery - HEIGHT // 2

        self.run()

    def draw(self):
        # Очистка экрана
        self.screen.fill(pg.Color("grey"))

        # Рисуем все платформы с учетом камеры
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image,
                             (sprite.rect.x - self.camera_x,
                              sprite.rect.y - self.camera_y))

        # Рисуем игрока
        self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Отображение статистики
        font = pg.font.Font(None, 36)
        hp_text = font.render(f"HP: {self.player.hp}", True, pg.Color("white"))
        self.screen.blit(hp_text, (10, 10))

        # Отладочная информация
        pos_text = font.render(f"Pos: ({int(self.player.rect.x)}, {int(self.player.rect.y)})", True, pg.Color("white"))
        self.screen.blit(pos_text, (10, 50))
        grounded_text = font.render(f"grounded: {self.player.is_grounded}", True, pg.Color("white"))
        self.screen.blit(grounded_text, (10, 80))
        pg.display.flip()

    def update(self):
        self.player.update(self.platforms)

        # Обновление камеры - следим за игроком
        self.camera_x = self.player.rect.centerx - WIDTH // 2
        self.camera_y = self.player.rect.centery - HEIGHT // 2

        # Ограничение камеры границами карты
        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - HEIGHT))

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_game = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.is_game = False
                elif event.key == pg.K_h:
                    self.player.get_damage()

    def run(self):
        while self.is_game:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pg.quit()
        quit()


if __name__ == "__main__":
    game = Game()