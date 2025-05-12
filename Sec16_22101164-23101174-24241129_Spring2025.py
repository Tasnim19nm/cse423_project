from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

window_width = 1000
window_height = 800

difficulty_levels = ["EASY", "MEDIUM", "HARD"]
current_level = 0
game_state = "MENU"
score = 0

GRID_LENGTH = 600
title_size = 20
grid_size = 20

cam_distance = 400
cam_height = 400
cam_angle = 45
cam_speed = 5
cam_height_speed = 10
min_cam_height = 50
camera_mode = "third_person"

player_x = 0
player_y = 0
player_z = 0
player_angle = 0
player_speed = 3
gun_rotation_speed = 4

level_colors = [
    [
        [0.9, 0.9, 1.0],
        [0.6, 0.8, 0.6]
    ],
    [
        [0.7, 0.7, 0.9],
        [0.4, 0.6, 0.4]
    ],
    [
        [0.5, 0.5, 0.8],
        [0.2, 0.4, 0.2]
    ]
]

wall_colors = [
    [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.5, 0.0, 1.0]],
    [[0.0, 0.8, 0.0], [0.0, 0.0, 0.8], [0.0, 0.8, 0.8], [0.4, 0.0, 0.8]],
    [[0.0, 0.6, 0.0], [0.0, 0.0, 0.6], [0.0, 0.6, 0.6], [0.3, 0.0, 0.6]]
]

balloons = []
balloon_spawn_rate = 2.0
last_balloon_time = 0
balloon_colors = [
    [1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 1.0, 0.0],
    [0.0, 1.0, 0.0],
    [1.0, 0.0, 1.0],
    [0.0, 1.0, 1.0]
]
popped_balloons = 0
balloon_fall_speed_min = 0.5
balloon_fall_speed_max = .1
pop_distance = 30

balloon_spawn_distance = 100
balloon_spawn_height = 150

balloon_cheat_mode = False
auto_pop_radius = 150
cheat_score_multiplier = 2

chocolate_active = False
chocolate_position = [0, 0, 0]
chocolate_rotation = 0
chocolates_collected = 0
sparkle_size = 0
sparkle_growing = True
sparkle_speed = 0.2
chocolate_size = 8
chocolate_fall_speed = 2.0
next_chocolate_milestone = 5

box_collections = [0, 0, 0, 0, 0, 0]
box_positions = []
box_size = 15
current_box_level = 0
medium_reward_given = False

total_fallen_balloons = 0
last_popped_count = 0
game_over = False

enemies = []
enemy_speed = 0.6
enemy_spawn_rate = 5.0
last_enemy_time = 0
max_active_enemies = 2
enemy_collision_distance = 20

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    init_medium_boxes()

