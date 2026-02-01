import pygame as pg



pg.init()
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.run_animation_right = []
        self.run_animation_left = []
        self.shot_animation_right = []
        self.shot_animation_left = []
        self.jump_animation_right = []
        self.jump_animation_left = []
        self.load_animations()
        self.current_animation = self.jump_animation_right
        self.current_image = 0
        self.image = self.current_animation[self.current_image]
        self.rect = self.image.get_rect()
        self.timer = pg.time.get_ticks()
        self.interval = 530
    def load_animations(self):
        # tile_size = 128
        # tile_scale = 0.5
        for i in range(8):
            self.run_animation_right.append(pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/ezgif-split/tile00{i}.png"))

        for image in self.run_animation_right:
            self.run_animation_left.append(pg.transform.flip(image,True, False))

        for i in range(12):
            if i < 10:
                t = "0"+str(i)
            else:
                t = str(i)
            self.shot_animation_right.append(pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/ezgif-split (2)/tile0{t}.png"))

        for image in self.shot_animation_right:
            self.shot_animation_left.append(pg.transform.flip(image,True, False))


        for i in range(11):
            if i < 10:
                t = "0"+str(i)
            else:
                t = str(i)
            self.jump_animation_right.append(pg.image.load(f"craftpix-net-679950-free-raider-sprite-sheets-pixel-art/ezgif-split (1)/tile0{t}.png"))

        for image in self.jump_animation_right:
            self.jump_animation_left.append(pg.transform.flip(image,True, False))
        num_images = 8

        # for i in range(num_images):
        #     x = i * tile_size + 48
        #     y = 64
        #
        #     rect = pg.Rect(x, y, tile_size / 4, tile_size / 2)
        #     image = spritesheet.subsurface(rect)
        #     image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
        #     self.run_animation_right.append(image)







    def animate(self):
        self.current_image += 1
        if self.current_image >= len(self.current_animation):
            self.current_image = 0
        if pg.time.get_ticks() - self.timer > self.interval:
            self.image = self.current_animation[self.current_image]
            self.mask = pg.mask.from_surface(self.image)  # ← обновляем маску
            self.timer = pg.time.get_ticks()

    def update(self):

        self.animate()
        print(self.current_image)
    def draw(self, screen):
        screen.blit(self.image,self.rect)

player = Player()
while True:
    screen.fill("grey")
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.exit()
    player.update()
    player.draw(screen)
    pg.display.flip()
