import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

# Beispiel-Sensorenliste
sensors = [
    {"active": True, "name": "Licht", "pinID": 3, "class": "Licht", "intervall": 1000},
    {"active": False, "name": "Temperatur", "pinID": 5, "class": "Temperatur", "intervall": 5000},
    {"active": True, "name": "Luftfeuchtigkeit", "pinID": 7, "class": "Luftfeuchtigkeit", "intervall": 3000}
]

# Konvertieren der Sensorenliste in ein Pandas DataFrame für die Anzeige in einer Tabelle
df_sensors = pd.DataFrame(sensors)

# Erstellung der Dash-App
app = dash.Dash(__name__)

# Layout des Dashboards mit einer Tabelle für die Sensoren und einer Submit-Schaltfläche
app.layout = html.Div([
    html.H1("Sensorenliste"),
    dcc.Loading(
        id="loading-1",
        children=[
            dcc.Store(id='sensor-state', data=sensors),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Name"),
                        html.Th("Pin-ID"),
                        html.Th("Klasse"),
                        html.Th("Intervall"),
                        html.Th("Active")
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(df_sensors.loc[i, "name"]),
                        html.Td(df_sensors.loc[i, "pinID"]),
                        html.Td(df_sensors.loc[i, "class"]),
                        html.Td(df_sensors.loc[i, "intervall"]),
                        html.Td(dcc.Checklist(
                            id={
                                'type': 'checkbox',
                                'index': i
                            },
                            options=[{'label': '', 'value': 'active'}],
                            value=[df_sensors.loc[i, "active"]]
                        ))
                    ]) for i in range(len(df_sensors))
                ])
            ])
        ],
        type="default"
    ),
    html.Button("Speichern", id="save-button")
])

# Callback zum Aktualisieren des Sensorzustands in der Store, wenn eine Checkbox ausgewählt wird
@app.callback(
    Output('sensor-state', 'data'),
    Input({'type': 'checkbox', 'index': str(Input("save-button", "n_clicks"))}, 'value'),
    State('sensor-state', 'data'))
def update_sensor_state(value, data):
    if value is not None:
        index = int(value[0])
        data[index]["active"] = not data[index]["active"]
    return data

# Callback zum Auslösen einer Benachrichtigung beim Speichern
@app.callback(
    Output("save-button", "children"),
    Input("save-button", "n_clicks"),
    State("sensor-state", "data"))
def save_sensors(n_clicks, data):
    if n_clicks is not None:
        return "Gespeichert!"
    else:
        return "Speichern"

if __name__ == '__main__':
    app.run_server(debug=True)
