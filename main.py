import pygame
import math
import sys
import random

# ============================================================
# USTAWIENIA GRY
# ============================================================

pygame.init()

WIDTH = 1280
HEIGHT = 720
RENDER_WIDTH = 640
RENDER_SCALE = WIDTH // RENDER_WIDTH
PLAYER_RADIUS = 0.40
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RETRO FPS - Kompaktowy HUD w Lewym Dolnym Rogu")

clock = pygame.time.Clock()

# ============================================================
# KOLORY
# ============================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 65)
DARK_GRAY = (30, 30, 35)
RED = (200, 40, 40)
CEILING_COLOR = (35, 35, 42)
FLOOR_COLOR = (65, 58, 50)

# ============================================================
# WCZYTANIE PORTRETÓW
# ============================================================
 
def load_portrait(path):
    try:
        # convert_alpha() zachowuje przezroczystość tła portretu PNG
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"Nie udało się wczytać portretu z ścieżki '{path}': {e}")
        # Awaryjny zastępczy awatar, jeśli plik nie istnieje
        surf = pygame.Surface((80, 80))
        surf.fill((120, 120, 130))
        pygame.draw.circle(surf, (200, 200, 200), (40, 30), 20)
        return surf

natan_portraits = {
    "full": load_portrait("assets/portraits/natan_100.png"),
    "high": load_portrait("assets/portraits/natan_75.png"),
    "mid": load_portrait("assets/portraits/natan_45.png"),
    "low": load_portrait("assets/portraits/natan_low.png")
}

jan_portraits = {
    "full": load_portrait("assets/portraits/jan_100.png"),
    "high": load_portrait("assets/portraits/jan_75.png"),
    "mid": load_portrait("assets/portraits/jan_45.png"),
    "low": load_portrait("assets/portraits/jan_low.png")
}

wika_portraits = {
    "full": load_portrait("assets/portraits/wika_100.png"),
    "high": load_portrait("assets/portraits/wika_75.png"),
    "mid": load_portrait("assets/portraits/wika_45.png"),
    "low": load_portrait("assets/portraits/wika_low.png")
}
# ============================================================
# TEKSTURY ŚCIAN, DRZWI I BRONI
# ============================================================
    
def load_texture(path):
    try:
        return pygame.image.load(path).convert()
    except Exception:
        surf = pygame.Surface((64, 64))
        surf.fill((100, 100, 100))
        pygame.draw.rect(surf, (200, 200, 200), (0, 0, 32, 32))
        pygame.draw.rect(surf, (200, 200, 200), (32, 32, 32, 32))
        return surf

def load_weapon_texture(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"Nie udało się wczytać grafiki broni z ścieżki '{path}': {e}")
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        surf.fill((150, 50, 50, 128))
        return surf


def load_enemy_sprite(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"Nie udało się wczytać grafiki przeciwnika {path}: {e}")

        # Awaryjna grafika, jeśli pliku brakuje.
        surf = pygame.Surface((100, 150), pygame.SRCALPHA)
        pygame.draw.rect(surf, (180, 30, 30), (10, 10, 80, 140))
        return surf


brute_sprites = {
    "walk": [
        load_enemy_sprite("assets/enemies/brute_walk1.png"),
        load_enemy_sprite("assets/enemies/brute_walk2.png")
    ],

    "attack": load_enemy_sprite("assets/enemies/brute_attack.png"),

    "dead": load_enemy_sprite("assets/enemies/brute_dead.png")
}


def load_portrait(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        surf = pygame.Surface((70, 70))
        surf.fill((120, 120, 130))
        pygame.draw.circle(surf, (200, 200, 200), (35, 25), 18)
        return surf

wall_textures = {
    "1": load_texture("assets/textures/wall_brick.png"),
    "2": load_texture("assets/textures/wall_stone.png"),
    "3": load_texture("assets/textures/wall_metal.png"),
    "D": load_texture("assets/textures/door.png")
}

# Wczytanie modeli broni
shotgun_idle = load_weapon_texture("assets/weapons/shotgun.png")
shotgun_fire = load_weapon_texture("assets/weapons/shotgun_shoot.png")


mp40_idle = load_weapon_texture("assets/weapons/mp40.png")
mp40_fire = load_weapon_texture("assets/weapons/mp40_shoot.png")


glock_idle = load_weapon_texture("assets/weapons/glock.png")
glock_fire = load_weapon_texture("assets/weapons/glock_shoot.png")

# Wczytanie portretów postaci
portraits = {
    1: load_portrait("assets/portraits/natan.png"),
    2: load_portrait("assets/portraits/jan.png"),
    3: load_portrait("assets/portraits/wika.png")
}


# ============================================================
# MAPA POZIOMU ("D" OZNACZA DRZWI)
# ============================================================


WORLD_MAP = [
    "11111111111111111111111111111111111111111111111111",
    "10000000010000000001000000000100000000010000000001",
    "1000000001000000000D000000000100000000010000000001",
    "10022200010000000001002222000100000000010000000001",
    "100000000D0000000001000000000100000000010000000001",
    "100000000100000000010000000001000333000D0000000001",
    "10000000010000000001000000000D00000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "111D11111111111D11111111D11111111111D11111D1111111",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "100000000D0003330001000000000100000000010022220001",
    "100000000100000000010033330001000000000D0000000001",
    "10030000010020000001000000000100200000010003330001",
    "10030000010020000001000000000D00200000010000000001",
    "1003000001002000000D000000000100200000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "11111D11111111D11111111111D11111D1111111111D111111",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10002220010000000001002000000100000000010003330001",
    "10000000010003330001002000000D00022200010000000001",
    "100000000100000000010020000001000000000D0000000001",
    "1000000001000000000D002000000100000000010000000001",
    "100000000D0000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "1111D11111111111D11111D1111111111D11111111111D1111",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "100200000100000000010002220001000300000D0000000001",
    "1002000001000333300D000000000100030000010022220001",
    "10020000010000000001000000000D00030000010000000001",
    "100200000D0000000001000000000100030000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "111111D11111D1111111111D11111111111D11111111D11111",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "10003330010000000001003333000D00000000010030000001",
    "100000000D0002220001000000000100222200010030000001",
    "1000000001000000000D000000000100000000010030000001",
    "10000000010000000001000000000100000000010030000001",
    "100000000100000000010000000001000000000D0000000001",
    "10000000010000000001000000000100000000010000000001",
    "10000000010000000001000000000100000000010000000001",
    "11111111111111111111111111111111111111111111111111"
]


MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)

