from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

# Window settings
window_width = 1000
window_height = 800

# Game variables
difficulty_levels = ["EASY", "MEDIUM", "HARD"]
current_level = 0  # 0: EASY, 1: MEDIUM, 2: HARD
game_state = "MENU"  # MENU, PLAYING, GAME_OVER
score = 0

# Grid and floor settings
GRID_LENGTH = 600
title_size = 20
grid_size = 20

# Camera settings
cam_distance = 400
cam_height = 400
cam_angle = 45
cam_speed = 5
cam_height_speed = 10
min_cam_height = 50
camera_mode = "third_person"

# Player settings
player_x = 0
player_y = 0
player_z = 0
player_angle = 0
player_speed = 3
gun_rotation_speed = 4

# Colors based on difficulty
level_colors = [
    # EASY: Brighter colors
    [
        [0.9, 0.9, 1.0],  # Light blue
        [0.6, 0.8, 0.6]   # Light green
    ],
    # MEDIUM: Medium colors
    [
        [0.7, 0.7, 0.9],  # Medium blue
        [0.4, 0.6, 0.4]   # Medium green
    ],
    # HARD: Darker colors
    [
        [0.5, 0.5, 0.8],  # Dark blue
        [0.2, 0.4, 0.2]   # Dark green
    ]
]

# Wall colors based on difficulty
wall_colors = [
    # EASY
    [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.5, 0.0, 1.0]],
    # MEDIUM
    [[0.0, 0.8, 0.0], [0.0, 0.0, 0.8], [0.0, 0.8, 0.8], [0.4, 0.0, 0.8]],
    # HARD
    [[0.0, 0.6, 0.0], [0.0, 0.0, 0.6], [0.0, 0.6, 0.6], [0.3, 0.0, 0.6]]
]

# Add balloon variables
balloons = []  # Will store [x, y, z, size, color, speed, rotation]
balloon_spawn_rate = 2.0  # Seconds between spawns
last_balloon_time = 0
balloon_colors = [
    [1.0, 0.0, 0.0],    # Red
    [0.0, 0.0, 1.0],    # Blue
    [1.0, 1.0, 0.0],    # Yellow
    [0.0, 1.0, 0.0],    # Green
    [1.0, 0.0, 1.0],    # Magenta
    [0.0, 1.0, 1.0]     # Cyan
]
popped_balloons = 0
balloon_fall_speed_min = 0.5
balloon_fall_speed_max = .1
pop_distance = 30  # Increased from 20 to 30

# Add or modify these variables for balloon spawning
balloon_spawn_distance = 100  # Max distance from player to spawn balloons
balloon_spawn_height = 150    # Height at which balloons spawn

# Add balloon cheat mode variables
balloon_cheat_mode = False  # Flag to enable/disable cheat mode
auto_pop_radius = 150       # Distance for auto-popping in cheat mode
cheat_score_multiplier = 2  # Score bonus when using cheat mode

# Modify chocolate variables for falling chocolate rewards
chocolate_active = False
chocolate_position = [0, 0, 0]  # Will be updated with x, y, fall height
chocolate_rotation = 0
chocolates_collected = 0
sparkle_size = 0
sparkle_growing = True
sparkle_speed = 0.2
chocolate_size = 8
chocolate_fall_speed = 2.0  # Speed at which chocolate falls
next_chocolate_milestone = 5  # First chocolate at 5 balloons

# Add variables for medium level boxes
box_collections = [0, 0, 0, 0, 0, 0]  # Count of balloons in each colored box
box_positions = []  # Will store [x, y, z] for each box
box_size = 15  # Size of the boxes
current_box_level = 0  # Current level all boxes have reached
medium_reward_given = False  # Flag to track if current level chocolate was given

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    init_medium_boxes()

