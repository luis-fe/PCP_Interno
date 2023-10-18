from flask import Flask, render_template
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

app = Flask(__name__)

# Crie um aplicativo Dash
dash_app = dash(__name__, server=app, url_base_pathname='/xxxxxx/')
app_dash = dash_app.server

# Seu layout Dash
df = pd.DataFrame({
    "Fases": ["Corte", "Separacao", "Bordado", "Silk", "Costura Pate", "Montagem"],
    "Carga": [400, 100, 200, 200, 400, 500]
})

#fig = px.bar(df, x="Fases", y="Carga", barmode="group")
fig = px.bar(df, x="Carga", y="Fases", orientation='h', text="Carga")


dash_app.layout = html.Div(children=[
    html.H1(children='Carga de setores'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

# Rota do Flask que incorpora o aplicativo Dash
@app.route('/home')
def dashboard():
    return dash_app.index()

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Defina a porta como 8000
