import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask
from app import app
from apps import viewer, login

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):

    allcookies = dict(flask.request.cookies)

    if 'username' in allcookies:
        return viewer.layout
    else:
        return login.layout
    
if __name__ == '__main__':
    app.run_server(
        port=65535,
        host='0.0.0.0'
)