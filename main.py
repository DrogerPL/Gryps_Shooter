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

# Wczytanie sprite'ów dubeltówki
shotgun_idle = load_weapon_texture("assets/weapons/shotgun.png")
shotgun_fire = load_weapon_texture("assets/weapons/shotgun_shoot.png")

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
    "11111111111111111111",
    "10000010000000100001",
    "10220010222200103301",
    "102200D0000D00103301",
    "10000011100111100001",
    "111D1110000003311111",
    "10000000111100000001",
    "10111102222201111101",
    "10100D0200020D001001",
    "10103302000203301001",
    "10103302222203301001",
    "101000000D0000001001",
    "10111111000111111101",
    "100000010D0100000001",
    "10220001111100022001",
    "10220000000000022001",
    "11111111111111111111"
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
# SYSTEM WROGÓW
# ============================================================

enemies = [
    {"x": 4.5, "y": 2.5, "health": 3, "state": "idle"},
    {"x": 15.5, "y": 2.5, "health": 3, "state": "idle"},
    {"x": 9.5, "y": 9.5, "health": 3, "state": "idle"},
    {"x": 3.5, "y": 13.5, "health": 3, "state": "idle"},
    {"x": 16.5, "y": 13.5, "health": 3, "state": "idle"}
]

ENEMY_SPEED = 1.2
ENEMY_DETECT_DIST = 5.0


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

def update_enemies(dt):
    for enemy in enemies:
        if enemy["health"] <= 0:
            continue

        dx = player_x - enemy["x"]
        dy = player_y - enemy["y"]
        dist = math.sqrt(dx**2 + dy**2)

        if dist < ENEMY_DETECT_DIST:
            enemy["state"] = "chasing"

        if enemy["state"] == "chasing" and dist > 0.5:
            move_x = (dx / dist) * ENEMY_SPEED * dt
            move_y = (dy / dist) * ENEMY_SPEED * dt

            if not is_wall(enemy["x"] + move_x, enemy["y"]):
                enemy["x"] += move_x
            if not is_wall(enemy["x"], enemy["y"] + move_y):
                enemy["y"] += move_y


# ============================================================
# RAYCASTING & RENDEROWANIE ŚWIATA
# ============================================================

