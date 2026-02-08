import pygame as pg

pg.init()
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
FPS = 60


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.idle_animation_right = []
        self.idle_animation_left = []
        self.run_animation_right = []
        self.run_animation_left = []
        self.shot_animation_right = []
        self.shot_animation_left = []
        self.jump_animation_right = []
        self.jump_animation_left = []
        self.load_animations()
        self.current_animation = self.idle_animation_right  # Начинаем с бега, а не прыжка
        self.current_image = 0
        self.image = self.current_animation[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)  # Позиция на экране
        self.timer = pg.time.get_ticks()
        self.interval = 50  # Увеличил интервал для наглядности (можно 60)
        self.direction = "right"
        self.is_jump_or_attack = False

    def load_animations(self):
        for i in range(6):
            self.idle_animation_right.append(
                pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/idle/idle00{i}.png"))

        for image in self.idle_animation_right:
            self.idle_animation_left.append(pg.transform.flip(image, True, False))

        for i in range(8):
            self.run_animation_right.append(
                pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/ezgif-split/tile00{i}.png"))

        for image in self.run_animation_right:
            self.run_animation_left.append(pg.transform.flip(image, True, False))

        for i in range(12):
            t = f"0{i}" if i < 10 else str(i)
            self.shot_animation_right.append(
                pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/ezgif-split (2)/tile0{t}.png"))

        for image in self.shot_animation_right:
            self.shot_animation_left.append(pg.transform.flip(image, True, False))

        for i in range(11):
            t = f"0{i}" if i < 10 else str(i)
            self.jump_animation_right.append(
                pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/ezgif-split (1)/tile0{t}.png"))

        for image in self.jump_animation_right:
            self.jump_animation_left.append(pg.transform.flip(image, True, False))

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = now
            if self.current_animation in [self.jump_animation_right,
                                          self.jump_animation_left] and self.current_image == len(
                    self.jump_animation_left) - 1:
                self.is_jump_or_attack = False
            if self.current_animation in [self.shot_animation_right,
                                          self.shot_animation_left] and self.current_image == len(
                self.shot_animation_left) - 1:
                self.is_jump_or_attack = False

    def update(self):
        if self.current_animation in [self.shot_animation_right, self.jump_animation_right, self.shot_animation_left, self.jump_animation_left] and self.is_jump_or_attack:

            self.animate()
        elif self.current_animation not in [self.shot_animation_right, self.jump_animation_right, self.shot_animation_left, self.jump_animation_left]:
            self.animate()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_animation(self, animation):
        if self.current_animation != animation:
            self.current_animation = animation
            self.current_image = 0
            self.image = self.current_animation[self.current_image]  # Сразу показываем первый кадр!
            self.timer = pg.time.get_ticks()


player = Player()

while True:
    screen.fill("grey")

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                player.direction = "left"
                player.set_animation(player.run_animation_left)
            if event.key == pg.K_RIGHT:
                player.direction = "right"
                player.set_animation(player.run_animation_right)
            if event.key == pg.K_SPACE:
                if player.direction == "right":
                    player.set_animation(player.jump_animation_right)
                else:
                    player.set_animation(player.jump_animation_left)

                player.is_jump_or_attack = True

            if event.key == pg.K_RETURN:
                if player.direction == "right":
                    player.set_animation(player.shot_animation_right)
                else:
                    player.set_animation(player.shot_animation_left)
                player.is_jump_or_attack = True
        elif event.type == pg.KEYUP:
            if player.direction == "right":
                player.set_animation(player.idle_animation_right)
            else:
                player.set_animation(player.idle_animation_left)

    player.update()
    player.draw(screen)
    pg.display.flip()
    clock.tick(FPS)


