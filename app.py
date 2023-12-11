from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)

app = Dash(__name__)

app.layout = html.Div(
    [
        html.Div(children="Kuris seimo narys mane atstovauja geriausiai?"),
        dash_table.DataTable(data=df.to_dict("records"), page_size=10),
        dcc.Graph(figure=px.histogram(df, x="continent", y="lifeExp", histfunc="avg")),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
