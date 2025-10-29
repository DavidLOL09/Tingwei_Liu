import time

def slow_function():
    time.sleep(0.5)
    for i in range(3):
        time.sleep(0.2)
    print("Done")

if __name__ == "__main__":
    slow_function()