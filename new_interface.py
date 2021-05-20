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
import auto_report
import logger

DATA = None
SAVING = False
SAVE_LOCATION = "ReportFiles/run.csv"
FOLDER_LOCATION = None
CONSOLE = "UI Initialized"

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

MAIN_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": "20%",
    "bottom": 0,
    "width": "80%",
    "padding": "2rem 1rem",
}

# Create traces
hz_list = ['<b>HZ</b>', '100', '125', '160', '200', '250', '315', '400', '500', '630', '800', '1000', '1250', '1600',
           '2000', '2500', '3150', '4000', '5000']
hz_table = go.Figure(data=[go.Table(header=dict(values=hz_list),
                                    cells=dict(values=[['<b>RT</b>', '<b>Pass/Fail</b>']]))
                           ])
# Resize Table Plot
hz_table.update_layout(height=120, margin=dict(r=50, l=50, t=10, b=5))

basic_settings = html.Div([
    html.Div([
        html.Label("Sample Present", style={"width": "130px"}),
        daq.ToggleSwitch(
            id='sample_bool',
            value=False,
            color='#309143'
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
    html.Div([
        html.Label("No. of Runs", style={"width": "130px"}),
        dcc.Input(id="number_of_runs", type="number", placeholder="No. of Runs", value=2,
                  style={"width": "30%", "marginRight": "20%"})
    ]),
    html.Div([
        html.Label("Decay Time (sec)", style={"width": "130px"}),
        dcc.Input(id="decay_time", type="number", placeholder="No. of Runs", value=4,
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
            id='db_decay',
            options=[
                {'label': 'T20', 'value': 't20'},
                {'label': 'T30', 'value': 't30'},
                {'label': 'MAX', 'value': 'all'}
            ],
            value='t30',
            clearable=False,
            style={"width": "110px"}
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
    html.Div([
        html.Label("Mounting", style={"width": "130px"}),
        dcc.Dropdown(
            id='bracket_type',
            options=[
                {'label': 'A Mounting', 'value': 'A'},
                {'label': 'A Mounting (Cavity)', 'value': 'A_Cavity'},
                {'label': 'E200 Mounting', 'value': 'E200'},
                {'label': 'E400 Mounting', 'value': 'E400'},
                {'label': 'G Mounting', 'value': 'G'}
            ],
            value='A',
            clearable=False,
            style={"width": "200px"}
        ),
    ], style={"marginTop": "10px", "display": "flex", "alignItems": "left", "justifyContent": "left"}),
    html.Div([
        html.Label("Save Raw Data", style={"width": "130px"}),
        daq.ToggleSwitch(
            id='save_data',
            value=False,
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
            html.Button('Start Measurement', id='start_btn', className="btn btn-primary", disabled=True,
                        style={"marginBottom": "10px", "marginRight": "10px"},
                        n_clicks=0),
            html.Button('Save As', id='save_btn', className="btn btn-success", style={"marginBottom": "10px"}, n_clicks=0),
        ]),
    ])

textarea = html.Div(id='textarea_container',
     style={
            'overflow': 'auto',
            'display': 'flex',
            'flex-direction': 'column-reverse'},
    children=[
            dcc.Textarea(id='console_out_textarea', disabled=True, value=CONSOLE,
                              style={'width': '100%', 'height': 100}),
    ])

sidebar = html.Div(
    [
        html.H3("Controls", className="display-5"),
        html.Hr(),
        html.P("Basic Settings", className="lead"),
        basic_settings,
        html.Hr(),
        html.P("Environment", className="lead"),
        environment,
        html.Hr(),
        controls,
        html.Hr(),
        textarea
    ],
    style=SIDEBAR_STYLE
)

graphs = html.Div([
        html.Div([
            html.H3("Reverb Frequency Times", className="display-5")
        ], style={"marginLeft": "5%"}),
        dcc.Graph(
            id='frequency-table',
            figure=hz_table
        )], id='graphs')

unique_variables = html.Div([
    html.Div([
        html.H3("Job Info", className="display-5")
    ], style={"marginBottom":"30px"}),
    html.Div([
        html.Label("Job Number: ", style={"width": "180px"}),
        dcc.Input(id="job_no", type="number", placeholder="Job No.",
                  style={"width": "10%", "marginRight": "5%"})
    ]),
    html.Div([
        html.Label("Client Name: ", style={"width": "180px"}),
        dcc.Input(id="client", type="text", placeholder="Client",
                  style={"width": "10%", "marginRight": "5%"})
    ], style={"marginBottom":"30px"}),
    html.Div([
        html.Label("Name of Specimen: ", style={"width": "180px"}),
        dcc.Input(id="specimen_name", type="text", placeholder="Name",
                  style={"width": "10%", "marginRight": "5%"})
    ]),
    html.Div([
        html.Label("Description of Specimen: ", style={"width": "180px"}),
        dcc.Input(id="specimen_desc", type="text", placeholder="Description",
                  style={"width": "10%", "marginRight": "5%"})
    ]),
    html.Div([
        html.Label("Size of Specimen: ", style={"width": "180px"}),
        dcc.Input(id="specimen_size", type="text", placeholder="Size",
                  style={"width": "10%", "marginRight": "5%"})
    ]),
    html.Div([
        html.Label("Mass of Specimen: ", style={"width": "180px"}),
        dcc.Input(id="specimen_mass", type="text", placeholder="Mass",
                  style={"width": "10%", "marginRight": "5%"})
    ]),
    html.Div([
        html.Label("Area of Specimen: ", style={"width": "180px"}),
        dcc.Input(id="specimen_area", type="text", placeholder="Area",
                  style={"width": "10%", "marginRight": "5%"})
    ]),

], style={"marginLeft": "5%", "marginTop": "5%", "marginBottom": "5%"})

main_component = html.Div([
    unique_variables,
    html.Hr(),
    graphs
], style=MAIN_STYLE)

app.layout = html.Div([
    sidebar,
    main_component,
    html.Div(id='measure_out'),
    html.Div(id='save_out'),
    html.Div(id='report_out'),
    html.Div(dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ))
])


# Main Function, measure and report/display RT
@app.callback(
    dash.dependencies.Output('frequency-table', 'figure'),
    dash.dependencies.Input('start_btn', 'n_clicks'),
    dash.dependencies.State('sample_bool', 'value'),
    dash.dependencies.State('number_of_runs', 'value'),
    dash.dependencies.State('decay_time', 'value'),
    dash.dependencies.State('noise_type', 'value'),
    dash.dependencies.State('db_decay', 'value'),
    dash.dependencies.State('room_volume', 'value'),
    dash.dependencies.State('room_temp', 'value'),
    dash.dependencies.State('room_humidity', 'value'),
    dash.dependencies.State('room_pressure', 'value'),
    dash.dependencies.State('bracket_type', 'value'),
    dash.dependencies.State('job_no', 'value'),
    dash.dependencies.State('client', 'value'),
    dash.dependencies.State('specimen_name', 'value'),
    dash.dependencies.State('specimen_desc', 'value'),
    dash.dependencies.State('specimen_size', 'value'),
    dash.dependencies.State('specimen_mass', 'value'),
    dash.dependencies.State('specimen_area', 'value'),
)
def trigger_measurements(n_clicks, number_of_runs, sample_bool, decay_time, noise_type, db_decay, room_volume, room_temp,
                         room_humidity, room_pressure, bracket_type, job_no, client, specimen_name, specimen_desc,
                         specimen_size, specimen_mass, specimen_area):
    if n_clicks > 0:
        print("Submitting Parameters for Measurements")
        print(number_of_runs, decay_time, noise_type, room_volume)
        global DATA
        global SAVE_LOCATION
        # Run Measurements
        DATA = new_functions.new_meas1(number_of_runs, decay_time, noise_type, db_decay, room_temp, room_humidity,
                                       room_pressure, 100)
        # Save Sample csv and generate report
        if sample_bool:
            new_functions.save_csv(SAVE_LOCATION + '/SAMPLE.csv', room_humidity, room_temp, room_pressure, DATA)
            global CONSOLE
            unique_values = [job_no, client, specimen_name, specimen_desc, specimen_size, specimen_mass, specimen_area,
                             room_temp, room_humidity, room_pressure]
            try:
                auto_report.changeValues(SAVE_LOCATION, bracket_type, unique_values)
                CONSOLE += "\nReport Created"
            except:
                CONSOLE += "\nError in Reporting Process"
            return hz_table
        else:
            # Save No_Sample csv and generate table
            SAVE_LOCATION += '/NO_SAMPLE.csv'
            new_functions.save_csv(SAVE_LOCATION + '/NO_SAMPLE.csv', room_humidity, room_temp, room_pressure, DATA)
            table_values = [['<b>RT</b>', '<b>Pass/Fail</b>']]
            hz_out = auto_report.full_values(SAVE_LOCATION)
            colour_map = ["white"]
            for entry in hz_out:
                table_values.append(('{0:.2f}'.format(entry[0]), entry[1]))
                if entry[1] == 1:
                    colour_map.append(("white", "lightgreen"))
                else:
                    colour_map.append(("white", "lightred"))
            return go.Figure(
                data=[go.Table(header=dict(values=hz_list), cells=dict(values=table_values, fill_color=colour_map))])


# Save folder location
@app.callback(
    dash.dependencies.Output('start_btn', 'disabled'),
    dash.dependencies.Input('save_btn', 'n_clicks'),
    dash.dependencies.State('save_data', 'value'),
    dash.dependencies.State('room_humidity', 'value'),
    dash.dependencies.State('room_temp', 'value'),
    dash.dependencies.State('room_pressure', 'value'),
)
def save_data(n_clicks, save_data, rh, room_temperature, pressure):
    global SAVING
    if SAVING:
        return True
    else:
        if n_clicks > 0:
            SAVING = True
            print("Choosing Save Location")
            global DATA
            global SAVE_LOCATION
            save_file_name = new_functions.new_save_data(save_data, rh, room_temperature, pressure, DATA)
            SAVING = False
            SAVE_LOCATION = save_file_name
            print("Save location changed to " + save_file_name)
            logger.add_text("Save location changed to " + save_file_name)
            return False
        return True


# Logger Loop
@app.callback(
    dash.dependencies.Output('console_out_textarea', 'value'),
    dash.dependencies.Input('interval-component', 'n_intervals')
)
def addConsole(n_intervals):
    if n_intervals != 0:
        return logger.get_text()
    return ""


if __name__ == '__main__':
    app.run_server(debug=True)
