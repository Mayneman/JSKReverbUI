import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_table
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Cleaner function interface
import new_functions

# Init dash app4
external_stylesheets = [dbc.themes.BOOTSTRAP, 'main.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Reverb Room"

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
}

GRAPH_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": "20%",
    "bottom": 0,
    "width": "80%"
}


# Sample Graph
def make_sample_data():
    x = []
    y = []
    for i in range(1, 100):
        x.append(1 / i)
        y.append(i)
    return {'x': x, 'y': y}


np.random.seed(1)

df = pd.DataFrame(data=make_sample_data())

fig = go.Figure()

fig.add_trace(go.Scatter(x=df.x, y=df.y, mode='lines+markers', name='lines'))
fig.update_layout(title='Graph of 1/Time',
                  xaxis_title='1/Time',
                  yaxis_title='Time')

N = 100
random_x = np.linspace(0, 1, N)
random_y0 = np.random.randn(N) + 5
random_y1 = np.random.randn(N)
random_y2 = np.random.randn(N) - 5

# Create traces
hz_list = ['<b>HZ</b>', '100', '125', '160', '200', '250', '315', '400', '500', '630', '800', '1000', '1250', '1600',
           '2000', '2500',
           '3150', '4000', '5000']
hz_table = go.Figure(data=[go.Table(header=dict(values=hz_list),
                                    cells=dict(values=[['<b>RT</b>', '<b>Pass/Fail</b>']]))
                           ])

basic_settings = html.Div([
    html.Div([
        html.Label("No. of Runs", style={"width": "130px"}),
        dcc.Input(id="number_of_runs", type="number", placeholder="No. of Runs", value=9,
                  style={"width": "30%", "marginRight": "20%"})
    ]),
    html.Div([
        html.Label("Decay Time (sec)", style={"width": "130px"}),
        dcc.Input(id="decay_time", type="number", placeholder="No. of Runs", value=8,
                  style={"width": "30%", "marginRight": "20%"}),
    ]),
    html.Div([
        html.Label("Room Volume", style={"width": "130px"}),
        dcc.Input(id="room_volume", type="number", placeholder="No. of Runs", value=219,
                  style={"width": "30%", "marginRight": "20%"}),
    ]),
    html.Div([
        html.Label("Noise Type", style={"width": "130px"}),
        dcc.Dropdown(
            id='noise_type',
            options=[
                {'label': 'White', 'value': 'White'},
                {'label': 'Pink', 'value': 'Pink'}
            ],
            value='White',
            clearable=False,
            style={"width": "110px", "align": "right"}
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
    html.Div([
        html.Label("T Value", style={"width": "130px"}),
        dcc.Dropdown(
            id='t_type',
            options=[
                {'label': 'T20', 'value': 'T20'},
                {'label': 'T30', 'value': 'T30'},
                {'label': 'MAX', 'value': 'MAX'}
            ],
            value='T30',
            clearable=False,
            style={"width": "110px"}
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
    html.Div([
        html.Label("Mounting", style={"width": "130px"}),
        dcc.Dropdown(
            id='bracket_type',
            options=[
                {'label': 'A-Mounting', 'value': 'A'},
                {'label': 'E-Mounting', 'value': 'E'},
                {'label': 'Other', 'value': 'Other'}
            ],
            value='A',
            clearable=False,
            style={"width": "130px"}
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
    html.Div([
        html.Label("Save Raw Data", style={"width": "130px"}),
        daq.ToggleSwitch(
            id='save_data',
            value=True,
            color='#309143'
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
])

environment = html.Div([
    html.Div([
        html.Label("Temperature (°C)", style={"width": "145px"}),
        dcc.Input(id="room_temp", type="number", placeholder="Temperature", value=20,
                  style={"width": "30%", "marginRight": "20%"})
    ]),
    html.Div([
        html.Label("Room Humidity (%)", style={"width": "145px"}),
        dcc.Input(id="room_humidity", type="number", placeholder="Humidity", value=60,
                  style={"width": "30%", "marginRight": "20%"})
    ]),
    html.Div([
        html.Label("Pressure (kPa)", style={"width": "145px"}),
        dcc.Input(id="room_pressure", type="number", placeholder="Pressure", value=101,
                  style={"width": "30%", "marginRight": "20%"})
    ]),
])

controls = html.Div(
    [
        html.Div([
            html.Button('Start Measurement', id='start_btn', className="btn btn-primary",
                        style={"marginBottom": "10px"},
                        n_clicks=0)
        ]),
        html.Button('Save', id='save_btn', className="btn btn-success", style={"marginRight": "10px"}),
        html.Button('Reset', id='reset_btn', className="btn btn-warning", style={"marginRight": "10px"}),
    ])

sidebar = html.Div(
    [
        html.H2("Controls", className="display-4"),
        html.Hr(),
        html.P("Basic Settings", className="lead"),
        basic_settings,
        html.Hr(),
        html.P("Environment", className="lead"),
        environment,
        html.Hr(),
        html.P("Actions", className="lead"),
        controls,
        html.Hr()
    ],
    style=SIDEBAR_STYLE
)

graphs = html.Div([
    dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),
    # Hz Graph for passing room
    dcc.Graph(
        id='example-graph-3',
        figure=hz_table
    ),
], style=GRAPH_STYLE
)

app.layout = html.Div([
    sidebar,
    graphs,
    html.Div(id='hidden_output')
])

@app.callback(
    dash.dependencies.Output('hidden_output', 'children'),
    dash.dependencies.Input('start_btn', 'n_clicks'),
    dash.dependencies.State('number_of_runs', 'value'),
    dash.dependencies.State('decay_time', 'value'),
    dash.dependencies.State('noise_type', 'value'),
    dash.dependencies.State('room_volume', 'value'),
    dash.dependencies.State('room_temp', 'value'),
    dash.dependencies.State('room_humidity', 'value'),
    dash.dependencies.State('room_pressure', 'value'),
)

def trigger_measurements(n_clicks, number_of_runs, decay_time, noise_type, room_volume, room_temp, room_humidity, room_pressure):
    if n_clicks > 0:
        print("Submitting Parameters for Measurements")
        print(number_of_runs, decay_time, noise_type, room_volume)
        new_functions.new_meas1(number_of_runs, decay_time, noise_type, room_volume, room_temp, room_humidity, room_pressure, 100)
    return ""


if __name__ == '__main__':
    app.run_server(debug=True)
