import dash
import json
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests


state_df = pd.read_csv(r'https://raw.githubusercontent.com/abinandha02/render_project/main/crimes_against_women_2001-2014-checkpoint.csv')
state_df.drop(columns="Unnamed: 0", inplace=True)
state_df["STATE/UT"] = state_df.apply(lambda row: row['STATE/UT'].lower(), axis=1)
state_df['STATE/UT'].replace(
    {'a & n islands': 'A & N Islands', 'a&n islands': 'A & N Islands', 'd & n haveli': 'd & n haveli',
     'd&n haveli': 'd & n haveli', 'delhi ut': 'NCT of Delhi', 'delhi': 'NCT of Delhi'}, inplace=True, regex=True)
state_df['STATE/UT'] = state_df['STATE/UT'].str.title()


url = "https://raw.githubusercontent.com/abinandha02/render_project/fa03a4c758e48508b5f1a68c137e32a4c13774a8/data/states_india.geojson"
response = requests.get(url)
if response.status_code == 200:
    india_states = response.json()
    # Now you can work with the 'india_states' GeoJSON data
else:
    print("Failed to retrieve GeoJSON file from GitHub")
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]



#grouped state_wise
grouped_df1 = state_df.groupby('STATE/UT', as_index=False).sum(numeric_only=True)
state_id_map = {key: state_id_map[key] for key in sorted(state_id_map)}
grouped_df1['Total Crimes'] = grouped_df1['Rape'] + grouped_df1['Kidnapping and Abduction'] + grouped_df1['Dowry Deaths'] + \
                           grouped_df1['Assault on women with intent to outrage her modesty'] + grouped_df1[
                               'Insult to modesty of Women'] + grouped_df1['Cruelty by Husband or his Relatives'] + \
                           grouped_df1['Importation of Girls']

keys = []
values = []
for key, value in state_id_map.items():
    keys.append(key)
    values.append(value)
grouped_df1['state'] = keys
grouped_df1['id'] = values
features_2=grouped_df1.columns[2:10]

app = dash.Dash()
server=app.server

app.layout=html.Div([
            html.H3("CRIME AGAINST WOMEN STATE WISE", style={'textAlign': 'center', 'marginBottom': '20px', 'marginTop': '40px'}),
            html.H4('Select a crime category', style={'marginBottom': '20px', 'marginLeft': '20px'}),
    dcc.Dropdown(
            id='state-crime-dropdown',
            options=[{'label': i.title(), 'value': i} for i in features_2],
            value='Total Crimes',
            style={'width': '60%', 'marginBottom': '10px'}
        ),
    dcc.Graph(
        id='choropleth-map',
        config={'scrollZoom': False},
        style={'height': '90vh'}
    ),
])

@app.callback(
    dash.dependencies.Output('choropleth-map', 'figure'),
    dash.dependencies.Input('state-crime-dropdown', 'value')
)
def update_choropleth_map(selectedcrime):
    # Create choropleth map
    choropleth_map = go.Figure(data=go.Choropleth(
        locations=grouped_df1['id'],
        z=grouped_df1[selectedcrime],
        locationmode='geojson-id',
        geojson=india_states,
        colorscale='Viridis',
        colorbar_title=selectedcrime,
        hovertext=grouped_df1['state'],
        hoverinfo='z+text'
    ))

    choropleth_map.update_geos(fitbounds="locations", visible=False)
    choropleth_map.update_layout(title="Crime analysis over States")

    return choropleth_map


if __name__ == '__main__':
    app.run_server()


