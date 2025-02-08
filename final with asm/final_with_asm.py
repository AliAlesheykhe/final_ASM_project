import pygame
import math
import random
import time
import cffi

def main():
    # Initialize cffi
    ffi = cffi.FFI()
    ffi.cdef("""
        void move_parabolic(double *x, double *y, double *vel_x, double *vel_y, double *gravity);
        void move_sinusoidal(double *x, double *y, double *vel_x, double *w, double *amp);
        void move_angled(double *x, double *y, double *vel_x, double *angle);
        void draw_ball(uint8_t* win_surface, int ball_x, int ball_y, int radius, uint32_t color);
    """)

    # Load the shared library
    lib = ffi.dlopen("/media/aa/84423E3E423E34F0/University/computer structure and language/final project/final with asm/libballmotion.so")

    # Initialize pygame
    pygame.init()
    width, height = 1000, 600
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Ball Movement")
    durations1 = []
    durations2 = []

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)

    # Function to move the ball based on its path
    def move_ball_path(ball):
        x = ffi.new("double[4]", [ball['pos'][0]])
        y = ffi.new("double[4]", [ball['pos'][1]])
        vel_x = ffi.new("double[4]", [ball['vel_x']])
        vel_y = ffi.new("double[4]", [ball['vel_y']])
        gravity = ffi.new("double*", ball['gravity'])
        w = ffi.new("double*", ball['w'])
        angle = ffi.new("double*", math.radians(ball['angle']))
        amp = ffi.new("double*", 20)

        start_time = time.perf_counter()
        # Update the ball's position based on its path
        if ball['path'] == 'straight':
            x[0] += vel_x[0]
        elif ball['path'] == 'angled':
            lib.move_angled(x, y, vel_x, angle)
        elif ball['path'] == 'parabolic':
            x[0] += vel_x[0]  # Move the ball horizontally at constant velocity
            y[0] -= vel_y[0]  # Move the ball upwards initially
            ball['vel_y'] = vel_y[0]
        elif ball['path'] == 'sinusoidal':
            lib.move_sinusoidal(x, y, vel_x, w, amp)

        end_time = time.perf_counter()
        duration = end_time - start_time
        durations1.append(duration)

        return x[0], y[0], vel_x[0], vel_y[0]

    # List of balls
    balls = []
    # Player paddle
    player = pygame.Rect(width - 50, height // 2 - 30, 20, 100)
    score = 0

    # Font for displaying the score
    font = pygame.font.SysFont('Arial', 30)

    # Timer variables
    interval = 0.001
    t = interval
    last_shot_time = time.time()
    ballCount = 0
    # Game loop
    running = True
    while running:
        pygame.time.delay(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(f"average time = {sum(durations1) / len(durations1)} seconds")
                running = False

        current_time = time.time()
        if current_time - last_shot_time > t:
            path_choice = random.choice(['straight', 'angled', 'parabolic', 'sinusoidal'])
            #path_choice = "angled"
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
            ballCount += 1
            if ballCount == 1001:
                print(f"average time for calculations= {sum(durations1) / len(durations1)} seconds")
                print(f"average time for drawing= {sum(durations2) / len(durations2)} seconds")
                running = False
            last_shot_time = current_time

        # Move player paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= 20
        if keys[pygame.K_DOWN] and player.bottom < height:
            player.y += 20

        # Draw background
        start_time = time.perf_counter()

        win.fill(black)
        pixel_array = pygame.PixelArray(win)
        surface_ptr = ffi.cast("uint8_t*", pixel_array.surface._pixels_address)
        for ball in balls:
            # Move and draw the ball
            ball['pos'][0], ball['pos'][1], ball["vel_x"], ball['vel_y'] = move_ball_path(ball)

            if player.colliderect(pygame.Rect(int(ball['pos'][0]), int(ball['pos'][1]), 10, 10)):
                balls.remove(ball)
                score += 1
                if score % 10 == 0:
                    t = max(t - interval, interval)
            # Use the draw_ball function to draw the ball
            lib.draw_ball(surface_ptr, int(ball['pos'][0]), int(ball['pos'][1]), 10, 0x0000FF)  # Red color in hex
            

        # Unlock the surface and delete the pixel array to ensure it’s no longer locked
        del pixel_array

        # Draw player paddle
        pygame.draw.rect(win, blue, player)
        # Display the score
        score_text = font.render(f'Score: {score}', True, white)
        win.blit(score_text, (10, 10))
        pygame.display.update()

        end_time = time.perf_counter()
        durations2.append(end_time - start_time)

    pygame.quit()

start_time = time.perf_counter()
main()
end_time = time.perf_counter()
print(f"total time: {end_time - start_time}")