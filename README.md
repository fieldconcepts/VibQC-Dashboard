# VibQC-Dashboard
The Sercel DPG VE416 Vibrator Controller prints a header statsus and QC information after every aqcuitsiotn/sweep.

This python app monitors a serial port and parses certain target strings, saves to disk key information to disk, and updates a Plotyl Dash dashboard in real time.

By monitoring a dashboard in real time, the seismic aqcuisiton engineer can verify the quality of the vibrator and alert truck operator if phase/distortion falls outside of clients threshold.
