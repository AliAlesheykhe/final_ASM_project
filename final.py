import pygame
import math
import random
import time

# مقداردهی اولیه
pygame.init()  # Initialize all imported Pygame modules
width, height = 1000, 600  # Set the width and height of the window
win = pygame.display.set_mode((width, height))  # Create the display window with specified dimensions
pygame.display.set_caption("Ball Movement")  # Set the caption for the window
durations = []

# رنگ‌ها
black = (0, 0, 0)  # RGB color for black
white = (255, 255, 255)  # RGB color for white
red = (255, 0, 0)  # RGB color for red
blue = (0, 0, 255)  # RGB color for blue

# تعریف تابع حرکت
def move_ball_path(ball):
    x, y = ball['pos']  # Get the current position of the ball
    vel_x = ball['vel_x']  # Get the horizontal velocity of the ball
    vel_y = ball['vel_y']  # Get the vertical velocity of the ball
    w = ball['w']  # Get the angular velocity or frequency for sinusoidal motion
    gravity = ball['gravity']  # Get the gravity value for parabolic motion

    start_time = time.perf_counter()

    if ball['path'] == 'straight':
        x += vel_x  # Move the ball horizontally at constant velocity
    elif ball['path'] == 'angled':
        x += vel_x  # Move the ball horizontally at constant velocity
        y -= vel_x * math.tan(math.radians(ball['angle']))  # Adjust the vertical position based on the angle
    elif ball['path'] == 'parabolic':
        x += vel_x  # Move the ball horizontally at constant velocity
        y -= vel_y  # Move the ball upwards initially
        vel_y -= gravity * 0.1  # Apply gravity over time to simulate parabolic motion
    elif ball['path'] == 'sinusoidal':
        x += vel_x  # Move the ball horizontally at constant velocity
        y = height / 2 + 50 * math.sin(w * x)  # Adjust the vertical position based on sinusoidal motion

    end_time = time.perf_counter()
    duration = end_time - start_time

    durations.append(duration)
   
    return x, y, vel_x, vel_y  # Return the updated position and vertical velocity of the ball

# لیست توپ‌ها
balls = []  # List to store all the balls
player = pygame.Rect(width - 50, height // 2 - 30, 20, 100)  # Create the player object as a rectangle
score = 0  # Initialize the player's score to zero

font = pygame.font.SysFont('Arial', 30)  # Initialize the font for displaying the score

# Timer variables
t = 0.1  # Initial seconds between shots
last_shot_time = time.time()  # Record the time when the last shot was made

running = True  # Set the running flag to True to start the game loop
while running:
    pygame.time.delay(30)  # Delay to control the frame rate
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Check if the user has requested to quit
            print(f"average time = {sum(durations) / len(durations)} seconds")
            running = False  # Set the running flag to False to exit the loop

    # Check timer and add a new ball if needed
    current_time = time.time()  # Get the current time
    if current_time - last_shot_time > t:  # Check if the time since the last shot exceeds t seconds
        path_choice = random.choice(['straight', 'angled', 'parabolic', 'sinusoidal'])  # Choose a random path
        path_choice = "sinusoidal"
        if path_choice == "parabolic":
            angle = random.randint(20, 30)
        else: 
            angle = random.randint(-20, 20)
        vel = random.randint(20, 30)  # Choose a random velocity
        vel_x = vel * math.cos(math.radians(angle))  # Calculate the horizontal velocity
        vel_y = vel * math.sin(math.radians(angle))  # Calculate the vertical velocity
        ball = {  # Create a new ball with the specified properties
            'pos': [100, height // 2],
            'path': path_choice,
            'vel_x': vel_x,
            'vel_y': vel_y if path_choice == 'parabolic' else 0,
            'angle': angle,
            'w': random.uniform(-0.05, 0.05),
            'gravity': random.randint(5, 10) if path_choice == 'parabolic' else 0
        }
        balls.append(ball)  # Add the new ball to the list of balls
        last_shot_time = current_time  # Update the last shot time

    keys = pygame.key.get_pressed()  # Get the state of all keyboard keys
    if keys[pygame.K_UP] and player.top > 0:  # Check if the up arrow key is pressed and the player is not at the top edge
        player.y -= 20  # Move the player upwards
    if keys[pygame.K_DOWN] and player.bottom < height:  # Check if the down arrow key is pressed and the player is not at the bottom edge
        player.y += 20  # Move the player downwards

    win.fill(black)  # Fill the window with black color
    for ball in balls:  # Iterate through all the balls
        ball['pos'][0], ball['pos'][1], ball["vel_x"], ball['vel_y'] = move_ball_path(ball)  # Update the position and velocity of the ball
        if player.colliderect(pygame.Rect(int(ball['pos'][0]), int(ball['pos'][1]), 10, 10)):  # Check for collision between the player and the ball
            balls.remove(ball)  # Remove the ball if a collision is detected
            score += 1  # Increase the player's score
            if score % 10 == 0:  # Check if the score is a multiple of 10
                t = max(t - 0.1, 0.1)  # Decrease t by 0.5 seconds, but not below 0.5 seconds
        pygame.draw.circle(win, red, (int(ball['pos'][0]), int(ball['pos'][1])), 10)  # Draw the ball

    pygame.draw.rect(win, blue, player)  # Draw the player
    score_text = font.render(f'Score: {score}', True, white)  # Render the score text
    win.blit(score_text, (10, 10))  # Display the score at the top left corner
    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame
