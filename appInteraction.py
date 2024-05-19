from dash import Dash, html, dcc, State, callback, Output, Input, clientside_callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Incorporate data
path = "./data"

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
    Input("genres-sort_ratings", "value"),
    Input("genres-plat_filter", "value")
)
def draw_top_genres(timeslot, sort_ratings, filter_plat):
    if filter_plat is None or filter_plat == []:
        sel = (library[["Year", "IMDb"]].loc[(timeslot[0] <= library['Year'])&
                                     (library['Year'] <= timeslot[1])]
                                .merge(genres, on="ID", how="left")
                                .drop(columns="Year"))
    else:
        sel = (library[["Year", "IMDb"]]
            .loc[(timeslot[0] <= library['Year'])&
                    (library['Year'] <= timeslot[1])&
                    (platform["Platform"].isin(filter_plat))]
            .merge(genres, on="ID", how="left")
            .drop(columns="Year"))
    
    sel = sel.groupby("Genres").agg(
            {"ID": "count", "IMDb": "mean"}
        ).sort_values(
            "IMDb" if sort_ratings else "ID"
         ).tail(10).reset_index().rename(columns={"ID": "Num"})

    fig = px.bar(
        sel,
        x="Num", y="Genres", 
        orientation="h",
        hover_data=['Num', "IMDb"])
    
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
    Input("timeslot-selector", "value"),
    Input("plat-agg_ratings", "value")
)
def draw_genres_bet_plat(timeslot, agg_ratings):
    sel = (library[["Year", "IMDb"]]
           .loc[(timeslot[0] <= library['Year'])&
                (library['Year'] <= timeslot[1])]
           .merge(genres, on="ID", how="left")
           .drop(columns="Year"))
    
    df = (sel.merge(platform, on="ID", how="left")
          .groupby(by=["Genres", "Platform"]).agg({"ID": "count", "IMDb": "mean"})
          .reset_index("Platform"))
    
    target = "IMDb" if agg_ratings else "ID"

    df['Netflix'] = df[target].loc[df['Platform'] == "Netflix"].round(2)
    df['Hulu'] = df[target].loc[df['Platform'] == "Hulu"].round(2)
    df['Prime Video'] = df[target].loc[df['Platform'] == "Prime Video"].round(2)
    df['Disney+'] = df[target].loc[df['Platform'] == "Disney+"].round(2)
    df = df.drop(columns=["Platform", "ID", "IMDb"]).groupby("Genres").max()

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

## load genres and platform
@callback(
    Output("search-filter_genres", "options"),
    Output("search-filter_plat", "options"),
    Input("timeslot-selector", "value")
)
def load_genres_and_palt(timeslot):
    sel = (library[["Year"]].loc[(timeslot[0] <= library['Year'])&
                                 (library['Year'] <= timeslot[1])])
    gr = sel.merge(genres, on="ID", how="left")["Genres"].drop_duplicates().dropna().sort_values().values

    pl = sel.merge(platform, on="ID", how="left")["Platform"].drop_duplicates().dropna().sort_values().values

    genre = {key: key for key in gr}
    plat = {key: key for key in pl}

    return genre, plat

@callback(
    Output("search-page", "max_value"),
    Input("pivot-total", "children")
)
def prepare_pagination(total_str):
    ttl = int(total_str)
    return ttl // 10 + 1

## control search result
@callback(
    Output("search_result", "children"),
    Input("search-sort-by", "value"),
    Input("search-sort-ascending", "value"),
    Input("search-filter_genres", "value"),
    Input("search-filter_plat", "value"),
    Input("timeslot-selector", "value")
)
def search_result(sort_by, ascend, filter_genres, filter_plat, timeslot):
    sel = (library[["Title", "Year", "Directors", 
                    "IMDb", "Genres", "Platform"]]
                    .loc[(timeslot[0] <= library['Year'])&
                         (library['Year'] <= timeslot[1])]
                    .sort_values(by=sort_by, ascending=(not ascend))).fillna('')
    
    if filter_genres is not None and filter_genres != []:
        sel = sel.loc[sel["Genres"].apply(lambda s: sum([gr in s for gr in filter_genres]) > 0)]

    if filter_plat is not None and filter_plat != []:
        sel = sel.loc[sel["Platform"].apply(lambda s: sum([pl in s for pl in filter_plat]) > 0)]

    return dbc.Table.from_dataframe(sel.head(10), size="sm", striped=True, bordered=True, hover=True)