doors = {}
for y, row in enumerate(WORLD_MAP):
    for x, cell in enumerate(row):
        if cell == "D":
            doors[(x, y)] = {
                "progress": 0.0,
                "timer": 0.0,
                "status": "closed"
            }

DOOR_SPEED = 2.0
AUTO_CLOSE_TIME = 3.0



# ============================================================
# SYSTEM POMIESZCZEŃ
# ============================================================

# Każde pomieszczenie otrzymuje własny identyfikator.
# Zamknięte drzwi oddzielają pomieszczenia.

room_ids = [
    [-1 for _ in range(MAP_WIDTH)]
    for _ in range(MAP_HEIGHT)
]

room_counter = 0

for start_y in range(MAP_HEIGHT):
    for start_x in range(MAP_WIDTH):

        if WORLD_MAP[start_y][start_x] != "0":
            continue

        if room_ids[start_y][start_x] != -1:
            continue

        queue = [(start_x, start_y)]
        room_ids[start_y][start_x] = room_counter

        while queue:
            current_x, current_y = queue.pop(0)

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx = current_x + dx
                ny = current_y + dy

                if not (0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT):
                    continue

                if WORLD_MAP[ny][nx] != "0":
                    continue

                if room_ids[ny][nx] != -1:
                    continue

                room_ids[ny][nx] = room_counter
                queue.append((nx, ny))

        room_counter += 1


def get_room_id(x, y):
    mx = int(x)
    my = int(y)

    if 0 <= mx < MAP_WIDTH and 0 <= my < MAP_HEIGHT:
        return room_ids[my][mx]

    return None


# ============================================================
# KONFIGURACJA RODZAJÓW WROGÓW
# ============================================================

ENEMY_TYPES = {
    "shooter": {
        "health": 5,
        "speed": 1.1,
        "damage": 5,
        "attack_range": 8.0,
        "attack_cooldown": 1.5
    },

    "brute": {
        "health": 12,
        "speed": 1.45,
        "damage": 18,
        "attack_range": 0.85,
        "attack_cooldown": 1.2
    },

    "dog": {
        "health": 4,
        "speed": 3,
        "damage": 8,
        "attack_range": 0.65,
        "attack_cooldown": 0.7
    }
}


def create_enemy(x, y, enemy_type):
    config = ENEMY_TYPES[enemy_type]

    return {
        "x": x,
        "y": y,
        "type": enemy_type,
        "health": config["health"],
        "max_health": config["health"],
        "state": "idle",
        "room_id": get_room_id(x, y),
        "attack_timer": random.uniform(0.5, 1.5),
        "zigzag_phase": random.uniform(0, math.pi * 2),

        # Animacja przeciwnika
        "anim_frame": 0,
        "anim_timer": 0.0,
        "anim_state": "walk",
        "anim_state_timer": 0.0
    }


# ============================================================
# ROZMIESZCZENIE WROGÓW
# ============================================================

enemies = [
    create_enemy(4.5, 2.5, "shooter"),
    create_enemy(15.5, 2.5, "brute"),
    create_enemy(17.5, 2.5, "dog"),
    create_enemy(14.5, 34.5, "shooter"),
    create_enemy(44.5, 44.5, "brute")
]

ENEMY_DETECT_DIST = 0.0

# Pomieszczenie, w którym aktualnie znajduje się gracz.
player_room_id = None



# ============================================================
# SYSTEM BRONI I POSTACI
# ============================================================

weapons = {
    1: {
        "name": "Dubeltówka Natana",
        "max_ammo": 8,
        "ammo": 8,
        "fire_rate": 0.5,
        "reload_time": 1.5,
        "cooldown": 0.0,
        "reloading": False,
        "reload_timer": 0.0,
        "damage": 3,
        "range": 4.0
    },
    2: {
        "name": "MP40 Jana",
        "max_ammo": 32,
        "ammo": 32,
        "fire_rate": 0.12,
        "reload_time": 2.0,
        "cooldown": 0.0,
        "reloading": False,
        "reload_timer": 0.0,
        "damage": 1,
        "range": 12.0
    },
    3: {
        "name": "2 Glocki Wiktorii",
        "max_ammo": 20,
        "ammo": 20,
        "fire_rate": 0.2,
        "reload_time": 1.2,
        "cooldown": 0.0,
        "reloading": False,
        "reload_timer": 0.0,
        "damage": 2,
        "range": 8.0
    }
}

selected_character = {
    "id": 1,
    "name": "Natan",
    "weapon_id": 1
}

player_health = 100
current_weapon_id = 1
is_shooting_flash = 0


# ============================================================
# GRACZ
# ============================================================

player_x = 1.5
player_y = 1.5
player_angle = 0.0

MOVE_SPEED = 3.0
ROTATION_SPEED = 2.0
MOUSE_SENSITIVITY = 0.003

# ============================================================
# SYSTEM SPRINTU
# ============================================================

SPRINT_MULTIPLIER = 1.6

SPRINT_MAX_ENERGY = 5.0
SPRINT_REGEN_TIME = 10.0

SPRINT_DRAIN_RATE = 1.5
SPRINT_REGEN_RATE = SPRINT_MAX_ENERGY / SPRINT_REGEN_TIME

sprint_energy = SPRINT_MAX_ENERGY
sprint_active = False
# ============================================================
# EKRAN WYBORU POSTACI
# ============================================================

