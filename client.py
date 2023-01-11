'''
DPG client - decoding vib QC report strings and sending to dataframe - decode lines 80 bytes long
'''

import serial
import time as t
from datetime import datetime
import pandas as pd
import csv
import sqlite3

def build_queries(row):
    d = row
    query = "INSERT INTO vib_data (vp,pc_time,sq,stack,acq,dpg_status,version,dpg_time,grp,vibrator,drive,fpmve,dsd_status,phase_ave,phase_peak,phase_peak_time,dist_ave,dist_peak,dist_peak_time,force_ave,force_peak,force_peak_time) VALUES({},'{}',{},{},{},{},{},'{}',{},{},{},'{}',{},{},{},{},{},{},{},{},{},{})".format(d['VP'], d['PC Time'] ,d['SQ'] ,d['Stack'] ,d['Acq'], d['DPG Status'], d['Version'], d['DPG Time'], d['Group'], d['Vibrator'], d['Drive'], d['FPMVE'], d['DSD Status'], d['Phase Ave'], d['Phase Peak'], d['Phase Peak Time'], d['Dist Ave'], d['Dist Peak'], d['Dist Peak Time'], d['Force Ave'], d['Force Peak'], d['Force Peak Time'])
    return query

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
    
    
    # start DB connection
    conn = sqlite3.connect('vib_db')
    c = conn.cursor()
    print("Connecting to db...")

    # Delete old table from previous session
    #c.execute("DROP TABLE IF EXISTS vib_data")
    #print("Removing previous session data")
    
    # Create fresh tables
    c.execute("CREATE TABLE IF NOT EXISTS vib_data ([vp] INTEGER PRIMARY KEY, [pc_time] TEXT, [sq] INTEGER, [stack] INTEGER, [acq] INTEGER, [dpg_status] INTEGER, [version] FLOAT, [dpg_time] TEXT, [grp] INTEGER, [vibrator] INTEGER, [drive] INTEGER, [fpmve] TEXT, [dsd_status] INTEGER, [phase_ave] INTEGER, [phase_peak] INTEGER, [phase_peak_time] FLOAT, [dist_ave] INTEGER, [dist_peak] INTEGER, [dist_peak_time] FLOAT, [force_ave] INTEGER, [force_peak] INTEGER, [force_peak_time] FLOAT)")
    print("Created new tables")
    

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

    # Open a file on disk to write seriel inputs
    with open('data-rx.csv', 'w', newline='') as f: # will overwrite old file at start of a sesion
        cols = ["PC Time","SQ", "VP", "Stack", "Acq", "DPG Status", "Version", "DPG Time","Group", "Vibrator", "Drive", "FPMVE", "DSD Status", "Phase Ave", "Phase Peak", "Phase Peak Time", "Dist Ave", "Dist Peak", "Dist Peak Time", "Force Ave", "Force Peak", "Force Peak Time"]
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()

        # Line read state
        header_rx = False
        qc_rx = False

        # Main loop to monitor serial port
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

                
                # Insert rows to SQL Database
                query = build_queries(full_row)
                c.execute(query)
                conn.commit()
                
                # reset line read state
                header_rx = False
                qc_rx = False
    


    




