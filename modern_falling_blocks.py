import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import numpy as np
import pygame

pygame.init()

# Create screen
FPS = 60
FULLSCREEN = True
START_BACKGROUND_COLOR = (28, 40, 51)
END_BACKGROUND_COLOR = (123, 36, 28)
NUM_BLOCKS = 15

if FULLSCREEN:
    display_info = pygame.display.Info()
    target_dims = display_info.current_w, display_info.current_h
    display_options = (
        pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED
    )
else:
    target_dims = 1200, 800
    display_options = pygame.SCALED

screen = pygame.display.set_mode(target_dims, display_options, vsync=1)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()
MIN_SCREEN_DIM = min(SCREEN_WIDTH, SCREEN_HEIGHT)

clock = pygame.time.Clock()
interframe_delay = 0


class PreciseRect(pygame.Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_x = self.x
        self.sub_y = self.y

    # `self.x` and `self.y` are rounded to the nearest whole number so
    # we create our own variables `self._x` and `self._y` to hold
    # the actual position of the ball down to the subpixel
    @property
    def sub_x(self):
        return self._x

    @sub_x.setter
    def sub_x(self, x):
        self.x = self._x = x

    @property
    def sub_y(self):
        return self._y

    @sub_y.setter
    def sub_y(self, y):
        self.y = self._y = y


interp_background_color = lambda x: np.average(
    [START_BACKGROUND_COLOR, END_BACKGROUND_COLOR], axis=0, weights=[1 - x, x]
)
background_color = START_BACKGROUND_COLOR

RECT_SIZE = MIN_SCREEN_DIM // NUM_BLOCKS
PLAYER_COLOR = (240, 243, 244)
PLAYER_POS = (SCREEN_WIDTH // 2, 0.99 * SCREEN_HEIGHT - RECT_SIZE)
player = PreciseRect(PLAYER_POS, (RECT_SIZE,) * 2)
START_LIVES = lives = 3
PLAYER_SPEED_FACTOR = 1.2
MAX_PLAYER_SPEED = SCREEN_HEIGHT

compute_block_color = lambda: np.clip(np.multiply(background_color, 1.2) + 20, 0, 255)
block_color = compute_block_color()
BASE_BLOCK_SPEED = block_speed = SCREEN_HEIGHT // 2
blocks = []
score = 0

generate_block_y = lambda: np.random.randint(
    -1.5 * SCREEN_HEIGHT - RECT_SIZE, -RECT_SIZE
)

for i in range(NUM_BLOCKS * SCREEN_WIDTH // MIN_SCREEN_DIM):
    block_height = generate_block_y()
    block = PreciseRect((i * RECT_SIZE, block_height), (RECT_SIZE,) * 2)
    blocks.append(block)

FONT_SIZE = MIN_SCREEN_DIM // 20
font = pygame.font.Font(None, FONT_SIZE)

right = left = False
direction = 0

running = True
while running:
    for event in pygame.event.get():
        # Quit if we hit the x-button on the window or use a shortcut
        if event.type == pygame.QUIT:
            running = False
            continue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                right = True
                direction = 1

            if event.key == pygame.K_LEFT:
                left = True
                direction = -1

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                right = False
                direction = -left

            if event.key == pygame.K_LEFT:
                left = False
                direction = right

    screen.fill(background_color)

    player.sub_x += interframe_delay * direction * min(block_speed * PLAYER_SPEED_FACTOR, MAX_PLAYER_SPEED)
    player.sub_x = np.clip(player.sub_x, 0, SCREEN_WIDTH - RECT_SIZE)

    for block in blocks:
        block.sub_y += interframe_delay * block_speed
        pygame.draw.rect(screen, block_color, block)

        if block.colliderect(player):
            lives -= 1
            background_color = interp_background_color(
                (START_LIVES - lives) / (START_LIVES - 1)
            )
            block_color = compute_block_color()
            block.sub_y = -2 * RECT_SIZE

        if not lives:
            running = False
            continue

        if block.sub_y > SCREEN_HEIGHT:
            block.sub_y = generate_block_y()
            score += 1
            block_speed = (0.75 * BASE_BLOCK_SPEED) * np.log(
                1 + score / 50
            ) + BASE_BLOCK_SPEED

    pygame.draw.rect(screen, PLAYER_COLOR, player)

    text_surf = font.render(f"Score: {score}", True, PLAYER_COLOR)
    text_rect = text_surf.get_rect(
        left=SCREEN_WIDTH - SCREEN_WIDTH // 5, top=SCREEN_HEIGHT // 20
    )
    screen.blit(text_surf, text_rect)

    pygame.display.flip()
    interframe_delay = clock.tick(FPS) / 1000

pygame.quit()

print("Score:", score)
