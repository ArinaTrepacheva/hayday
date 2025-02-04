import os
import time
import pygame


# Функция обработки изображения(удаление фона)
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# Класс поля
class Field(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__(all_sprites)
        if type == 'з':
            self.image = load_image('земля.png')
            self.type = 0
        elif type == 'с':
            self.image = load_image('сено.png')
            self.type = 1
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = pygame.Rect(x, y, 60, 60)
        self.mask = pygame.mask.from_surface(self.image)


# Класс препятствия(вода)
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(obstacle_sprites)
        self.image = load_image('вода.jpeg')
        self.type = 1
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = pygame.Rect(x, y, 60, 60)
        self.mask = pygame.mask.from_surface(self.image)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows):
        super().__init__(hero_sprites)
        self.lavel = 1
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        # Картинки для анимации движения вниз
        self.down = self.frames[:4]
        # Картинки для анимации движения влево
        self.left = self.frames[4:8]
        # Картинки для анимации движения вправо
        self.right = self.frames[8:12]
        # Картинки для анимации движения вверх
        self.up = self.frames[12:16]
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 120, 60, 60)
        self.mask = pygame.mask.from_surface(self.image)

    # Функция обработки картинки для анимации
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size))
                frame = pygame.transform.scale(frame, (60, 60))
                self.frames.append(frame)

    # Замена земли на сено при взаимодействии
    def replace(self, x, y):
        self.rect = self.rect.move(x, y)
        for block in blocks:
            if pygame.sprite.collide_rect(player, block) and block.__class__.__name__ != 'Obstacle':
                block.type = 0
                block.image = load_image('земля.png')
                block.image = pygame.transform.scale(block.image, (60, 60))

    def start_position(self):
        self.rect.topleft = (0, 120)

    # Обновление анимации
    def update(self, val):
        if val == 'down':
            self.cur_frame = (self.cur_frame + 1) % 4
            self.image = self.down[self.cur_frame]
        elif val == 'left':
            self.cur_frame = (self.cur_frame + 1) % 4
            self.image = self.left[self.cur_frame]
        elif val == 'right':
            self.cur_frame = (self.cur_frame + 1) % 4
            self.image = self.right[self.cur_frame]
        elif val == 'up':
            self.cur_frame = (self.cur_frame + 1) % 4
            self.image = self.up[self.cur_frame]


# Класс трактора
class Tractor(pygame.sprite.Sprite):
    def __init__(self, x, move):
        super().__init__(tractor_sprites)
        self.move = move
        self.image = load_image('трактор.png', (0, 0, 0))
        self.image = pygame.transform.scale(self.image, (60, 60))
        # Если 60, то движение слева направо
        if move == 60:
            self.rect = pygame.Rect(0, 120 + x * 60, 60, 60)
        else:
            # Иначе движение справа налево
            self.rect = pygame.Rect(540, 120 + x * 60, 60, 60)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect = self.rect.move(self.move, 0)


