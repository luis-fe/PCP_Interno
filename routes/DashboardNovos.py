from flask import Blueprint
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

dashboard_bp = Blueprint('dashboard_routes', __name__)

app = Dash(__name__, server=dashboard_bp, url_base_pathname='/dashboard/')

# Assume que você tem um "long-form" data frame
df = pd.DataFrame({
    "Fases": ["Corte", "Separacao", "Bordado", "Silk", "Cosutra Pate", "Montagem"],
    "Carga": [400, 100, 200, 200, 400, 500]
})

fig = px.bar(df, x="Fases", y="Carga", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Carga de setores'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])
