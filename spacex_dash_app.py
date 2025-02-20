# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                                options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                                ],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                            ),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites

                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',  # Unique ID for the slider
                                    min=0,  # Slider starting point
                                    max=10000,  # Slider ending point
                                    step=1000,  # Interval between slider values
                                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},  # Labels on the slider
                                    value=[min_payload, max_payload]  # Default range selection
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    """
    Generates a pie chart based on the selected launch site.

    - If 'ALL' is selected, the pie chart shows total successful launches by site.
    - If a specific site is selected, the pie chart shows success (1) vs. failure (0) count for that site.
    """
    filtered_df = spacex_df  # Use full dataset by default

    if entered_site == 'ALL':
        # Filter only successful launches
        success_counts = filtered_df[filtered_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Count']

        # Create pie chart showing total successful launches per site
        fig = px.pie(success_counts, 
                     values='Count', 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')

    else:
        # Filter dataset for selected launch site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        # Count success (1) and failure (0)
        outcome_counts = site_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['Launch Outcome', 'Count']

        # Create pie chart showing success vs. failure count
        fig = px.pie(outcome_counts, 
                     values='Count', 
                     names='Launch Outcome', 
                     title=f'Success vs. Failure for {entered_site}',
                     labels={'Launch Outcome': 'Outcome'})  # Renaming legend labels

    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    """
    Generates a scatter plot based on the selected launch site and payload range.

    - If 'ALL' sites are selected, the scatter plot displays all launches.
    - If a specific site is selected, the scatter plot filters data accordingly.
    - Colors indicate different Booster Versions.
    """
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    if entered_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version',
                         title='Correlation between Payload and Success for All Sites',
                         hover_data=['Launch Site'])
    else:
        # Filter data for the selected launch site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        # Scatter plot for the selected site
        fig = px.scatter(site_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version',
                         title=f'Payload vs. Outcome for {entered_site}',
                         hover_data=['Launch Site'])

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
