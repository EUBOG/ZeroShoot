import pygame
import random
import sys

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 800, 700
PANEL_HEIGHT = 100
GAME_HEIGHT = HEIGHT - PANEL_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Тир")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)

# Шрифты
font = pygame.font.SysFont(None, 48)
input_font = pygame.font.SysFont(None, 60)

# Загрузка графики
cursor_img = pygame.image.load('cursor.png').convert_alpha()
cursor_img = pygame.transform.scale(cursor_img, (32, 32))

# Фоновое изображение
try:
    background_img = pygame.image.load('background.png').convert()
except FileNotFoundError:
    try:
        background_img = pygame.image.load('background.jpg').convert()
    except FileNotFoundError:
        background_img = None

# Изображения монстров
monster_images = [
    pygame.image.load('monster1.png').convert_alpha(),
    pygame.image.load('monster2.png').convert_alpha(),
    pygame.image.load('monster3.png').convert_alpha()
]

# Масштабируем все изображения монстров
for i in range(len(monster_images)):
    monster_images[i] = pygame.transform.scale(monster_images[i], (80, 80))

# Загрузка звуков
try:
    hit_sound = pygame.mixer.Sound('hit.wav')
    miss_sound = pygame.mixer.Sound('miss.wav')
    pygame.mixer.music.load('background.mp3')
    pygame.mixer.music.play(-1)  # Воспроизведение музыки в цикле
except Exception as e:
    print(f"Ошибка загрузки звука: {e}")

# Начальная громкость
volume = 0.1
pygame.mixer.music.set_volume(volume)
hit_sound.set_volume(volume)
miss_sound.set_volume(volume)

# Класс мишени
class Target:
    def __init__(self):
        self.reset()

    def reset(self):
        self.image = random.choice(monster_images)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(PANEL_HEIGHT, GAME_HEIGHT + PANEL_HEIGHT - self.rect.height)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_hit(self, pos):
        return self.rect.collidepoint(pos)

# Загрузка рекордов
def load_high_scores():
    try:
        with open("highscores.txt", "r") as file:
            scores = [line.strip().split(":") for line in file.readlines()]
            return [(name, int(score)) for name, score in scores]
    except FileNotFoundError:
        return []

# Сохранение рекордов
def save_high_scores(scores):
    with open("highscores.txt", "w") as file:
        for name, score in scores:
            file.write(f"{name}:{score}\n")

# Добавление нового рекорда
def add_new_score(name, new_score):
    scores = load_high_scores()
    scores.append((name, new_score))
    scores.sort(key=lambda x: -x[1])
    save_high_scores(scores[:5])

# Получаем лучший результат
def get_best_score():
    scores = load_high_scores()
    if scores:
        return scores[0][1]
    return 0

# Переменные игры
target = Target()
score = 0
misses = 0
move_interval = 2000
last_move_time = pygame.time.get_ticks()
game_over = False
inputting_name = False
player_name = ""
best_score = get_best_score()

# Основной цикл игры
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(GRAY)

    # Рисуем фон только в игровой области
    if background_img:
        screen.blit(background_img, (0, PANEL_HEIGHT))
    else:
        screen.fill(GRAY, (0, PANEL_HEIGHT, WIDTH, GAME_HEIGHT))

    # Верхняя панель
    screen.fill(WHITE, (0, 0, WIDTH, PANEL_HEIGHT))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif game_over and inputting_name:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    add_new_score(player_name, score)
                    best_score = get_best_score()
                    game_over = False
                    inputting_name = False
                    score = 0
                    misses = 0
                    move_interval = 2000
                    target.reset()
                    last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 10 and event.unicode.isalnum():
                    player_name += event.unicode

        elif not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] > PANEL_HEIGHT:
                    if target.is_hit(mouse_pos):
                        score += 1
                        hit_sound.play()
                        target.reset()
                        move_interval = max(500, move_interval - 100)
                        misses = 0
                    else:
                        miss_sound.play()
                        misses += 1
                        if misses >= 5:
                            game_over = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    volume = min(1.0, volume + 0.1)
                    pygame.mixer.music.set_volume(volume)
                    hit_sound.set_volume(volume)
                    miss_sound.set_volume(volume)
                elif event.key == pygame.K_DOWN:
                    volume = max(0.0, volume - 0.1)
                    pygame.mixer.music.set_volume(volume)
                    hit_sound.set_volume(volume)
                    miss_sound.set_volume(volume)

    # Автоматическое перемещение мишени
    current_time = pygame.time.get_ticks()
    if current_time - last_move_time > move_interval and not game_over:
        target.reset()
        last_move_time = current_time

    # Рисуем мишень
    target.draw(screen)

    # Рисуем информацию на панели
    score_text = font.render(f"Счёт: {score}", True, BLACK)
    screen.blit(score_text, (20, 20))

    vol_text = font.render(f"Громкость: {int(volume * 100)}%", True, BLACK)
    screen.blit(vol_text, (WIDTH - 260, 20))

    best_text = font.render(f"Рекорд: {best_score}", True, BLACK)
    screen.blit(best_text, (WIDTH // 2 - 100, 20))

    # Рисуем курсор
    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(cursor_img, (mouse_x - 16, mouse_y - 16))

    # Экран проигрыша
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        game_over_text = font.render("Игра окончена!", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 170, HEIGHT // 2 - 60))

        score_final_text = font.render(f"Ваш счёт: {score}", True, WHITE)
        screen.blit(score_final_text, (WIDTH // 2 - 100, HEIGHT // 2 - 10))

        enter_name_text = font.render("Введите имя:", True, WHITE)
        screen.blit(enter_name_text, (WIDTH // 2 - 120, HEIGHT // 2 + 40))

        name_input = input_font.render(player_name, True, WHITE)
        screen.blit(name_input, (WIDTH // 2 - 100, HEIGHT // 2 + 90))

        inputting_name = True

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение работы
pygame.quit()
sys.exit()