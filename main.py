from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.io as pio
import os
import dash_bootstrap_components as dbc
from app import app

import ballot_result as layout_file

pio.templates.default = "seaborn"


app.layout = layout_file.layout()

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=False)