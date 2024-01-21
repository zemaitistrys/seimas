import plotly.graph_objs as go
from plotly.subplots import make_subplots
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
    ClientsideFunction,
)
import dash_bootstrap_components as dbc
import json
from enum import Enum
from constants import question_contents, mp_to_fraction_map, party_color_codes

app_name = "RenkuProtingai.lt"
app = Dash(app_name, external_stylesheets=[dbc.themes.LUX])
app.title = app_name
server = app.server

# question_contents = question_contents[:3]


class AnswerOptions(Enum):
    FOR = "for"
    AGAINST = "against"
    DONTCARE = "dontcare"


html.Div([html.Link(rel="icon", href="/assets/favicon.ico")])


question_elements = [
    dbc.Row(
        dbc.Col(
            html.Div(
                [
                    html.H6(
                        f"{question_id+1}. {question['motion_title_for_questionaire']}",
                        className="mt-3",
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                "Už",
                                id={
                                    "type": "answer-button",
                                    "index": question_id,
                                    "value": AnswerOptions.FOR.value,
                                },
                                color="success",
                                outline=True,
                                className="mb-2",
                            ),
                            dbc.Button(
                                "Prieš",
                                id={
                                    "type": "answer-button",
                                    "index": question_id,
                                    "value": AnswerOptions.AGAINST.value,
                                },
                                color="danger",
                                outline=True,
                                className="mb-2",
                            ),
                            dbc.Button(
                                "Man nesvarbu",
                                id={
                                    "type": "answer-button",
                                    "index": question_id,
                                    "value": AnswerOptions.DONTCARE.value,
                                },
                                color="info",
                                outline=True,
                                className="mb-4",
                            ),
                        ],
                        className="d-grid gap-2 col-6 mx-auto",
                    ),
                ],
                id=f"question_id_{question_id}",
            ),
            md=12,
            xl=6,
        ),
        justify="center",
        className="g-2",
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
                width=8,
            ),
            justify="center",
        ),
        # Hidden div to trigger clientside callback
        html.Div(id="clientside-script-trigger", style={"display": "none"}),
        # Footer
        html.Footer(
            html.Div(
                [
                    html.A(
                        [
                            html.I(className="fab fa-linkedin footer-icon"),
                            "Simonas",
                        ],
                        href="https://www.linkedin.com/in/simonas-mulevicius/",
                        target="_blank",
                    ),
                    html.A(
                        [
                            html.I(className="fab fa-linkedin footer-icon"),
                            "Mykolas",
                        ],
                        href="https://de.linkedin.com/in/mykolas-sveistrys",
                        target="_blank",
                    ),
                    html.A(
                        [
                            html.I(className="fab fa-github footer-icon"),
                            "GitHub Repository",
                        ],
                        href="https://github.com/zemaitistrys/seimas",
                        target="_blank",
                    ),
                    html.A(
                        [
                            html.I(className="fas fa-database footer-icon"),
                            "Duomenys",
                        ],
                        href="http://www.lrs.lt",
                        target="_blank",
                    ),
                ],
                className="footer",
            )
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


def calculate_similarity_scores(question_contents):
    mp_names = mp_to_fraction_map.keys()
    mp_results = {
        mp_name: {
            "mp_name": mp_name,
            "party": party,
            "identical_votes": 0,
        }
        for mp_name, party in mp_to_fraction_map.items()
    }

    voter_relevant_questions = [
        question
        for question in question_contents
        if question["user_selected_answer"] != AnswerOptions.DONTCARE.value
    ]

    for question in voter_relevant_questions:
        mp_votes_for_this_question = question["votes"]
        user_selected_answer = question["user_selected_answer"]

        for mp_vote_for_one_question in mp_votes_for_this_question:
            mp_name = mp_vote_for_one_question["mp_name"]

            if user_selected_answer == mp_vote_for_one_question["vote"]:
                mp_results[mp_name]["identical_votes"] += 1

    number_of_relevant_questions = len(voter_relevant_questions)
    mp_results_list = mp_results.values()
    for mp_result in mp_results_list:
        mp_result["similarity_percent"] = 100 * (
            (mp_result["identical_votes"] / number_of_relevant_questions)
            if number_of_relevant_questions != 0
            else 0.0
        )
        mp_result["color"] = party_color_codes[mp_result["party"]]
        mp_result[
            "mp_name"
        ] = f"{mp_result['mp_name']} ({mp_result['party']}, {int(mp_result['similarity_percent'])}%)"

    mp_results_list = sorted(
        mp_results_list, key=lambda mp: mp["similarity_percent"], reverse=True
    )
    return mp_results_list


def calculate_average_similarity_score_per_fraction(mps):
    # mps
    # group by 'party'
    # take average score of 'similarity_percent'
    # TODO
    return


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

    mps = calculate_similarity_scores(question_contents)
    average_similarity_score_per_fraction = (
        calculate_average_similarity_score_per_fraction(mps)
    )

    # FUTURE TODO - deleteme?
    # return [
    #     html.Div(
    #         mp["mp_name"],
    #         style={
    #             "background-color": mp["color"],
    #             "border-radius": "15px",
    #             "width": f'{max(mp["similarity_percent"], 10)}%',  # Ensure a minimum width of 10%
    #             "min-width": "100px",  # Or any other suitable minimum width
    #             "max-width": "1000px",  # Or any other suitable minimum width
    #             "padding": "10px",
    #             "margin-bottom": "10px",
    #             "text-align": "center",
    #         },
    #     )
    #     for mp in mps
    # ]

    countries = [
        "Switzerland",
        "Sweden",
        "Belgium",
        "United States",
        "Netherlands",
        "Canada",
        "United Kingdom",
        "Japan",
    ]
    savings = [
        17.52,
        15.21,
        7.51,
        7.48,
        6.51,
        4.98,
        2.26,
        1.36,
    ]  # This should be the household savings rates
    net_worth = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]  # Replace None with actual net worth data if available

    # Create a figure with subplots
    fig = make_subplots(rows=1, cols=1)

    # Add savings data
    fig.add_trace(go.Bar(x=countries, y=savings, name="Household savings"))

    # Here you would add the net worth data as another bar trace, if you have that data
    # fig.add_trace(go.Bar(x=countries, y=net_worth, name='Household net worth'))

    # Update the layout
    fig.update_layout(
        title="Panašumas tarp manęs ir kiekvienos šios kadencijos frakcijos (0-100%)",
        xaxis_title="Frakcija",
        yaxis_title="Panašumas (0-100%)",
        barmode="group",
    )

    return [
        html.Div(
            [html.H1("Mano įsitikinimams panašiausia frakcija"), dcc.Graph(figure=fig)]
        ),
        html.Script(
            """
            setTimeout(function() {
                window.scrollTo(0, document.body.scrollHeight);
            }, 1000);
        """
        ),
    ]


# Clientside callback to scroll to the bottom
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="scrollToBottom"),
    Output("clientside-script-trigger", "children"),
    [Input("submit-button", "n_clicks")],
)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
