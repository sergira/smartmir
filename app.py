# Import required libraries
import os

import plotly.plotly as py
import plotly.graph_objs as go

import flask
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

import numpy as np
import pandas as pd
import random

import requests
from bs4 import BeautifulSoup  

# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(random.randint(0, 1000000)))
app = dash.Dash(__name__, server=server)



# Put your Dash code here

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css",
})

app.index_string = '<!DOCTYPE html>\n<html>\n    <head>\n        {%metas%}\n        <title>{%title%}</title>\n        {%favicon%}\n        {%css%}\n<style>body {background: url(/static/JpagxN.jpg);  background-attachment:fixed; background-position:center; background-size:cover}</style>\n    </head>\n    <body>\n        {%app_entry%}\n        <footer>\n            {%config%}\n            {%scripts%}\n        </footer>\n    </body>\n</html>'

# Import places
places = pd.read_csv('resultats.csv',index_col=[0], encoding='latin-1')

# Some functions
def quotes():
#	p = int(pages(category))
#	page = range(1,p+1)
#	random_page = random.choice(page)
    url = "http://www.brainyquote.com/quotes/topics/motivational"
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    quoteslist = soup.find(id='quotesList').find_all('div',{'class':'m-brick'})
    res = []
    for quotebox in quoteslist:
        el = quotebox.find('div',{'class':''}).find('div',{'class':'clearfix'}).find_all('a')
        try:
            res.append((el[1].text,el[2].text))
        except:
            res.append((el[0].text,el[1].text))
        
    idx = random.choice(range(len(res)))
    return """{}

- *{}*
""".format(res[idx][0], res[idx][1])


# Declare layout
app.layout = html.Div(
#        className='container',
        children=[
            html.Div([dcc.Markdown(
"""# SMARTMIR
{}

""".format(quotes())),
                html.Div(dcc.Dropdown(
                        id='dd-ccaa', 
                        placeholder='Escull una o més CCAA...',
                        options=[{'label':com,'value':com} for com in places['comunidad'].sort_values().unique()],
                        multi=True
                )),
                html.Div(dcc.Dropdown(
                        id='dd-especialitat', 
                        placeholder='Escull una o més especialitats...',
                        options=[{'label':com,'value':com} for com in places['especialidad'].sort_values().unique()],
                        multi=True
                )),
                html.Div(dcc.Dropdown(
                        id='dd-localitat', 
                        placeholder='Escull una o més localitats...',
                        options=[{'label':com,'value':com} for com in places['localidad'].sort_values().unique()],
                        multi=True
                )),
				html.Br()
                ], className='container'),
            html.Div(className='row', 
                children=[
                    html.Div(className='six columns',
                        children=[
                            dcc.Graph(id='graf-ccaa-places', style={'border':'1px'},
                                figure={
                                    'data':[
                                        go.Bar(
                                            x = list(places.groupby('comunidad').sum().sort_values('plazas',ascending=False).index),
                                            y = places.groupby('comunidad').sum().sort_values('plazas',ascending=False).values[:,0],
                                            name='Rest of world',
                                            marker=go.bar.Marker(
                                                    color='rgb(55, 83, 109)'
                                            )
                                        )
                                    ]
                                }
                            )
                        ]         
                    ),
                    html.Div(className='six columns',
                        children=[
                            dcc.Graph(id='graf-especialitat-places', style={'border':'1px'},
                                figure={
                                    'data':[
                                        go.Bar(
                                            x = list(places.groupby('especialidad').sum().sort_values('plazas',ascending=False).index),
                                            y = places.groupby('especialidad').sum().sort_values('plazas',ascending=False).values[:,0],
                                            name='Rest of world',
                                            marker=go.bar.Marker(
                                                    color='rgb(55, 83, 109)'
                                            )
                                        )
                                    ]
                                }
                            )
                        ]         
                    ),
            ]),
            html.Br(),
            html.Div(style={'margin':'25'},
                children=[
                    dt.DataTable(id='table',
                        columns=[{"name": i.upper(), "id": i} for i in places.columns],
                        data=places.to_dict("rows")
                    )
                ]
            )         
        ]
    )
        
