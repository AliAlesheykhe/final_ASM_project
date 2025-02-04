import pygame
import math
import random
import time
import ctypes


# Path to the shared library
lib_path = "/media/aa/84423E3E423E34F0/University/computer structure and language/final project/final with asm/libballmotion.so"

# Load the shared library
lib = ctypes.CDLL(lib_path)

# Define the argument and return types for the C functions
lib.move_parabolic.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
                               ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]

lib.move_sinusoidal.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
                                ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]

lib.move_angled.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
                            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]

# Initialize pygame
pygame.init()
width, height = 1000, 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ball Movement")
durations = []

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)

# Function to move the ball based on its path
def move_ball_path(ball):
    x = ctypes.c_double(ball['pos'][0])
    y = ctypes.c_double(ball['pos'][1])
    vel_x = ctypes.c_double(ball['vel_x'])
    vel_y = ctypes.c_double(ball['vel_y'])
    gravity = ctypes.c_double(ball['gravity'] * 0.1)
    w = ctypes.c_double(ball['w'])
    angle = ctypes.c_double(math.radians(ball['angle']))
    amp = ctypes.c_double(20)
    
    
    # Update the ball's position based on its path
    if ball['path'] == 'straight':
        x.value += vel_x.value
    elif ball['path'] == 'angled':
        lib.move_angled(ctypes.byref(x), ctypes.byref(y), ctypes.byref(vel_x), ctypes.byref(angle))
    elif ball['path'] == 'parabolic':
        lib.move_parabolic(ctypes.byref(x), ctypes.byref(y), ctypes.byref(vel_x), ctypes.byref(vel_y), ctypes.byref(gravity))
        ball['vel_y'] = vel_y.value
    elif ball['path'] == 'sinusoidal':
        start_time = time.perf_counter()

        lib.move_sinusoidal(ctypes.byref(x), ctypes.byref(y), ctypes.byref(vel_x), ctypes.byref(w), ctypes.byref(amp))

        end_time = time.perf_counter()
        duration = end_time - start_time
        durations.append(duration)
    

    

    return x.value, y.value, vel_x.value, vel_y.value

# List of balls
balls = []
# Player paddle
player = pygame.Rect(width - 50, height // 2 - 30, 20, 100)
score = 0

# Font for displaying the score
font = pygame.font.SysFont('Arial', 30)

# Timer variables
t = 3
last_shot_time = time.time()

# Game loop
running = True
while running:
    pygame.time.delay(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print(f"average time = {sum(durations) / len(durations)} seconds")
            running = False

    current_time = time.time()
    if current_time - last_shot_time > t:
        path_choice = random.choice(['straight', 'angled', 'parabolic', 'sinusoidal'])
        path_choice = "sinusoidal"
        if path_choice == "parabolic":
            angle = random.randint(20, 30)
        else: 
            angle = random.randint(-20, 20)
        vel = random.randint(20, 30)
        vel_x = vel * math.cos(math.radians(angle))
        vel_y = vel * math.sin(math.radians(angle))
        ball = {
            'pos': [100, height // 2],
            'path': path_choice,
            'vel_x': vel_x,
            'vel_y': vel_y if path_choice == 'parabolic' else 0,
            'angle': angle,
            'w': random.uniform(-0.05, 0.05),
            'gravity': random.randint(5, 10) if path_choice == 'parabolic' else 0
        }
        balls.append(ball)
        last_shot_time = current_time

    # Move player paddle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= 20
    if keys[pygame.K_DOWN] and player.bottom < height:
        player.y += 20

    # Draw background
    win.fill(black)
    for ball in balls:
        # Move and draw the ball
        ball['pos'][0], ball['pos'][1], ball["vel_x"], ball['vel_y'] = move_ball_path(ball)
        
        if player.colliderect(pygame.Rect(int(ball['pos'][0]), int(ball['pos'][1]), 10, 10)):
            balls.remove(ball)
            score += 1
            if score % 10 == 0:
                t = max(t - 0.5, 0.5)
        pygame.draw.circle(win, red, (int(ball['pos'][0]), int(ball['pos'][1])), 10)

    # Draw player paddle
    pygame.draw.rect(win, blue, player)
    # Display the score
    score_text = font.render(f'Score: {score}', True, white)
    win.blit(score_text, (10, 10))
    pygame.display.update()

pygame.quit()
