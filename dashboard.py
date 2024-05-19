from dash import Dash
import dash_bootstrap_components as dbc

from appLayout import Layout, dbc_css

app = Dash(__name__, external_stylesheets=[
    dbc.themes.UNITED, 
    dbc.icons.BOOTSTRAP,
    dbc.icons.FONT_AWESOME,
    dbc_css
])

app.layout = Layout

app.run(debug=True)

