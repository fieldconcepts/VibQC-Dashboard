import pandas as pd
import dash
from dash import dcc, html
import plotly.subplots
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import client
import multiprocessing
import sqlite3



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

# Phase CallBack
# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
            Input('interval-component', 'n_intervals'))

def update_graph_live(n):


    conn = sqlite3.connect('vib_db')
    sql_query = pd.read_sql('SELECT * FROM vib_data', conn)
    df_sql = pd.DataFrame(sql_query)
    #print(df_sql.tail(1))

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

    # add threshold line
    fig.add_hline(y=5.5, line_width=1, line_dash="dash", line_color="white", row=1, col=0) # phase threshold
    fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="white", row=3, col=0) # distortion threshold

    # Update yaxis properties
    fig.update_yaxes(title_text="Phase (deg)", row=1, col=1)
    fig.update_yaxes(title_text="Phase Max Time (s)", row=2, col=1)
    fig.update_yaxes(title_text="Distortion (%)", row=3, col=1)
    fig.update_yaxes(title_text="Distortion Max Time (s)", row=4, col=1)

    # Hide grid loines
    fig.for_each_xaxis(lambda x: x.update(showgrid=False))
    fig.for_each_yaxis(lambda x: x.update(showgrid=False))

    fig.update_layout(
        height=1000,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.05)',
        font=dict(color='#ffffff'),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5)
        )
    return fig

# Main Loop
if __name__ == '__main__':

    # start client in serpate thread
    p1 = multiprocessing.Process(target=client.start_client)
    p1.start()

    app.run_server(debug=True, use_reloader=False)
    