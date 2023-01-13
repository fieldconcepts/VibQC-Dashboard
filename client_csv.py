'''
DPG client - decoding vib QC report strings and sending to CSV file
'''

import serial
from datetime import datetime
import pandas as pd
import csv

def parse_header_line(line):
    '''
    Fucntion that takes a Header string from DPG and parses information
    Header line 80bytes
    SQ# 1 VP#  122.00    ST# 1 A# 1 DPG s:12         VE416 V8.0  08/12/2022 12:24:57
    '''
    vp = float(line[9:17])

    row = {
        "PC Time": (datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        "SQ": int(line[3:5]),
        "VP": int(vp),
        "Stack": int(line[24:26]),
        "Acq": int(line[29:31]),
        "DPG Status": int(line[38:40]),
        "Version": float( line[56:59]),
        "DPG Time": str(line[61:80])
        }

    return row

def parse_qc_line(line):
    '''
    Fucntion that takes a QC string from DPG and parses information
    QC line 80bytes
    V1,1 D: 80%       s:12 P:  4,   7d @  4.0s D: 13, 25% @  2.5s F: 66, 77% @  1.0s
    '''

    row = {
        "Group": int(line[1]),
        "Vibrator": int(line[3]),
        "Drive": int(line[8:10]),
        "FPMVE": str(line[12:17]),
        "DSD Status": int(line[20:22]),
        "Phase Ave": int(line[25:28]),
        "Phase Peak": int(line[29:33]),
        "Phase Peak Time": float(line[37:41]),
        "Dist Ave": int(line[45:48]),
        "Dist Peak": int(line[49:52]),
        "Dist Peak Time": float(line[56:60]),
        "Force Ave": int(line[64:67]),
        "Force Peak": int(line[68:71]),
        "Force Peak Time": float(line[75:79])
        }
    
    
    return row

def start_client():
    
    # Serial Port Setup
    ser = serial.Serial(port='COM5',
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout=1)
    
    if(ser.isOpen() == False):
        ser.open()
    print("connected to: " + ser.portstr)


    # Open a file on disk to write seriel inputs
    with open('data-rx.csv', 'w', newline='') as f: # will overwrite old file at start of a sesion
        cols = ["PC Time","SQ", "VP", "Stack", "Acq", "DPG Status", "Version", "DPG Time","Group", "Vibrator", "Drive", "FPMVE", "DSD Status", "Phase Ave", "Phase Peak", "Phase Peak Time", "Dist Ave", "Dist Peak", "Dist Peak Time", "Force Ave", "Force Peak", "Force Peak Time"]
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()

        # State of each received line over seriel
        header_rx = False
        qc_rx = False

        # Main loop to monitor serial port
        while True:
            # Read line seriel line and decode
            line = ser.readline().decode("utf-8") 

            # Check if line is not empty
            if len(line) > 0:
                 # Parse header line if begins with SQ
                if line[0:3] == "SQ#":
                    header_rx = True
                    header = parse_header_line(line)
                
                 # Parse second QC line if begins with V
                if line[0:1] == "V":
                    qc_rx = True
                    qc = parse_qc_line(line[0:80])

            # Check states - only run if both lines have been received over seriel
            if header_rx == True and qc_rx == True:
                # Merge two dictoionarys
                full_row = header | qc 
                print(full_row)
                
                # Write to CSV
                writer.writerow(full_row)
                f.flush() # need this to update file whilst program is looping
                
                # Reset line read state
                header_rx = False
                qc_rx = False
    


    




