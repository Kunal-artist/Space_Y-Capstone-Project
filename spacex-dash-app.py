# Import required libraries
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # Dropdown for Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),
    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df[spacex_df['class'] == 1], 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        class_counts['class'] = class_counts['class'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            class_counts,
            names='class',
            values='count',
            title=f'Total Success Launches for site {selected_site}'
        )
    return fig

# Callback for Scatter Chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    df_filtered = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        fig = px.scatter(
            df_filtered, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        df_site = df_filtered[df_filtered['Launch Site'] == selected_site]
        fig = px.scatter(
            df_site, 
            x='Payload Mass (kg)', 
            y='class', 
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {selected_site}'
        )
    return fig

# Run the app on a different port if needed
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8050)
    except OSError:
        print("Port 8050 is in use. Try running on another port, e.g., 8051:")
        app.run(host='0.0.0.0', port=8051)
