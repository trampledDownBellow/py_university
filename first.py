import random
import time

def action():
    actions = [
        lambda: print("..."),
        lambda: time.sleep(1),
        lambda: print("\n" * 10),
        lambda: random.randint(1, 100)
    ]
    random.choice(actions)()

if __name__ == "__main__":
    while True:
        action()
        time.sleep(0.5)
