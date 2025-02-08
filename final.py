import tkinter as tk
import math
import random
import time

class BallGame:
    def __init__(self, root):
        self.width, self.height = 1000, 600
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='black')
        self.canvas.pack()
        self.durations1 = []
        self.durations2 = []
        self.balls = []
        self.player = self.canvas.create_rectangle(self.width - 50, self.height // 2 - 30, self.width - 30, self.height // 2 + 80, fill='blue')
        self.score = 0
        self.interval = 0.001
        self.t = self.interval
        self.last_shot_time = time.time()
        self.ballCount = 0
        self.running = True
        self.root = root
        self.score_text = self.canvas.create_text(10, 10, anchor='nw', fill='white', font=('Arial', 30), text='Score: 0')
        self.ball_radius = 10  # Set the radius of the ball
        self.update_game()

    def move_ball_path(self, ball):
        x, y = ball['pos']
        vel_x = ball['vel_x']
        vel_y = ball['vel_y']
        w = ball['w']
        gravity = ball['gravity']

        start_time = time.perf_counter()

        if ball['path'] == 'straight':
            x += vel_x
        elif ball['path'] == 'angled':
            x += vel_x
            y -= vel_x * math.tan(math.radians(ball['angle']))
        elif ball['path'] == 'parabolic':
            x += vel_x
            y -= vel_y
            vel_y -= gravity * 0.1
        elif ball['path'] == 'sinusoidal':
            x += vel_x
            y = self.height / 2 + 50 * math.sin(w * x)

        end_time = time.perf_counter()
        duration = end_time - start_time

        self.durations1.append(duration)

        return x, y, vel_x, vel_y

    def update_game(self):
        if not self.running:
            return

        current_time = time.time()
        if current_time - self.last_shot_time > self.t:
            path_choice = random.choice(['straight', 'angled', 'parabolic', 'sinusoidal'])
            if path_choice == 'parabolic':
                angle = random.randint(20, 30)
            else:
                angle = random.randint(-20, 20)
            vel = random.randint(20, 30)
            vel_x = vel * math.cos(math.radians(angle))
            vel_y = vel * math.sin(math.radians(angle))
            ball = {
                'pos': [100, self.height // 2],
                'path': path_choice,
                'vel_x': vel_x,
                'vel_y': vel_y if path_choice == 'parabolic' else 0,
                'angle': angle,
                'w': random.uniform(-0.05, 0.05),
                'gravity': random.randint(5, 10) if path_choice == 'parabolic' else 0,
                'id': self.canvas.create_oval(100, self.height // 2, 100 + self.ball_radius * 2, self.height // 2 + self.ball_radius * 2, fill='red')
            }
            self.balls.append(ball)
            self.ballCount += 1
            if self.ballCount == 1001:
                print(f"average time for calculations= {sum(self.durations1) / len(self.durations1)} seconds")
                print(f"average time for drawing= {sum(self.durations2) / len(self.durations2)} seconds")
                self.running = False
            self.last_shot_time = current_time

        start_time = time.perf_counter()

        for ball in self.balls[:]:
            ball['pos'][0], ball['pos'][1], ball["vel_x"], ball['vel_y'] = self.move_ball_path(ball)
            self.canvas.coords(ball['id'], ball['pos'][0], ball['pos'][1], ball['pos'][0] + self.ball_radius * 2, ball['pos'][1] + self.ball_radius * 2)

            if self.canvas.bbox(self.player)[2] > ball['pos'][0] > self.canvas.bbox(self.player)[0] and \
               self.canvas.bbox(self.player)[3] > ball['pos'][1] > self.canvas.bbox(self.player)[1]:
                self.balls.remove(ball)
                self.canvas.delete(ball['id'])
                self.score += 1
                if self.score % 10 == 0:
                    self.t = max(self.t - self.interval, self.interval)
                self.canvas.itemconfig(self.score_text, text=f'Score: {self.score}')

        end_time = time.perf_counter()
        self.durations2.append(end_time - start_time)

        self.root.after(30, self.update_game)

    def move_player_up(self, event):
        if self.canvas.coords(self.player)[1] > 0:
            self.canvas.move(self.player, 0, -20)

    def move_player_down(self, event):
        if self.canvas.coords(self.player)[3] < self.height:
            self.canvas.move(self.player, 0, 20)

def main():
    root = tk.Tk()
    game = BallGame(root)
    root.bind('<Up>', game.move_player_up)
    root.bind('<Down>', game.move_player_down)
    start_time = time.perf_counter()
    root.mainloop()
    end_time = time.perf_counter()
    print(f"total time: {end_time - start_time}")

if __name__ == '__main__':
    main()
