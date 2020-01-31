import os, sys
import datetime
import csv
import time
import numpy as np
import shutil

sys.path.append(os.path.join("/home/pi/.local/lib/python2.7/site-packages"))

from yoctopuce.yocto_api import *
from yoctopuce.yocto_tilt import *
from yoctopuce.yocto_compass import *
from yoctopuce.yocto_accelerometer import *
from yoctopuce.yocto_gyro import *


def usage():
    scriptname = os.path.basename(sys.argv[0])
    print("Usage:")
    print(scriptname + ' <serial_number>')
    print(scriptname + ' <logical_name>')
    print(scriptname + ' any  ')
    sys.exit()

def die(msg):
    sys.exit(msg + ' (check USB cable)')


class Sensor(object):

    def __init__(self):

        self.errmsg = YRefParam()
        errmsg = YRefParam()
        if len(sys.argv) < 2:
            usage()
        target = sys.argv[1]

        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            sys.exit("init error" + errmsg.value)

        if target == 'any':
            # retreive any tilt sensor
            anytilt = YTilt.FirstTilt()

            if anytilt is None:
                die('No module connected (check USB cable)')

            m = anytilt.get_module()
            self.module = m
            target = m.get_serialNumber()

        else:
            anytilt = YTilt.FindTilt(target + ".tilt1")
            if not (anytilt.isOnline()):
                die('Module not connected (check identification and USB cable)')


        
        serial = anytilt.get_module().get_serialNumber()
        tilt1 = YTilt.FindTilt(serial + ".tilt1")
        tilt2 = YTilt.FindTilt(serial + ".tilt2")
        compass = YCompass.FindCompass(serial + ".compass")
        accelerometer = YAccelerometer.FindAccelerometer(serial + ".accelerometer")

        #acceleration x,y, and z components (units mg)
        qt1 = YQt.FindQt(serial + ".qt1")
        qt1.set_logicalName("ax")

        qt2 = YQt.FindQt(serial + ".qt2")
        qt2.set_logicalName("ay")


        qt3 = YQt.FindQt(serial + ".qt3")
        qt3.set_logicalName("az")


        self.start = datetime.datetime.now()
        self.sensors = [tilt1,tilt2,compass, accelerometer, qt1, qt2, qt3]
        self.names = ['starttime','tilt1','tilt2','compass', 'accelerometer', 'ax', 'ay', 'az']

    def senddata(self):
        
        #Move all data from Handoff folder to Data folder
        fromDirectory = "/home/pi/Processing/Spatial_Clustering/Handoff"
        toDirectory = "/home/pi/Processing/Spatial_Clustering/Data"
        shutil.move(fromDirectory, toDirectory)

        #Erase contents of Handoff folder
        
        
    
    def erase(self):
        #Erase data logger contents from previous run
        datalogger = YDataLogger.FirstDataLogger()
        datalogger.forgetAllDataStreams()
    def calibrate(self):
        self.errmsg = YRefParam()


        sensors = self.sensors
        tilt1 = sensors[0]
        tilt2 = sensors[1]
        compass = sensors[2]
        accelerometer = sensors[3]

        caltime = datetime.datetime.now()
        tilt1_cal = tilt1.get_currentValue()
        tilt2_cal = tilt2.get_currentValue()
        compass_cal = compass.get_currentValue()
        accelerometer_cal = accelerometer.get_currentValue()

        os.chdir('/home/pi/Processing/Spatial_Clustering/Handoff')  

        with open('Calibration.csv', mode='w') as file:

            #Output file   

            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['starttime','tilt1', 'tilt2','compass','accelerometer'])
            writer.writerow([caltime, tilt1_cal, tilt2_cal, compass_cal, accelerometer_cal])
            

        #Flash yocto light for calibration
        self.module.set_luminosity(0)
        time.sleep(0.25)
        self.module.set_luminosity(100)
        time.sleep(0.25)
        self.module.set_luminosity(0)
        time.sleep(0.25)
        self.module.set_luminosity(100)
        time.sleep(0.25)


        
    def run(self):

        self.errmsg = YRefParam()

        #Change yocto light to 0 to indicate the start of recording
        self.module.set_luminosity(0)
        
        count = 0
        sensors = self.sensors
        names = self.names

        accelerometer = sensors[3]

        start = datetime.datetime.now()

        if not (accelerometer.isOnline()):
            die("Module not connected (check identification and USB cable)")

        for i in self.sensors: 
            i.set_logFrequency("10/s")
            i.startDataLogger()
        print("Recording Data....")
            
    def stop(self):
        accelerometer = self.sensors[3]

        #stop call stops dataLogger
        accelerometer.stopDataLogger()
        YAPI.Sleep(250, self.errmsg)
        print("Logger Stopped....")        

    def extract(self):
        sensors = self.sensors
        names = self.names
        #Extracting using datalogger

        #Flash yocto light for extraction
        self.module.set_luminosity(0)
        time.sleep(0.25)
        self.module.set_luminosity(100)
        time.sleep(0.25)
        self.module.set_luminosity(0)
        time.sleep(0.25)
        self.module.set_luminosity(100)
        time.sleep(0.25)

        print("Begin Datalogger extraction")
        cnt = 0
        long_lst = []
        #set path
        os.chdir('/home/pi/Processing/Spatial_Clustering/Handoff')   
        for i in sensors:
            name = names[cnt]
            dataset = i.get_recordedData(0,0)
            dataset.loadMore()
            progress = 0

            while progress < 100:
                progress = dataset.loadMore()
            details = dataset.get_measures()
            
            fmt = 'hh:mm:ss,fff'
            lst = []

            for m in details:
                if cnt == 0:
                    long_lst.append([str(m.get_startTimeUTC_asDatetime()), m.get_averageValue()])
                else:
                    lst.append(m.get_averageValue())               
            for i in range(len(lst)):
                long_lst[i].append(lst[i])
            cnt += 1
        
        with open(str(self.start)+'.csv', mode='w') as file:

                #Output file   

                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.names)     
                for row in long_lst:
                    writer.writerow(row)

        

                #Save calibrated values
        print("End Datalogger extraction")





        #Resume Yoctopuce light
        self.module.set_luminosity(50)
            
        YAPI.FreeAPI()
    
    
	
def main():
    import time
    x = Sensor()
    x.erase()
    x.run()

    time.sleep(2)
    
    x.stop()
    x.extract()

if __name__ == '__main__':
    main()
