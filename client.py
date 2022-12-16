'''
DPG client - decoding vib QC report strings and sending to dataframe - decode lines 80 bytes long
'''

import serial
import time as t
from datetime import datetime
import pandas as pd
import csv


# Serial Port Setup
ser = serial.Serial(port='COM5',
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)

print("connected to: " + ser.portstr)
if(ser.isOpen() == False):
    ser.open()


# SQ# 1 VP#  122.00    ST# 1 A# 1 DPG s:12         VE416 V8.0  08/12/2022 12:24:57
def parse_header_line(line):
    sequence = line[3:5]
    vibe_point = line[9:17]
    stack = line[24:26]
    acq = line[29:31]
    status = line[38:40]
    version = line[56:59]
    date_time = line[61:80]

    row = {
        "PC Time": (datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        "SQ": int(sequence),
        "VP": float(vibe_point),
        "Stack": int(stack),
        "Acq": int(acq),
        "DPG Status": int(status),
        "Version": float(version),
        "DPG Time": str(date_time)
        }

    return row

# V1,1 D: 80%       s:12 P:  4,   7d @  4.0s D: 13, 25% @  2.5s F: 66, 77% @  1.0s
def parse_qc_line(line):
    '''
    Fucntion that takes a string from DPG and parses information
    '''

    group = line[1]
    vibrator = line[3]
    drive = line[8:10]
    FPMVE = line[12:17]
    status = line[20:22]
    p_mean = line[25:28]
    p_peak = line[29:33]
    p_peak_t = line[37:41]
    d_mean = line[45:48]
    d_peak = line[49:52]
    d_peak_t = line[56:60]
    f_mean = line[64:67]
    f_peak = line[68:71]
    f_peak_t = line[75:79]

    row = {
        "Group": int(group),
        "Vibrator": int(vibrator),
        "Drive": int(drive),
        "FPMVE": str(FPMVE),
        "DSD Status": int(status),
        "Phase Ave": int(p_mean),
        "Phase Peak": int(p_peak),
        "Phase Peak Time": float(p_peak_t),
        "Dist Ave": int(d_mean),
        "Dist Peak": int(d_peak),
        "Dist Peak Time": float(d_peak_t),
        "Force Ave": int(f_mean),
        "Force Peak": int(f_peak),
        "Force Peak Time": float(f_peak_t)
        }
    
    return row
    



# open a file on disk to write seriel inputs
with open('data-rx.csv', 'w', newline='') as f: # will overwrite old file at start of a sesion
    cols = ["PC Time","SQ", "VP", "Stack", "Acq", "DPG Status", "Version", "DPG Time","Group", "Vibrator", "Drive", "FPMVE", "DSD Status", "Phase Ave", "Phase Peak", "Phase Peak Time", "Dist Ave", "Dist Peak", "Dist Peak Time", "Force Ave", "Force Peak", "Force Peak Time"]
    writer = csv.DictWriter(f, fieldnames=cols)
    writer.writeheader()

    # Line read state
    header_rx = False
    qc_rx = False

    while True:
        # read line
        line = ser.readline().decode("utf-8") 

        if len(line) > 0:
            #parse header line
            if line[0:3] == "SQ#":
                header_rx = True
                header = parse_header_line(line)
            
            # parse second QC line
            if line[0:1] == "V":
                qc_rx = True
                qc = parse_qc_line(line[0:80])

        
        if header_rx == True and qc_rx == True:
            # merge two dictoionarys
            full_row = header | qc 
            print(full_row)
            
            # write to disk
            writer.writerow(full_row)
            f.flush() # need this to update file whilst program is looping

            # reset line read state
            header_rx = False
            qc_rx = False
    


    




