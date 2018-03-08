import math
import numpy as np
y = 0
p = 0
r = 0
yaw = math.radians(y)
pitch = math.radians(p)
roll = math.radians(r)
Rx = np.mat([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]])
Ry = np.mat([[math.cos(pitch), 0, math.sin(pitch)], [0, 1, 0], [-math.sin(pitch), 0, math.cos(pitch)]])
Rz = np.mat([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
Vx = np.mat([[1], [0], [0]])
Vy = np.mat([[0], [1], [0]])
Vz = np.mat([[0], [0], [1]])
Vxx = Rx * Ry * Rz * Vx
Vyy = Rx * Ry * Rz * Vy
Vzz = Rx * Ry * Rz * Vz

sum = (Vxx.T*Vxx).tolist()[0] + (Vyy.T*Vyy).tolist()[0] + (Vzz.T*Vzz).tolist()[0]
print(Vxx.tolist(), Vyy.tolist(), Vzz.tolist())
print(sum)