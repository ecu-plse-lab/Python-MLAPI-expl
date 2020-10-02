#!/usr/bin/env python
# coding: utf-8

# In[3]:


from IPython.display import YouTubeVideo
YouTubeVideo(id='BPfzqVK6gmk', width=800, height=600)


# ## Interactive Exploratory Dashboard
# 
# This dashboard serves for exploratory purposes for both specialists and lay people. 
# 1. Specialists: It's a quick way to 'query' the dataset and see general trends over time, and across different geographies. 
# 2. Lay people: It's a way to 'read' the data and have an overview of the trends available. 
# 
# A lot can and will be done, but for now, the following types of questions can be answered immediately and visually: 
# 
# - How many terrorist events happened in countries A, B, and C between years Y and Z? 
# - How does the annual trend compare between countries A and B? 
# - Where on the map did terrorist attacks happen in during Year1 - Year2, and countries A, B, C, and D? (with visual pan, zoom, and drag)
# - During the period Year1 - Year2, which were the countries where most terrorist acts happened, and which were the top in terms of the number of deaths? 
# 
# All the magic in interactivity comes from Plotly and Plotly's Dash. 
# 
# The dashboard is hosted on Heroku, and is embedded below for immediate exploration. 
# It might be easier to explore it on the main page, as the notebook width is a bit limiting:   
# https://goo.gl/sxYD1y    
# The code follows below on the page. 

# In[4]:


from IPython.display import HTML
HTML('<iframe width="1400" height="900" src="https://terrorism.herokuapp.com/" frameborder="0" allowfullscreen></iframe>')


# In[ ]:


# import random # many attacks are listed on the same lat/long cooridinates and would be plotted on top of each other, so we add some minor noise
# import textwrap # to better display the hover text showing some data about attacks, as well as the description
# import datetime as dt 
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import plotly.graph_objs as go
# import pandas as pd

# terrorism = pd.read_csv('../input/globalterrorismdb_0617dist.csv', 
#                         encoding='latin-1', low_memory=False, 
#                         usecols=['iyear', 'imonth', 'iday', 'country_txt', 'city', 'longitude', 
#                                  'latitude', 'nkill', 'nwound', 'summary', 'target1', 'gname'])

# terrorism = terrorism[terrorism['imonth'] != 0]
# terrorism['day_clean'] = [15 if x == 0 else x for x in terrorism['iday']]
# terrorism['date'] = [pd.datetime(y, m, d) for y, m, d in zip(terrorism['iyear'], terrorism['imonth'], terrorism['day_clean'])]


# app = dash.Dash()
# server = app.server
# app.title = 'Terrorist Attacks 1970 - 2016 | Global Terrorism Database Visuzalizations'

# app.layout = html.Div([
#     dcc.Graph(id='map',
#               config={'displayModeBar': False}),
#     html.Div([
#         dcc.RangeSlider(id='years',
#                         min=1970,
#                         max=2016,
#                         dots=True,
#                         value=[2010, 2016],
#                         marks={str(yr): "'" + str(yr)[2:] for yr in range(1970, 2017)}),
         
#         html.Br(), html.Br(), 
#     ], style={'width': '75%', 'margin-left': '12%', 'background-color': '#eeeeee'}),
#     html.Div([
#         dcc.Dropdown(id='countries',
#                      multi=True,
#                      value=[''],
#                      placeholder='Select Countries',
#                      options=[{'label': c, 'value': c}
#                               for c in sorted(terrorism['country_txt'].unique())])        
#     ], style={'width': '50%', 'margin-left': '25%', 'background-color': '#eeeeee'}),
    
#     dcc.Graph(id='by_year_country',
#               config={'displayModeBar': False}),
#     html.Hr(), 
#     html.Content('Top Countries', style={'font-family': 'Palatino', 'margin-left': '45%',
#                                          'font-size': 25}),
#     html.Br(), html.Br(),
#     html.Div([
#         html.Div([
#             html.Div([
#                 dcc.RangeSlider(id='years_attacks',
#                                 min=1970,
#                                 max=2016,
#                                 dots=True,
#                                 value=[2010, 2016],
#                                 marks={str(yr): str(yr) for yr in range(1970, 2017, 5)}),
#                 html.Br(),
                
