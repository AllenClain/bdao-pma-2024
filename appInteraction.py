from dash import Dash, html, dcc, State, callback, Output, Input, clientside_callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Incorporate data
path = "."

movies    = pd.read_csv(path + "/Movies.csv", index_col="ID")
country   = pd.read_csv(path + "/Country.csv")
directors = pd.read_csv(path + "/Directors.csv")
genres    = pd.read_csv(path + "/Genres.csv")
language  = pd.read_csv(path + "/Language.csv")
platform  = pd.read_csv(path + "/Platform.csv")
library   = pd.read_csv(path + "/MoviesLibrary.csv", index_col="ID")

# Callbacks

## control light and dark mode
clientside_callback(
    """ 
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');  
       return window.dash_clientside.no_update
    }
    """,
    Output("color_mode-switch", "id"),
    Input("color_mode-switch", "value"),
)

## control undefined components
@callback(
    Output("construction", "is_open"),
    Input("database_save", "n_clicks"),
    Input("database_refresh", "n_clicks"),
    Input("database_upload", "n_clicks"),
    Input("search_button", "n_clicks"),
    Input("construction_close", "n_clicks"),
    State("construction", "is_open")
)
def toggle_modal(n1, n2, n3, n4, click_close, is_open):
    if n1 or n2 or n3 or n4 or click_close:
        return not is_open
    return is_open

## control timeslot selector
@callback(
    Output("pivot-total", "children"),
    Output("pivot-Netflix", "children"),
    Output("pivot-Hulu", "children"),
    Output("pivot-Prime Video", "children"),
    Output("pivot-Disney+", "children"),
    Input("timeslot-selector", "value")
)
def change_timeslot(timeslot):
    sel = (library[["Year"]]
           .loc[
               (timeslot[0] <= library['Year'])&
               (library['Year'] <= timeslot[1])
            ]
            .merge(platform, on="ID", how="left"))
    
    total = f'{sel["ID"].drop_duplicates().count()}'
    netflix = f'{(sel["Platform"] == "Netflix").sum()}'
    hulu = f'{(sel["Platform"] == "Hulu").sum()}'
    prime = f'{(sel["Platform"] == "Prime Video").sum()}'
    disney = f'{(sel["Platform"] == "Disney+").sum()}'
    
    return total, netflix, hulu, prime, disney

## control selected tables
@callback(
    Output("table-top_rated", "children"),
    Input("timeslot-selector", "value")
)
def select_top_rated(timeslot):
    sel = (library[['Title', 'Year', 'Directors', 'Runtime', 'IMDb']]
           .loc[(timeslot[0] <= library['Year'])&(library['Year'] <= timeslot[1])])
    tbl = dbc.Table.from_dataframe(
        sel.sort_values(by=['IMDb', 'Year'], ascending=False).head(3),
        size="sm", striped=True, bordered=True, hover=True)
    return tbl

@callback(
    Output("table-recent", "children"),
    Input("timeslot-selector", "value")
)
def select_top_rated(timeslot):
    sel = (library[['Title', 'Year', 'Directors', 'Runtime', 'IMDb']]
           .loc[(timeslot[0] <= library['Year'])&(library['Year'] <= timeslot[1])])
    tbl = dbc.Table.from_dataframe(
        sel.sort_values(by=['Year', 'IMDb'], ascending=False).head(3),
        size="sm", striped=True, bordered=True, hover=True)
    return tbl

## control top genres bar chart
@callback(
    Output("graph-top_genres_bar", "figure"),
    Input("timeslot-selector", "value"),

    Input("genres-plat_filter", "value")
)
def draw_top_genres(timeslot, filter_plat):
    if filter_plat is None:
        filter_plat = ["Netflix", "Hulu", "Prime Video", "Disney+"]
    
    sel = (library[["Year"]]
           .loc[(timeslot[0] <= library['Year'])&
                (library['Year'] <= timeslot[1])&
                (platform["Platform"].isin(filter_plat))]
           .merge(genres, on="ID", how="left")
           .drop(columns="Year"))
    
    fig = px.bar(
        sel.groupby("Genres").count().sort_values("ID").tail(10)
        .reset_index().rename(columns={"ID": "Num"}),
        x="Num", y="Genres", 
        orientation="h",
        hover_data=['Num'])
    
    fig.update_layout(
        template="plotly_white",
        height=300,
        xaxis=dict(
            side='top',
            title=None
        ),
        yaxis=dict(
            title=None
        ),
        margin=dict(
            b=0,
            l=0,
            r=0,
            t=0
        ),
        font=dict(
            size=8
        )
    )
    return fig

## control genres plat. heatmap
@callback(
    Output("graph-genres_plat_heat1", "figure"),
    Output("graph-genres_plat_heat2", "figure"),
    Input("timeslot-selector", "value")
)
def draw_genres_bet_plat(timeslot):
    sel = (library[["Year"]]
           .loc[(timeslot[0] <= library['Year'])&
                (library['Year'] <= timeslot[1])]
           .merge(genres, on="ID", how="left")
           .drop(columns="Year"))
    
    df = (sel.merge(platform, on="ID", how="left")
          .groupby(by=["Genres", "Platform"]).count()
          .reset_index("Platform"))
    
    df['Netflix'] = df['ID'].loc[df['Platform'] == "Netflix"]
    df['Hulu'] = df['ID'].loc[df['Platform'] == "Hulu"]
    df['Prime Video'] = df['ID'].loc[df['Platform'] == "Prime Video"]
    df['Disney+'] = df['ID'].loc[df['Platform'] == "Disney+"]
    df = df.drop(columns=["Platform", "ID"]).groupby("Genres").max()

    fig1 = px.imshow(df.head(df.shape[0] // 2).T, text_auto=True)
    fig2 = px.imshow(df.tail(df.shape[0] // 2).T, text_auto=True)

    layout = dict(
        template = "plotly_white",
        height = 150,
        margin = dict(b=0, l=0, r=0, t=0),
        coloraxis = dict(showscale=False),
        font = dict(
            size=8
        ),
        xaxis = dict(
            side='top',
            title=None
        ),
        yaxis = dict(
            title=None
        )
    )

    fig1.update_layout(layout)
    fig2.update_layout(layout)

    return fig1, fig2


## control search result
@callback(
    Output("search_result", "children"),
    Input("search-sort-by", "value"),
    Input("search-sort-ascending", "value"),
    Input("search-filter_genres", "value"),
    Input("search-filter_plat", "value"),
    Input("timeslot-selector", "value")
)
def search_result(sort_by, ascending, filter_genres, filter_plat, timeslot):
    pass

