import serial                                                                               #access to serial hardware on RPi Zero 2 W
import os                                                                                   #for clearing terminal                                                                      
import time

class HLK_LD2450:
    '''
        The HLK_LD24560 is advertised as a RADAR sensor:
            - which can track up to 3 objects at a time
            - human presence detector
    '''
    def __init__(self, Port, Speed):
        '''
            generator
                creates dictionary of objects tracked by sensor
                Handles communication parameters
        '''
        
        self.serialPort = serial.Serial()
        self.serialPort.port=Port
        self.serialPort.baudrate=Speed
        self.serialPort.timeout=2
        self.objectsTracked={
            "Object1":{"x_mm": 0, 'y_mm': 0, 'v_cm/s':0, 'dres_mm': 0},
            "Object2":{"x_mm": 0, 'y_mm': 0, 'v_cm/s':0, 'dres_mm': 0}, 
            "Object3":{"x_mm": 0, 'y_mm': 0, 'v_cm/s':0, 'dres_mm': 0}
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
        print('Attempting to open serial port')
        try:                                                  
            self.serialPort.open()
            while not self.serialPort.is_open:
                pass
            print('DONE!')
        except Exception as e:
            print(e)


    def getobjectsTracked(self, printing=False):
        '''
            Returns dictionary of tracked objects
        '''
        if printing == True:
            for _ in self.objectsTracked:
                print(_+':')
                for __ in self.objectsTracked[_]:
                    print('\t'+__+': '+str(self.objectsTracked[_][__]))
        return self.objectsTracked

    def getSerial(self):
        '''
            Returns handle to serial port
        '''
        return self.serialPort

    def flushSerial(self):
        self.serialPort.flushOutput()
        self.serialPort.flushInput()

    def getDatafromSerial(self):
        '''
            Reads data from serial port into dictionary
        '''      
        message=self.serialPort.read(30)
        message=self.converString(message)
        data=self.splitString(message)
        self.updateObjectsTracked(data)

    def converString(self, message):
        return message.hex()
    
    def splitString(self, datastring=''):
        '''
            Splits string read from serial port into components representing the tracked objects
        '''
        #datastring= "AAFF03000E03B186100040010000000000000000000000000000000055CC" example from manual
        try:
            data=datastring.split('aaff0300')[1]                                                    #cut away header
            data=data.split('55cc')[0]                                                              #cut away end of frame - now that i ahve hardware running, this sequence is never in the data read from serial port 
            target1, target2, target3 = [data[i: i+16] for i in range(0, len(data),16)]             #part string into chunks representing the tracked objects 
            return [target1, target2, target3]
        except Exception as e:
                print(e)

    def swapBytes(self, data):
        '''
            Swaps high bits 8-15 and low bits 0-7
        '''
        returnData = []
        for values in data:
            returnData.append(((int(values,16)&0xFF00)>>8) + ((int(values,16)&0xFF)<<8))
        return returnData                                                                       #above lines already cast it into an integer

    def subtractOffset(self, data):
        '''
            substracts offset from x,y,v
        '''
        returnData = []
        for values in data:
            if values >= 0x8000:                                                               # vales > 0x8000 (0b1000 0000 0000 0000) need to substract the leading 1 because thats just the +-sign and not the value
                returnData.append(values-0x8000)
            if values < 0x8000:
                returnData.append(0-values)                                                    # if values <0x8000 that means it is points towards negative direction
        return returnData 

    def updateObjectsTracked(self, data):
        '''
            Formats data and updates dictionary of traced objects with dataset handed into this method
        '''
        tempData=[]                                                                          #list will be filled with a list of datapoints
        for objects in data:                                                                  #iterate over list of incomming data  
            objectdata = [x, y, v, dr] = [objects[i: i+4] for i in range(0, len(objects),4)]  #cut lsit into chunks corresponding to the tracked objects -> this leaves us with swapped high and low bytes becaus thats hwo data is send
            objectdata = self.swapBytes(objectdata)                                           #this repairs the swapped bytes
            objectdata = self.subtractOffset(objectdata)                                      #documentation says highes byte = 0 -> negative direction wich is contrariy to signed into convention 
            tempData.append(objectdata)
        list_of_keys=list(self.objectsTracked.keys())                                         #makes a list of keys of a dict to merge other list into dict
        for counter, dataset in enumerate(tempData):
            self.objectsTracked[list_of_keys[counter]]['x_mm']=dataset[0]
            self.objectsTracked[list_of_keys[counter]]['y_mm']=dataset[1]
            self.objectsTracked[list_of_keys[counter]]['v_cm/s']=dataset[2]
            self.objectsTracked[list_of_keys[counter]]['dres_mm']=dataset[3]

if __name__ =="__main__":
    Sensor=HLK_LD2450('/dev/ttyS0', '256000') 
    Sensor.connSerial()                                                                       #make sure serial hardware is initalized (sudo raspi-config) and your user must be part of teh dialoutgroup (sudo gpasswd --add $user dialout)
    Sensor.getSerial()
    while True:
        Sensor.flushSerial() 
        Sensor.getDatafromSerial()
        Sensor.getobjectsTracked(True)
        #os.system('clear')                                                                     #empties read buffer
