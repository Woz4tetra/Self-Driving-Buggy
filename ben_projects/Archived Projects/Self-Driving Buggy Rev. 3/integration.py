class integrate(object):

    def __init__(self, initial_value, initial_velocity, initial_acc):
        self.val = initial_value
        self.velocity = initial_velocity
        self.acc = initial_acc

    def update(self, dt, new_val = None):
        self.update_velocity(new_val)
        self.val += dt * self.velocity

    def update_velocity(self, new_acc):
        if (new_acc == None):
            continue
        else:

        self.velocity = (self)

