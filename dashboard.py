from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')


# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='Data Dashboard'),
    html.Hr(),
    dcc.RadioItems(options=['pop', 'lifeExp','gdpPercap'],
                   value='lifeExp',
                   id='controls-and-radio-item'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=6),
    dcc.Graph(figure={}, id='controls-and-graph')
])

# Interaction control
@callback(
    Output(component_id='controls-and-graph', 
           component_property='figure'),
    Input(component_id='controls-and-radio-item', 
          component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df,
                       x='continent',
                       y=col_chosen,
                       histfunc='avg')
    return fig

# Run the app
app.run(debug=True)