def render_world():
    # Świat zajmuje teraz całą wysokość ekranu (HEIGHT)
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

    for x in range(RENDER_WIDTH):
        camera_x = 2.0 * x / RENDER_WIDTH - 1.0

        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        map_x = int(player_x)
        map_y = int(player_y)

        delta_dist_x = abs(1 / ray_dir_x) if abs(ray_dir_x) > 1e-7 else float("inf")
        delta_dist_y = abs(1 / ray_dir_y) if abs(ray_dir_y) > 1e-7 else float("inf")

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

            if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                hit = True
                break

            cell = WORLD_MAP[map_y][map_x]
            if cell != "0":
                if cell == "D":
                    door_data = doors.get((map_x, map_y))
                    if door_data and door_data["progress"] >= 1.0:
                        continue
                hit = True

        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            continue

        if side == 0:
            perp_wall_dist = (map_x - player_x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_dist = (map_y - player_y + (1 - step_y) / 2) / ray_dir_y

        perp_wall_dist = max(0.05, perp_wall_dist)
        z_buffer[x] = perp_wall_dist

        line_height = int(HEIGHT / perp_wall_dist)
        draw_start = max(0, HEIGHT // 2 - line_height // 2)
        draw_end = min(HEIGHT, HEIGHT // 2 + line_height // 2)

        wall_type = WORLD_MAP[map_y][map_x]
        texture = wall_textures.get(wall_type, wall_textures["1"])
        texture_width = texture.get_width()
        texture_height = texture.get_height()

        if side == 0:
            wall_x = player_y + perp_wall_dist * ray_dir_y
        else:
            wall_x = player_x + perp_wall_dist * ray_dir_x
        wall_x -= math.floor(wall_x)

        if wall_type == "D":
            door_data = doors.get((map_x, map_y))
            open_progress = door_data["progress"] if door_data else 0.0
            wall_x = (wall_x + open_progress) % 1.0

        texture_x = int(wall_x * texture_width)
        texture_x = max(0, min(texture_width - 1, texture_x))

        if side == 0 and ray_dir_x > 0:
            texture_x = texture_width - texture_x - 1
        if side == 1 and ray_dir_y < 0:
            texture_x = texture_width - texture_x - 1

        texture_column = texture.subsurface((texture_x, 0, 1, texture_height))
        full_wall_surface = pygame.transform.scale(texture_column, (RENDER_SCALE, line_height))

        wall_top = HEIGHT // 2 - line_height // 2
        visible_top = draw_start - wall_top
        visible_height = draw_end - draw_start

        if visible_height > 0:
            wall_surface = full_wall_surface.subsurface((0, max(0, visible_top), RENDER_SCALE, visible_height))

            brightness = max(35, min(255, int(255 / (1 + perp_wall_dist * 0.18))))
            if side == 1:
                brightness = int(brightness * 0.7)

            wall_surface.fill(
                (brightness, brightness, brightness),
                special_flags=pygame.BLEND_RGB_MULT
            )

            screen.blit(wall_surface, (x * RENDER_SCALE, draw_start))

    # RENDEROWANIE WROGÓW
    sorted_enemies = sorted(enemies, key=lambda e: (player_x - e["x"])**2 + (player_y - e["y"])**2, reverse=True)

    for enemy in sorted_enemies:
        if enemy["health"] <= 0:
            continue

        sprite_x = enemy["x"] - player_x
        sprite_y = enemy["y"] - player_y

        inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)
        transform_x = inv_det * (dir_y * sprite_x - dir_x * sprite_y)
        transform_y = inv_det * (-plane_y * sprite_x + plane_x * sprite_y)

        if transform_y > 0.2:
            screen_x = int((WIDTH / 2) * (1.0 + transform_x / transform_y))

            sprite_height = abs(int(HEIGHT / transform_y))
            sprite_width = abs(int(HEIGHT / transform_y))

            draw_start_y = max(0, HEIGHT // 2 - sprite_height // 2)
            draw_end_y = min(HEIGHT, HEIGHT // 2 + sprite_height // 2)

            draw_start_x = max(0, screen_x - sprite_width // 2)
            draw_end_x = min(WIDTH, screen_x + sprite_width // 2)

            for stripe in range(draw_start_x, draw_end_x):
                render_stripe_idx = stripe // RENDER_SCALE
                if 0 <= render_stripe_idx < RENDER_WIDTH:
                    if transform_y < z_buffer[render_stripe_idx]:
                        color_val = max(50, min(255, int(255 / (1 + transform_y * 0.2))))
                        enemy_color = (color_val, 20, 20)
                        pygame.draw.line(screen, enemy_color, (stripe, draw_start_y), (stripe, draw_end_y))


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

    if current_weapon_id == 1:
        scale_factor = 1.2 
        current_sprite = shotgun_fire if is_shooting_flash > 0 else shotgun_idle

        new_width = int(current_sprite.get_width() * scale_factor)
        new_height = int(current_sprite.get_height() * scale_factor)
        scaled_gun = pygame.transform.scale(current_sprite, (new_width, new_height))

        gun_x = center_x - new_width // 2
        gun_y = base_y - new_height + 20  
        screen.blit(scaled_gun, (gun_x, gun_y))


    elif current_weapon_id == 2:
        gun_width = 100
        gun_height = 250
        gun_rect = pygame.Rect(center_x - 20, base_y - gun_height, gun_width, gun_height)
        pygame.draw.rect(screen, (50, 55, 60), gun_rect)
        pygame.draw.rect(screen, (30, 30, 35), (center_x + 30, base_y - 180, 25, 120))

        if is_shooting_flash > 0:
            flash_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 180, 50, 220), (40, 40), random.randint(30, 50))
            screen.blit(flash_surf, (center_x + 10, base_y - gun_height - 50))

    elif current_weapon_id == 3:
        left_rect = pygame.Rect(center_x - 280, base_y - 180, 90, 180)
        pygame.draw.rect(screen, (60, 60, 65), left_rect)
        pygame.draw.rect(screen, (30, 30, 30), left_rect, 3)

        right_rect = pygame.Rect(center_x + 190, base_y - 180, 90, 180)
        pygame.draw.rect(screen, (60, 60, 65), right_rect)
        pygame.draw.rect(screen, (30, 30, 30), right_rect, 3)

        if is_shooting_flash > 0:
            flash_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 200, 50, 220), (35, 35), 35)
            screen.blit(flash_surf, (center_x - 270, base_y - 230))
            screen.blit(flash_surf, (center_x + 200, base_y - 230))


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

    # Informacje sterowania u góry ekranu
    info_text = f"Postać: {selected_character['name']} | LMB/Spacja: Strzał | R: Przeładuj | F: Drzwi"
    info_surface = font_small.render(info_text, True, (200, 200, 200))
    screen.blit(info_surface, (20, 10))
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

        for enemy in enemies:
            if enemy["health"] > 0:
                enemy["state"] = "chasing"

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

    keys = pygame.key.get_pressed()

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

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move_x += forward_x
        move_y += forward_y
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move_x -= forward_x
        move_y -= forward_y
    if keys[pygame.K_d]:
        move_x += right_x
        move_y += right_y
    if keys[pygame.K_a]:
        move_x -= right_x
        move_y -= right_y

    length = math.sqrt(move_x ** 2 + move_y ** 2)
    if length > 0:
        move_x /= length
        move_y /= length

    new_x = player_x + move_x * MOVE_SPEED * dt
    new_y = player_y + move_y * MOVE_SPEED * dt

    margin = PLAYER_RADIUS
    if not (is_wall(new_x + math.copysign(margin, move_x), player_y)):
        player_x = new_x

    if not (is_wall(player_x, new_y + math.copysign(margin, move_y))):
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
                    global player_health  # <--- TO ROZWIĄZUJE PROBLEM!

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
        draw_wolfenstein_hud()  # Zeznaje w lewym dolnym rogu
        draw_minimap()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()