def init_medium_boxes():
    """Initialize the positions of the 6 colored boxes"""
    global box_positions
    
    box_positions = []
    radius = 150  # Distance from center
    
    # Place boxes in a hexagon arrangement
    for i in range(6):
        angle = math.radians(i * 60)  # 6 boxes evenly spaced
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        box_positions.append([x, y, box_size/2])  # z is half height of box

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width / window_height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == "first_person":
        # First-person camera setup
        eye_x = player_x + math.cos(math.radians(player_angle)) * 15
        eye_y = player_y + math.sin(math.radians(player_angle)) * 15
        eye_z = player_z + 13  # Eye height
        
        look_x = eye_x + math.cos(math.radians(player_angle))
        look_y = eye_y + math.sin(math.radians(player_angle))
        look_z = eye_z
        
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        # Third-person camera setup (overhead view)
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
    """Draws text at specified screen coordinates"""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection for text rendering
    gluOrtho2D(0, window_width, 0, window_height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_checkerboard():
    """Draws the 3D floor with a checkerboard pattern based on current difficulty"""
    # Get colors based on current difficulty level
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
    """Draws walls around the grid perimeter"""
    wall_height = 30  
    wall_thickness = 1
    
    # Get wall colors based on current difficulty
    colors = wall_colors[current_level]

    # Right wall (x-positive)
    glColor3f(*colors[0])
    glPushMatrix()
    glTranslatef(grid_size//2 * title_size, 0, wall_height/2)  
    glScalef(wall_thickness, grid_size*title_size, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    # Left wall (x-negative)
    glColor3f(*colors[1])
    glPushMatrix()
    glTranslatef(-grid_size//2 * title_size, 0, wall_height/2)
    glScalef(wall_thickness, grid_size*title_size, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    # Back wall (y-positive)
    glColor3f(*colors[2])
    glPushMatrix()
    glTranslatef(0, grid_size//2 * title_size, wall_height/2)
    glScalef(grid_size*title_size, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

    # Front wall (y-negative)
    glColor3f(*colors[3])
    glPushMatrix()
    glTranslatef(0, -grid_size//2 * title_size, wall_height/2)
    glScalef(grid_size*title_size, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def draw_player():
    """Draw a simple player indicator"""
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + 10)  # Elevate player above floor
    glRotatef(player_angle, 0, 0, 1)
    
    # Body - increased size
    glColor3f(1.0, 1.0, 0.0)
    glPushMatrix()
    glScalef(8, 4, 15)  # Doubled size from (4,2,10) to (8,4,15)
    glutSolidCube(1)
    glPopMatrix()
    
    # Head - increased size
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 10)  # Adjusted height for the bigger body
    glutSolidSphere(5, 20, 20)  # Increased from 3 to 5
    glPopMatrix()
    
    # Add arms for better visibility
    glColor3f(0.9, 0.7, 0.0)
    # Left arm
    glPushMatrix()
    glTranslatef(0, -6, 7)
    glScalef(2, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    # Right arm
    glPushMatrix()
    glTranslatef(0, 6, 7)
    glScalef(2, 5, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()

def draw_menu():
    """Draws the game menu with difficulty selection"""
    # Draw centered title
    title_text = "Baloon Popper"
    draw_text(window_width/2 - 150, window_height - 100, title_text, GLUT_BITMAP_TIMES_ROMAN_24)
    
    # Draw difficulty options
    draw_text(window_width/2 - 100, window_height - 200, "SELECT DIFFICULTY:", GLUT_BITMAP_HELVETICA_18)
    
    y_pos = window_height - 250
    for i, level in enumerate(difficulty_levels):
        if i == current_level:
            # Highlight selected level
            draw_text(window_width/2 - 50, y_pos, f"> {level} <", GLUT_BITMAP_HELVETICA_18)
        else:
            draw_text(window_width/2 - 35, y_pos, level, GLUT_BITMAP_HELVETICA_18)
        y_pos -= 50
    
    # Draw controls info
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
    """Draw the 6 colored boxes for balloon collection"""
    if current_level != 1:  # Only in medium level
        return
    
    for i in range(6):
        # Get box position
        x, y, z = box_positions[i]
        
        # Use balloon color for the box
        color = balloon_colors[i]
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Draw the box
        glColor3f(*color)
        glutSolidCube(box_size)
        
        # Draw count text above box
        count_pos = [x, y, z + box_size]
        
        # Set up text in 3D space
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos3f(0, 0, box_size/2 + 5)
        text = str(box_collections[i])
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        glPopMatrix()

def check_medium_milestone():
    """Check if all boxes have reached a new level for chocolate reward"""
    global medium_reward_given, current_box_level, chocolate_active
    
    # Find minimum count across all boxes
    min_count = min(box_collections)
    
    # If all boxes have at least one more balloon than current level
    # and we haven't given a reward for this level yet
    if min_count > current_box_level and not medium_reward_given and not chocolate_active:
        current_box_level = min_count
        spawn_chocolate()
        medium_reward_given = True
        print(f"Medium level milestone reached! All boxes have {current_box_level} balloons!")

def add_balloon_to_box(color_index):
    """Add a balloon to its corresponding colored box"""
    global box_collections, medium_reward_given
    
    box_collections[color_index] += 1
    print(f"Added a balloon to box {color_index}. Now has {box_collections[color_index]}")
    
    # After adding, check if we've hit a new milestone
    check_medium_milestone()
    
    # If we just awarded a chocolate, reset the flag when the chocolate is gone
    if not chocolate_active and medium_reward_given:
        medium_reward_given = False

def spawn_balloon():
    """Create a new balloon close to the player's position"""
    global player_x, player_y
    
    # Generate random angle and distance from player
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(30, balloon_spawn_distance)
    
    # Calculate position relative to player
    x = player_x + math.cos(angle) * distance
    y = player_y + math.sin(angle) * distance
    
    # Make sure the balloon is within the grid boundaries
    half_grid = grid_size//2 * title_size - 20
    x = max(-half_grid, min(half_grid, x))
    y = max(-half_grid, min(half_grid, y))
    
    # Other balloon properties
    z = balloon_spawn_height
    
    # For medium level, we want even distribution of colors
    if current_level == 1:
        # Choose the color that has the fewest balloons in its box
        if len(balloons) < 6:  # In the beginning, ensure one of each color
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
    
    # Store color_index with the balloon for medium level tracking
    balloons.append([x, y, z, size, color, speed, rotation, color_index])

def update_balloons():
    """Update balloon positions and remove those that hit the ground"""
    global balloons, popped_balloons, last_balloon_time, score
    current_time = time.time()
    
    # Remove balloons that hit the ground
    balloons_to_remove = []
    for i, balloon in enumerate(balloons):
        # Update position - move downward
        balloon[2] -= balloon[5]  # z position -= speed
        
        # Check if balloon hit the ground
        if balloon[2] < 0:
            balloons_to_remove.append(i)
    
    # Auto-pop balloons in cheat mode (easy level only)
    if current_level == 0 and balloon_cheat_mode and camera_mode == "third_person":
        for i, balloon in enumerate(balloons):
            if i in balloons_to_remove:
                continue  # Skip balloons already marked for removal
                
            # Calculate distance from player to balloon
            dx = player_x - balloon[0]
            dy = player_y - balloon[1]
            dz = (player_z + 10) - balloon[2]  # Adjust player z for height
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Auto-pop balloons within radius
            if dist < auto_pop_radius:
                balloons_to_remove.append(i)
                # Give bonus score in cheat mode
                score += 10 * cheat_score_multiplier
                popped_balloons += 1
                
    # Remove balloons
    for i in sorted(balloons_to_remove, reverse=True):
        if i < len(balloons):
            balloons.pop(i)
    
    # Spawn new balloons at the set rate (both in easy and medium mode)
    if (current_level == 0 or current_level == 1) and current_time - last_balloon_time > balloon_spawn_rate:
        spawn_balloon()
        last_balloon_time = current_time

def spawn_chocolate():
    """Create a chocolate that falls from the sky near the player"""
    global chocolate_active, chocolate_position, chocolate_rotation
    
    if chocolate_active:
        return  # Already have an active chocolate
    
    # Generate position directly above the player
    x = player_x + random.uniform(-30, 30)  # Slight randomness
    y = player_y + random.uniform(-30, 30)
    z = 150  # Start high in the sky
    
    # Make sure it's within boundaries
    half_grid = grid_size//2 * title_size - 30
    x = max(-half_grid, min(half_grid, x))
    y = max(-half_grid, min(half_grid, y))
    
    # Set chocolate properties
    chocolate_position = [x, y, z]
    chocolate_rotation = random.uniform(0, 360)
    chocolate_active = True

def update_chocolate():
    """Update the falling chocolate position"""
    global chocolate_active, chocolate_position, chocolates_collected, next_chocolate_milestone
    
    if not chocolate_active:
        return
    
    # Make the chocolate fall
    chocolate_position[2] -= chocolate_fall_speed
    
    # Rotate the chocolate as it falls
    global chocolate_rotation
    chocolate_rotation = (chocolate_rotation + 2) % 360
    
    # Check if player has collected the chocolate
    dx = player_x - chocolate_position[0]
    dy = player_y - chocolate_position[1]
    dz = (player_z + 10) - chocolate_position[2]  # Adjust for player height
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Check if chocolate hit the ground or player collected it
    if chocolate_position[2] <= 5 or dist < 20:
        if dist < 20:  # Player collected it
            print(f"Chocolate collected! Total: {chocolates_collected + 1}")
        else:  # Hit the ground
            print(f"Chocolate landed! Total: {chocolates_collected + 1}")
            
        chocolate_active = False
        chocolates_collected += 1
        # Next milestone is current popped_balloons plus 5
        next_chocolate_milestone = ((popped_balloons // 5) + 1) * 5

def draw_chocolate():
    """Draw a chocolate with sparkle effect"""
    global sparkle_size, sparkle_growing
    
    if not chocolate_active:
        return
    
    x, y, z = chocolate_position
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(chocolate_rotation, 0, 1, 1)
    
    # Draw sparkle effect
    glColor3f(1.0, 1.0, 0.5)  # Golden color
    glutWireSphere(chocolate_size + sparkle_size, 10, 10)
    
    # Update sparkle size for animation
    if sparkle_growing:
        sparkle_size += sparkle_speed
        if sparkle_size > 3:
            sparkle_growing = False
    else:
        sparkle_size -= sparkle_speed
        if sparkle_size < 0.5:
            sparkle_growing = True
    
    # Draw chocolate (brown cube)
    glColor3f(0.5, 0.25, 0.0)  # Brown color
    glutSolidCube(chocolate_size)
    
    glPopMatrix()

def check_balloon_pop():
    """Check if player has popped any balloons"""
    global balloons, popped_balloons, score, next_chocolate_milestone
    
    # Only check in third person mode
    if camera_mode != "third_person":
        return
        
    balloons_to_pop = []
    for i, balloon in enumerate(balloons):
        # Calculate distance from player to balloon
        dx = player_x - balloon[0]
        dy = player_y - balloon[1]
        dz = (player_z + 10) - balloon[2]  # Adjust player z for height
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # If player is close enough, pop the balloon
        if dist < pop_distance:
            balloons_to_pop.append(i)
            score += 10  # Add to score
            popped_balloons += 1
            
            # For medium level, add to the appropriate box
            if current_level == 1 and len(balloon) > 7:  # Make sure we have color_index
                color_index = balloon[7]
                add_balloon_to_box(color_index)
    
    # Remove popped balloons
    for i in sorted(balloons_to_pop, reverse=True):
        balloons.pop(i)
    
    # Check for easy-level chocolate (only for level 0)
    if current_level == 0 and popped_balloons >= next_chocolate_milestone and not chocolate_active:
        spawn_chocolate()
        print(f"Easy level chocolate spawned at milestone: {next_chocolate_milestone}")

def draw_balloon(x, y, z, size, color, rotation):
    """Draw a single balloon"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 0, 1)
    
    # Draw balloon body (sphere)
    glColor3f(*color)
    glutSolidSphere(size, 20, 20)
    
    # Draw balloon tie (small sphere at bottom)
    glColor3f(0.7, 0.7, 0.7)
    glTranslatef(0, 0, -size)
    glutSolidSphere(size/4, 10, 10)
    
    # Draw string
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -size*3)
    glEnd()
    
    glPopMatrix()

def draw_balloons():
    """Draw all active balloons"""
    for balloon in balloons:
        if len(balloon) > 7:  # New format with color_index
            x, y, z, size, color, speed, rotation, _ = balloon
        else:
            x, y, z, size, color, speed, rotation = balloon
        draw_balloon(x, y, z, size, color, rotation)

def keyboardListener(key, x, y):
    """Handles keyboard inputs"""
    global player_x, player_y, player_angle, game_state, current_level, balloon_cheat_mode
    global balloons, popped_balloons, last_balloon_time, score
    
    if isinstance(key, bytes):
        key = key.decode('utf-8').lower()
    else:
        key = key.lower()
    
    if key == '\x1b':  # ESC key
        glutLeaveMainLoop()
        return
    
    if game_state == "MENU":
        if key == '\r':  # Enter key
            game_state = "PLAYING"
            return
    
    if game_state == "PLAYING":
        if key == 'm':  # Return to menu
            game_state = "MENU"
            return
        
        # Restart game with 's' key
        elif key == 's':
            # Reset game state
            balloons = []
            popped_balloons = 0
            score = 0
            balloon_cheat_mode = False
            last_balloon_time = time.time()
            player_x = 0
            player_y = 0
            player_angle = 0
            print("Game restarted!")
        
        # Forward/backward movement
        elif key == 'f':  # Forward (changed from 'w')
            # Forward movement (along player's facing direction)
            angle_rad = math.radians(player_angle)
            player_x += math.cos(angle_rad) * player_speed
            player_y += math.sin(angle_rad) * player_speed
        elif key == 'b':  # Backward (changed from 's')
            # Backward movement (opposite to player's facing direction)
            angle_rad = math.radians(player_angle)
            player_x -= math.cos(angle_rad) * player_speed
            player_y -= math.sin(angle_rad) * player_speed
        
        # Left/right movement (strafe)
        elif key == 'l':  # Strafe left (changed from 'q')
            # Strafe left (perpendicular to player's facing direction)
            angle_rad = math.radians(player_angle - 90)  # 90 degrees to the left
            player_x += math.cos(angle_rad) * player_speed
            player_y += math.sin(angle_rad) * player_speed
        elif key == 'r':  # Strafe right (changed from 'e')
            # Strafe right (perpendicular to player's facing direction)
            angle_rad = math.radians(player_angle + 90)  # 90 degrees to the right
            player_x += math.cos(angle_rad) * player_speed
            player_y += math.sin(angle_rad) * player_speed
        
        # Rotation controls - kept the same
        elif key == 'a':
            player_angle += gun_rotation_speed
        elif key == 'd':
            player_angle -= gun_rotation_speed
        
        # Toggle balloon cheat mode with 'c' key
        elif key == 'c':
            if current_level == 0:  # Only enable in Easy mode
                balloon_cheat_mode = not balloon_cheat_mode
                print(f"Balloon cheat mode {'enabled' if balloon_cheat_mode else 'disabled'}")
        
        # Boundary checking to keep player within floor
        half_grid = grid_size//2 * title_size - 20
        player_x = max(-half_grid, min(half_grid, player_x))
        player_y = max(-half_grid, min(half_grid, player_y))
        
        # Add check for balloon popping after movement
        if current_level == 0 or current_level == 1:  # Check in both easy and medium mode
            check_balloon_pop()
    
    glutPostRedisplay()

def specialKeyListener(key, x, y):
    """Handles special key inputs (arrow keys)"""
    global cam_angle, cam_height, current_level
    
    if game_state == "MENU":
        # Menu navigation
        if key == GLUT_KEY_UP:
            current_level = max(0, current_level - 1)
        elif key == GLUT_KEY_DOWN:
            current_level = min(len(difficulty_levels) - 1, current_level + 1)
    
    elif game_state == "PLAYING" and camera_mode == "third_person":
        # Camera controls in third-person mode (from sample code)
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
    """Handles mouse inputs"""
    global camera_mode
    
    if game_state == "PLAYING":
        # Toggle between first and third person views with right mouse button
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            if camera_mode == "third_person":
                camera_mode = "first_person"
            else:
                camera_mode = "third_person"
            glutPostRedisplay()
    
    glutPostRedisplay()

def idle():
    """Idle function that runs continuously"""
    if game_state == "PLAYING":
        if current_level == 0 or current_level == 1:  # Update in both easy and medium mode
            update_balloons()
            # Update falling chocolate
            update_chocolate()
    glutPostRedisplay()

def display():
    """Display function to render the game scene"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if game_state == "MENU":
        # 2D Interface for menu
        glViewport(0, 0, window_width, window_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        draw_menu()
    
    else:  # PLAYING
        # 3D environment
        setup_camera()
        
        # Draw environment
        draw_checkerboard()
        draw_boundaries()
        
        # Draw boxes for medium level
        if current_level == 1:
            draw_medium_boxes()
        
        # Draw player (only in third-person view)
        if camera_mode == "third_person":
            draw_player()
        
        # Draw balloons in easy mode
        if current_level == 0 or current_level == 1:
            draw_balloons()
            
            # Draw falling chocolate if active
            if chocolate_active:
                draw_chocolate()
        
        # Display game info
        draw_text(10, window_height - 30, f"Level: {difficulty_levels[current_level]}")
        draw_text(10, window_height - 60, f"Camera Mode: {camera_mode.replace('_', ' ').title()}")
        
        # Display balloon score and chocolate count in easy mode
        if current_level == 0:
            draw_text(10, window_height - 90, f"Balloons Popped: {popped_balloons}")
            draw_text(10, window_height - 120, f"Chocolates: {chocolates_collected}")
            draw_text(10, window_height - 150, f"Next Chocolate: {next_chocolate_milestone} balloons", GLUT_BITMAP_HELVETICA_12)
            
            # Display cheat mode status if active
            if balloon_cheat_mode:
                draw_text(10, window_height - 180, f"CHEAT MODE: AUTO-POP ENABLED", GLUT_BITMAP_HELVETICA_12)
                
                # Draw auto-pop radius as a circle on the floor
                if camera_mode == "third_person":
                    glPushMatrix()
                    glColor4f(1.0, 0.0, 0.0, 0.3)  # Transparent red
                    glTranslatef(player_x, player_y, 1)  # Just above the floor
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
        
        # Instructions - updated to show new controls
        draw_text(10, 30, "Press 'F/B' to move, 'L/R' to strafe, 'A/D' to rotate")
        draw_text(10, 10, "Press 'S' to restart, 'M' for menu, 'C' for cheat mode")
    
    glutSwapBuffers()

def reset_game():
    """Reset the game state when changing modes or starting a new game"""
    global balloons, popped_balloons, last_balloon_time, score, balloon_cheat_mode
    global chocolate_active, chocolates_collected, next_chocolate_milestone
    global box_collections, current_box_level, medium_reward_given
    
    balloons = []
    popped_balloons = 0
    score = 0
    balloon_cheat_mode = False
    last_balloon_time = time.time()
    
    # Reset chocolate variables
    chocolate_active = False
    chocolates_collected = 0
    next_chocolate_milestone = 5
    
    # Reset medium level variables
    box_collections = [0, 0, 0, 0, 0, 0]
    current_box_level = 0
    medium_reward_given = False
    init_medium_boxes()

def main():
    """Initialize and start the game"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Navigation Game")
    
    # Initialize OpenGL settings
    init()
    
    # Initialize balloon system
    reset_game()
    
    # Register callbacks
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    main()