def init_medium_boxes():
    global box_positions
    box_positions = []
    radius = 150
    for i in range(6):
        angle = math.radians(i * 60)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        box_positions.append([x, y, box_size/2])

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width / window_height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == "first_person":
        eye_x = player_x + math.cos(math.radians(player_angle)) * 15
        eye_y = player_y + math.sin(math.radians(player_angle)) * 15
        eye_z = player_z + 13
        
        look_x = eye_x + math.cos(math.radians(player_angle))
        look_y = eye_y + math.sin(math.radians(player_angle))
        look_z = eye_z
        
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        cam_x = cam_distance * math.sin(math.radians(cam_angle))
        cam_y = -cam_distance * math.cos(math.radians(cam_angle))
        cam_z = cam_height
        
        target_x = 0
        target_y = 0
        target_z = 0
        
        gluLookAt(cam_x, cam_y, cam_z,  
                  target_x, target_y, target_z,  
                  0, 0, 1)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_checkerboard():
    color1, color2 = level_colors[current_level]
    for i in range(-grid_size//2, grid_size//2):
        for j in range(-grid_size//2, grid_size//2):
            if (i + j) % 2 == 0:
                glColor3f(*color1)
            else:
                glColor3f(*color2)
            glBegin(GL_QUADS)
            glVertex3f(i*title_size, j*title_size, 0)
            glVertex3f((i+1)*title_size, j*title_size, 0)
            glVertex3f((i+1)*title_size, (j+1)*title_size, 0)
            glVertex3f(i*title_size, (j+1)*title_size, 0)
            glEnd()

def draw_boundaries():
    wall_height = 30  
    wall_thickness = 1
    colors = wall_colors[current_level]

    glColor3f(*colors[0])
    glPushMatrix()
    glTranslatef(grid_size//2 * title_size, 0, wall_height/2)  
    glScalef(wall_thickness, grid_size*title_size, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*colors[1])
    glPushMatrix()
    glTranslatef(-grid_size//2 * title_size, 0, wall_height/2)
    glScalef(wall_thickness, grid_size*title_size, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*colors[2])
    glPushMatrix()
    glTranslatef(0, grid_size//2 * title_size, wall_height/2)
    glScalef(grid_size*title_size, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*colors[3])
    glPushMatrix()
    glTranslatef(0, -grid_size//2 * title_size, wall_height/2)
    glScalef(grid_size*title_size, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + 10)
    glRotatef(player_angle, 0, 0, 1)
    
    glColor3f(1.0, 1.0, 0.0)
    glPushMatrix()
    glScalef(8, 4, 15)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glutSolidSphere(5, 20, 20)
    glPopMatrix()
    
    glColor3f(0.9, 0.7, 0.0)
    glPushMatrix()
    glTranslatef(0, -6, 7)
    glScalef(2, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 6, 7)
    glScalef(2, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()

def draw_menu():
    title_text = "Baloon Popper"
    draw_text(window_width/2 - 150, window_height - 100, title_text, GLUT_BITMAP_TIMES_ROMAN_24)
    
    draw_text(window_width/2 - 100, window_height - 200, "SELECT DIFFICULTY:", GLUT_BITMAP_HELVETICA_18)
    
    y_pos = window_height - 250
    for i, level in enumerate(difficulty_levels):
        if i == current_level:
            draw_text(window_width/2 - 50, y_pos, f"> {level} <", GLUT_BITMAP_HELVETICA_18)
        else:
            draw_text(window_width/2 - 35, y_pos, level, GLUT_BITMAP_HELVETICA_18)
        y_pos -= 50
    
    controls_y = 200
    draw_text(window_width/2 - 100, controls_y, "CONTROLS:", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 180, controls_y - 40, "F/B: Move forward/backward", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 60, "L/R: Strafe left/right", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 80, "A/D: Rotate left/right", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 100, "S: Restart game", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 120, "Arrow Keys: Adjust camera (third-person)", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 140, "Right Click: Toggle first/third person", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 160, "C: Toggle balloon auto-pop (Easy mode only)", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 180, "M: Return to menu", GLUT_BITMAP_HELVETICA_12)
    draw_text(window_width/2 - 180, controls_y - 200, "ESC: Exit game", GLUT_BITMAP_HELVETICA_12)

def draw_medium_boxes():
    if current_level not in [1, 2]:
        return
    
    for i in range(6):
        x, y, z = box_positions[i]
        color = balloon_colors[i]
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        glColor3f(*color)
        glutSolidCube(box_size)
        
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos3f(0, 0, box_size/2 + 5)
        text = str(box_collections[i])
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        glPopMatrix()

def check_medium_milestone():
    global medium_reward_given, current_box_level, chocolate_active
    
    min_count = min(box_collections)
    
    if min_count > current_box_level and not medium_reward_given and not chocolate_active:
        current_box_level = min_count
        spawn_chocolate()
        medium_reward_given = True
        print(f"Medium level milestone reached! All boxes have {current_box_level} balloons!")

def add_balloon_to_box(color_index):
    global box_collections, medium_reward_given
    
    box_collections[color_index] += 1
    print(f"Added a balloon to box {color_index}. Now has {box_collections[color_index]}")
    
    check_medium_milestone()
    
    if not chocolate_active and medium_reward_given:
        medium_reward_given = False

def spawn_balloon():
    global player_x, player_y
    
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(30, balloon_spawn_distance)
    
    x = player_x + math.cos(angle) * distance
    y = player_y + math.sin(angle) * distance
    
    half_grid = grid_size//2 * title_size - 20
    x = max(-half_grid, min(half_grid, x))
    y = max(-half_grid, min(half_grid, y))
    
    z = balloon_spawn_height
    
    if current_level == 1 or current_level == 2:
        if len(balloons) < 6:
            available_indices = [i for i in range(6) if not any(balloon[4] == balloon_colors[i] for balloon in balloons)]
            if available_indices:
                color_index = random.choice(available_indices)
            else:
                color_index = random.randint(0, 5)
        else:
            min_count = min(box_collections)
            min_indices = [i for i, count in enumerate(box_collections) if count == min_count]
            color_index = random.choice(min_indices)
        color = balloon_colors[color_index]
    else:
        color_index = random.randint(0, 5)
        color = balloon_colors[color_index]
    
    size = random.uniform(5, 10)
    speed = random.uniform(balloon_fall_speed_min, balloon_fall_speed_max)
    rotation = random.uniform(0, 360)
    
    balloons.append([x, y, z, size, color, speed, rotation, color_index])

def update_balloons():
    global balloons, popped_balloons, last_balloon_time, score
    global total_fallen_balloons, last_popped_count, game_over, game_state
    current_time = time.time()
    
    balloons_to_remove = []
    for i, balloon in enumerate(balloons):
        balloon[2] -= balloon[5]
        
        if balloon[2] < 0:
            balloons_to_remove.append(i)
            total_fallen_balloons += 1
            
            if current_level in [0, 1]:
                if total_fallen_balloons >= 20:
                    current_popped = popped_balloons - last_popped_count
                    if current_popped < 5:
                        game_over = True
                        game_state = "GAME_OVER"
                        print(f"Game Over! You only popped {current_popped} out of 20 balloons!")
                    else:
                        last_popped_count = popped_balloons
                        total_fallen_balloons = 0
                        print(f"Good job! You popped {current_popped} balloons!")
    
    if current_level == 0 and balloon_cheat_mode and camera_mode == "third_person":
        for i, balloon in enumerate(balloons):
            if i in balloons_to_remove:
                continue
                
            dx = player_x - balloon[0]
            dy = player_y - balloon[1]
            dz = (player_z + 10) - balloon[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < auto_pop_radius:
                balloons_to_remove.append(i)
                score += 10 * cheat_score_multiplier
                popped_balloons += 1
                
    for i in sorted(balloons_to_remove, reverse=True):
        if i < len(balloons):
            balloons.pop(i)
    
    if (current_level in [0, 1, 2]) and current_time - last_balloon_time > balloon_spawn_rate and not game_over:
        spawn_balloon()
        last_balloon_time = current_time

def spawn_chocolate():
    global chocolate_active, chocolate_position, chocolate_rotation
    
    if chocolate_active:
        return
    
    x = player_x + random.uniform(-30, 30)
    y = player_y + random.uniform(-30, 30)
    z = 150
    
    half_grid = grid_size//2 * title_size - 30
    x = max(-half_grid, min(half_grid, x))
    y = max(-half_grid, min(half_grid, y))
    
    chocolate_position = [x, y, z]
    chocolate_rotation = random.uniform(0, 360)
    chocolate_active = True

def update_chocolate():
    global chocolate_active, chocolate_position, chocolates_collected, next_chocolate_milestone
    
    if not chocolate_active:
        return
    
    chocolate_position[2] -= chocolate_fall_speed
    
    global chocolate_rotation
    chocolate_rotation = (chocolate_rotation + 2) % 360
    
    dx = player_x - chocolate_position[0]
    dy = player_y - chocolate_position[1]
    dz = (player_z + 10) - chocolate_position[2]
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    if chocolate_position[2] <= 5 or dist < 20:
        if dist < 20:
            print(f"Chocolate collected! Total: {chocolates_collected + 1}")
        else:
            print(f"Chocolate landed! Total: {chocolates_collected + 1}")
            
        chocolate_active = False
        chocolates_collected += 1
        next_chocolate_milestone = ((popped_balloons // 5) + 1) * 5

def draw_chocolate():
    global sparkle_size, sparkle_growing
    
    if not chocolate_active:
        return
    
    x, y, z = chocolate_position
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(chocolate_rotation, 0, 1, 1)
    
    glColor3f(1.0, 1.0, 0.5)
    glutWireSphere(chocolate_size + sparkle_size, 10, 10)
    
    if sparkle_growing:
        sparkle_size += sparkle_speed
        if sparkle_size > 3:
            sparkle_growing = False
    else:
        sparkle_size -= sparkle_speed
        if sparkle_size < 0.5:
            sparkle_growing = True
    
    glColor3f(0.5, 0.25, 0.0)
    glutSolidCube(chocolate_size)
    
    glPopMatrix()

def check_balloon_pop():
    global balloons, popped_balloons, score, next_chocolate_milestone
    
    if camera_mode != "third_person":
        return
        
    balloons_to_pop = []
    for i, balloon in enumerate(balloons):
        dx = player_x - balloon[0]
        dy = player_y - balloon[1]
        dz = (player_z + 10) - balloon[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist < pop_distance:
            balloons_to_pop.append(i)
            score += 10
            popped_balloons += 1
            
            if (current_level == 1 or current_level == 2) and len(balloon) > 7:
                color_index = balloon[7]
                add_balloon_to_box(color_index)
    
    for i in sorted(balloons_to_pop, reverse=True):
        balloons.pop(i)
    
    if current_level == 0 and popped_balloons >= next_chocolate_milestone and not chocolate_active:
        spawn_chocolate()
        print(f"Easy level chocolate spawned at milestone: {next_chocolate_milestone}")

def draw_balloon(x, y, z, size, color, rotation):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 0, 1)
    
    glColor3f(*color)
    glutSolidSphere(size, 20, 20)
    
    glColor3f(0.7, 0.7, 0.7)
    glTranslatef(0, 0, -size)
    glutSolidSphere(size/4, 10, 10)
    
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -size*3)
    glEnd()
    
    glPopMatrix()

def draw_balloons():
    for balloon in balloons:
        if len(balloon) > 7:
            x, y, z, size, color, speed, rotation, _ = balloon
        else:
            x, y, z, size, color, speed, rotation = balloon
        draw_balloon(x, y, z, size, color, rotation)

def spawn_enemy():
    global enemies
    
    if current_level != 2 or len(enemies) >= max_active_enemies:
        return
    
    start_wall = random.randint(0, 3)
    
    possible_targets = [(start_wall + 1) % 4, (start_wall - 1) % 4]
    target_wall = random.choice(possible_targets)
    
    half_grid = grid_size//2 * title_size
    
    if start_wall == 0:
        x = half_grid - 5
        y = random.uniform(-half_grid + 20, half_grid - 20)
    elif start_wall == 1:
        x = -half_grid + 5
        y = random.uniform(-half_grid + 20, half_grid - 20)
    elif start_wall == 2:
        x = random.uniform(-half_grid + 20, half_grid - 20)
        y = half_grid - 5
    else:
        x = random.uniform(-half_grid + 20, half_grid - 20)
        y = -half_grid + 5
    
    if target_wall == 0:
        target_x = half_grid - 5
        target_y = random.uniform(-half_grid + 20, half_grid - 20)
    elif target_wall == 1:
        target_x = -half_grid + 5
        target_y = random.uniform(-half_grid + 20, half_grid - 20)
    elif target_wall == 2:
        target_x = random.uniform(-half_grid + 20, half_grid - 20)
        target_y = half_grid - 5
    else:
        target_x = random.uniform(-half_grid + 20, half_grid - 20)
        target_y = -half_grid + 5
    
    dx = target_x - x
    dy = target_y - y
    dist = math.sqrt(dx*dx + dy*dy)
    direction = [dx/dist, dy/dist]
    
    enemies.append([x, y, 10, direction, start_wall, target_wall, 0])

def update_enemies():
    global enemies, game_over, game_state, last_enemy_time
    
    if current_level != 2:
        return
    
    enemies_to_remove = []
    for i, enemy in enumerate(enemies):
        x, y, z, direction, start_wall, target_wall, progress = enemy
        
        new_x = x + direction[0] * enemy_speed
        new_y = y + direction[1] * enemy_speed
        enemy[0] = new_x
        enemy[1] = new_y
        enemy[6] += enemy_speed
        
        half_grid = grid_size//2 * title_size
        if (target_wall == 0 and new_x >= half_grid - 5) or \
           (target_wall == 1 and new_x <= -half_grid + 5) or \
           (target_wall == 2 and new_y >= half_grid - 5) or \
           (target_wall == 3 and new_y <= -half_grid + 5):
            enemies_to_remove.append(i)
        
        dx = player_x - new_x
        dy = player_y - new_y
        dz = (player_z + 10) - z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist < enemy_collision_distance:
            game_over = True
            game_state = "GAME_OVER"
            print("Game Over! You were caught by an enemy!")
    
    for i in sorted(enemies_to_remove, reverse=True):
        enemies.pop(i)
    
    current_time = time.time()
    if len(enemies) < max_active_enemies and current_time - last_enemy_time > enemy_spawn_rate:
        spawn_enemy()
        last_enemy_time = current_time

def draw_enemy(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    angle = math.degrees(math.atan2(y, x))
    glRotatef(angle, 0, 0, 1)
    
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glScalef(8, 4, 15)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glutSolidSphere(5, 20, 20)
    glPopMatrix()
    
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, -6, 7)
    glScalef(2, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 6, 7)
    glScalef(2, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()

def draw_enemies():
    if current_level != 2:
        return
    
    for enemy in enemies:
        x, y, z = enemy[0], enemy[1], enemy[2]
        draw_enemy(x, y, z)

def keyboardListener(key, x, y):
    global player_x, player_y, player_angle, game_state, current_level, balloon_cheat_mode
    global balloons, popped_balloons, last_balloon_time, score
    global total_fallen_balloons, last_popped_count, game_over
    
    if isinstance(key, bytes):
        key = key.decode('utf-8').lower()
    else:
        key = key.lower()
    
    if key == '\x1b':
        glutLeaveMainLoop()
        return
    
    if game_state == "MENU":
        if key == '\r':
            total_fallen_balloons = 0
            last_popped_count = 0
            popped_balloons = 0  
            game_over = False
            game_state = "PLAYING"
            return
    
    if game_state == "GAME_OVER":
        if key == 's':
            reset_game()
            game_state = "PLAYING"
            return
        elif key == 'm':
            total_fallen_balloons = 0
            last_popped_count = 0
            popped_balloons = 0  
            game_over = False
            game_state = "MENU"
            return
    
    if game_state == "PLAYING":
        if key == 'm':
            total_fallen_balloons = 0
            last_popped_count = 0
            popped_balloons = 0  
            game_over = False
            game_state = "MENU"
            return
        
        elif key == 's':
            reset_game()
            print("Game restarted!")
        
        elif key == 'f':
            angle_rad = math.radians(player_angle)
            new_x = player_x + math.cos(angle_rad) * player_speed
            new_y = player_y + math.sin(angle_rad) * player_speed
            
            half_grid = grid_size//2 * title_size - 20
            if balloon_cheat_mode:
                if abs(new_x) + auto_pop_radius > half_grid or abs(new_y) + auto_pop_radius > half_grid:
                    return
            
            player_x = new_x
            player_y = new_y
            
        elif key == 'b':
            angle_rad = math.radians(player_angle)
            new_x = player_x - math.cos(angle_rad) * player_speed
            new_y = player_y - math.sin(angle_rad) * player_speed
            
            half_grid = grid_size//2 * title_size - 20
            if balloon_cheat_mode:
                if abs(new_x) + auto_pop_radius > half_grid or abs(new_y) + auto_pop_radius > half_grid:
                    return
            
            player_x = new_x
            player_y = new_y
        
        elif key == 'l':
            angle_rad = math.radians(player_angle - 90)
            new_x = player_x + math.cos(angle_rad) * player_speed
            new_y = player_y + math.sin(angle_rad) * player_speed
            
            half_grid = grid_size//2 * title_size - 20
            if balloon_cheat_mode:
                if abs(new_x) + auto_pop_radius > half_grid or abs(new_y) + auto_pop_radius > half_grid:
                    return
            
            player_x = new_x
            player_y = new_y
            
        elif key == 'r':
            angle_rad = math.radians(player_angle + 90)
            new_x = player_x + math.cos(angle_rad) * player_speed
            new_y = player_y + math.sin(angle_rad) * player_speed
            
            half_grid = grid_size//2 * title_size - 20
            if balloon_cheat_mode:
                if abs(new_x) + auto_pop_radius > half_grid or abs(new_y) + auto_pop_radius > half_grid:
                    return
            
            player_x = new_x
            player_y = new_y
        
        elif key == 'a':
            player_angle += gun_rotation_speed
        elif key == 'd':
            player_angle -= gun_rotation_speed
        
        elif key == 'c':
            balloon_cheat_mode = not balloon_cheat_mode
            print(f"Balloon cheat mode {'enabled' if balloon_cheat_mode else 'disabled'}")
            
            if balloon_cheat_mode:
                half_grid = grid_size//2 * title_size - 20
                player_x = max(-half_grid + auto_pop_radius, min(half_grid - auto_pop_radius, player_x))
                player_y = max(-half_grid + auto_pop_radius, min(half_grid - auto_pop_radius, player_y))
        
        half_grid = grid_size//2 * title_size - 20
        if not balloon_cheat_mode:
            player_x = max(-half_grid, min(half_grid, player_x))
            player_y = max(-half_grid, min(half_grid, player_y))
        
        if current_level == 0 or current_level == 1:
            check_balloon_pop()
    
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global cam_angle, cam_height, current_level
    
    if game_state == "MENU":
        if key == GLUT_KEY_UP:
            current_level = max(0, current_level - 1)
        elif key == GLUT_KEY_DOWN:
            current_level = min(len(difficulty_levels) - 1, current_level + 1)
    
    elif game_state == "PLAYING" and camera_mode == "third_person":
        if key == GLUT_KEY_UP:
            cam_height += cam_height_speed
        elif key == GLUT_KEY_DOWN:
            cam_height = max(min_cam_height, cam_height - cam_height_speed)
        elif key == GLUT_KEY_LEFT:
            cam_angle += cam_speed
        elif key == GLUT_KEY_RIGHT:
            cam_angle -= cam_speed

        cam_angle %= 360
    
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global camera_mode
    
    if game_state == "PLAYING":
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            if camera_mode == "third_person":
                camera_mode = "first_person"
            else:
                camera_mode = "third_person"
            glutPostRedisplay()
    
    glutPostRedisplay()

def idle():
    if game_state == "PLAYING":
        if current_level == 0 or current_level == 1:
            update_balloons()
            update_chocolate()
        elif current_level == 2:
            update_balloons()
            update_enemies()
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if game_state == "MENU":
        glViewport(0, 0, window_width, window_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        draw_menu()
    
    elif game_state == "GAME_OVER":
        glViewport(0, 0, window_width, window_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        draw_text(window_width/2 - 100, window_height/2, "GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24)
        current_popped = popped_balloons - last_popped_count
        draw_text(window_width/2 - 200, window_height/2 - 50, f"You only popped {current_popped} out of 20 balloons!", GLUT_BITMAP_HELVETICA_18)
        draw_text(window_width/2 - 100, window_height/2 - 100, "Press 'S' to restart", GLUT_BITMAP_HELVETICA_18)
        draw_text(window_width/2 - 100, window_height/2 - 150, "Press 'M' for menu", GLUT_BITMAP_HELVETICA_18)
    
    else:
        setup_camera()
        
        draw_checkerboard()
        draw_boundaries()
        
        if current_level == 1 or current_level == 2:
            draw_medium_boxes()
        
        if current_level == 2:
            draw_enemies()
        
        if camera_mode == "third_person":
            draw_player()
        
        if current_level == 0 or current_level == 1:
            draw_balloons()
            
            if chocolate_active:
                draw_chocolate()
        
        elif current_level == 2:
            draw_balloons()
            
            if chocolate_active:
                draw_chocolate()
        
        draw_text(10, window_height - 30, f"Level: {difficulty_levels[current_level]}")
        draw_text(10, window_height - 60, f"Camera Mode: {camera_mode.replace('_', ' ').title()}")
        
        if current_level == 0:
            draw_text(10, window_height - 90, f"Balloons Popped: {popped_balloons}")
            draw_text(10, window_height - 120, f"Chocolates: {chocolates_collected}")
            draw_text(10, window_height - 150, f"Next Chocolate: {next_chocolate_milestone} balloons", GLUT_BITMAP_HELVETICA_12)
            current_popped = popped_balloons - last_popped_count
            draw_text(10, window_height - 180, f"Popped in this set: {current_popped}/5", GLUT_BITMAP_HELVETICA_12)
            draw_text(10, window_height - 210, f"Total Fallen: {total_fallen_balloons}/20", GLUT_BITMAP_HELVETICA_12)
            
            if balloon_cheat_mode:
                draw_text(10, window_height - 240, f"CHEAT MODE: AUTO-POP ENABLED", GLUT_BITMAP_HELVETICA_12)
                
                if camera_mode == "third_person":
                    glPushMatrix()
                    glColor4f(1.0, 0.0, 0.0, 0.3)
                    glTranslatef(player_x, player_y, 1)
                    
                    glBegin(GL_LINE_LOOP)
                    for angle in range(0, 360, 10):
                        rad = math.radians(angle)
                        x = auto_pop_radius * math.cos(rad)
                        y = auto_pop_radius * math.sin(rad)
                        glVertex3f(x, y, 0)
                    glEnd()
                    glPopMatrix()
        elif current_level == 1:
            draw_text(10, window_height - 90, f"Balloons Collected: {sum(box_collections)}")
            draw_text(10, window_height - 120, f"Chocolates: {chocolates_collected}")
            draw_text(10, window_height - 150, f"Current Box Level: {current_box_level}", GLUT_BITMAP_HELVETICA_12)
            current_popped = popped_balloons - last_popped_count
            draw_text(10, window_height - 180, f"Popped in this set: {current_popped}/5", GLUT_BITMAP_HELVETICA_12)
            draw_text(10, window_height - 210, f"Total Fallen: {total_fallen_balloons}/20", GLUT_BITMAP_HELVETICA_12)
            
            if balloon_cheat_mode:
                draw_text(10, window_height - 240, f"CHEAT MODE: AUTO-POP ENABLED", GLUT_BITMAP_HELVETICA_12)
                
                if camera_mode == "third_person":
                    glPushMatrix()
                    glColor4f(1.0, 0.0, 0.0, 0.3)
                    glTranslatef(player_x, player_y, 1)
                    
                    glBegin(GL_LINE_LOOP)
                    for angle in range(0, 360, 10):
                        rad = math.radians(angle)
                        x = auto_pop_radius * math.cos(rad)
                        y = auto_pop_radius * math.sin(rad)
                        glVertex3f(x, y, 0)
                    glEnd()
                    glPopMatrix()
        
        elif current_level == 2:
            draw_text(10, window_height - 90, f"Balloons Collected: {sum(box_collections)}")
            draw_text(10, window_height - 120, f"Chocolates: {chocolates_collected}")
            draw_text(10, window_height - 150, f"Current Box Level: {current_box_level}", GLUT_BITMAP_HELVETICA_12)
            draw_text(10, window_height - 180, "WARNING: Avoid the enemies!", GLUT_BITMAP_HELVETICA_12)
            
            if balloon_cheat_mode:
                draw_text(10, window_height - 210, f"CHEAT MODE: AUTO-POP ENABLED", GLUT_BITMAP_HELVETICA_12)
                
                if camera_mode == "third_person":
                    glPushMatrix()
                    glColor4f(1.0, 0.0, 0.0, 0.3)
                    glTranslatef(player_x, player_y, 1)
                    
                    glBegin(GL_LINE_LOOP)
                    for angle in range(0, 360, 10):
                        rad = math.radians(angle)
                        x = auto_pop_radius * math.cos(rad)
                        y = auto_pop_radius * math.sin(rad)
                        glVertex3f(x, y, 0)
                    glEnd()
                    glPopMatrix()
        
        draw_text(10, 30, "Press 'F/B' to move, 'L/R' to strafe, 'A/D' to rotate")
        draw_text(10, 10, "Press 'S' to restart, 'M' for menu, 'C' for cheat mode")
    
    glutSwapBuffers()

def reset_game():
    global balloons, popped_balloons, last_balloon_time, score, balloon_cheat_mode
    global chocolate_active, chocolates_collected, next_chocolate_milestone
    global box_collections, current_box_level, medium_reward_given
    global total_fallen_balloons, last_popped_count, game_over
    global enemies, last_enemy_time
    
    balloons = []
    popped_balloons = 0
    score = 0
    balloon_cheat_mode = False
    last_balloon_time = time.time()
    
    total_fallen_balloons = 0
    last_popped_count = 0
    game_over = False
    
    chocolate_active = False
    chocolates_collected = 0
    next_chocolate_milestone = 5
    
    box_collections = [0, 0, 0, 0, 0, 0]
    current_box_level = 0
    medium_reward_given = False
    init_medium_boxes()
    
    enemies = []
    last_enemy_time = time.time()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Navigation Game")
    
    init()
    
    reset_game()
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()