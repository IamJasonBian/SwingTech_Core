
import os, sys

sys.path.append(os.path.join("usr/local/lib/python2.7/dist-packages (1.3.2)"))

from bluedot import*
from signal import pause
import Capture

bd = BlueDot()
bd.when_pressed = execfile("Capture.py")

pause()
