#!/usr/bin/python3
""" graph.py - show info like an graph
    v0.0.1 - 2021-11-03 - nelbren@nelbren.com"""
from pathlib import Path
import datetime
import sqlite3
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd

HOME = str(Path.home())
BASE = HOME + "/.miner_preview.db"
TS_FMT = "%Y-%m-%d %H:%M:%S"

conn = sqlite3.connect(BASE, check_same_thread=False)
c = conn.cursor()
DATAFRAME = None
EACH_HOURS = 4

def get_new_data():
    """Updates the global variable 'DATAFRAME' with new data"""
    #print(datetime.datetime.now(), "get_new_data - begin")
    dataframe = pd.read_sql("SELECT * FROM unpaid", conn)
    dataframe = dataframe[["source", "currency", "timestamp", "usd", "value"]]
    dataframe.head(1)
    #print(datetime.datetime.now(), "get_new_data - end")
    return dataframe


def get_timestamp():
    """Get timestamp"""
    timestamp = f"{datetime.datetime.now()}"
    timestamp_obj = datetime.datetime.strptime(timestamp, TS_FMT + ".%f")
    timestamp = timestamp_obj.strftime(TS_FMT)
    return "🕑" + timestamp


def make_layout():
    """Make Layout"""
    title_style = {
        "text-align": "center",
        "font-weight": "700",
        "line-height": "32px",
        "font-size": "32px",
    }
    timestamp_style = {
        "font-family": "'Console', sans-serif",
        "line-height": "32px",
        "font-size": "30px",
        "font-weight": "bold",
        "text-align": "center",
    }
    tabs_styles = {"height": "44px", "align-items": "center"}
    tab_style = {
        "borderBottom": "1px solid #d6d6d6",
        "fontWeight": "bold",
        "font-size": "24px",
        "border-radius": "15px",
        "background-color": "#F2F2F2",
        "padding": "2px",
    }
    tab_selected_style = {
        "borderTop": "1px solid #d6d6d6",
        "borderBottom": "1px solid #d6d6d6",
        "backgroundColor": "#119DFF",
        "fontWeight": "bold",
        "font-size": "24px",
        "color": "white",
        "padding": "2px",
        "border-radius": "15px",
    }

    return html.Div(
        [
            html.H1("⛏️ Miner Preview 👀", style=title_style),
            html.Div(
                [
                    html.H5(
                        get_timestamp(),
                        style=timestamp_style,
                        id="live-update-text",
                    ),
                    dcc.Interval(
                        id="interval-component",
                        interval=EACH_HOURS * 60 * 60 * 1000,
                        n_intervals=0,
                    ),
                ]
            ),  # , style=dict(display='flex') ),
            dcc.Tabs(
                id="tabs",
                value="tab-2",
                children=[
                    dcc.Tab(
                        label="Table",
                        value="tab-1",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                    dcc.Tab(
                        label="Graph",
                        value="tab-2",
                        style=tab_style,
                        selected_style=tab_selected_style,
                    ),
                ],
                style=tabs_styles,
            ),
            html.Div(id="tabs-content", style={"height": "83vh"}),
        ],
        style={"height": "100vh", "padding": "5px"},
    )


app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP]
)  # , server=server)
server = app.server
app.config.suppress_callback_exceptions = True

# get_new_data()

app.layout = make_layout


def tabla(dataframe):
    """tabla"""
    return html.Div(
        dash_table.DataTable(
            id="table-sorting-filtering",
            columns=[
                {"name": i, "id": i, "deletable": True}
                for i in dataframe.columns
            ],
            style_table={"overflowX": "scroll"},
            style_cell={
                "height": "90",
                # all three widths are needed
                "minWidth": "140px",
                "width": "140px",
                "maxWidth": "140px",
                "whiteSpace": "normal",
            },
            page_current=0,
            page_size=23,
            page_action="custom",
            filter_action="custom",
            filter_query="",
            sort_action="custom",
            sort_mode="multi",
            sort_by=[],
        )
    )


