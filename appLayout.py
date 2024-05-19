from dash import html, dcc
import dash_bootstrap_components as dbc

from appInteraction import library, platform

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


# App layout
construction = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Alert")),
    dbc.ModalBody("Under construction here. Please go back"),
    dbc.ModalFooter(
        dbc.Button(
            "Close", id="construction_close", className="ms-auto", n_clicks=0
        )
    ),
    ],
    id="construction",
    is_open=False
)

copyright_instruction = dbc.Row(
    dbc.Col([
        html.Span("This project is powered by "),
        html.A("Python", 
               href="https://python.org/"),
        html.Span(", "),
        html.A("Plotly", 
               href="https://plotly.com/python/"),
        html.Span(", "),
        html.A("Dash", 
               href="https://dash.plotly.com/"),
        html.Span(", "),
        html.A("Dash Bootstrap Components", 
               href="https://dash-bootstrap-components.opensource.faculty.ai/")
        ],
        class_name="fw-light",
        style={"font-size": ".7rem"}
    )
)

database_info = dbc.Row([
    dbc.Col([
        html.Span("Current database: "),
        html.Span(
            "MoviesOfStream.csv",
            id="tooltip-current_file",
            style={"textDecoration": "underline", 
                   "cursor": "pointer"}
            )
        ],
        class_name="col-8"
    ),

    dbc.Col([
        dbc.ButtonGroup([
            dbc.Button("Save", id="database_save"),
            dbc.Button("Refresh", id="database_refresh"),
            dbc.Button("Upload", id="database_upload")
            ],
            size="sm",
            class_name="ms-3"
            )
        ],
        class_name="col-4"
    )
    ],
    class_name="align-items-center justify-content-between"
)

language_change = dbc.DropdownMenu(
    label="Language", 
    children=[
        dbc.DropdownMenuItem("en-GB", active=True),
        dbc.DropdownMenuItem("en-US", disabled=True),
        dbc.DropdownMenuItem("zh-CN", disabled=True),
        dbc.DropdownMenuItem("ja-JP", disabled=True)
    ], 
    direction="end"
)

settings_bar = dbc.Row([
    dbc.Col([
        dbc.DropdownMenu(
            label="Settings",
            children=[
                language_change,
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Version"),
                dbc.DropdownMenuItem("About")
                ]
            )
        ],
        class_name="col-6 d-flex justify-content-center"
    ),

    dbc.Col(dbc.Row(
        dbc.Col([
            dbc.Label(className="fa fa-moon mb-0 text-dark", html_for="switch"),
            dbc.Switch(
                id="color_mode-switch", 
                value=True, 
                persistence=True,
                className="d-inline-block ms-1"
                ),
            dbc.Label(className="fa fa-sun mb-0 text-primary", html_for="switch")
            ], 
            class_name="d-flex justify-content-center"
        ),
        class_name="align-items-center"
        ),
        class_name="col-6"
    )
])

head_bar = dbc.Row([
    ## title
    dbc.Col([
        html.A(
            "Superb Movie Library", 
            href="",
            className="fw-bold h3 dbc")
        ],
        class_name="col-3 border-end border-2"
    ),

    ## mid_bar
    dbc.Col([
        copyright_instruction,
        database_info
        ], 
        class_name="col-6"
    ),

    ## set_bar
    dbc.Col([
        settings_bar
        ],
        class_name="col-3 border-start border-2"
    ),

    ## alert
    construction

    ],
    class_name="align-items-center pt-4"
)

plat_stat = dict(zip(
    plat := ['Netflix', 'Hulu', 'Prime Video', 'Disney+'],
    [
        dbc.Col([
            dbc.Row(dbc.Col(
                f"{(platform['Platform'] == pl).sum()}",
                id=f"pivot-{pl}", 
                class_name="fw-bold lead")),
            dbc.Row(dbc.Col(pl, class_name="fw-bold lead"))
        ]) 
        for pl in plat
    ]
))

total_plat = dbc.Row([
    dbc.Col(
        "Total",
        class_name="col-6 lead fw-bold fs-2 text-primary"
    ),

    dbc.Col(
        f"{library['Title'].count()}",
        id="pivot-total",
        class_name="col-6 lead fw-bold fs-2 text-danger"
    )
    ],
    class_name="py-3"
)

graph_genres_plat_filter = dbc.Row(
    dbc.Col(
        dcc.Dropdown(
            options={
                'Netflix': 'Netflix',
                'Hulu': 'Hulu',
                'Prime Video': 'Prime Video',
                'Disney+': 'Disney+'
            },
            id="genres-plat_filter",
            multi=True,
            searchable=False,
            placeholder="Select platform",
            className="dbc"
        ),
        style={"font-size": ".8rem"}
    ),
    class_name="mb-2"
)

graph_genres_sort_ratings = dbc.Row([
    dbc.Col(
        dbc.Switch(id="genres-sort_ratings",
                   value=False,
                   label="Sort: Ratings", 
                   style={"font-size": ".8rem"}), 
        class_name="col-12 d-flex justify-content-end")
    ],
    class_name="align-items-center mt-1"
)

