import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),
    
    # Launch Site Dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True
                 ),

    html.Br(),

    # Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload Slider
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 11000, 1000)},
                    value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]),

    # Scatter Plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for Pie Chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate success counts per launch site
        pie_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(pie_data, values='class', names='Launch Site', title='Total Successful Launches for All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class', title=f'Total Success Launches for {entered_site}')
    
    return fig

# Callback for Scatter Plot
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", 
                         color="Launch Site",
                         title="Correlation between Payload and Success for all Sites")
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", 
                         color="Booster Version Category",
                         title=f'Correlation between Payload and Success for {entered_site}')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port = 8070)

