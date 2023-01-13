'''
Ben Kaack
13/01/2023
Sercel VE416 DPG QC Data String Dashboard
Version 1.0

How to Run - Type "python dashboard.py 5" in command line.
The final intger represents the comm port that the Seriel-USB interface is connected to.
The dashboard can be viewed in any browser by going to http://127.0.0.1:8050/

The application creates a parallel process called start_client at startup.
This paralell process opens a seriel port and SQL database connection, updating as new data
is received over the user selected comm port.
The dash application refreshes at regular interval and updates plots with new data points
'''
# Imports
import pandas as pd
import dash
from dash import dcc, html
import plotly.subplots
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import client_sql
import multiprocessing
import sqlite3
import sys

# Dashboard Layout
app = dash.Dash(__name__)
app.layout = html.Div(
html.Div([
    html.H1('VE416 QC Dashboard'),

    dcc.Graph(
        id='live-update-graph'
    ),

    dcc.Interval(
        id='interval-component',
        interval=5*1000, # in milliseconds
        n_intervals=0
    )
])
)

# Live updates callback
@app.callback(Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals'))

def update_graph_live(n):
    # Connect to SQL database and build dataframe
    db_name = 'vib_db'
    conn = sqlite3.connect(db_name)
    sql_query = pd.read_sql('SELECT * FROM vib_data', conn)
    df = pd.DataFrame(sql_query)

    # Dictionary to hold data pulled from SQL database
    data = {
        'Time': df['pc_time'],
        'Phase Ave': df['phase_ave'],
        'Phase Peak' :df['phase_peak'],
        'Phase Peak Time' :df['phase_peak_time'],
        'Distortion Ave': df['dist_ave'],
        'Distortion Peak' :df['dist_peak'],
        'Distortion Peak Time' :df['dist_peak_time']
    }

    # Create the graph with subplots
    fig = plotly.subplots.make_subplots(
        rows=4,
        cols=1,
        row_heights=[0.3, 0.2,0.3,0.2],
        shared_xaxes=True
        )

    # Phase Subplot1
    fig.append_trace(go.Scatter(x=data['Time'], y=data['Phase Ave'], mode='lines+markers', name='Phase Ave'), 1, 1)
    fig.append_trace(go.Scatter(x=data['Time'], y=data['Phase Peak'], mode='lines+markers', name='Phase Peak'), 1, 1)

    # Phase subplot2
    fig.append_trace(go.Scatter(x=data['Time'], y=data['Phase Peak Time'], mode='markers', name='Phase Peak Time'), 2, 1)

    # Distortion subplot3
    fig.append_trace(go.Scatter(x=data['Time'], y=data['Distortion Ave'], mode='lines+markers', name='Distortion Ave'), 3, 1)
    fig.append_trace(go.Scatter(x=data['Time'], y=data['Distortion Peak'], mode='lines+markers', name='Distortion Peak'), 3, 1)

    # Distortion subplot4
    fig.append_trace(go.Scatter(x=data['Time'], y=data['Distortion Peak Time'], mode='markers', name='Distortion Peak Time'), 4, 1)

    # Add threshold lines
    fig.add_hline(y=5.5, line_width=1, line_dash="dash", line_color="white", row=1, col=0) # phase threshold
    fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="white", row=3, col=0) # distortion threshold

    # Update yaxis properties
    fig.update_yaxes(title_text="Phase (deg)", row=1, col=1)
    fig.update_yaxes(title_text="Phase Max Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Distortion (%)", row=3, col=1)
    fig.update_yaxes(title_text="Distortion Max Time (s)", row=4, col=1)

    # Hide grid lines
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(showgrid=False))

    # Update plotly figure
    fig.update_layout(
        height=1000,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='#ffffff'),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5)
        )
    return fig

# Main
if __name__ == '__main__':

    # Start the client in a parallel thread
    comm_port = sys.argv[1] # grab the comm port number
    p1 = multiprocessing.Process(target=client_sql.start_client, kwargs={"comm":comm_port})
    p1.start()

    # Main thread
    app.run_server(debug=True, use_reloader=False)
    