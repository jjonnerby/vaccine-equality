import pandas as pd
import plotly.express as px
import plotly.io as pio
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np


pd.set_option('max_rows', 20)
pio.renderers.default = "browser"
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Vaccine equality'

colors = {
    'background': 'white',
    'bodyColor': 'white',
    'text': 'black'
}


# --- Plot functions
fig = go.Figure()


def plot_country(data, name, colour, pop, per_hundred):
    factor = 1
    if per_hundred:
        factor = pop/100
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data['total']/factor,
                mode='lines',
                name=name,
                marker=dict(
                    color=colour
                )))
        fig.add_annotation(
            xref="x domain",
            x=1.0,
            y=data['total'].iloc[-1]/factor,
            xanchor='left',
            text=name,
            font=dict(
                family='sans serif',
                size=14,
                color=colour
            ),
            showarrow=False,
            arrowhead=False)


def plot_looks(xlabel, ylabel):
    fig.update_layout(showlegend=False)
    fig.update_layout(
        autosize=False,
        width=600,
        height=500,
        margin=dict(
            l=50,
            r=100,
            b=100,
            t=100,
            pad=10
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="",
        yaxis_title="Doses given per 100 people",
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
    )


# --- Read and plot vaccine data
# Plot individual countries
# plot_individual_country('Mexico', 'red', per_hundred=True)
# plot_individual_country('United States', 'blue', per_hundred=True)

# Plot a collection of countries
LMIC = pd.read_csv('../result/LMIC.csv', index_col=0)
HIC = pd.read_csv('../result/HIC.csv', index_col=0)
LMIC_pop = np.loadtxt('../result/LMIC_pop.txt')
HIC_pop = np.loadtxt('../result/HIC_pop.txt')

plot_country(LMIC, 'LMIC', 'red', LMIC_pop, per_hundred='True')
plot_country(HIC, 'HIC', 'blue', HIC_pop, per_hundred='True')
plot_looks('Date', 'Doses  / 100 individuals')


# --- Graph container
def graph1():
    return dcc.Graph(id='graph1', figure=fig)


# --- Set up dashboard
def get_page_heading_style():
    return {'backgroundColor': colors['background']}


def get_page_heading_title():
    return html.H1(
        children='Vaccine equality project',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })


def get_page_heading_subtitle():
    return html.H2(
        children='An MD4SG Initiative',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })


def generate_page_header():
    main_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_title(), md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    subtitle_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_subtitle(), md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    header = (main_header, subtitle_header)
    return header


def generate_layout():
    page_header = generate_page_header()
    layout = dbc.Container(
        [
            page_header[0],
            dbc.Row(
                [
                    dbc.Col(graph1(), md=dict(size=6, offset=4))
                ],
                style={'backgroundColor': colors['bodyColor']},
                align="center",

            ),
        ],
        fluid=True, style={'backgroundColor': colors['bodyColor']}
    )
    return layout


app.layout = generate_layout()
app.run_server(host='0.0.0.0', debug=True)