def character_select_screen():
    global selected_character, current_weapon_id
    selecting = True

    font_title = pygame.font.SysFont(None, 60)
    font_option = pygame.font.SysFont(None, 40)
    font_info = pygame.font.SysFont(None, 24)

    while selecting:
        screen.fill(DARK_GRAY)

        title_surf = font_title.render("WYBIERZ SWOJĄ POSTAĆ", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 100))

        chars = [
            ("1. Natan (Dubeltówka - Potężny bliski zasięg)", 1, (200, 80, 80)),
            ("2. Jan (MP40 - Szybki karabin maszynowy)", 2, (80, 200, 80)),
            ("3. Wiktoria (2 Glocki - Zbalansowany duet)", 3, (80, 150, 200))
        ]

        for idx, (text, char_id, color) in enumerate(chars):
            opt_surf = font_option.render(text, True, color)
            screen.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, 280 + idx * 80))

        hint_surf = font_info.render("Naciśnij 1, 2 lub 3 na klawiaturze, aby rozpocząć grę", True, (180, 180, 180))
        screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, 580))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_1:
                    selected_character = {"id": 1, "name": "Natan", "weapon_id": 1}
                    selecting = False
                elif event.key == pygame.K_2:
                    selected_character = {"id": 2, "name": "Jan", "weapon_id": 2}
                    selecting = False
                elif event.key == pygame.K_3:
                    selected_character = {"id": 3, "name": "Wiktoria", "weapon_id": 3}
                    selecting = False

        clock.tick(FPS)

    current_weapon_id = selected_character["weapon_id"]
    print(f"Wybrano postać: {selected_character['name']} z bronią ID: {current_weapon_id}")


# ============================================================
# KOLIZJE
# ============================================================

def is_wall(x, y):
    map_x = int(x)
    map_y = int(y)

    if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
        return True

    cell = WORLD_MAP[map_y][map_x]
    if cell in ["1", "2", "3"]:
        return True
    
    if cell == "D":
        door_data = doors.get((map_x, map_y))
        if door_data and door_data["progress"] > 0.8:
            return False
        return True

    return False


# ============================================================
# AKTUALIZACJA DRZWI I WROGÓW
# ============================================================

def update_doors(dt):
    for pos, door in doors.items():
        mx, my = pos
        player_on_door = (int(player_x) == mx and int(player_y) == my)

        if door["status"] == "opening":
            door["progress"] += DOOR_SPEED * dt
            if door["progress"] >= 1.0:
                door["progress"] = 1.0
                door["status"] = "open"
                door["timer"] = AUTO_CLOSE_TIME

        elif door["status"] == "open":
            if player_on_door:
                door["timer"] = AUTO_CLOSE_TIME
            else:
                door["timer"] -= dt
                if door["timer"] <= 0:
                    door["status"] = "closing"

        elif door["status"] == "closing":
            if player_on_door:
                door["status"] = "opening"
            else:
                door["progress"] -= DOOR_SPEED * dt
                if door["progress"] <= 0.0:
                    door["progress"] = 0.0
                    door["status"] = "closed"


def enemy_has_line_of_sight(enemy):
    dx = player_x - enemy["x"]
    dy = player_y - enemy["y"]

    dist = math.sqrt(dx ** 2 + dy ** 2)

    if dist <= 0:
        return True

    steps = max(1, int(dist * 10))

    for i in range(1, steps):
        check_x = enemy["x"] + dx * i / steps
        check_y = enemy["y"] + dy * i / steps

        if is_wall(check_x, check_y):
            return False

    return True


def move_enemy(enemy, move_x, move_y):
    new_x = enemy["x"] + move_x
    new_y = enemy["y"] + move_y

    # Kolizje z mapą
    if not is_wall(new_x, enemy["y"]):
        enemy["x"] = new_x

    if not is_wall(enemy["x"], new_y):
        enemy["y"] = new_y