# Класс финального окна
class End(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(end_sprites)
        self.image = load_image('конец.png', (0, 0, 0))
        self.rect = pygame.Rect(0, 0, 600, 600)
        self.mask = pygame.mask.from_surface(self.image)


# Инициализация игры
pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('FIELD')
screen.fill((20, 235, 26))
x, y = 0, 120
run = True
isgame = False
timer = False
kill = False
end_flag = False
blocks = []
ochki = 0
ochki_list = [100, 200, 300, 400, 500]
direction = 'down'
levels = []
current_level = []
tractor_pos = [[0, 6, 5, 7], [4, 5, 1, 0], [1, 5, 6, 2], [0, 1, 2, 3, 4, 6], [4, 5]]
tractor_pos_copy = tractor_pos[:]
tractor_way = [[60, -60, 60, 60], [-60, -60, 60, 60], [-60, 60, -60, 60], [60, -60, 60, -60, 60, -60], [60, -60]]
tractor_way_copy = tractor_way[:]
tractor_sek = [[17, 15, 5, 8], [15, 12, 19, 14], [18, 14, 7, 5], [18, 16, 15, 14, 12, 8], [18, 14]]
tractor_sek_copy = tractor_sek[:]

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
tractor = pygame.sprite.Sprite(all_sprites)
coin = pygame.sprite.Sprite(all_sprites)
coin2 = pygame.sprite.Sprite(all_sprites)
hero_sprites = pygame.sprite.Group()
tractor_sprites = pygame.sprite.Group()
kill_sprites = pygame.sprite.Group()
money_sprites = pygame.sprite.Group()
notractor_sprites = pygame.sprite.Group()
buy_sprites = pygame.sprite.Group()
bg_sprites = pygame.sprite.Group()
bg = pygame.sprite.Sprite(bg_sprites)
obstacle_sprites = pygame.sprite.Group()
end_sprites = pygame.sprite.Group()

# Загрузка изображения монет
coin.image = load_image("монета.png", (0, 0, 0))
coin.image = pygame.transform.scale(coin.image, (40, 30))
coin.rect = (200, 5, 30, 30)
coin2.image = load_image("монета.png", (0, 0, 0))
coin2.image = pygame.transform.scale(coin.image, (20, 20))
coin2.rect = (400, 15, 20, 20)

# Загрузка изображения трактора
tractor.image = load_image("трактор.png", (0, 0, 0))
tractor.image = pygame.transform.scale(tractor.image, (60, 40))
tractor.rect = (320, 5, 60, 40)

# Чтение файла с уровнями
with open('level.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Загрузка уровней
for line in lines:
    line = line.strip()
    if not line:
        if current_level:
            levels.append(current_level)
            current_level = []
    else:
        current_level.append(line)

if current_level:
    levels.append(current_level)

# Конвертация первого уровня в формат игры
for row in levels[0]:
    for col in row:
        if col == 'в':
            block = Obstacle(x, y)
        else:
            block = Field(x, y, col)
        blocks.append(block)
        x += 60
    y += 60
    x = 0

# Инициализация игрока
player = Player(load_image('фермер.png', -1), 4, 4)

# Отображение текста с номером уровня
font = pygame.font.Font(None, 50)
text = font.render(f"level {player.lavel}", True, (0, 0, 0))
screen.blit(text, (2, 5))

# Отображение текста с таймером
pygame.draw.rect(screen, (255, 0, 0), (2, 60, 185, 50), 0, 3)
font = pygame.font.Font(None, 28)
text = font.render(f"20 сек.", True, (255, 255, 255))
screen.blit(text, (500, 20))

# Отображение кнопки включения таймера
font = pygame.font.Font(None, 28)
text = font.render(f"Включить таймер", True, (255, 255, 255))
screen.blit(text, (10, 75))

# Установка таймеров
start = time.time() - 10000
start2 = time.time() - 10000
start3 = time.time() - 10000
start4 = time.time() - 10000
clock = pygame.time.Clock()
MYEVENTTYPE = pygame.USEREVENT + 1
pygame.time.set_timer(MYEVENTTYPE, 200)

# Отображение стартового окна
pygame.mixer.init()
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.play(-1)
bg.image = load_image("стартокно.png", (0, 0, 0))
bg.rect = (0, 0, 600, 600)

# Создание класса окончания игры
end = End()

# Игровой цикл
while run:
    # Проверка на взаимодействие игрока с препятствиями
    if (pygame.sprite.spritecollideany(player, tractor_sprites) or pygame.sprite.spritecollideany(player,
                                                                                                  obstacle_sprites)) and isgame:
        kill = True
    if isgame:
        # Отображение текста
        screen.fill((20, 235, 26))
        font = pygame.font.Font(None, 40)
        text = font.render("50", True, (0, 0, 0))
        screen.blit(text, (370, 15))
        font = pygame.font.Font(None, 50)
        text = font.render(f"level {player.lavel}", True, (0, 0, 0))
        screen.blit(text, (2, 5))

        # В зависимости от количество очков определяется размер поля "очки"
        if ochki == 0:
            font = pygame.font.Font(None, 50)
            text = font.render(f"{ochki}", True, (0, 0, 0))
            screen.blit(text, (180, 5))

        elif ochki > 0 and ochki < 1000:
            font = pygame.font.Font(None, 50)
            text = font.render(f"{ochki}", True, (0, 0, 0))
            screen.blit(text, (140, 5))

        else:
            font = pygame.font.Font(None, 50)
            text = font.render(f"{ochki}", True, (0, 0, 0))
            screen.blit(text, (120, 5))

    # Цикл обработки нажатий
    for event in pygame.event.get():
        # Конец игры
        if event.type == pygame.QUIT:
            run = False

        # Движение тракторов
        if event.type == MYEVENTTYPE and timer and isgame:
            tractor_sprites.update()

        if event.type == pygame.KEYDOWN and isgame:
            if timer:
                # Перемещение игрока
                if event.key == pygame.K_UP and player.rect.top != 120:
                    player.replace(0, -60)
                    direction = 'up'
                    player.cur_frame = 0

                elif event.key == pygame.K_DOWN and player.rect.bottom != 600:
                    player.replace(0, 60)
                    direction = 'down'
                    player.cur_frame = 0

                elif event.key == pygame.K_LEFT and player.rect.left != 0:
                    player.replace(-60, 0)
                    direction = 'left'
                    player.cur_frame = 0

                elif event.key == pygame.K_RIGHT and player.rect.right != 600:
                    player.replace(60, 0)
                    direction = 'right'
                    player.cur_frame = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Старт игры
            if event.pos[0] >= 350 and event.pos[0] <= 535 and event.pos[1] >= 500 and event.pos[
                1] <= 550 and not isgame:
                isgame = True

            # Покупка защиты от трактора
            if not timer and event.pos[0] >= 320 and event.pos[0] <= 380 and event.pos[1] >= 5 and event.pos[
                1] <= 45 and isgame:
                if player.lavel - 1 <= len(levels):
                    if ochki < 50:
                        start2 = time.time()
                        money = pygame.sprite.Sprite(money_sprites)
                        money.image = load_image("недостаток.png")
                        money.image = pygame.transform.scale(money.image, (600, 600))
                        money.rect = (0, 0, 600, 600)
                    else:
                        if len(tractor_pos_copy[player.lavel - 1]) == 0:
                            start3 = time.time()
                            notractor = pygame.sprite.Sprite(notractor_sprites)
                            notractor.image = load_image("конецтракторов.png")
                            notractor.image = pygame.transform.scale(notractor.image, (600, 600))
                            notractor.rect = (0, 0, 600, 600)
                        else:
                            ochki -= 50
                            start4 = time.time()
                            buy = pygame.sprite.Sprite(buy_sprites)
                            buy.image = load_image("куплено.png")
                            buy.image = pygame.transform.scale(buy.image, (600, 600))
                            buy.rect = (0, 0, 600, 600)
                            del tractor_pos_copy[player.lavel - 1][0]
                            del tractor_way_copy[player.lavel - 1][0]
                            del tractor_sek_copy[player.lavel - 1][0]

            # Завершение уровня досрочно
            if isgame and event.pos[0] >= 260 and event.pos[0] <= 445 and event.pos[1] >= 60 and event.pos[
                1] <= 110 and timer:
                timer = not timer
                start_time = pygame.time.get_ticks()
                time_limit = 20000
                tractor_sprites.empty()
                s = 0
                for block in blocks:
                    if block.__class__.__name__ == 'Obstacle':
                        s += 0
                    else:
                        s += block.type
                # Проверка на отстутствие сена
                if s == 0:
                    player.lavel += 1
                    if player.lavel - 1 == len(levels):
                        end_flag = True
                    else:
                        # Очищение поля, подготовка нового уровня, если это был непоследний
                        obstacle_sprites.empty()
                        player.start_position()
                        blocks = []
                        x, y = 0, 120
                        for row in levels[player.lavel - 1]:
                            for col in row:
                                if col == 'в':
                                    block = Obstacle(x, y)
                                else:
                                    block = Field(x, y, col)
                                blocks.append(block)
                                x += 60
                            y += 60
                            x = 0
                        ochki += ochki_list[player.lavel - 2]
                else:
                    # Иначе отрисовываем по новой этот уровень
                    timer = not timer
                    start_time = pygame.time.get_ticks()
                    time_limit = 20000
                    s = 0
                    kill = False
                    timer = not timer
                    player.start_position()
                    blocks = []
                    x, y = 0, 120
                    for row in levels[player.lavel - 1]:
                        for col in row:
                            if col == 'в':
                                block = Obstacle(x, y)
                            else:
                                block = Field(x, y, col)
                            blocks.append(block)
                            x += 60
                        y += 60
                        x = 0

            # Обработка кнопки начать заново
            if isgame and event.pos[0] >= 2 and event.pos[0] <= 187 and event.pos[1] >= 60 and event.pos[
                1] <= 110 and timer:
                obstacle_sprites.empty()
                kill = False
                tractor_sprites.empty()
                timer = not timer
                player.start_position()
                blocks = []
                x, y = 0, 120
                for row in levels[player.lavel - 1]:
                    for col in row:
                        if col == 'в':
                            block = Obstacle(x, y)
                        else:
                            block = Field(x, y, col)
                        blocks.append(block)
                        x += 60
                    y += 60
                    x = 0

            # Нажатие на кнопку "включить таймер"
            elif isgame and event.pos[0] >= 2 and event.pos[0] <= 187 and event.pos[1] >= 60 and event.pos[
                1] <= 110 and not timer:
                tractor_pos = tractor_pos_copy[:]
                tractor_way = tractor_way_copy[:]
                tractor_sek = tractor_sek_copy[:]
                kill = False
                tractor_sprites.empty()
                timer = not timer
                start_time = pygame.time.get_ticks()
                time_limit = 20000

    if timer and isgame:
        # Если идет прохождения уровня, делаем новую отрисовку
        pygame.draw.rect(screen, (255, 0, 0), (260, 60, 185, 50), 0, 3)
        font = pygame.font.Font(None, 28)
        text = font.render(f"Завершить", True, (255, 255, 255))
        screen.blit(text, (300, 75))
        # Уменьшение секунд
        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, time_limit - elapsed_time)
        seconds = remaining_time // 1000

        # Обработка смерти
        if kill:
            start = time.time()
            wasted = pygame.sprite.Sprite(kill_sprites)
            wasted.image = load_image("убит.jpg")
            wasted.image = pygame.transform.scale(wasted.image, (600, 600))
            wasted.rect = (0, 0, 600, 600)

            # Отрисовка этого уровня
            tractor_sprites.empty()
            timer = not timer
            start_time = pygame.time.get_ticks()
            time_limit = 20000
            player.start_position()
            blocks = []
            x, y = 0, 120
            for row in levels[player.lavel - 1]:
                for col in row:
                    if col == 'в':
                        block = Obstacle(x, y)
                    else:
                        block = Field(x, y, col)
                    blocks.append(block)
                    x += 60
                y += 60
                x = 0

        # Если таймер истёк делаем проверку на наличие сена
        if seconds == 0:
            timer = not timer
            start_time = pygame.time.get_ticks()
            time_limit = 20000
            s = 0
            for block in blocks:
                if block.__class__.__name__ == 'Obstacle':
                    s += 0
                else:
                    s += block.type
            if s == 0:
                player.lavel += 1
                if player.lavel - 1 == len(levels):
                    end_flag = True
                else:
                    obstacle_sprites.empty()
                    player.start_position()
                    blocks = []
                    x, y = 0, 120
                    for row in levels[player.lavel - 1]:
                        for col in row:
                            if col == 'в':
                                block = Obstacle(x, y)
                            else:
                                block = Field(x, y, col)
                            blocks.append(block)
                            x += 60
                        y += 60
                        x = 0
                    ochki += ochki_list[player.lavel - 2]
            else:
                player.start_position()
                blocks = []
                x, y = 0, 120
                for row in levels[player.lavel - 1]:
                    for col in row:
                        if col == 'в':
                            block = Obstacle(x, y)
                        else:
                            block = Field(x, y, col)
                        blocks.append(block)
                        x += 60
                    y += 60
                    x = 0
        # Если это непоследний уровень, то переходим на следующий по тракторам
        if player.lavel - 1 < len(levels):
            if seconds in tractor_sek[player.lavel - 1]:
                index = tractor_sek[player.lavel - 1].index(seconds)
                tractor = Tractor(tractor_pos[player.lavel - 1][index], tractor_way[player.lavel - 1][index])
                tractor_sek[player.lavel - 1] = tractor_sek[player.lavel - 1][:index] + tractor_sek[player.lavel - 1][
                                                                                        index + 1:]
                tractor_pos[player.lavel - 1] = tractor_pos[player.lavel - 1][:index] + tractor_pos[player.lavel - 1][
                                                                                        index + 1:]
                tractor_way[player.lavel - 1] = tractor_way[player.lavel - 1][:index] + tractor_way[player.lavel - 1][

                                                                                        index + 1:]

        # Отрисовка количества оставшихся секунд
        font = pygame.font.Font(None, 40)
        text = font.render(f"{seconds} сек.", True, (255, 255, 255))
        screen.blit(text, (490, 20))

    # Отрисовка текста
    elif isgame:
        font = pygame.font.Font(None, 40)
        text = font.render(f"20 сек.", True, (255, 255, 255))
        screen.blit(text, (490, 20))
    pygame.draw.rect(screen, (255, 0, 0), (2, 60, 185, 50), 0, 3)
    if not timer and isgame:
        font = pygame.font.Font(None, 28)
        text = font.render(f"Включить таймер", True, (255, 255, 255))
        screen.blit(text, (10, 75))
    elif isgame:
        font = pygame.font.Font(None, 28)
        text = font.render(f"Заново", True, (255, 255, 255))
        screen.blit(text, (65, 75))
        x, y = 0, 120

    # Отображение всех спрайтов
    all_sprites.draw(screen)
    obstacle_sprites.draw(screen)
    hero_sprites.draw(screen)
    hero_sprites.update(direction)
    tractor_sprites.draw(screen)

    # Подсчёт всех таймеров картинок
    if time.time() - start < 2:
        kill_sprites.draw(screen)
    else:
        kill_sprites.empty()

    if time.time() - start2 < 2:
        money_sprites.draw(screen)

    if time.time() - start3 < 2:
        notractor_sprites.draw(screen)

    if time.time() - start4 < 2:
        buy_sprites.draw(screen)

    # Отрисовка стартового окна
    if not isgame:
        bg_sprites.draw(screen)
        pygame.draw.rect(screen, (255, 0, 0), (350, 500, 185, 50), 0, 3)
        font = pygame.font.Font(None, 50)
        text = font.render(f"Играть", True, (255, 255, 255))
        screen.blit(text, (390, 510))

    # Если конец игры, отрисовка финального окна
    if end_flag:
        end_sprites.draw(screen)

    clock.tick(30)
    pygame.display.flip()
pygame.quit()