mid_bar = dbc.Row([
    ## pivot information
    dbc.Col([
        total_plat,
        html.Hr(),
        dbc.Row([plat_stat['Netflix'], plat_stat['Hulu']], class_name="py-3"),
        dbc.Row([plat_stat['Prime Video'], plat_stat['Disney+']]),
        html.Hr(),
        dbc.Row(dbc.Col("Time range: ", class_name="text-start"), class_name="p-3"),
        dcc.RangeSlider(1900, 2020, step=5, 
                        marks={
                            1900: "1900",
                            1920: "1920",
                            1940: "1940",
                            1960: "1960",
                            1980: "1980",
                            2000: "2000",
                            2020: "2020"
                        }, 
                        id="timeslot-selector",
                        value=[1980, 2010], 
                        tooltip={"placement": "bottom"},
                        className="dbc mt-2")
        ],
        class_name="col-3 text-center"
    ),

    ## selected table
    dbc.Col([
        dbc.Row(dbc.Col(
            dbc.Label("Top Rated:", html_for="", class_name="fw-bold fs-4"))),
        dbc.Table(id="table-top_rated"),
        dbc.Row(dbc.Col(
            dbc.Label("Recent Released: ", html_for="", class_name="fw-bold fs-4"))),
        dbc.Table(id="table-recent")
        ],
        class_name="col-6 border-start border-end border-2"
    ),

    dbc.Col([
        dbc.Row(dbc.Col(
            dbc.Label("Top Genres", html_for="", class_name="fw-bold fs-4"))),
        graph_genres_plat_filter,
        graph_genres_sort_ratings,
        dbc.Row(dbc.Col(
            dcc.Graph(id="graph-top_genres_bar",className="border")))

        ],
        class_name="col-3"
    )

    ],
    class_name="align-items-start"
)

search_bar = dbc.Row([
    dbc.Col([
        dbc.InputGroup([
            dbc.InputGroupText("Sort"),
            dbc.Select(
                options={
                    "Title": "Title",
                    "Year": "Year",
                    "IMDb": "IMDb"
                },
                id="search-sort-by",
                value="Title",
                placeholder="Sort by..",
                class_name="pe-1"
            ),
            dbc.InputGroupText(
                dbc.Switch(id="search-sort-ascending", value=True,
                            class_name="fa-solid fa-arrow-down-wide-short mb-0"),
                class_name="d-flex align-items-center justify-content-center")
            ], size="md", style={"font-size": ".8rem"})
        ],
        class_name="col-3"
    ),

    dbc.Col([
        dbc.InputGroup([
            dbc.Input(id="search_movies", placeholder="Enter movie names", size="md"),
            dbc.Button([
                html.I(
                    className="bi bi-search"),
                    html.Span(" Search")
                ], id="search_button", size="sm"
                )
            ])
        ],
        class_name="col-5"
    ),

    dbc.Col(
        dcc.Dropdown(
            options={},
            id="search-filter_genres",
            multi=True,
            placeholder="Filter Genres",
            className="dbc"
        ),
        class_name="col-2"
    ),

    dbc.Col(
        dcc.Dropdown(
            options={},
            id="search-filter_plat",
            multi=True,
            placeholder="Filter Plat.",
            className="dbc"
        ),
        class_name="col-2"
    )
    ],
    class_name="pt-1 pb-4"
)

bottom_bar = dbc.Row([
    dbc.Col([
        dbc.Row(dbc.Col(
            dbc.Label("Genres between Plat.", class_name="fw-bold fs-4"))),

        dbc.Row([
            dbc.Col(
                dbc.Switch(id="plat-agg_ratings", 
                           value=False,
                           label="Ratings", 
                           style={"font-size": ".8rem"}), 
                class_name="col-12 d-flex justify-content-end")
            ],
            class_name="align-items-center"
        ),

        dbc.Row(dbc.Col(
            dcc.Graph(id="graph-genres_plat_heat1"))),

        dbc.Row(dbc.Col(
            dcc.Graph(id="graph-genres_plat_heat2")))

        ],
        class_name="col-3"
    ),

    dbc.Col([
        dbc.Row(dbc.Col(
            dbc.Label("Search movies", html_for="", class_name="fw-bold fs-4"))),

        search_bar,

        dbc.Row(dbc.Col([
            dbc.Table(id="search_result")
            ])),

        dbc.Row(dbc.Col([
            html.P("Showing 10 instances in one page.", className="fw-lighter fs-6"),
            dbc.Pagination(id="search-page", 
                           max_value=10,
                           first_last=True, previous_next=True,
                           fully_expanded=False,
                           size="sm")
            ]),
            class_name="align-items-center justify-content-start py-2"
            )
        
        ],
        class_name="col-9 border-start border-2",
        style={"min-height": 400}
    ),

    ],
    class_name="align-items-start pb-4"
)

Layout = dbc.Container([
    head_bar,

    html.Hr(),

    mid_bar,

    html.Hr(),

    bottom_bar,

    html.Hr()

    ],
    class_name=""
)
