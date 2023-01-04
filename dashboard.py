import pandas as pd
import dash
from dash import dcc, html
import plotly.subplots
from dash.dependencies import Input, Output
import client
import multiprocessing

# Dashboard Layout
app = dash.Dash(__name__)
app.layout = html.Div(
html.Div([
    html.H4('VE416 QC Dashboard'),

    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000, # in milliseconds
        n_intervals=0
    )
])
)


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals'))

def update_graph_live(n):

    df = pd.read_csv('data-rx.csv')

    data = {
        'Time': df['PC Time'],
        'Phase Ave': df['Phase Ave'],
        'Phase Peak' :df['Phase Peak'],
        'Phase Peak Time' :df['Phase Peak Time'],
        'Distortion Ave': df['Dist Ave'],
        'Distortion Peak' :df['Dist Peak'],
        'Distortion Peak Time' :df['Dist Peak Time']
    }

    # Create the graph with subplots
    fig = plotly.subplots.make_subplots(
        rows=6,
        cols=1,
        shared_xaxes=True
        )

    fig.append_trace({
        'x': data['Time'],
        'y': data['Phase Ave'],
        'name': 'Phase Mean',
        'mode': 'lines',
        'type': 'scatter'
    }, 1, 1)
    fig.append_trace({
        'x': data['Time'],
        'y': data['Phase Peak'],
        'name': 'Phase Peak',
        'mode': 'lines',
        'type': 'scatter'
    }, 2, 1)
    fig.append_trace({
        'x': data['Time'],
        'y': data['Phase Peak Time'],
        'name': 'Phase Peak Time',
        'mode': 'lines',
        'type': 'scatter'
    }, 3, 1)

    fig.append_trace({
        'x': data['Time'],
        'y': data['Distortion Ave'],
        'name': 'Distortion Mean',
        'mode': 'lines',
        'type': 'scatter'
    }, 4, 1)

    fig.append_trace({
        'x': data['Time'],
        'y': data['Distortion Peak'],
        'name': 'Distortion Peak',
        'mode': 'lines',
        'type': 'scatter'
    }, 5, 1)

    fig.append_trace({
        'x': data['Time'],
        'y': data['Distortion Peak Time'],
        'name': 'Distortion Peak Time',
        'mode': 'lines',
        'type': 'scatter'
    }, 6, 1)

    fig.update_layout(height=1000)
    return fig

# Main Loop
if __name__ == '__main__':

    # start client in serpate thread
    p1 = multiprocessing.Process(target=client.start_client)
    p1.start()
    
    app.run_server(debug=True)