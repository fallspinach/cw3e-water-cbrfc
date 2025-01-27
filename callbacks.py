from main import app

from dash.dependencies import ClientsideFunction, Input, Output, State
from datetime import datetime, timedelta
import pandas as pd

from site_tools import draw_retro
from basin_tools import draw_basin_ts
from snow_tools import draw_course, draw_pillow
from river_tools import draw_mofor_river_db, draw_rev_esp
from config import base_url, cloud_url
## Callbacks from here on

# callback to update data var in the title section
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_title_var'
    ),
    Output('title-var', 'children'),
    Input(component_id='data-sel',  component_property='value'),
    Input(component_id='met-vars',  component_property='value'),
    Input(component_id='hydro-vars', component_property='value')
)

# callback to update data date in the title section
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_title_date'
    ),
    Output('title-date', 'children'),
    Input('datepicker', 'date')
)

# callback to update url of image overlay
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_img_url'
    ),
    Output('data-img', 'url'),
    Input('datepicker', 'date'),
    Input(component_id='data-sel',  component_property='value'),
    Input(component_id='met-vars',  component_property='value'),
    Input(component_id='hydro-vars', component_property='value')
)

# callback to update url of color bar
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_cbar'
    ),
    Output('data-cbar-img', 'src'),
    Input(component_id='data-sel',  component_property='value'),
    Input(component_id='met-vars',  component_property='value'),
    Input(component_id='hydro-vars', component_property='value')
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_cbar_visibility'
    ),
    Output('data-cbar', 'style'),
    Input(component_id='data-map-ol', component_property='checked')
)

# callback to update datepicker and slider on button clicks
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_date'
    ),
    Output('datepicker', 'date'),
    Input('button-forward-day',  'n_clicks_timestamp'),
    Input('button-backward-day', 'n_clicks_timestamp'),
    Input('button-forward-month',   'n_clicks_timestamp'),
    Input('button-backward-month',  'n_clicks_timestamp'),
    Input('datepicker', 'date'),
    Input('datepicker', 'min_date_allowed'),
    Input('datepicker', 'max_date_allowed')
)

# update system status periodically
@app.callback(Output(component_id='datepicker', component_property='max_date_allowed'),
              Input('interval-check_system', 'n_intervals'))
def update_system_status(basin):
    #df_status = pd.read_csv(f'{base_url}/data/system_status.csv', parse_dates=True)
    df_status = pd.read_csv(f'{cloud_url}/imgs/monitor/system_status.csv', parse_dates=True)
    return datetime.fromisoformat(df_status['WRF-Hydro NRT'][1]).date()

# callback to switch HUC sources according to zoom level
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switch_huc'
    ),
    Output('huc-bound', 'url'),
    Output('huc-bound', 'zoomToBoundsOnClick'),
    Input('map-region', 'zoom')
)

# callback to switch river vector sources according to zoom level
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switch_river_vector'
    ),
    Output('nwm-rivers', 'url'),
    Output('nwm-rivers', 'zoomToBoundsOnClick'),
    Input('map-region', 'zoom'),
    Input('map-region', 'center')
)

# callback to switch region boundary according to zoom level
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switch_region'
    ),
    Output('cbrfc-bound', 'url'),
    Output('cbrfc-bound', 'zoomToBoundsOnClick'),
    Input('map-region', 'zoom'),
    Input('map-region', 'center')
)

# callback to toggle collapse-openmore
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='toggle_openmore'
    ),
    Output('collapse-openmore', 'is_open'),
    Output('button-openmore', 'children'),
    Input('button-openmore', 'n_clicks'),
    State('collapse-openmore', 'is_open')
)

# create/update historic time series graph in popup
@app.callback(Output(component_id='basin-graph-nrt',     component_property='figure'),
              Output(component_id='basin-graph-nrt-m',   component_property='figure'),
              Output(component_id='basin-graph-retro',   component_property='figure'),
              Output(component_id='basin-graph-retro-m', component_property='figure'),
              Output('basin-popup-plots', 'is_open'),
              Output('basin-popup-plots', 'title'),
              Input('huc-bound', 'clickData'))
def update_basin(basin):
    huc = 'huc8'
    if 'huc8' in basin['properties']:
        staid = basin['properties']['huc8']
        stain = basin['properties']['tooltip']
        is_open = True
    elif 'huc10' in basin['properties']:
        staid = basin['properties']['huc10']
        stain = basin['properties']['tooltip']
        is_open = True
        huc = 'huc10'
    else:
        staid = ''
        stain = ''
        is_open = False

    fig_nrt     = draw_basin_ts(staid, 'nrt', huc, 'daily')
    fig_nrt_m   = draw_basin_ts(staid, 'nrt', huc, 'monthly')
    fig_retro   = draw_basin_ts(staid, 'retro', huc, 'daily')
    fig_retro_m = draw_basin_ts(staid, 'retro', huc, 'monthly')

    return [fig_nrt, fig_nrt_m, fig_retro, fig_retro_m, is_open, stain]
    #return [fig_nrt, is_open, stain]

# create/update historic time series graph in popup
@app.callback(Output(component_id='graph-retro', component_property='figure'),
              Output('popup-plots', 'is_open'),
              Output('popup-plots', 'title'),
              Input('fnf-sites', 'clickData'))
def update_flows(fcst_point):
    if fcst_point==None:
        staid = 'FTO'
        stain = 'FTO: Feather River at Oroville'
    else:
        staid = fcst_point['properties']['station_id']
        stain = fcst_point['properties']['tooltip']
    fig_retro = draw_retro(staid)

    return [fig_retro, True, stain]

