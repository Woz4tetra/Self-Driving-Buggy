
from controllers.pid import PID


if __name__ == '__main__':
    pid = PID()

    current = (0, 0, 0)

    while True:
        goal_raw = raw_input("goal: ")
        latitude, longitude, theta = [float(element) for element in goal_raw.split(",")]

        for _ in xrange(100):
            pid.update((latitude, longitude, theta), current)
            print(pid.output)