#             ], style={'margin-left': '5%', 'margin-right': '5%'}),
#             dcc.Graph(id='top_countries_attacks',
#                       figure={'layout': {'margin': {'r': 10, 't': 50}}},
#                       config={'displayModeBar': False})
#         ], style={'width': '48%', 'display': 'inline-block'}),
        
#         html.Div([
#             html.Div([
#                 dcc.RangeSlider(id='years_deaths',
#                                 min=1970,
#                                 max=2016,
#                                 dots=True,
#                                 value=[2010, 2016],
#                                 marks={str(yr): str(yr) for yr in range(1970, 2017, 5)}),
#                 html.Br(),
                
#             ], style={'margin-left': '5%', 'margin-right': '5%'}),

#             dcc.Graph(id='top_countries_deaths',
#                       config={'displayModeBar': False},
#                       figure={'layout': {'margin': {'l': 10, 't': 50}}})

#         ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
#     ]),
    
#     html.A('@eliasdabbas', href='https://www.twitter.com/eliasdabbas'), 
#     html.P(),
#     html.Content('  Code: '),
#     html.A('github.com/eliasdabbas/terrorism', href='https://github.com/eliasdabbas/terrorism'), html.Br(), html.Br(),
#     html.Content('Data: National Consortium for the Study of Terrorism and Responses to Terrorism (START). (2016). '
#                  'Global Terrorism Database [Data file]. Retrieved from https://www.start.umd.edu/gtd')
    
# ], style={'background-color': '#eeeeee'})

# @app.callback(Output('by_year_country', 'figure'),
#              [Input('countries', 'value'), Input('years', 'value')])
# def annual_by_country_barchart(countries, years):
#     df = terrorism[terrorism['country_txt'].isin(countries) & terrorism['iyear'].between(years[0], years[1])]
#     df = df.groupby(['iyear', 'country_txt'], as_index=False)['date'].count()
    
#     return {
#         'data': [go.Bar(x=df[df['country_txt'] == c]['iyear'],
#                         y=df[df['country_txt'] == c]['date'], 
#                         name=c)
#                  for c in countries] ,
#         'layout': go.Layout(title='Yearly Terrorist Attacks ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
#                             plot_bgcolor='#eeeeee',
#                             paper_bgcolor='#eeeeee',
#                             font={'family': 'Palatino'})
#     }

# @app.callback(Output('map', 'figure'),
#              [Input('countries', 'value'), Input('years', 'value')])
# def countries_on_map(countries, years):
#     df = terrorism[terrorism['country_txt'].isin(countries) & terrorism['iyear'].between(years[0], years[1])]
    
