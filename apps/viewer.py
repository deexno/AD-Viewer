from dash import *
import dash_html_components as html
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash
from app import app
from apps import viewer_lib
import flask

display_type = "group_viewer"

cyto.load_extra_layouts()

nodes, edges = viewer_lib.item_ini(None, display_type)

stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(name)',
            'width': 'data(size)',
            'height': 'data(size)',
            'position': 'absolute',
            'padding-top': '50px',
            'padding-left': '0px',
            'padding-bottom': '50px',
            'padding-right': '0px', 
            'background-color': 'data(color)',
            'text-valign':'center',
            'text-halign':'center',
            'text-wrap': 'wrap',
            'color':'white'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'mid-target-arrow-color': 'data(color)',
            'mid-target-arrow-shape': 'triangle',
            'arrow-scale': 3,
            'line-color': 'data(color)'
        }
    }
]

layout = html.Div(
    [
        html.Div(
            [
                html.P("ACTIVE DIRECTORY VISUALISER", className='header'),
                html.Div([
                    dcc.Dropdown(
                        id='dropdown_layout_update',
                        value='breadthfirst',
                        clearable=False,
                        options=[
                            {'label': name.capitalize(), 'value': name}
                            for name in ['breadthfirst', 'grid', 'random', 'circle', 'cose', 'klay', 'dagre']
                        ]
                    )],
                    className="layout_menu"
                ),
                html.Div(
                    [
                        html.Div([dcc.Input(id='text_search', type='text', className="text_search", placeholder="TEXT TO SEARCH"),
                        html.Button('SEARCH', id='value_submit', n_clicks=0)], className="search_items"), 
                        html.Div(
                            [
                                html.Button('RESET FILTER', id='filter_reset', n_clicks=0), 
                                dcc.Link(html.Button('USER VIEW', id='change_view', n_clicks=0), href="/user_viewer"), 
                                dcc.Link(html.Button('GROUP VIEW', id='change_view', n_clicks=0), href="/group_viewer")
                            ],
                            className="filter_reset"
                        )
                    ], 
                    className="settings"
                )
            ],
            className="control_panel"
        ),
        html.Div(
            [
                cyto.Cytoscape(
                    id='adgv',
                    elements=edges+nodes,
                    layout={'name': 'breadthfirst'},
                    style={'width': '83%', 'height': '850px', 'float': 'left', 'background-color': '#465473', 'border-radius': '5px'},
                    stylesheet=stylesheet,
                    autoRefreshLayout=True,
                    className="graph"
                 ),
                html.Div(
                     [
                        html.H2("NODE-INFORMATION:"),
                        html.Div(id="node_information")
                    ], 
                    className="node_info"
                )
            ], 
            className="main"
        ),
        dcc.Location(id='path')
    ]
)

@app.callback(
    Output('adgv', 'elements'),
    Input('adgv', 'selectedNodeData'),
    Input('filter_reset', 'n_clicks'),
    Input('value_submit', 'n_clicks'),
    Input('change_view', 'n_clicks'),
    State('text_search', 'value'),
    State('path', 'pathname')
)
def node_update(data_list, reset_button, seach_button, change_view, search_text, path):

    global edges
    global nodes
    global display_type

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if ("filter_reset.n_clicks" == changed_id):
        nodes.clear()
        edges.clear()
        nodes, edges = viewer_lib.item_ini(None, display_type)

    elif ("adgv.selectedNodeData" == changed_id):
        nodes.clear()
        edges.clear()
        nodes, edges = viewer_lib.item_ini(data_list[0]["id"], display_type)

    elif ("value_submit.n_clicks" == changed_id):
        node_list = viewer_lib.node_lookup(search_text)
        nodes.clear()
        edges.clear()

        print(len(node_list))

        for similar_node in node_list:
            nodes_tmp, edges_tmp = viewer_lib.item_ini(similar_node["id"], display_type)
            nodes = nodes + nodes_tmp
            edges = edges + edges_tmp

    elif ("change_view.n_clicks" == changed_id):
        if (path == "/user_viewer"):
            display_type = "user_viewer"
        else:
            display_type = "group_viewer"
        
        nodes.clear()
        edges.clear()

        nodes, edges = viewer_lib.item_ini(None, display_type)

    return nodes + edges

@app.callback(
    Output('adgv', 'layout'),
    Input('dropdown_layout_update', 'value')
)
def update_layout(layout):
    return {
        'name': layout,
        'animate': True
}

@app.callback(
    Output('node_information', 'children'),
    Input('adgv', 'mouseoverNodeData')
)
def displayTapNodeData(data):

    info = []

    if data:
        for key in data:
            info.append(html.H3("{}: {}".format(key, data[key])))
        return info