def update_enemies(dt):

    global player_health, player_room_id

    # Aktualny pokój gracza.
    player_room_id = get_room_id(player_x, player_y)

    for enemy in enemies:

        enemy_type = enemy["type"]
        config = ENEMY_TYPES[enemy_type]

        # ====================================================
        # OBSŁUGA ŚMIERCI PRZECIWNIKÓW
        # ====================================================

        if enemy["health"] <= 0:

            if enemy_type == "brute":
                enemy["anim_state"] = "dead"

            continue

        # ====================================================
        # ANIMACJA OSIŁKA
        # ====================================================

        if enemy_type == "brute":

            # Jeżeli trwa animacja ataku, odliczamy jej czas.
            if enemy["anim_state"] == "attack":

                enemy["anim_state_timer"] -= dt

                if enemy["anim_state_timer"] <= 0:

                    enemy["anim_state"] = "walk"
                    enemy["anim_timer"] = 0.0
                    enemy["anim_frame"] = 0

            else:

                # Animacja chodzenia.
                enemy["anim_timer"] += dt

                if enemy["anim_timer"] >= 0.25:

                    enemy["anim_timer"] = 0.0
                    enemy["anim_frame"] = 1 - enemy["anim_frame"]

        # ====================================================
        # ODLICZANIE CZASU ATAKU
        # ====================================================

        enemy["attack_timer"] -= dt

        # ====================================================
        # AKTYWOWANIE PRZECIWNIKA
        # ====================================================

        # Przeciwnik pozostaje nieaktywny, dopóki gracz
        # nie wejdzie do pomieszczenia, w którym się znajduje.

        if enemy["state"] == "idle":

            if player_room_id == enemy["room_id"]:

                enemy["state"] = "chasing"

                print(
                    f"Aktywowano przeciwnika: {enemy_type}"
                )

            else:
                continue

        # ====================================================
        # OBLICZANIE ODLEGŁOŚCI OD GRACZA
        # ====================================================

        dx = player_x - enemy["x"]
        dy = player_y - enemy["y"]

        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist <= 0.001:
            continue

        dir_x = dx / dist
        dir_y = dy / dist

        # ====================================================
        # 1. STRZELEC
        # ====================================================

        if enemy_type == "shooter":

            # Strzelec stara się utrzymywać średni dystans.
            preferred_distance = 4.5

            if dist > preferred_distance + 0.7:

                move_enemy(
                    enemy,
                    dir_x * config["speed"] * dt,
                    dir_y * config["speed"] * dt
                )

            elif dist < preferred_distance - 0.7:

                move_enemy(
                    enemy,
                    -dir_x * config["speed"] * dt,
                    -dir_y * config["speed"] * dt
                )

            else:

                # Poruszanie się na boki.
                enemy["zigzag_phase"] += dt * 2.0

                strafe = math.sin(
                    enemy["zigzag_phase"]
                )

                move_x = -dir_y * strafe
                move_y = dir_x * strafe

                move_enemy(
                    enemy,
                    move_x * config["speed"] * 0.65 * dt,
                    move_y * config["speed"] * 0.65 * dt
                )

            # Strzał tylko wtedy, gdy przeciwnik widzi gracza.
            if (
                2.0 <= dist <= config["attack_range"]
                and enemy_has_line_of_sight(enemy)
                and enemy["attack_timer"] <= 0
            ):

                player_health = max(
                    0,
                    player_health - config["damage"]
                )

                enemy["attack_timer"] = config["attack_cooldown"]

                print("Strzelec trafił gracza!")

        # ====================================================
        # 2. OSIŁEK
        # ====================================================

        elif enemy_type == "brute":

            # Osiłek nie może wejść w model gracza.
            stop_distance = 0.95

            if dist > stop_distance:

                move_x = dir_x * config["speed"] * dt
                move_y = dir_y * config["speed"] * dt

                move_enemy(
                    enemy,
                    move_x,
                    move_y
                )

            else:

                # Atak wręcz.
                if enemy["attack_timer"] <= 0:

                    player_health = max(
                        0,
                        player_health - config["damage"]
                    )

                    enemy["attack_timer"] = config["attack_cooldown"]

                    # Uruchomienie animacji ataku.
                    enemy["anim_state"] = "attack"
                    enemy["anim_state_timer"] = 0.45

                    print("Osiłek uderzył gracza!")

        # ====================================================
        # 3. PIES
        # ====================================================

        elif enemy_type == "dog":

            # Pies zatrzymuje się bardzo blisko gracza,
            # ale nie wchodzi bezpośrednio w jego pozycję.
            stop_distance = 0.75

            if dist > stop_distance:

                enemy["zigzag_phase"] += dt * 2.5

                # Delikatny ruch na boki.
                zigzag = (
                    math.sin(enemy["zigzag_phase"]) * 0.35
                )

                move_x = dir_x - dir_y * zigzag
                move_y = dir_y + dir_x * zigzag

                # Normalizacja kierunku.
                length = math.sqrt(
                    move_x ** 2 + move_y ** 2
                )

                if length > 0:

                    move_x /= length
                    move_y /= length

                move_enemy(
                    enemy,
                    move_x * config["speed"] * dt,
                    move_y * config["speed"] * dt
                )

            else:

                # Ugryzienie z bardzo bliskiej odległości.
                if enemy["attack_timer"] <= 0:

                    player_health = max(
                        0,
                        player_health - config["damage"]
                    )

                    enemy["attack_timer"] = config["attack_cooldown"]

                    print("Pies ugryzł gracza!")


# ============================================================
# RAYCASTING & RENDEROWANIE ŚWIATA
# ============================================================


