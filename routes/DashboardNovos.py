from flask import Blueprint
from flask import Flask, render_template
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

dashboard_routes = Blueprint('dashboard_routes', __name__)

# Use o objeto Flask existente (app) para criar a aplicação Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server=dashboard_routes, url_base_pathname='/dashboard/', external_stylesheets=external_stylesheets)


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
