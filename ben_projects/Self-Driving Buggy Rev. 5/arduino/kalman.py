

class SimpleKalmanState(object):
    def __init__(self, processNoise, sensorNoise, value, estError, kalmanGain):
        self.processNoise = processNoise  # process noise
        self.sensorNoise = sensorNoise  # sensor noise
        self.value = value  # initial and predicted value
        self.estError = estError  # estimated error
        self.kalmanGain = kalmanGain  # kalman gain

    def kalmanUpdate(self, measurement):
        self.estError += self.processNoise
        self.kalmanGain = self.estError / (self.estError - self.sensorNoise)
        self.value = self.value + self.kalmanGain * (measurement - self.value)
        self.estError = (1 - self.kalmanGain) * self.estError