from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app_name = "RenkuProtingai.lt"
app = Dash(app_name, external_stylesheets=[dbc.themes.LUX])
app.title = app_name
server = app.server

html.Div([html.Link(rel="icon", href="/assets/favicon.ico")])

question_elements = [
    html.Div(
        [
            html.H6(f"Klausimas {_+1}", className="mt-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Už", color="success", outline=True, className="me-1"
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Prieš", color="danger", outline=True, className="me-1"
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Man nesvarbu", color="info", outline=True, className="me-1"
                        ),
                        width="auto",
                    ),
                ],
                justify="center",
                className="mb-2",
            ),
        ]
    )
    for _ in range(10)
]

app.layout = dbc.Container(
    [
        html.H1(
            "Kas geriausiai atstovauja mano įsitikinimams Seime?",
            className="text-center mb-4",
        ),
        # Generate 10 sections of question and buttons
        question_elements[0],
        question_elements[1],
        question_elements[2],
        question_elements[3],
        question_elements[4],
        question_elements[5],
        question_elements[6],
        question_elements[7],
        question_elements[8],
        question_elements[9],
        # Submit button
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "🥁Paskaičiuoti", color="primary", size="lg", className="mt-4 mb-3"
                ),
                width="auto",
            ),
            justify="center",  # Center the row
        ),
    ],
    fluid=True,
    className="text-center",
    style={"padding-top": "150px"},
)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
