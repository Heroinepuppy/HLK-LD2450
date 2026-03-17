import serial #access to serial hardware
import signal #behaviour on ctrl+c

class HLK_LD2450:
    def __init__(self, Port, Speed):
        '''
            generator
                creates dictionary of objects tracked by sensor
                Handles communication parameters
        '''
        self.Port=Port
        self.Speed=Speed
        self.objectsTracked={
            "Object1":{"x": 0, 'y': 0, 'v':0, 'dres': 0},
            "Object2":{"x": 0, 'y': 0, 'v':0, 'dres': 0}, 
            "Object3":{"x": 0, 'y': 0, 'v':0, 'dres': 0}
            }                                            
   
    def closeSerial(self):
        '''
            closes serial communication port
        '''
        self.serialPort.close()

    def connSerial(self):
        '''
            Opens Serial communication port
        '''    
        try:                                                  
            self.serialPort=serial.Serial(port=self.Port, baudrate=self.Speed, timeout=2)
        except Exception as e:
            print(e)

    def getobjectsTracked(self, printing=False):
        '''
            Returns dictionary of tracked objects
        '''
        if printing == True:
            for _ in self.objectsTracked:
                print(_)
                for __ in self.objectsTracked[_]:
                    print('\t'+__+': '+str(self.objectsTracked[_][__]))

    def getSerial(self):
        '''
            Returns handle to serial port
        '''
        print(self.serialPort)
        return self.serialPort

    def getDatafromSerial(self):
        '''
            Reads data from serial port into dictionary
        '''      
        print(self.serialPort.read())


if __name__ =="__main__":
    Sensor=HLK_LD2450('/dev/ttyS0', '256000') 
    Sensor.connSerial() #make sure serial hardware is initalized (sudo raspi-config)
    Sensor.getSerial()
    while True:
        Sensor.getDatafromSerial()

