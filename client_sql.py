'''
DPG client - decoding vib QC report strings and sending to SQL database
'''

import serial
from datetime import datetime
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

def start_client(comm: int):
    
    # Open SQL DB connection
    db_name = 'vib_db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Create fresh tables
    c.execute("CREATE TABLE IF NOT EXISTS vib_data ([vp] INTEGER PRIMARY KEY, [pc_time] TEXT, [sq] INTEGER, [stack] INTEGER, [acq] INTEGER, [dpg_status] INTEGER, [version] FLOAT, [dpg_time] TEXT, [grp] INTEGER, [vibrator] INTEGER, [drive] INTEGER, [fpmve] TEXT, [dsd_status] INTEGER, [phase_ave] INTEGER, [phase_peak] INTEGER, [phase_peak_time] FLOAT, [dist_ave] INTEGER, [dist_peak] INTEGER, [dist_peak_time] FLOAT, [force_ave] INTEGER, [force_peak] INTEGER, [force_peak_time] FLOAT)")
    print("Connecting to SQL databse: " + db_name)
    
    # Serial Port Setup
    comm_port = f"COM{comm}"
    ser = serial.Serial(port=comm_port,
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout=1)
    
    if(ser.isOpen() == False):
        ser.open()
    print("Connected to: " + ser.portstr)
   
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
            
            # Insert rows to SQL Database
            query = build_queries(full_row)
            c.execute(query)
            conn.commit()
            
            # Reset line read state
            header_rx = False
            qc_rx = False








