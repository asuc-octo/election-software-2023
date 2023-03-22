from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.graph_objects as go
import plotly.io as pio

import base64
import datetime
import io

import pandas as pd

import config.template_css as style
from config.template_functions import tabs_layout
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
    return html.Div(
        [html.Div(id='upload-file'),
         html.Div(id='transfer-rslt')
        ]
    )


@app.callback(
        Output("transfer-rslt", "children"),
        Input("tabs", "value")
)
def transfer_table(val):
    data = ''
    with open('results/transfer_representative.txt', 'r') as file:
        data = file.read()
    # return html.Div(data, style={'whiteSpace': 'pre-line'})

    StringData = io.StringIO("""{}""".format(data))
    
    # let's read the data using the Pandas
    # read_csv() function
    dataframe = pd.read_csv(StringData, sep ="\r\n")
    first_col = dataframe.columns[0]
    dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
    dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
    dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
    dataframe = dataframe.loc[:, dataframe.columns != first_col]
    max_rows = 26
    result = [html.Tr([html.Th(col, style={"border-left": "thin solid"}) if col != 'Candidate' else html.Th(col) for col in dataframe.columns])] # Header
    merge_span = len(dataframe.columns)
    for i in range(min(len(dataframe), max_rows)):
        # Body
        
        # if i == 4:
        #     result = result + [html.Tr([html.Th("KBA Quality Indicators", colSpan=merge_span, style={"text-align": "center"})], style={"text-align": "center"})]
        # elif i == 0:
        #     result = result + [html.Tr([html.Th("KB Quality & Compliance Indicators", colSpan=merge_span, style={"text-align": "center"})],
        #                                style={"text-align": "center"})]
        if dataframe.iloc[i][2] == "Elected":
            result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style={"border-left": "thin solid"}) if col != 'Candidate' else html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])]
        else:
            result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style={"border-left": "thin solid"}) if col != 'Candidate' else html.Td(dataframe.iloc[i][col]) for col in dataframe.columns],
                                   style={"text-align": "center"})]
        #     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style={"border-left": "thin solid"}) if col == "N" else html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])]
    return html.Table(result, style=style.TABLE_CONTENT)

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