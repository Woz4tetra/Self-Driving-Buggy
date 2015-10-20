import time


class PID:
    def __init__(self):
        self.prev_time = time.time()
        self.prev_error = 0
        self.integral = 0
        self.derivative = 0
        self.output = 0
        self.prop_const = 1
        self.int_const = 1
        self.deriv_const = 1

    def update(self, measured_value, set_point):
        time1 = time.time()
        error = self.error_finder(set_point, measured_value)
        dt = time1 - self.prev_time
        self.integral = self.integral + error * dt
        self.derivative = (error - self.prev_error) / dt
        self.output = (self.prop_const * error +
                      self.int_const * self.integral +
                      self.deriv_const * self.derivative)  # need to calibrate this like hell
        self.prev_error = error
        self.prev_time = time1

    def error_finder(self, set, measured):
        lat1, long1, theta1 = set
        lat2, long2, theta2 = measured
        dist = ((lat1 - lat2) ** 2 + (long1 - long2) ** 2) ** 0.5
        return dist + abs(theta1 - theta2)