def graph_all(dataframe):
    """graph_all"""
    opts_styles = [
        dict(
            target="cloudatcost_btc",
            value=dict(marker=dict(color="darkgoldenrod")),
        ),
        dict(target="ethermine_eth", value=dict(marker=dict(color="darkcyan"))),
        dict(
            target="cloudatcost_usd", value=dict(marker=dict(color="goldenrod"))
        ),
        dict(target="ethermine_usd", value=dict(marker=dict(color="cyan"))),
    ]

    return html.Div(
        [
            dcc.Graph(
                id="graph_all",
                style={"height": "80vh"},
                config={"displayModeBar": "hover", "displaylogo": False},
                figure={
                    "data": [
                        dict(
                            y=dataframe["usd"],
                            x=dataframe["timestamp"],
                            mode="lines+markers",
                            # opacity = 0.7,
                            marker={
                                "size": 8,
                                "line": {"width": 0.5, "color": "white"},
                            },
                            name="USD",
                            # stackgroup='one',
                            transforms=[
                                dict(
                                    type="groupby",
                                    groups=dataframe["source"] + "_usd",
                                    styles=opts_styles,
                                ),
                            ],
                        ),
                        dict(
                            y=dataframe["value"],
                            x=dataframe["timestamp"],
                            mode="lines+markers",
                            # opacity = 0.7,
                            marker={
                                "size": 8,
                                "line": {"width": 0.5, "color": "white"},
                            },
                            name="VALUE",
                            # stackgroup='one',
                            transforms=[
                                dict(
                                    type="groupby",
                                    groups=dataframe["source"]
                                    + "_"
                                    + dataframe["currency"],
                                    styles=opts_styles,
                                ),
                            ],
                        ),
                    ],
                    "layout": dict(
                        xaxis={"title": "Timestamp"},
                        yaxis={"type": "log", "title": "USD"},
                        margin={"l": 40, "b": 40, "t": 10, "r": 10},
                        legend={"x": 0.99, "y": 0.01},
                        # legend={"yanchor": "bottom", "xanchor": "left"},
                        hovermode="closest",
                    ),
                },
            )
        ]
    )


@app.callback(
    Output("live-update-text", "children"),
    [Input("interval-component", "n_intervals")],
)
# pylint: disable=unused-argument
def update_text(n_intervals):
    """Update Text"""
    return get_timestamp()


@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value")],
    [Input("interval-component", "n_intervals")],
)
# pylint: disable=unused-argument
def render_content(tab, n_intervals):
    """Render Content"""
    dataframe = get_new_data()
    if tab == "tab-1":
        return tabla(dataframe)
    return graph_all(dataframe)


operators = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


def split_filter_part(filter_part):
    """Split Filter Part"""
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]
                value_part = value_part.strip()
                value_part0 = value_part[0]
                if value_part0 == value_part[-1] and value_part0 in (
                    "'",
                    '"',
                    "`",
                ):
                    value = value_part[1:-1].replace(
                        "\\" + value_part0, value_part0
                    )
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value
    return [None] * 3


@app.callback(
    Output("table-sorting-filtering", "data"),
    [
        Input("table-sorting-filtering", "page_current"),
        Input("table-sorting-filtering", "page_size"),
        Input("table-sorting-filtering", "sort_by"),
        Input("table-sorting-filtering", "filter_query"),
    ],
)
def update_table(page_current, page_size, sort_by, filter_query):
    """Update Table"""
    dataframe = get_new_data()
    filtering_expressions = filter_query.split(" && ")
    # dataframe = DATAFRAME
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dataframe = dataframe.loc[
                getattr(dataframe[col_name], operator)(filter_value)
            ]
        elif operator == "contains":
            dataframe = dataframe.loc[
                dataframe[col_name].str.contains(filter_value)
            ]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dataframe = dataframe.loc[
                dataframe[col_name].str.startswith(filter_value)
            ]
        if len(sort_by):
            dataframe = dataframe.sort_values(
                [col["column_id"] for col in sort_by],
                ascending=[col["direction"] == "asc" for col in sort_by],
                inplace=False,
            )
    page = page_current
    size = page_size
    dataframe = dataframe.sort_values(by="timestamp", ascending=False)
    return dataframe.iloc[page * size : (page + 1) * size].to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
