import tkinter as tk
import math
import random
import time
import cffi
from PIL import Image, ImageTk

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

    # Initialize Tkinter
    root = tk.Tk()
    width, height = 1000, 600
    canvas = tk.Canvas(root, width=width, height=height, bg="black")
    canvas.pack()
    durations1 = []
    durations2 = []

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 0, 255)

    # Ball radius variable
    ball_radius = 10

    # Create a buffer image for drawing
    buffer_image = Image.new("RGBA", (width, height), black)
    buffer_data = ffi.new("uint8_t[]", buffer_image.tobytes())
    buffer_tk = ImageTk.PhotoImage(buffer_image)
    canvas_image = canvas.create_image(0, 0, anchor="nw", image=buffer_tk)

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
    player = canvas.create_rectangle(width - 50, height // 2 - 30, width - 30, height // 2 + 80, fill="blue")
    score = 0

    # Timer variables
    interval = 0.001
    t = interval
    last_shot_time = time.time()
    ballCount = 0
    # Label for displaying the score
    score_text = canvas.create_text(10, 10, anchor="nw", fill="white", font=("Arial", 30), text=f"Score: {score}")

    # Function to update the game
    def update_game():
        nonlocal last_shot_time, ballCount, score, t, running, buffer_image, buffer_data, buffer_tk

        if not running:
            return

        current_time = time.time()
        if current_time - last_shot_time > t:
            path_choice = random.choice(['straight', 'angled', 'parabolic', 'sinusoidal'])
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

        start_time = time.perf_counter()

        # Clear the buffer
        buffer_image.paste((0, 0, 0, 0), (0, 0, width, height))
        buffer_data = ffi.new("uint8_t[]", buffer_image.tobytes())

        for ball in balls[:]:
            ball['pos'][0], ball['pos'][1], ball["vel_x"], ball['vel_y'] = move_ball_path(ball)

            if canvas.bbox(player)[2] > ball['pos'][0] > canvas.bbox(player)[0] and \
               canvas.bbox(player)[3] > ball['pos'][1] > canvas.bbox(player)[1]:
                balls.remove(ball)
                score += 1
                if score % 10 == 0:
                    t = max(t - interval, interval)
                canvas.itemconfig(score_text, text=f"Score: {score}")

            # Use the draw_ball function to draw the ball on the buffer
            lib.draw_ball(buffer_data, int(ball['pos'][0]), int(ball['pos'][1]), ball_radius, 0xFF0000)  # Red color in hex

        end_time = time.perf_counter()
        durations2.append(end_time - start_time)

        # Update the canvas with the buffer image
        buffer_image = Image.frombytes("RGBA", (width, height), bytes(buffer_data))
        buffer_tk = ImageTk.PhotoImage(buffer_image)
        canvas.itemconfig(canvas_image, image=buffer_tk)
        canvas.image = buffer_tk

        root.after(30, update_game)

    # Function to move player paddle up
    def move_player_up(event):
        if canvas.coords(player)[1] > 0:
            canvas.move(player, 0, -20)

    # Function to move player paddle down
    def move_player_down(event):
        if canvas.coords(player)[3] < height:
            canvas.move(player, 0, 20)

    # Bind keys for player paddle movement
    root.bind('<Up>', move_player_up)
    root.bind('<Down>', move_player_down)

    # Start the game loop
    running = True
    update_game()
    root.mainloop()

# Measure total time taken for the game
start_time = time.perf_counter()
main()
end_time = time.perf_counter()
print(f"total time: {end_time - start_time}")
