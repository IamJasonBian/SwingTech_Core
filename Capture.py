import os, sys
import datetime
import csv

sys.path.append(os.path.join("/home/pi/.local/lib/python2.7/site-packages"))

from yoctopuce.yocto_api import *
from yoctopuce.yocto_tilt import *
from yoctopuce.yocto_compass import *
from yoctopuce.yocto_accelerometer import *


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
        self.start = datetime.datetime.now()
        self.sensors = [tilt1,tilt2,compass, accelerometer]
        self.names = ['tilt1','tilt2','compass', 'accelerometer']

    
    def erase(self):
        #Erase data logger contents from previous run
        datalogger = YDataLogger.FirstDataLogger()
        datalogger.forgetAllDataStreams()

    def run(self):

        self.errmsg = YRefParam()
        
        count = 0
        sensors = self.sensors
        names = self.names

        tilt1 = sensors[0]
        tilt2 = sensors[1]
        compass = sensors[2]
        accelerometer = sensors[3]
        start = datetime.datetime.now()

        if not (accelerometer.isOnline()):
            die("Module not connected (check identification and USB cable)")

        for i in self.sensors: 
            i.set_logFrequency("5/s")
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
        names = ['tilt1','tilt2','compass', 'accelerometer']
        #Extracting using datalogger
        print("Begin Datalogger extraction")
        cnt = 0

        #set path
        os.chdir('../Recorded_Data')
                
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
                lst.append([str(m.get_startTimeUTC_asDatetime()),
                    #Average value is the sensor recording average over time interval
                    m.get_averageValue()])
            with open(name+str(self.start)+'.csv', mode='w') as file:

                #Output file   
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['start','end','avg'])
                for row in lst:
                    writer.writerow(row)

            cnt += 1
            
        YAPI.FreeAPI()

def main():
    import time
    
    x = Sensor()
    x.erase()
    x.run()

    time.sleep(5)
    
    x.stop()
    x.extract()

if __name__ == '__main__':
    main()
