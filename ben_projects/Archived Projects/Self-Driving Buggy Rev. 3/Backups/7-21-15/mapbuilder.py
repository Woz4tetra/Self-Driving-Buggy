import buggyinfo
import arduino
import draw
import kalman
import mapmaker

def run():
    IMU = arduino.IMU()
    
    start = (0, 0)
    end = (200, 200)
    grid, start, end = mapmaker.read()
    
    mToI = 1
    
    posX = buggyinfo.Position(start[0], metersToIndex=mToI)
    posY = buggyinfo.Position(start[1], metersToIndex=mToI)
    posZ = buggyinfo.Position(0, initialV=1, metersToIndex=mToI)

    drawer = draw.Drawer(300, 300, 700, 700, start, end)
    
    while drawer.done is False:
        accel, gyro, dt = IMU.getIMU()
        
        accel.x = 0.01
        accel.y = 0.01
        dt = 1
        
        posX.update(accel.x, dt)
        posY.update(accel.y, dt)
        posZ.update(accel.z, dt)
        
        drawer.updateNode(posX.convert(), posY.convert(), posZ.convert(), False)
        
        drawer.loop()
        drawer.drawParticle(int(posX), int(posY))
        drawer.update()

if __name__ == '__main__':
    run()