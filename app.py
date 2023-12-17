from dash import Dash, html, dcc, callback, callback_context, Output, Input, MATCH, ALL
import dash_bootstrap_components as dbc
import json

app_name = "RenkuProtingai.lt"
app = Dash(app_name, external_stylesheets=[dbc.themes.LUX])
app.title = app_name
server = app.server

html.Div([html.Link(rel="icon", href="/assets/favicon.ico")])

question_elements = [
    html.Div(
        [
            html.H6(f"Klausimas {question_id}", className="mt-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Už",
                            id={
                                "type": "answer-button",
                                "index": question_id,
                                "value": "for",
                            },
                            color="success",
                            outline=True,
                            className="me-1",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Prieš",
                            id={
                                "type": "answer-button",
                                "index": question_id,
                                "value": "against",
                            },
                            color="danger",
                            outline=True,
                            className="me-1",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Man nesvarbu",
                            id={
                                "type": "answer-button",
                                "index": question_id,
                                "value": "dontcare",
                            },
                            color="info",
                            outline=True,
                            className="me-1",
                        ),
                        width="auto",
                    ),
                ],
                justify="center",
                className="mb-2",
            ),
        ],
        id=f"question_id_{question_id}",
    )
    for question_id in range(1, 11)
]

app.layout = dbc.Container(
    [
        html.H1(
            "Kas geriausiai atstovauja mano įsitikinimams Seime?",
            className="text-center mb-4",
        ),
        *question_elements,
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "🥁Paskaičiuoti",
                    id="submit-button",
                    color="primary",
                    size="lg",
                    className="mt-4 mb-3",
                ),
                width="auto",
            ),
            justify="center",
        ),
    ],
    fluid=True,
    className="text-center",
    style={"paddingTop": "150px"},
)


@app.callback(
    [
        Output({"type": "answer-button", "index": MATCH, "value": "for"}, "outline"),
        Output(
            {"type": "answer-button", "index": MATCH, "value": "against"}, "outline"
        ),
        Output(
            {"type": "answer-button", "index": MATCH, "value": "dontcare"}, "outline"
        ),
    ],
    [Input({"type": "answer-button", "index": MATCH, "value": ALL}, "n_clicks")],
    prevent_initial_call=True,
)
def update_button_outline(*args):
    if not callback_context.triggered:
        return [True, True, True]  # All buttons start with outline=True

    button_id = json.loads(callback_context.triggered[0]["prop_id"].split(".")[0])
    clicked_button_value = button_id["value"]

    # Determine which buttons to outline
    return [
        clicked_button_value != "for",
        clicked_button_value != "against",
        clicked_button_value != "dontcare",
    ]


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