@app.callback(Output('dd-localitat','options'),
              [Input('dd-ccaa','value'), Input('dd-especialitat','value')])
def actualitza_localitats(ccaa, especialitat):
    subplaces = places
    if ccaa != None:
        subplaces = subplaces[places['comunidad'].isin(ccaa)]
    if especialitat != None:
        subplaces = subplaces[places['especialidad'].isin(especialitat)]
    
    return [{'label':com,'value':com} for com in subplaces['localidad'].sort_values().unique()]


@app.callback(Output('graf-ccaa-places','figure'),
              [Input('dd-ccaa','value'), Input('dd-especialitat','value'), Input('dd-localitat','value')])
def graf_ccaa_places(ccaa, especialitat, localitat):
    subplaces = places
    
    if ccaa is not None and len(ccaa) > 1:
        subplaces = subplaces[places['comunidad'].isin(ccaa)]
        
    if especialitat is not None and len(especialitat) > 0:
        subplaces = subplaces[places['especialidad'].isin(especialitat)]
        
    if localitat is not None and len(localitat) > 0:
        subplaces = subplaces[places['localidad'].isin(localitat)]
        
        return {'data':[
                go.Bar(
                    x = list(subplaces.groupby('localidad').sum().sort_values('plazas',ascending=False).index),
                    y = subplaces.groupby('localidad').sum().sort_values('plazas',ascending=False).values[:,0],
                    name='Rest of world',
                    marker=go.bar.Marker(
                            color='rgb(55, 83, 109)'
                    )
                )
            ]
        }
        
    return {'data':[
            go.Bar(
                x = list(subplaces.groupby('comunidad').sum().sort_values('plazas',ascending=False).index),
                y = subplaces.groupby('comunidad').sum().sort_values('plazas',ascending=False).values[:,0],
                name='Rest of world',
                marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                )
            )
        ]
    }


@app.callback(Output('graf-especialitat-places','figure'),
              [Input('dd-ccaa','value'), Input('dd-especialitat','value'), Input('dd-localitat','value')])
def graf_ccaa_places(ccaa, especialitat, localitat):
    subplaces = places
    
    if ccaa is not None and len(ccaa) > 0:
        subplaces = subplaces[places['comunidad'].isin(ccaa)]
        
    if especialitat is not None and len(especialitat) > 1:
        subplaces = subplaces[places['especialidad'].isin(especialitat)]
    
    if localitat is not None and len(localitat) > 0:
        subplaces = subplaces[places['localidad'].isin(localitat)]
        
    return {'data':[
            go.Bar(
                x = list(subplaces.groupby('especialidad').sum().sort_values('plazas',ascending=False).index),
                y = subplaces.groupby('especialidad').sum().sort_values('plazas',ascending=False).values[:,0],
                name='Rest of world',
                marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                )
            )
        ]
    }
    
    
@app.callback(Output('table','columns'),
              [Input('dd-ccaa','value'), Input('dd-especialitat','value'), Input('dd-localitat','value')])
def taula_labels(ccaa, especialitat, localitat):
    subplaces = places
    
    if ccaa is not None:
        subplaces = subplaces[places['comunidad'].isin(ccaa)]
        
    if especialitat is not None:
        subplaces = subplaces[places['especialidad'].isin(especialitat)]
    
    if localitat is not None:
        subplaces = subplaces[places['localidad'].isin(localitat)]
        
    return [{"name": i.upper(), "id": i} for i in subplaces.columns]
    
@app.callback(Output('table','data'),
              [Input('dd-ccaa','value'), Input('dd-especialitat','value'), Input('dd-localitat','value')])
def taula_valors(ccaa, especialitat, localitat):
    subplaces = places
    
    if ccaa is not None:
        subplaces = subplaces[places['comunidad'].isin(ccaa)]
        
    if especialitat is not None:
        subplaces = subplaces[places['especialidad'].isin(especialitat)]
    
    if localitat is not None:
        subplaces = subplaces[places['localidad'].isin(localitat)]
        
    return subplaces.to_dict('rows')


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
