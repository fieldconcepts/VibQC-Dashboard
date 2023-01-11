'''
DPG server - simulating vib QC report strings
'''

import serial
import time as t
from datetime import datetime
import random

# Program Settings
interval = 5
diskette = False


# Serial Port Setup
ser = serial.Serial(port='COM4',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)

print("connected to: " + ser.portstr)
if(ser.isOpen() == False):
    ser.open()


# Sweep Header Line
sequence = 1
vibe_point = 1
stack = 1
acq = 1
status = 12
version = 8.0

# Vibrator QC variables
group = 1
vibrator = 1
drive = 80
FPMVE = "     "
p_mean = 4
p_peak = 7
p_peak_t = 4.0
d_mean = 13
d_peak = 25
d_peak_t = 2.5
f_mean = 66
f_peak = 77
f_peak_t = 1.0


# run program
while True:
    
    p_mean += random.randint(-1,1)
    p_peak += random.randint(-1,1)
    d_mean += random.randint(-2,2)
    d_peak += random.randint(-2,2)


    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    
    line1 = "SQ#{:2.0f} VP#{:8.2f}    ST#{:2.0f} A#{:2.0f} DPG s:{:2.0f}         VE416 V{:3.1f}  {}\r\n".format(sequence, vibe_point, stack, acq, status, version,date_time)
    ser.write(line1.encode())
    print(line1)
    t.sleep(0.1)
    
    line2 = "V{},{} D:{:3.0f}% {} s:12 P:{:3.0f}, {:3.0f}d @ {:4.1f}s D:{:3.0f},{:3.0f}% @ {:4.1f}s F:{:3.0f},{:3.0f}% @ {:4.1f}s\r\n".format(group, vibrator, drive, FPMVE, p_mean, p_peak, p_peak_t + random.randint(-1,1), d_mean, d_peak, d_peak_t + random.randint(-1,1), f_mean, f_peak, f_peak_t)
    ser.write(line2.encode())
    print(line2)
    t.sleep(0.1)

    if diskette == True:
        line3 = " GV: 18/ 37/ 54 GS: 43/ 83/148 \r\n"
        ser.write(line3.encode())
        print(line3)
        t.sleep(0.1)
    
    t.sleep(10 + random.randint(-5,5))
    vibe_point += 1

ser.close()