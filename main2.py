import tkinter as tk
import random

# -------- WINDOW --------
WIDTH, HEIGHT = 900, 600
window = tk.Tk()
window.title("Smart Accident Detection System")

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT)
canvas.pack()

# -------- ROAD --------
def draw_road():
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#333", outline="")

    # grass
    canvas.create_rectangle(0, 0, WIDTH, 80, fill="green", outline="")
    canvas.create_rectangle(0, HEIGHT-80, WIDTH, HEIGHT, fill="green", outline="")

    # lane divider
    for i in range(0, WIDTH, 50):
        canvas.create_rectangle(i, HEIGHT//2 - 5, i+25, HEIGHT//2 + 5, fill="white", outline="")

# -------- CAR CLASS --------
class Car:
    def __init__(self, x, y, color, ai=False):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 35
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.ai = ai

        # direction: 1 = right, -1 = left
        self.direction = random.choice([1, -1])
        self.speed = random.randint(3, 6) * self.direction

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # boundaries for player
        if not self.ai:
            self.x = max(0, min(self.x, WIDTH - self.width))
            self.y = max(80, min(self.y, HEIGHT - 80 - self.height))

    def auto_move(self):
        if self.ai:
            self.x += self.speed

            # moving right
            if self.speed > 0 and self.x > WIDTH + 50:
                self.x = -100
                self.y = random.randint(130, 220)

            # moving left
            if self.speed < 0 and self.x < -100:
                self.x = WIDTH + 50
                self.y = random.randint(350, 480)
    def draw(self):
        # body
        canvas.create_rectangle(self.x, self.y,
                                self.x+self.width, self.y+self.height,
                                fill=self.color, outline="black", width=2)

        # window
        canvas.create_rectangle(self.x+10, self.y+5,
                                self.x+50, self.y+25,
                                fill="lightblue", outline="")

        # wheels
        canvas.create_oval(self.x+5, self.y+self.height-5,
                           self.x+15, self.y+self.height+5,
                           fill="black")
        canvas.create_oval(self.x+45, self.y+self.height-5,
                           self.x+55, self.y+self.height+5,
                           fill="black")

    def get_rect(self):
        return (self.x, self.y, self.x+self.width, self.y+self.height)

    def get_speed(self):
        return abs(self.vel_x) + abs(self.vel_y) + (self.speed if self.ai else 0)


# -------- COLLISION --------
def check_collision(c1, c2):
    x1, y1, x1b, y1b = c1.get_rect()
    x2, y2, x2b, y2b = c2.get_rect()
    return not (x1b < x2 or x1 > x2b or y1b < y2 or y1 > y2b)


# -------- RESET --------
def reset_game():
    global player, traffic_cars, collision_detected, accident_text

    # Player car (center lane)
    player = Car(200, 300, "cyan")

    traffic_cars = []

    # -------- TOP LANE (LEFT → RIGHT) --------
    for _ in range(3):
        car = Car(
            random.randint(0, WIDTH),
            random.randint(130, 220),   # top lane
            "orange",
            ai=True
        )
        car.speed = random.randint(3, 6)   # positive → right
        traffic_cars.append(car)

    # -------- BOTTOM LANE (RIGHT → LEFT) --------
    for _ in range(3):
        car = Car(
            random.randint(0, WIDTH),
            random.randint(350, 480),   # bottom lane
            "yellow",
            ai=True
        )
        car.speed = -random.randint(3, 6)  # negative → left
        traffic_cars.append(car)

    # Reset states
    collision_detected = False
    accident_text = ""


# -------- INPUT --------
keys = set()

def key_press(e):
    keys.add(e.keysym.lower())

def key_release(e):
    if e.keysym in keys:
        keys.remove(e.keysym.lower())

window.bind("<KeyPress>", key_press)
window.bind("<KeyRelease>", key_release)


# -------- GAME LOOP --------
def update():
    global collision_detected, accident_text

    canvas.delete("all")
    draw_road()

    if not collision_detected:
        player.vel_x = player.vel_y = 0

        if "w" in keys: player.vel_y = -5
        if "s" in keys: player.vel_y = 5
        if "a" in keys: player.vel_x = -5
        if "d" in keys: player.vel_x = 5

        player.move()

        for car in traffic_cars:
            car.auto_move()

    # collision check with all cars
    for car in traffic_cars:
        if check_collision(player, car):
            if not collision_detected:
                collision_detected = True

                player_speed = abs(player.vel_x) + abs(player.vel_y)
                ai_speed = abs(car.speed)

                # 🟡 Case 1: Player not moving → Minor
                if player_speed == 0:
                    accident_text = "Minor Accident ⚠️"
                    color = "yellow"

                # 🔴 Case 2: Both moving → Major
                elif player_speed > 0 and ai_speed > 0:
                    accident_text = "Severe Accident 🔥"
                    color = "red"

                # 🟠 Optional fallback (rare case)
                else:
                    accident_text = "Moderate Accident 🚨"
                    color = "orange"

                player.color = color
                car.color = color

    # draw everything
    player.draw()
    for car in traffic_cars:
        car.draw()

    # UI
    canvas.create_text(450, 30, text="Smart Accident Detection System",
                       fill="white", font=("Arial", 20, "bold"))

    if collision_detected:
        canvas.create_text(450, 100, text=accident_text,
                           fill="red", font=("Arial", 22, "bold"))
        canvas.create_text(450, 140, text="Press R to Restart",
                           fill="white", font=("Arial", 14))
    else:
        canvas.create_text(120, 80, text="Status: SAFE",
                           fill="lightgreen", font=("Arial", 14, "bold"))

    canvas.create_text(450, 580,
                       text="Move: WASD | Avoid Traffic | R to Restart",
                       fill="white", font=("Arial", 12))

    window.after(16, update)


# -------- RESTART --------
def restart(e):
    if e.keysym == "r":
        reset_game()

window.bind("<KeyPress-r>", restart)

# -------- START --------
reset_game()
update()
window.mainloop()