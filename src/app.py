from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.io as pio
import os
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

pio.templates.default = "seaborn"

from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.io as pio

import base64
import datetime
import io
import os.path

import pandas as pd

from config.template_functions import tabs_layout
import config.template_css as style

from backend.tabulations_calc import calculate_senate, calculate_propositions, calculate_execs

title = html.P("ASUC Election 2023", style=style.TITLE)
tabs = html.Div([tabs_layout(["Results", "About", "FAQ"])])

RESULTS_PATH = str(os.getcwd()) + "/results/" #for heroku 
# RESULTS_PATH = str(os.getcwd()) + "/src/results/" # for local

def split_list(a_list):
    half = len(a_list)//2
    return a_list[:half], a_list[half:]

def split_list_into_n(a, n):
    k, m = divmod(len(a), n)
    generator = (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
    return list(generator)

def layout():
    return html.Div([
        html.Div([
            html.Div([title, tabs], id="topbar-div", style=style.TOPBAR),  # Topbar (Tabs, Title, ...)
            html.Div("Loading Content...", id="content-div", style=style.CONTENT),  # Content (Loads in body() function)
            html.Div(id="data-div", style={"display": "none"}),  # Invisible Div to store data in json string format
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
        [html.Br(),
         dbc.Row(
            [
            dbc.Col([dbc.Col(html.Div("Upload Position Title File")),
            html.Br(),
            html.Div(id='upload-position-file')]),

            # html.Br(), html.Br(),
            dbc.Col([dbc.Col(html.Div("Upload Proposition Name File")),
            html.Br(),
            html.Div(id='upload-proposition-file'),
            html.Br()])
            ]),
        html.Div(id='upload-results-file'),
        html.Br()
        ],
        style={'width': '70%'}
    )


@app.callback(
    Output("upload-proposition-file", "children"),
    Input("topbar-div", "children"))
def upload_file(null):
    return html.Div([
                dcc.Upload(
                    id='upload-proposition-data',
                    children=
                        html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                    style=style.UPLOAD_FILE_BIG,
                    # Allow multiple files to be uploaded
                    multiple=False
                ),
                html.Div(id='output-proposition-str')
            ])

@app.callback(Output('output-proposition-str', 'value'),
              Input('upload-proposition-data', 'contents'),
              State('upload-proposition-data', 'filename'),
              State('upload-proposition-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    """
    return: str
        ie: "Proposition 22A\nProposition 22B\n..."
    """
    print("Received the proposition file")
    if list_of_contents is not None:
        children = parse_contents_txt(list_of_contents, list_of_names, list_of_dates).getvalue()
        return children

@app.callback(
    Output("upload-position-file", "children"),
    Input("topbar-div", "children"))
def upload_file(null):
    return html.Div([
                dcc.Upload(
                    id='upload-position-data',
                    children=
                        html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                    style=style.UPLOAD_FILE_BIG,
                    # Allow multiple files to be uploaded
                    multiple=False
                ),
                html.Div(id='output-position-str')
            ])

@app.callback(Output('output-position-str', 'value'),
              Input('upload-position-data', 'contents'),
              State('upload-position-data', 'filename'),
              State('upload-position-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    """
    return: str
        ie: "President\nExecutive Vice President\n..."
    """
    print("Received the position file")
    if list_of_contents is not None:
        children = parse_contents_txt(list_of_contents, list_of_names, list_of_dates).getvalue()
        return children
    
def txt_str_to_list(string):
    """
    return list:
        ie. input: "President\nExecutive Vice President\n..."
        output: ['President', 'Executive Vice President', ...]
    """
    return string.split("\n")

def parse_contents_txt(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'txt' in filename:
            return io.StringIO(decoded.decode('utf-8'))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    

def layout_about():
    return html.Div("About Content")

def layout_faq():
    return html.Div("FAQ Content")

@app.callback(
    Output("upload-results-file", "children"),
    Input("topbar-div", "children"),
    Input('upload-position-data', 'contents'),
    Input('upload-proposition-data', 'contents')
)
def upload_file(null, position_file_content, proposition_file_content):
    if (position_file_content is not None) & (proposition_file_content is not None):
        return html.Div([
                    html.Br(), html.Br(),
                    dbc.Row(dbc.Col(html.Div("Upload Results File"))),
                    html.Br(),
                    dcc.Upload(
                        id='upload-results-data',
                        children=
                            html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                        style=style.UPLOAD_FILE_BIG,
                        # Allow multiple files to be uploaded
                        multiple=False
                    ),
                    html.Div(id='loading'),
                    html.Div(id='exec-first-group-calc'),
                    html.Div(id='exec-second-group-calc'),
                    html.Div(id='exec-third-group-calc'),
                    html.Div(id='senate-calc'),
                    html.Div(id='proposition-calc'),
                    html.Div(id='output-data-upload'),
                ])

@app.callback(
        Output('loading', 'children'),
        Input('upload-results-data', 'contents'),
        # Input('loading-result-progress', 'value'),
        State('upload-results-data', 'filename'),
        State('upload-results-data', 'last_modified')
)
def get_loading(list_of_contents, list_of_names, list_of_dates): # calc_fin_num
    if (list_of_contents is not None):
        return html.Div("Reading the results & calculating. This might take a few moments")


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), low_memory=False)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    # run calculations
    return df
    # calculate_senate(df)
    # calculate_propositions(proposition_lst, df)
    # return "Parse Content Success"

def parse_contents_execs(contents, filename, date, position_lst, proposition_lst):
    """
    Calculates file for senate
    Returns nothing
    Input: contents, filename, date, position_lst, proposition_lst
    """
    df = parse_contents(contents, filename)
    calculate_execs(position_lst, df)
    return

def parse_contents_senate(contents, filename, date, position_lst, proposition_lst):
    """
    Calculates file for senate
    Returns nothing
    Input: contents, filename, date, position_lst, proposition_lst
    """
    df = parse_contents(contents, filename)
    calculate_senate(df)
    return

def parse_contents_proposition(contents, filename, date, position_lst, proposition_lst):
    """
    Calculates file for proposition
    Returns nothing
    Input: contents, filename, date, position_lst, proposition_lst
    """
    df = parse_contents(contents, filename)
    calculate_propositions(proposition_lst, df)
    return


def convert_dtype(x):
    if not x:
        return ''
    try:
        return str(x)   
    except:        
        return ''



"""
html.Div(id='exec-first-group-calc'),
html.Div(id='exec-second-group-calc'),
html.Div(id='senate-calc'),
html.Div(id='proposition-calc'),
"""

SPLIT_POSITION_N = 3

@app.callback(Output('exec-first-group-calc', 'value'),
              Input('upload-results-data', 'contents'),
              State('upload-results-data', 'filename'),
              State('upload-results-data', 'last_modified'),
              Input('output-position-str', 'value'),
              Input('output-proposition-str', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, position_lst_str, proposition_list_str):
    print("Received the file")
    if list_of_contents is not None:
        position_lst = txt_str_to_list(position_lst_str)
        position_first_group = split_list_into_n(position_lst, SPLIT_POSITION_N)[0]
        proposition_lst = txt_str_to_list(proposition_list_str)
        parse_contents_execs(list_of_contents, list_of_names, list_of_dates, position_first_group, proposition_lst)
        return 1


@app.callback(Output('exec-second-group-calc', 'value'),
              Input('upload-results-data', 'contents'),
              State('upload-results-data', 'filename'),
              State('upload-results-data', 'last_modified'),
              Input('output-position-str', 'value'),
              Input('output-proposition-str', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, position_lst_str, proposition_list_str):
    print("Received the file")
    if list_of_contents is not None:
        position_lst = txt_str_to_list(position_lst_str)
        position_second_group = split_list_into_n(position_lst, SPLIT_POSITION_N)[1]
        proposition_lst = txt_str_to_list(proposition_list_str)
        parse_contents_execs(list_of_contents, list_of_names, list_of_dates, position_second_group, proposition_lst)
        return 1

@app.callback(Output('exec-third-group-calc', 'value'),
              Input('upload-results-data', 'contents'),
              State('upload-results-data', 'filename'),
              State('upload-results-data', 'last_modified'),
              Input('output-position-str', 'value'),
              Input('output-proposition-str', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, position_lst_str, proposition_list_str):
    print("Received the file")
    if list_of_contents is not None:
        position_lst = txt_str_to_list(position_lst_str)
        position_third_group = split_list_into_n(position_lst, SPLIT_POSITION_N)[2]
        proposition_lst = txt_str_to_list(proposition_list_str)
        parse_contents_execs(list_of_contents, list_of_names, list_of_dates, position_third_group, proposition_lst)
        return 1


@app.callback(Output('senate-calc', 'value'),
              Input('upload-results-data', 'contents'),
              State('upload-results-data', 'filename'),
              State('upload-results-data', 'last_modified'),
              Input('output-position-str', 'value'),
              Input('output-proposition-str', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, position_lst_str, proposition_list_str):
    print("Received the file")
    if list_of_contents is not None:
        position_lst = txt_str_to_list(position_lst_str)
        proposition_lst = txt_str_to_list(proposition_list_str)
        parse_contents_senate(list_of_contents, list_of_names, list_of_dates, position_lst, proposition_lst)
        return 1
    

@app.callback(Output('proposition-calc', 'value'),
              Input('upload-results-data', 'contents'),
              State('upload-results-data', 'filename'),
              State('upload-results-data', 'last_modified'),
              Input('output-position-str', 'value'),
              Input('output-proposition-str', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, position_lst_str, proposition_list_str):
    print("Received the file")
    if list_of_contents is not None:
        position_lst = txt_str_to_list(position_lst_str)
        proposition_lst = txt_str_to_list(proposition_list_str)
        parse_contents_proposition(list_of_contents, list_of_names, list_of_dates, position_lst, proposition_lst)
        return 1


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-results-data', 'contents'),
              State('upload-results-data', 'filename'),
              State('upload-results-data', 'last_modified'),
              Input('output-position-str', 'value'),
              Input('output-proposition-str', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, position_lst_str, proposition_list_str):
    print("Received the file")
    if list_of_contents is not None:
        # position_lst = txt_str_to_list(position_lst_str)
        # proposition_lst = txt_str_to_list(proposition_list_str)
        # parse_contents_senate(list_of_contents, list_of_names, list_of_dates, position_lst, proposition_lst)
        return html.Div(id='total-rslt')


# @app.callback(
#     Output('results', 'children'),
#     Input('upload-results-data', 'contents')
# )
# def get_final_results(data):
#     return html.Div([
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div("President"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='president-rslt'), width={"size": 9}), justify="around"),
#             html.Br(), html.Br(),

#             dbc.Row(dbc.Col(html.Div("Executive Vice President"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='execvp-rslt'), width={"size": 9}), justify="around"),
#             html.Br(), html.Br(),

#             dbc.Row(dbc.Col(html.Div("Academic Affairs Vice President"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='academic-rslt'), width={"size": 9}), justify="around"),
#             html.Br(), html.Br(),

#             dbc.Row(dbc.Col(html.Div("External Affairs Vice President"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='external-rslt'), width={"size": 9}), justify="around"),
#             html.Br(), html.Br(),

#             dbc.Row(dbc.Col(html.Div("Student Advocate"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='advocate-rslt'), width={"size": 9}), justify="around"),
#             html.Br(), html.Br(),

#             dbc.Row(dbc.Col(html.Div("Transfer Representative"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='transfer-rslt'), width={"size": 9}), justify="around"),
#             html.Br(), html.Br(),

#             dbc.Row(dbc.Col(html.Div("Senate"), width={"size": 9}), justify="center"),
#             html.Br(),
#             dbc.Row(dbc.Col(html.Div(id='senate-rslt'), width={"size": 9}), justify="around"),

#             html.Br()],
#             style={'width': '100%'})


# @app.callback(
#         Output("transfer-rslt", "children"),
#         Input("tabs", "value")
# )
# def transfer_table(val):
#     if os.path.isfile('results/transfer_representative.txt'):
#         data = ''
#         with open('results/transfer_representative.txt', 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         # let's read the data using the Pandas
#         # read_csv() function
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 26
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if dataframe.iloc[i][2] == "Elected":
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on Transfer Data")


# @app.callback(
#         Output("senate-rslt", "children"),
#         Input("tabs", "value")
# )
# def senate_table(val):
#     file_name = 'results/senate.txt'
#     if os.path.isfile(file_name):
#         data = ''
#         with open(file_name, 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         # let's read the data using the Pandas
#         # read_csv() function
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 100
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if dataframe.iloc[i][2] == "Elected":
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on Senate Data")


# @app.callback(
#         Output("president-rslt", "children"),
#         Input("tabs", "value")
# )
# def president_table(val):
#     file_name = 'results/president.txt'
#     if os.path.isfile(file_name):
#         data = ''
#         with open(file_name, 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         # let's read the data using the Pandas
#         # read_csv() function
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 100
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if dataframe.iloc[i][2] == "Elected":
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on President Data")


# @app.callback(
#         Output("execvp-rslt", "children"),
#         Input("tabs", "value")
# )
# def execvp_table(val):
#     file_name = 'results/executive_vice_president.txt'
#     if os.path.isfile(file_name):
#         data = ''
#         with open(file_name, 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         # let's read the data using the Pandas
#         # read_csv() function
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 100
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if dataframe.iloc[i][2] == "Elected":
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on Exec VP Data")


# @app.callback(
#         Output("academic-rslt", "children"),
#         Input("tabs", "value")
# )
# def academic_table(val):
#     file_name = 'results/academic_affairs_vice_president.txt'
#     if os.path.isfile(file_name):
#         data = ''
#         with open(file_name, 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         # let's read the data using the Pandas
#         # read_csv() function
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 100
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if dataframe.iloc[i][2] == "Elected":
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on Academic Affairs VP Data")

# @app.callback(
#         Output("external-rslt", "children"),
#         Input("tabs", "value")
# )
# def external_table(val):
#     file_name = 'results/external_affairs_vice_president.txt'
#     if os.path.isfile(file_name):
#         data = ''
#         with open(file_name, 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         # let's read the data using the Pandas
#         # read_csv() function
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 100
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if dataframe.iloc[i][2] == "Elected":
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on External Affairs VP Data")

# @app.callback(
#         Output("advocate-rslt", "children"),
#         Input("tabs", "value")
# )
# def advocate_table(val):
#     file_name = 'results/student_advocate.txt'
#     if os.path.isfile(file_name):
#         data = ''
#         with open(file_name, 'r') as file:
#             data = file.read()
#         # return html.Div(data, style={'whiteSpace': 'pre-line'})

#         StringData = io.StringIO("""{}""".format(data))
        
#         dataframe = pd.read_csv(StringData, sep ="\r\n")
#         first_col = dataframe.columns[0]
#         dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
#         dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
#         dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
#         dataframe = dataframe.loc[:, dataframe.columns != first_col]
#         max_rows = 100
#         result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
#         merge_span = len(dataframe.columns)
#         for i in range(min(len(dataframe), max_rows)):
#             if i != 0:
#                 # Body
#                 if (dataframe.iloc[i][2] == "Elected"):
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
#                                             style={"text-align": "left"})]
#                 else:
#                     result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
#                                             style={"text-align": "left"})]
#         return html.Table(result, style=style.TABLE_CONTENT)
#     else:
#         html.Div("Waiting on Student Advocate Data")



@app.callback(
        Output("total-rslt", "children"),
        Input("tabs", "value"),
        Input('output-position-str', 'value'),
        Input('output-proposition-str', 'value')
)
def result_table(val, position_lst_str, proposition_list_str):
    """
    With given position_lst_str and proposition_list_str, read the .txt files under results folder.
    """
    position_lst = txt_str_to_list(position_lst_str)
    proposition_lst = txt_str_to_list(proposition_list_str)
    all_result_lst = position_lst + proposition_lst
    all_html_result_lst = []
    for result_name in all_result_lst:
        print("RESULTS_PATH")
        print(RESULTS_PATH)
        file_name = RESULTS_PATH + result_name + '.txt'
        if os.path.isfile(file_name):
            data = ''
            with open(file_name, 'r') as file:
                data = file.read()

            StringData = io.StringIO("""{}""".format(data))
            
            dataframe = pd.read_csv(StringData, sep ="\r\n")
            first_col = dataframe.columns[0]
            if result_name not in proposition_lst:
                dataframe["Candidate"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
            else:
                dataframe["Option"] = dataframe[first_col].str.split('\s+').str[:-2].apply(lambda parts: " ".join(parts))
            dataframe["Votes"] = dataframe[first_col].str.split('\s+').str[-2]
            dataframe["Status"] = dataframe[first_col].str.split('\s+').str[-1]
            dataframe = dataframe.loc[:, dataframe.columns != first_col]
            max_rows = 100
            result = [html.Tr([html.Th(col, style=style.TABLE_CELL) for col in dataframe.columns], style={"text-align": "left"})] # Header
            merge_span = len(dataframe.columns)
            for i in range(min(len(dataframe), max_rows)):
                if i != 0:
                    # Body
                    if (dataframe.iloc[i][2] == "Elected") or (dataframe.iloc[i][2] == "Winner"):
                        result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL_ELECTED) for col in dataframe.columns], 
                                                style={"text-align": "left"})]
                    else:
                        result = result + [html.Tr([html.Td(dataframe.iloc[i][col], style=style.TABLE_CELL) for col in dataframe.columns],
                                                style={"text-align": "left"})]
            all_html_result_lst += DOUBLE_SPACE
            all_html_result_lst += [
                dbc.Row(dbc.Col(html.Div(result_name), width={"size": 9}), justify="center"),
                html.Br(), 
                dbc.Row(dbc.Col(html.Table(result, style=style.TABLE_CONTENT), width={"size": 9}), justify="around")]
        else:
            all_html_result_lst.append(html.Div("Waiting on " + result_name + " Data"))
    return all_html_result_lst + [CONGRATULATIONS]

DOUBLE_SPACE = [html.Br(), html.Br()]

def get_congratulations():
    return html.Div(DOUBLE_SPACE + [dbc.Row(dbc.Col([
        html.Div("🎉 Congratulations to all the elected officials and the winning propositions!\n", style = style.TEXT_CENTER),
        html.Div("And biggest wholehearted support to all the candidates who ran.", style = style.TEXT_CENTER),
        html.Br(),
        html.Div("Tabulations Created by ASUC OCTO Team in collaboration with the ASUC Elections Council", style = style.TEXT_CENTER),
        html.Div("Kindness and Love for All", style = style.TEXT_CENTER)]), justify="center", align="center")
    ], style={'width': '70%', 'text-align':'center'})

CONGRATULATIONS = get_congratulations()

app.layout = layout()
server = app.server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=True)