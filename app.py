import dash
from dash.html.Title import Title

app = dash.Dash(__name__, suppress_callback_exceptions=True, title="ADV")
server = app.server