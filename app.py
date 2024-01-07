from dash import (
    Dash,
    html,
    dcc,
    callback,
    callback_context,
    Output,
    Input,
    MATCH,
    State,
    ALL,
)
import dash_bootstrap_components as dbc
import json
from enum import Enum
from constants import question_contents

app_name = "RenkuProtingai.lt"
app = Dash(app_name, external_stylesheets=[dbc.themes.LUX])
app.title = app_name
server = app.server


class AnswerOptions(Enum):
    FOR = "for"
    AGAINST = "against"
    DONTCARE = "dontcare"


html.Div([html.Link(rel="icon", href="/assets/favicon.ico")])


question_elements = [
    html.Div(
        [
            html.H6(
                f"{question_id+1}. {question['motion_title_for_questionaire']}",
                className="mt-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Už",
                            id={
                                "type": "answer-button",
                                "index": question_id,
                                "value": AnswerOptions.FOR.value,
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
                                "value": AnswerOptions.AGAINST.value,
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
                                "value": AnswerOptions.DONTCARE.value,
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
    for question_id, question in enumerate(question_contents)
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
        dbc.Row(
            dbc.Col(
                html.Div(id="output-container"),
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
        Output(
            {"type": "answer-button", "index": MATCH, "value": "for"},
            "outline",
        ),
        Output(
            {
                "type": "answer-button",
                "index": MATCH,
                "value": AnswerOptions.AGAINST.value,
            },
            "outline",
        ),
        Output(
            {
                "type": "answer-button",
                "index": MATCH,
                "value": AnswerOptions.DONTCARE.value,
            },
            "outline",
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
        clicked_button_value != AnswerOptions.FOR.value,
        clicked_button_value != AnswerOptions.AGAINST.value,
        clicked_button_value != AnswerOptions.DONTCARE.value,
    ]


def get_selected_option_per_question(array_of_options_per_question):
    assert len(array_of_options_per_question) == 3

    if array_of_options_per_question[0] == False:
        return AnswerOptions.FOR.value
    if array_of_options_per_question[1] == False:
        return AnswerOptions.AGAINST.value
    if array_of_options_per_question[2] == False:
        return AnswerOptions.DONTCARE.value
    return None


@app.callback(
    Output("output-container", "children"),
    [Input("submit-button", "n_clicks")],
    [State({"type": "answer-button", "index": ALL, "value": ALL}, "outline")],
    prevent_initial_call=True,
)
def update_output(n_clicks, button_outlines):
    if n_clicks is None:
        return "Pasirinkite, kaip būtumėte balsavę jūs ir tada pamatysite rezultatus"

    # Group the button outlines into triplets for each question
    grouped_button_outlines = [
        button_outlines[i : i + 3] for i in range(0, len(button_outlines), 3)
    ]

    for question_id, array_of_options_per_question in enumerate(
        grouped_button_outlines
    ):
        selected_option_per_question = get_selected_option_per_question(
            array_of_options_per_question
        )
        if selected_option_per_question is None:
            return f"Dar nepasirinkote atsakymo į {question_id+1} klausimą"

        question_contents[question_id][
            "user_selected_answer"
        ] = selected_option_per_question

    # TODO - pick most similar MP
    return f"{question_contents}"


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