#     return {
#         'data': [go.Scattergeo(lon=[x + random.gauss(0.04, 0.03) for x in df[df['country_txt'] == c]['longitude']],
#                                lat=[x + random.gauss(0.04, 0.03) for x in df[df['country_txt'] == c]['latitude']],
#                                name=c,
#                                hoverinfo='text',
#                                opacity=0.9,
#                                marker={'size': 9, 'line': {'width': .2, 'color': '#cccccc'}},
#                                hovertext=df[df['country_txt'] == c]['city'].astype(str) + ', ' + df[df['country_txt'] == c]['country_txt'].astype(str)+ '<br>' +
#                                          [dt.datetime.strftime(d, '%d %b, %Y') for d in df[df['country_txt'] == c]['date']] + '<br>' +
#                                          'Perpetrator: ' + df[df['country_txt'] == c]['gname'].astype(str) + '<br>' +
#                                          'Target: ' + df[df['country_txt'] == c]['target1'].astype(str) + '<br>' + 
#                                          'Deaths: ' + df[df['country_txt'] == c]['nkill'].astype(str) + '<br>' +
#                                          'Injured: ' + df[df['country_txt'] == c]['nwound'].astype(str) + '<br><br>' + 
#                                          ['<br>'.join(textwrap.wrap(x, 40)) if not isinstance(x, float) else '' for x in df[df['country_txt'] == c]['summary']])
#                  for c in countries],
#         'layout': go.Layout(title='Terrorist Attacks ' + ', '.join(countries) + '  ' + ' - '.join([str(y) for y in years]),
#                             font={'family': 'Palatino'},
#                             titlefont={'size': 22},
#                             paper_bgcolor='#eeeeee',
#                             plot_bgcolor='#eeeeee',
#                             width=1420,
#                             height=650,
#                             annotations=[{'text': '<a href="https://www.twitter.com">@eliasdabbas</a>', 'x': .2, 'y': -.1, 
#                                           'showarrow': False},
#                                          {'text': 'Data: START Consortium', 'x': .2, 'y': -.13, 'showarrow': False}],                            
#                             geo={'showland': True, 'landcolor': '#eeeeee',
#                                  'countrycolor': '#cccccc',
#                                  'showsubunits': True,
#                                  'subunitcolor': '#cccccc',
#                                  'subunitwidth': 5,
#                                  'showcountries': True,
#                                  'oceancolor': '#eeeeee',
#                                  'showocean': True,
#                                  'showcoastlines': True, 
#                                  'showframe': False,
#                                  'coastlinecolor': '#cccccc',
#                                  'lonaxis': {'range': [df['longitude'].min()-1, df['longitude'].max()+1]},
#                                  'lataxis': {'range': [df['latitude'].min()-1, df['latitude'].max()+1]}
#                                               })
#     }

# @app.callback(Output('top_countries_attacks', 'figure'),
#              [Input('years_attacks', 'value')])
# def top_countries_count(years):
#     df_top_countries = terrorism[terrorism['iyear'].between(years[0], years[1])]
#     df_top_countries = df_top_countries.groupby(['country_txt'], as_index=False)['nkill'].agg(['count', 'sum'])
#     df = df_top_countries.sort_values(['count']).tail(20)
#     return {
#         'data': [go.Bar(x=df['count'],
#                         y=df.index,
#                         orientation='h',
#                         constraintext='none',
#                         text=df_top_countries.sort_values(['count']).tail(20).index,
#                         textposition='outside')],
#         'layout': go.Layout(title='Number of Terrorist Attacks ' + '  ' + ' - '.join([str(y) for y in years]),
#                             plot_bgcolor='#eeeeee',
#                             paper_bgcolor='#eeeeee',
#                             font={'family': 'Palatino'},
#                             height=700,
#                             yaxis={'visible': False})
#     }
    
# @app.callback(Output('top_countries_deaths', 'figure'),
#              [Input('years_deaths', 'value')])
# def top_countries_deaths(years):
#     df_top_countries = terrorism[terrorism['iyear'].between(years[0], years[1])]
#     df_top_countries = df_top_countries.groupby(['country_txt'], as_index=False)['nkill'].agg(['count', 'sum'])
    
#     return {
#         'data': [go.Bar(x=df_top_countries.sort_values(['sum']).tail(20)['sum'],
#                         y=df_top_countries.sort_values(['sum']).tail(20).index,
#                         orientation='h',
#                         constraintext='none',
#                         showlegend=False, 
#                         text=df_top_countries.sort_values(['sum']).tail(20).index,
#                         textposition='outside')],
#         'layout': go.Layout(title='Total Deaths from Terrorist Attacks ' + '  ' + ' - '.join([str(y) for y in years]),
#                             plot_bgcolor='#eeeeee',
#                             font={'family': 'Palatino'},
#                             paper_bgcolor='#eeeeee',
#                             height=700,
#                             yaxis={'visible': False})
#     }

# if __name__ == '__main__':
#     app.run_server()
