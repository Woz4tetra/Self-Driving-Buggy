import math
import scipy.integrate
import time

sign = 1
data = []

# square wave accel:
#for x0 in xrange(1000):
#     if x0 % 50 == 0:
#          sign *= -1
#     data.append(10 * sign)

# constant:
#data = [1] + [0] * (1000 - 1)
data = [0.01] * 1000
#print data

v = scipy.integrate.cumtrapz(data, initial=0, dx=0.5) # formula: initialV + avg(a_previous, a_current)
s = scipy.integrate.cumtrapz(v, initial=0, dx=0.5)

print list(s)