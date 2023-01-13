# VibQC-Dashboard
The Sercel DPG VE416 Vibrator Controller prints a header status line and QC information line after every acquisition/sweep.

This python app monitors a serial port, parses target strings, saves data to SQL database, and updates a Plotly Dash dashboard in real time.

By monitoring a dashboard in real time, the seismic aqcuisiton engineer can verify the quality of the vibrator and alert truck operator if phase/distortion falls outside of clients threshold.