def render_world():

    # ============================================================
    # TŁO – NIEBO I PODŁOGA
    # ============================================================

    screen.fill(CEILING_COLOR)

    pygame.draw.rect(
        screen,
        FLOOR_COLOR,
        (0, HEIGHT // 2, WIDTH, HEIGHT // 2)
    )

    dir_x = math.cos(player_angle)
    dir_y = math.sin(player_angle)

    plane_length = 0.66
    plane_x = -dir_y * plane_length
    plane_y = dir_x * plane_length

    z_buffer = [float("inf")] * RENDER_WIDTH

    # ============================================================
    # RENDEROWANIE ŚCIAN
    # ============================================================

    for x in range(RENDER_WIDTH):

        camera_x = 2.0 * x / RENDER_WIDTH - 1.0

        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        map_x = int(player_x)
        map_y = int(player_y)

        delta_dist_x = (
            abs(1 / ray_dir_x)
            if abs(ray_dir_x) > 1e-7
            else float("inf")
        )

        delta_dist_y = (
            abs(1 / ray_dir_y)
            if abs(ray_dir_y) > 1e-7
            else float("inf")
        )

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (player_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - player_x) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (player_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - player_y) * delta_dist_y

        hit = False
        side = 0

        while not hit:

            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if (
                map_x < 0
                or map_x >= MAP_WIDTH
                or map_y < 0
                or map_y >= MAP_HEIGHT
            ):
                hit = True
                break

            cell = WORLD_MAP[map_y][map_x]

            if cell != "0":

                if cell == "D":

                    door_data = doors.get((map_x, map_y))

                    if door_data and door_data["progress"] >= 1.0:
                        continue

                hit = True

        if (
            map_x < 0
            or map_x >= MAP_WIDTH
            or map_y < 0
            or map_y >= MAP_HEIGHT
        ):
            continue

        if side == 0:
            perp_wall_dist = (
                map_x - player_x + (1 - step_x) / 2
            ) / ray_dir_x
        else:
            perp_wall_dist = (
                map_y - player_y + (1 - step_y) / 2
            ) / ray_dir_y

        perp_wall_dist = max(0.05, perp_wall_dist)

        z_buffer[x] = perp_wall_dist

        line_height = int(HEIGHT / perp_wall_dist)

        draw_start = max(
            0,
            HEIGHT // 2 - line_height // 2
        )

        draw_end = min(
            HEIGHT,
            HEIGHT // 2 + line_height // 2
        )

        wall_type = WORLD_MAP[map_y][map_x]

        texture = wall_textures.get(
            wall_type,
            wall_textures["1"]
        )

        texture_width = texture.get_width()
        texture_height = texture.get_height()

        if side == 0:
            wall_x = player_y + perp_wall_dist * ray_dir_y
        else:
            wall_x = player_x + perp_wall_dist * ray_dir_x

        wall_x -= math.floor(wall_x)

        if wall_type == "D":

            door_data = doors.get((map_x, map_y))

            open_progress = (
                door_data["progress"]
                if door_data
                else 0.0
            )

            wall_x = (wall_x + open_progress) % 1.0

        texture_x = int(wall_x * texture_width)

        texture_x = max(
            0,
            min(texture_width - 1, texture_x)
        )

        if side == 0 and ray_dir_x > 0:
            texture_x = texture_width - texture_x - 1

        if side == 1 and ray_dir_y < 0:
            texture_x = texture_width - texture_x - 1

        texture_column = texture.subsurface(
            (texture_x, 0, 1, texture_height)
        )

        full_wall_surface = pygame.transform.scale(
            texture_column,
            (RENDER_SCALE, line_height)
        )

        wall_top = HEIGHT // 2 - line_height // 2

        visible_top = draw_start - wall_top
        visible_height = draw_end - draw_start

        if visible_height > 0:

            wall_surface = full_wall_surface.subsurface(
                (
                    0,
                    max(0, visible_top),
                    RENDER_SCALE,
                    visible_height
                )
            )

            brightness = max(
                35,
                min(
                    255,
                    int(255 / (1 + perp_wall_dist * 0.18))
                )
            )

            if side == 1:
                brightness = int(brightness * 0.7)

            wall_surface.fill(
                (brightness, brightness, brightness),
                special_flags=pygame.BLEND_RGB_MULT
            )

            screen.blit(
                wall_surface,
                (x * RENDER_SCALE, draw_start)
            )

    # ============================================================
    # RENDEROWANIE WROGÓW
    # ============================================================

    sorted_enemies = sorted(
        enemies,
        key=lambda e: (
            (player_x - e["x"]) ** 2
            + (player_y - e["y"]) ** 2
        ),
        reverse=True
    )

    inv_det = 1.0 / (
        plane_x * dir_y - dir_x * plane_y
    )

    for enemy in sorted_enemies:

        sprite_x = enemy["x"] - player_x
        sprite_y = enemy["y"] - player_y

        transform_x = inv_det * (
            dir_y * sprite_x - dir_x * sprite_y
        )

        transform_y = inv_det * (
            -plane_y * sprite_x + plane_x * sprite_y
        )

        if transform_y <= 0.2:
            continue

        screen_x = int(
            (WIDTH / 2) * (
                1.0 + transform_x / transform_y
            )
        )

        # ========================================================
        # OSIŁEK – GRAFIKI PNG
        # ========================================================

        if enemy["type"] == "brute":

            # Wybór odpowiedniej klatki animacji.
            if enemy["health"] <= 0:

                brute_image = brute_sprites["dead"]

            elif enemy["anim_state"] == "attack":

                brute_image = brute_sprites["attack"]

            else:

                brute_image = brute_sprites["walk"][
                    enemy["anim_frame"]
                ]

            original_width = brute_image.get_width()
            original_height = brute_image.get_height()

            if original_height <= 0:
                continue


            if enemy["health"] <= 0:
                 sprite_height = max(
                    1,
                int(HEIGHT / transform_y * 0.30)
                )
                 
            else:
                sprite_height = max(
                    1,
                    int(HEIGHT / transform_y * 1.25)
                )

            # Zachowanie proporcji oryginalnej grafiki.
            aspect_ratio = original_width / original_height

            sprite_width = max(
                1,
                int(sprite_height * aspect_ratio)
            )

            if enemy["health"] <= 0:
                draw_start_y = HEIGHT // 2 + int(sprite_height * 0.35)

            else:
                draw_start_y = HEIGHT // 2 - sprite_height // 2

            draw_start_x = screen_x - sprite_width // 2
            
            # Skalowanie grafiki.
            scaled_sprite = pygame.transform.scale(
                brute_image,
                (sprite_width, sprite_height)
            )

            # Oświetlenie zależne od odległości.
            brightness = max(
                35,
                min(
                    255,
                    int(255 / (1 + transform_y * 0.2))
                )
            )

            # Przyciemnienie grafiki bez usuwania przezroczystości.
            scaled_sprite.fill(
                (brightness, brightness, brightness, 255),
                special_flags=pygame.BLEND_RGBA_MULT
            )

            # Renderowanie kolumnami z uwzględnieniem Z-buffera.
            for stripe in range(
                max(0, draw_start_x),
                min(WIDTH, draw_start_x + sprite_width)
            ):

                render_stripe_idx = stripe // RENDER_SCALE

                if not (
                    0 <= render_stripe_idx < RENDER_WIDTH
                ):
                    continue

                # Sprawdzenie, czy ściana nie zasłania przeciwnika.
                if transform_y < z_buffer[render_stripe_idx]:

                    source_x = stripe - draw_start_x

                    sprite_column = scaled_sprite.subsurface(
                        (
                            source_x,
                            0,
                            1,
                            sprite_height
                        )
                    )

                    screen.blit(
                        sprite_column,
                        (stripe, draw_start_y)
                    )

            # ====================================================
            # PASEK ŻYCIA OSIŁKA
            # ====================================================

            if enemy["health"] > 0 and transform_y < 8.0:

                bar_width = max(
                    8,
                    int(sprite_width * 0.7)
                )

                bar_height = max(
                    2,
                    int(sprite_height * 0.035)
                )

                bar_x = screen_x - bar_width // 2
                bar_y = draw_start_y - bar_height - 5

                health_ratio = max(
                    0,
                    enemy["health"] / enemy["max_health"]
                )

                pygame.draw.rect(
                    screen,
                    (35, 15, 15),
                    (
                        bar_x,
                        bar_y,
                        bar_width,
                        bar_height
                    )
                )

                pygame.draw.rect(
                    screen,
                    (40, 210, 55),
                    (
                        bar_x,
                        bar_y,
                        int(bar_width * health_ratio),
                        bar_height
                    )
                )

        # ========================================================
        # STRZELEC I PIES – DOTYCHCZASOWE SYLWETKI
        # ========================================================

        elif enemy["type"] == "shooter":

            if enemy["health"] <= 0:
                continue

            sprite_height = abs(
                int(HEIGHT / transform_y)
            )

            sprite_width = int(
                sprite_height * 0.55
            )

            base_color = (220, 115, 30)

        elif enemy["type"] == "dog":

            if enemy["health"] <= 0:
                continue

            sprite_height = abs(
                int(HEIGHT / transform_y * 0.60)
            )

            sprite_width = int(
                sprite_height * 0.90
            )

            base_color = (190, 150, 65)

        else:
            continue

        # ========================================================
        # RENDEROWANIE SYLWETEK STRZELCA I PSA
        # ========================================================

        if enemy["type"] in ("shooter", "dog"):

            draw_start_y = max(
                0,
                HEIGHT // 2 - sprite_height // 2
            )

            draw_end_y = min(
                HEIGHT,
                HEIGHT // 2 + sprite_height // 2
            )

            draw_start_x = max(
                0,
                screen_x - sprite_width // 2
            )

            draw_end_x = min(
                WIDTH,
                screen_x + sprite_width // 2
            )

            brightness = max(
                35,
                min(
                    255,
                    int(255 / (1 + transform_y * 0.2))
                )
            )

            enemy_color = (
                int(base_color[0] * brightness / 255),
                int(base_color[1] * brightness / 255),
                int(base_color[2] * brightness / 255)
            )

            for stripe in range(
                draw_start_x,
                draw_end_x
            ):

                render_stripe_idx = stripe // RENDER_SCALE

                if not (
                    0 <= render_stripe_idx < RENDER_WIDTH
                ):
                    continue

                if transform_y < z_buffer[render_stripe_idx]:

                    pygame.draw.line(
                        screen,
                        enemy_color,
                        (stripe, draw_start_y),
                        (stripe, draw_end_y)
                    )

            # Pasek życia.
            if transform_y < 8.0:

                bar_width = max(
                    8,
                    int(sprite_width * 0.7)
                )

                bar_height = max(
                    2,
                    int(sprite_height * 0.035)
                )

                bar_x = screen_x - bar_width // 2
                bar_y = draw_start_y - bar_height - 5

                health_ratio = max(
                    0,
                    enemy["health"] / enemy["max_health"]
                )

                pygame.draw.rect(
                    screen,
                    (35, 15, 15),
                    (
                        bar_x,
                        bar_y,
                        bar_width,
                        bar_height
                    )
                )

                pygame.draw.rect(
                    screen,
                    (40, 210, 55),
                    (
                        bar_x,
                        bar_y,
                        int(bar_width * health_ratio),
                        bar_height
                    )
                )



# ============================================================
# RENDEROWANIE BRONI NA EKRANIE
# ============================================================


def draw_weapon():
    global is_shooting_flash

    weapon = weapons[current_weapon_id]

    if weapon["reloading"]:
        return

    center_x = WIDTH // 2
    base_y = HEIGHT

    # ========================================================
    # NATAN - DUBELTÓWKA
    # ========================================================
    if current_weapon_id == 1:
        scale_factor = 1.2

        current_sprite = (
            shotgun_fire if is_shooting_flash > 0
            else shotgun_idle
        )

        new_width = int(current_sprite.get_width() * scale_factor)
        new_height = int(current_sprite.get_height() * scale_factor)

        scaled_gun = pygame.transform.smoothscale(
            current_sprite, (new_width, new_height)
        )

        gun_x = center_x - new_width // 2
        gun_y = base_y - new_height + 20

        screen.blit(scaled_gun, (gun_x, gun_y))

    # ========================================================
    # JAN - MP40
    # ========================================================
    elif current_weapon_id == 2:
        scale_factor = 1.0

        current_sprite = (
            mp40_fire if is_shooting_flash > 0
            else mp40_idle
        )

        new_width = int(current_sprite.get_width() * scale_factor)
        new_height = int(current_sprite.get_height() * scale_factor)

        scaled_gun = pygame.transform.smoothscale(
            current_sprite, (new_width, new_height)
        )

        gun_x = center_x - new_width // 2
        gun_y = base_y - new_height + 10

        screen.blit(scaled_gun, (gun_x, gun_y))

    # ========================================================
    # WIKTORIA - DWA GLOCKI
    # ========================================================
    elif current_weapon_id == 3:
        gun_img = glock_fire if is_shooting_flash > 0 else glock_idle

        scale_factor = 0.85
        new_width = int(gun_img.get_width() * scale_factor)
        new_height = int(gun_img.get_height() * scale_factor)

        scaled_gun = pygame.transform.scale(
            gun_img,
            (new_width, new_height)
        )

        gun_x = center_x - new_width // 2
        gun_y = base_y - new_height + 10

        screen.blit(scaled_gun, (gun_x, gun_y))

# ============================================================
# KOMPAKTOWY HUD W LEWYM DOLNYM ROGU (WOLF 3D STYLE)
# ============================================================

font_hud = pygame.font.SysFont(None, 32)
font_small = pygame.font.SysFont(None, 18)

def draw_wolfenstein_hud():
    # Pozycja w lewym dolnym rogu
    panel_x = 0
    panel_y = HEIGHT - 100
    panel_w = 335
    panel_h = 100

    # Tło panelu w stylu retro
    pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(screen, DARK_GRAY, (panel_x + 4, panel_y + 4, panel_w - 8, panel_h - 8))
    
    # Ramki 3D (efekt wklęsłości/wypukłości)
    pygame.draw.line(screen, (180, 180, 180), (panel_x, panel_y), (panel_x + panel_w, panel_y), 3)
    pygame.draw.line(screen, (180, 180, 180), (panel_x, panel_y), (panel_x, panel_y + panel_h), 3)
    pygame.draw.line(screen, (20, 20, 20), (panel_x, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h), 3)
    pygame.draw.line(screen, (20, 20, 20), (panel_x + panel_w, panel_y), (panel_x + panel_w, panel_y + panel_h), 3)

    # Większy portret dosunięty do lewego górnego rogu wnętrza panelu (bez luzów na brzegach)
    portrait_size = 86
    portrait_x = panel_x + 7
    portrait_y = panel_y + 7
    pygame.draw.rect(screen, (40, 40, 45), (portrait_x, portrait_y, portrait_size, portrait_size))

    def pick_portrait(portrait_set):
        if player_health >= 95:
            return portrait_set["full"]
        elif player_health >= 75:
            return portrait_set["high"]
        elif player_health >= 45:
            return portrait_set["mid"]
        else:
            return portrait_set["low"]

    # Wybór odpowiedniego portretu na podstawie HP
    if selected_character["id"] == 1:
        char_portrait = pick_portrait(natan_portraits)
    elif selected_character["id"] == 2:
        char_portrait = pick_portrait(jan_portraits)
    elif selected_character["id"] == 3:
        char_portrait = pick_portrait(wika_portraits)
    else:
        # Awaryjnie dla innych postaci, jeśli jeszcze nie mają kompletów
        char_portrait = portraits.get(selected_character["id"], portraits[1])

    scaled_portrait = pygame.transform.scale(char_portrait, (portrait_size, portrait_size))
    screen.blit(scaled_portrait, (portrait_x, portrait_y))

    # Statystyki po prawej stronie portretu
    stat_x = portrait_x + portrait_size + 14
    
    # Zdrowie (%)
    hp_label = font_small.render("ZDROWIE", True, (180, 180, 180))
    hp_text = f"{player_health}%"
    hp_surf = font_hud.render(hp_text, True, RED if player_health < 30 else WHITE)
    
    screen.blit(hp_label, (stat_x, panel_y + 14))
    screen.blit(hp_surf, (stat_x, panel_y + 32))

    # Amunicja
    weapon = weapons[current_weapon_id]
    ammo_label = font_small.render("AMUNICJA", True, (180, 180, 180))
    ammo_text = f"{weapon['ammo']} / {weapon['max_ammo']}"
    if weapon["reloading"]:
        ammo_text = "RELOAD"
        
    ammo_surf = font_hud.render(ammo_text, True, (255, 220, 50))

    screen.blit(ammo_label, (stat_x + 110, panel_y + 14))
    screen.blit(ammo_surf, (stat_x + 110, panel_y + 32))

    
    # ========================================================
    # PASEK ENERGII SPRINTU
    # ========================================================

    sprint_label = font_small.render(
        "SPRINT [SHIFT]",
        True,
        (180, 180, 180)
    )

    screen.blit(sprint_label, (stat_x, panel_y + 61))

    # Wymiary paska
    bar_x = stat_x
    bar_y = panel_y + 80
    bar_width = 210
    bar_height = 10

    # Tło paska
    pygame.draw.rect(
        screen,
        (20, 20, 20),
        (bar_x, bar_y, bar_width, bar_height)
    )

    # Aktualny poziom energii
    sprint_ratio = sprint_energy / SPRINT_MAX_ENERGY
    filled_width = int(bar_width * sprint_ratio)

    # Kolor zależny od poziomu energii
    if sprint_ratio > 0.5:
        sprint_color = (50, 200, 70)
    elif sprint_ratio > 0.2:
        sprint_color = (230, 180, 40)
    else:
        sprint_color = (220, 50, 40)

    if filled_width > 0:
        pygame.draw.rect(
            screen,
            sprint_color,
            (bar_x, bar_y, filled_width, bar_height)
        )

    # Obramowanie paska
    pygame.draw.rect(
        screen,
        (180, 180, 180),
        (bar_x, bar_y, bar_width, bar_height),
        1
    )

# ============================================================
# INTERAKCJA, STRZELANIE I TRAFIENIA
# ============================================================

def check_door_interaction():
    look_ahead_dist = 1.2
    target_x = player_x + math.cos(player_angle) * look_ahead_dist
    target_y = player_y + math.sin(player_angle) * look_ahead_dist

    map_x = int(target_x)
    map_y = int(target_y)

    if (map_x, map_y) in doors:
        door = doors[(map_x, map_y)]
        if door["status"] in ["closed", "closing"]:
            door["status"] = "opening"

def shoot():
    global is_shooting_flash
    weapon = weapons[current_weapon_id]

    if weapon["reloading"] or weapon["cooldown"] > 0:
        return

    if weapon["ammo"] > 0:
        weapon["ammo"] -= 1
        weapon["cooldown"] = weapon["fire_rate"]
        is_shooting_flash = 4

        hit_enemy = None
        min_dist = weapon["range"]

        for enemy in enemies:
            if enemy["health"] <= 0:
                continue

            dx = enemy["x"] - player_x
            dy = enemy["y"] - player_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist > min_dist:
                continue

            angle_to_enemy = math.atan2(dy, dx)
            angle_diff = (angle_to_enemy - player_angle + math.pi) % (2 * math.pi) - math.pi

            if abs(angle_diff) < 0.25:
                ray_blocked = False
                steps = int(dist * 10)
                for i in range(1, steps):
                    check_x = player_x + (dx * i / steps)
                    check_y = player_y + (dy * i / steps)
                    
                    if is_wall(check_x, check_y):
                        ray_blocked = True
                        break
                
                if not ray_blocked and dist < min_dist:
                    min_dist = dist
                    hit_enemy = enemy

        if hit_enemy:
            hit_enemy["health"] -= weapon["damage"]
            print(f"Trafiono wroga! Zdrowie wroga: {hit_enemy['health']}")
            if hit_enemy["health"] <= 0:
                print("Wróg pokonany!")

    else:
        print("Pusto! Wciśnij R, aby przeładować.")

def reload_weapon():
    weapon = weapons[current_weapon_id]
    if not weapon["reloading"] and weapon["ammo"] < weapon["max_ammo"]:
        weapon["reloading"] = True
        weapon["reload_timer"] = weapon["reload_time"]
        print(f"Przeładowywanie ({weapon['name']})...")

def update_weapons(dt):
    global is_shooting_flash
    
    if is_shooting_flash > 0:
        is_shooting_flash -= 1

    for w_id, weapon in weapons.items():
        if weapon["cooldown"] > 0:
            weapon["cooldown"] -= dt

        if weapon["reloading"]:
            weapon["reload_timer"] -= dt
            if weapon["reload_timer"] <= 0:
                weapon["ammo"] = weapon["max_ammo"]
                weapon["reloading"] = False
                print("Przeładowano!")


# ============================================================
# MINIMAPA
# ============================================================

def draw_minimap():
    tile_size = 12
    offset_x = WIDTH - (MAP_WIDTH * tile_size) - 20
    offset_y = 20

    for y, row in enumerate(WORLD_MAP):
        for x, cell in enumerate(row):
            if cell == "D":
                door_data = doors.get((x, y))
                if door_data and door_data["progress"] > 0.5:
                    color = (100, 255, 100)
                else:
                    color = (200, 150, 50)
            elif cell != "0":
                color = WHITE
            else:
                color = (35, 35, 35)

            pygame.draw.rect(
                screen,
                color,
                (
                    offset_x + x * tile_size,
                    offset_y + y * tile_size,
                    tile_size - 1,
                    tile_size - 1
                )
            )

    for enemy in enemies:
        if enemy["health"] > 0:
            ex = offset_x + int(enemy["x"] * tile_size)
            ey = offset_y + int(enemy["y"] * tile_size)
            pygame.draw.circle(screen, (255, 0, 0), (ex, ey), 3)

    px = offset_x + int(player_x * tile_size)
    py = offset_y + int(player_y * tile_size)

    pygame.draw.circle(screen, (50, 50, 255), (px, py), 4)
    pygame.draw.line(
        screen,
        (50, 50, 255),
        (px, py),
        (
            px + int(math.cos(player_angle) * 15),
            py + int(math.sin(player_angle) * 15)
        ),
        2
    )


# ============================================================
# STEROWANIE GRACZEM
# ============================================================


def update_player(dt):
    global player_x, player_y, player_angle
    global sprint_energy, sprint_active

    keys = pygame.key.get_pressed()

    # Obracanie postaci
    if keys[pygame.K_q] or keys[pygame.K_LEFT]:
        player_angle -= ROTATION_SPEED * dt

    if keys[pygame.K_e] or keys[pygame.K_RIGHT]:
        player_angle += ROTATION_SPEED * dt

    mouse_rel = pygame.mouse.get_rel()
    player_angle += mouse_rel[0] * MOUSE_SENSITIVITY

    move_x = 0
    move_y = 0

    forward_x = math.cos(player_angle)
    forward_y = math.sin(player_angle)
    right_x = -math.sin(player_angle)
    right_y = math.cos(player_angle)

    # Ruch do przodu i do tyłu
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move_x += forward_x
        move_y += forward_y

    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move_x -= forward_x
        move_y -= forward_y

    # Ruch na boki
    if keys[pygame.K_d]:
        move_x += right_x
        move_y += right_y

    if keys[pygame.K_a]:
        move_x -= right_x
        move_y -= right_y

    # Normalizacja ruchu
    length = math.sqrt(move_x ** 2 + move_y ** 2)

    if length > 0:
        move_x /= length
        move_y /= length

    # ========================================================
    # SPRINT
    # ========================================================

    sprint_requested = (
        keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    )

    # Sprint tylko podczas poruszania się
    sprint_active = (
        sprint_requested
        and length > 0
        and sprint_energy > 0
    )

    if sprint_active:
        sprint_energy -= SPRINT_DRAIN_RATE * dt
        sprint_energy = max(0.0, sprint_energy)

        # Wyłączenie sprintu po wyczerpaniu energii
        if sprint_energy <= 0:
            sprint_active = False

    else:
        # Regeneracja energii
        sprint_energy += SPRINT_REGEN_RATE * dt
        sprint_energy = min(SPRINT_MAX_ENERGY, sprint_energy)

    # Prędkość zależna od sprintu
    current_speed = MOVE_SPEED

    if sprint_active:
        current_speed *= SPRINT_MULTIPLIER

    # ========================================================
    # RUCH I KOLIZJE
    # ========================================================

    new_x = player_x + move_x * current_speed * dt
    new_y = player_y + move_y * current_speed * dt

    margin = PLAYER_RADIUS

    if not is_wall(new_x + math.copysign(margin, move_x), player_y):
        player_x = new_x

    if not is_wall(player_x, new_y + math.copysign(margin, move_y)):
        player_y = new_y


# ============================================================
# GŁÓWNA PĘTLA GRY
# ============================================================

def main():
    character_select_screen()

    print(f"Uruchomiono grę jako {selected_character['name']}!")
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_f:
                    check_door_interaction()
                if event.key == pygame.K_r:
                    reload_weapon()
                if event.key == pygame.K_SPACE:
                    shoot()

                # KLAWISZE TESTOWE DO SPRAWDZENIA PORTRETÓW:
                if event.key in [pygame.K_9, pygame.K_8, pygame.K_7, pygame.K_6]:
                    global player_health  

                if event.key == pygame.K_9:  # Ustaw HP na 100% (stan początkowy)
                    player_health = 100
                    print("Test HP: 100%")
                if event.key == pygame.K_8:  # Ustaw HP na 80% (drugi portret)
                    player_health = 80
                    print("Test HP: 80%")
                if event.key == pygame.K_7:  # Ustaw HP na 50% (trzeci portret)
                    player_health = 50
                    print("Test HP: 50%")
                if event.key == pygame.K_6:  # Ustaw HP na 20% (czwarty portret - ranny)
                    player_health = 20
                    print("Test HP: 20% (Ranny!)")
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    shoot()

        update_player(dt)
        update_doors(dt)
        update_weapons(dt)
        update_enemies(dt)
       
        render_world()
        draw_weapon()
        draw_wolfenstein_hud() 
       # draw_minimap()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()