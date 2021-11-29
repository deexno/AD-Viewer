import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import *
import configparser
import codecs
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE
from ldap3.core.exceptions import LDAPCursorError
import dash
from app import app
import flask

# Initialising all necessary variables from the config.ini file
config = configparser.ConfigParser()
config.readfp(codecs.open("config.ini", "r", "utf8"))

ad_server = config['AD_INFO']['server']
ad_domain = config['AD_INFO']['domain']

layout = html.Div(
    [
        html.H3('LOGIN - ADV'),
        dcc.Input(id="username_input", type="text", placeholder="USERNAME"),
        html.Br(),
        dcc.Input(id="password_input", type="password", placeholder="PASSWORD"),
        html.Br(),
        html.Button('LOGIN', id='login_button', n_clicks=0),
        html.Div(id='login')
    ],
    className="login"
)

@app.callback(
    Output('login', 'children'),
    Input('login_button', 'n_clicks'),
    State('username_input', 'value'),
    State('password_input', 'value'))
def display_value(button, username, password):
    
    allcookies=dict(flask.request.cookies)

    if (username == None or password == None and 'username' not in allcookies):
        return html.H6('LOG IN WITH YOUR ACTIVE DIRECTORY USER!')
    else:
        try:
            server = Server(ad_server, get_info=ALL)
            conn = Connection(server, user="{}\\{}".format(ad_domain, username), password=password, authentication=NTLM, auto_bind=True)
            dash.callback_context.response.set_cookie('username', username)
            return dcc.Link(html.Button('GROUP VIEWER'), href="/group_viewer")
        except:
            return html.H6('LOGIN FAILED!')