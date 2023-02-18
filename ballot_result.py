from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import plotly.io as pio

import base64
import datetime
import io

import pandas as pd

import template_css as style
from template_functions import tabs_layout
from app import app

title = html.P("ASUC Election 2023", style=style.TITLE)
tabs = html.Div([tabs_layout(["Results", "About", "FAQ"])])

def layout():
    return html.Div([
        html.Div([
            html.Div([title, tabs], id="topbar-div", style=style.TOPBAR),  # Topbar (Tabs, Title, ...)
            html.Div("Loading Content...", id="content-div", style=style.CONTENT),  # Content (Loads in body() function)
            # html.Div(id="data-div", style={"display": "none"}),  # Invisible Div to store data in json string format
        ], id="body", style=style.BODY),
    ], style={"width": "100vw", "height": "100vh"})


@app.callback(
    Output("content-div", "children"),
    Input("tabs", "value"),
)
def content(tab):
    if tab == "Results":
        return layout_results()
    elif tab == "About":
        return layout_about()
    elif tab == "FAQ":
        return layout_faq()

def layout_results():
    return html.Div(id = "upload-file", style={"width": "80%"})

def layout_about():
    return html.Div("About Content")

def layout_faq():
    return html.Div("FAQ Content")

@app.callback(
    Output("upload-file", "children"),
    Input("topbar-div", "children"))
def upload_file(null):
    return html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=False
                ),
                html.Div(id='output-data-upload'),
            ])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    print(df.columns)
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children