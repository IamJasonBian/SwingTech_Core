### Swingtech is a Sensoring based solution for Swing Analytics 
  
* SwingTech Site: https://swingtech.io/
* At its core, Swingtech allows you to record a series of motion swings, download them into your local desktop (Figure 1), and visualize the swing trajectories of those swings (Figure 2).

Figure 1: SwingTech Captured Swings

![image](https://user-images.githubusercontent.com/16582383/119071386-8f97e580-b99e-11eb-9217-fe57bb822b4e.png)


Figure 2: SwingTech Swings Deep-Dive

Here, we can see the orientation time-series, the acceleration time-series, and the displacement time-series projected and within the xyz plane.

![image](https://user-images.githubusercontent.com/16582383/119071697-249ade80-b99f-11eb-85eb-0f288cf21918.png)

### Building the Device:

At the bare minimum, the following set of items is needed to assemble the device:
  1. pi zero
  2. sd card
  3. yoctopuce sensor
  4. micro usb connection
  5. pi zero power supply

We 3d printed an enclosure for this device and its specs can be found in this whitepaper: https://swingtechio.files.wordpress.com/2020/02/project-doc.pdf

Additionally, you can request beta devices here: 
https://docs.google.com/forms/d/e/1FAIpQLSdCNZfaUu4nQ0SYeTc7iaQ_SiNzVzpYLAXgBIuaWSeN1zN-_g/viewform

### Using the Beta Build 
To use the beta build, fork the pi-test into your raspberry pi and download the pi-build repo into your pi. Within pi-build there are two possible scripts you can use via init scripts within the pi:

  1. anydot.py: The build will auto record once the pi is live
  2. mydot.py: The build will record according to commands from bluedot: https://bluedot.readthedocs.io/en/latest/

To run the App, fork the Desktop App contents into your Desktop. If you wish to view the contents of the pi, plug it via usb into your computer and use the Usb_Copy.py code to locally save pi data into your computer. Make sure to move the contents of the usb transfer into the Assets folder as Data.csv.


