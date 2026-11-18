import pygame
import math
import sys

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
pygame.display.set_caption("RETRO FPS - Automatyczne Drzwi")

clock = pygame.time.Clock()

# ============================================================
# KOLORY
# ============================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CEILING_COLOR = (35, 35, 42)
FLOOR_COLOR = (65, 58, 50)


# ============================================================
# TEKSTURY ŚCIAN I DRZWI
# ============================================================

def load_texture(path):
    try:
        return pygame.image.load(path).convert()
    except Exception:
        # Awaryjna tekstura proceduralna (szachownica)
        surf = pygame.Surface((64, 64))
        surf.fill((100, 100, 100))
        pygame.draw.rect(surf, (200, 200, 200), (0, 0, 32, 32))
        pygame.draw.rect(surf, (200, 200, 200), (32, 32, 32, 32))
        return surf

wall_textures = {
    "1": load_texture("assets/textures/wall_brick.png"),
    "2": load_texture("assets/textures/wall_stone.png"),
    "3": load_texture("assets/textures/wall_metal.png"),
    "D": load_texture("assets/textures/door.png")
}


# ============================================================
# MAPA POZIOMU ("D" OZNACZA DRZWI)
# ============================================================

WORLD_MAP = [
    "111111111111",
    "100000000001",
    "102200010001",
    "100000010001",
    "100011300001",
    "100000D00001",  # Drzwi
    "101000330001",
    "100000000001",
    "100110000001",
    "100000000001",
    "100000000001",
    "111111111111"
]

MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)

# Słownik stanów drzwi (progress: 0.0 = zamknięte, 1.0 = otwarte)
doors = {}
for y, row in enumerate(WORLD_MAP):
    for x, cell in enumerate(row):
        if cell == "D":
            doors[(x, y)] = {
                "progress": 0.0,
                "timer": 0.0,
                "status": "closed"  # "closed", "opening", "open", "closing"
            }

DOOR_SPEED = 2.0        # Prędkość otwierania/zamykania
AUTO_CLOSE_TIME = 3.0   # Czas w sekundach, przez jaki drzwi pozostają otwarte


# ============================================================
# GRACZ
# ============================================================

player_x = 1.5
player_y = 1.5
player_angle = 0.0

MOVE_SPEED = 3.0
ROTATION_SPEED = 2.0


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
    
    # Jeśli to drzwi, sprawdzamy ich stopień otwarcia
    if cell == "D":
        door_data = doors.get((map_x, map_y))
        if door_data and door_data["progress"] > 0.8:
            return False  # Gracz może przejść, gdy są w większości otwarte
        return True

    return False


# ============================================================
# AKTUALIZACJA DRZWI (ANIMACJA I TIMER)
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
                # Jeśli gracz stoi w progu, resetujemy timer, żeby drzwi się nie zamknęły
                door["timer"] = AUTO_CLOSE_TIME
            else:
                door["timer"] -= dt
                if door["timer"] <= 0:
                    door["status"] = "closing"

        elif door["status"] == "closing":
            if player_on_door:
                # Jeśli gracz wejdzie w zamykające się drzwi, natychmiast je otwórz z powrotem
                door["status"] = "opening"
            else:
                door["progress"] -= DOOR_SPEED * dt
                if door["progress"] <= 0.0:
                    door["progress"] = 0.0
                    door["status"] = "closed"


# ============================================================
# RAYCASTING & RENDEROWANIE ŚWIATA
# ============================================================

def render_world():
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
                        continue  # Promień przechodzi przez w pełni otwarte drzwi
                hit = True

        if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
            continue

        if side == 0:
            perp_wall_dist = (map_x - player_x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_dist = (map_y - player_y + (1 - step_y) / 2) / ray_dir_y

        perp_wall_dist = max(0.05, perp_wall_dist)

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

        # Przesunięcie tekstury drzwi w zależności od animacji
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


# ============================================================
# INTERAKCJA Z DRZWIAMI (OTWIERANIE NA KLAWISZ F)
# ============================================================

def check_door_interaction():
    look_ahead_dist = 1.2
    target_x = player_x + math.cos(player_angle) * look_ahead_dist
    target_y = player_y + math.sin(player_angle) * look_ahead_dist

    map_x = int(target_x)
    map_y = int(target_y)

    if (map_x, map_y) in doors:
        door = doors[(map_x, map_y)]
        # Jeśli drzwi są zamknięte lub się zamykają, wyzwól ich otwarcie
        if door["status"] in ["closed", "closing"]:
            door["status"] = "opening"


# ============================================================
# MINIMAPA
# ============================================================

def draw_minimap():
    tile_size = 12
    offset_x = 20
    offset_y = 20

    for y, row in enumerate(WORLD_MAP):
        for x, cell in enumerate(row):
            if cell == "D":
                # Kolor drzwi zmienia się w zależności od stanu na minimapie
                door_data = doors.get((x, y))
                if door_data and door_data["progress"] > 0.5:
                    color = (100, 255, 100)  # Jasnozielony = otwarte
                else:
                    color = (200, 150, 50)   # Pomarańczowy = zamknięte
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

    px = offset_x + int(player_x * tile_size)
    py = offset_y + int(player_y * tile_size)

    pygame.draw.circle(screen, (255, 50, 50), (px, py), 4)
    pygame.draw.line(
        screen,
        (255, 50, 50),
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
    print("Uruchomiono silnik z automatycznymi drzwiami!")
    print("Sterowanie: W/S/A/D (ruch), Q/E lub Strzałki (obrót), F (otwórz drzwi).")
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

        update_player(dt)
        update_doors(dt)  # Aktualizacja stanu i timera drzwi w każdej klatce
        render_world()
        draw_minimap()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()