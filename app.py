from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)

# html.Div(children="Kuris Seimo narys mane atstovauja geriausiai?"),
app.layout = html.Div(
    [
        html.Div(
            className="row",
            children="Kuris Seimo narys mane atstovauja geriausiai?",
            # style={"textAlign": "center", "color": "blue", "fontSize": 30},
        ),
        html.Div(
            className="row",
            children=[
                dcc.RadioItems(
                    options=["pop", "lifeExp", "gdpPercap"],
                    value="lifeExp",
                    inline=True,
                    id="my-radio-buttons-final",
                )
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        dash_table.DataTable(
                            data=df.to_dict("records"),
                            page_size=11,
                            style_table={"overflowX": "auto"},
                        )
                    ],
                ),
                html.Div(
                    className="six columns",
                    children=[dcc.Graph(figure={}, id="histo-chart-final")],
                ),
            ],
        ),
    ]
)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
