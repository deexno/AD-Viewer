import configparser
import pymysql
import codecs

config = configparser.ConfigParser()
config.readfp(codecs.open("config.ini", "r", "utf8"))

db_server = config['DB_INFO']['server']
db_name = config['DB_INFO']['dbname']
db_user = config['DB_INFO']['user']
db_password = config['DB_INFO']['password']

conn = pymysql.connect (
    host=db_server,
    database=db_name,
    user=db_user,
    password=db_password,
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

def item_ini(node_selection, display_type):

    nodes = []
    nodes_by_id = []
    edges = []

    if (node_selection == None):
        if (display_type == "group_viewer"):
            cursor.execute("SELECT * FROM NODES WHERE active=1 ORDER BY child_amount DESC;")
        else:
            cursor.execute("SELECT * FROM NODES WHERE active=1 AND type=3 ORDER BY child_amount DESC;")
        
        nodes_ls = cursor.fetchall()

        for node in nodes_ls:
            
            node_id = str(node["id"])

            nodes.append(
                {
                    'data': 
                    {
                        'id': node_id, 
                        'name': node["name"], 
                        'size': node["child_amount"], 
                        'color': node["color"],
                        'admin count': node["admin_count"],
                        'country': node["country"],
                        'country code': node["country_code"],
                        'department': node["department"],
                        'last logoff': node["last_logoff"],
                        'last logon': node["last_logon"],
                        'postal code': node["postal_code"],
                        'telephone Nr.': node["telephone_nr"],
                        'bad password time': node["bad_password_time"],
                        'manager': node["manager"],
                        'account name': node["account_name"],
                        'last change': node["last_change"],
                        'created': node["created"]
                    }
                }
            )
        
            nodes_by_id.append(node_id)

        cursor.execute("SELECT * from EDGES;")
        edges_ls = cursor.fetchall()

        for edge in edges_ls:
            
            edge_source = str(edge["source"])
            edge_target = str(edge["target"])

            if (edge_source in nodes_by_id and edge_target in nodes_by_id):
                
                cursor.execute("SELECT color from NODES WHERE id={};".format(edge_source))
                color = cursor.fetchone()
                color = color["color"]

                edges.append(
                    {
                        'data': 
                        {
                            'source': edge_source, 
                            'target': edge_target,
                            'color': color
                        }, 
                        'classes': edge_source
                    }
                )  

    else:
        cursor.execute("SELECT * FROM NODES WHERE id=%s;", (node_selection))
        main_node = cursor.fetchone()
        
        node_id = main_node["id"]

        parent_nodes, parent_edges = family_lookup(node_id, True, [], [], [])
        child_nodes, child_edges = family_lookup(node_id, False, [], [], [])

        nodes = parent_nodes + child_nodes
        edges = parent_edges + child_edges

    return nodes, edges

def family_lookup(node_id, dir, parent_nodes, parent_edges, nodes_by_id):
    
    if dir:
        cursor.execute("SELECT * FROM EDGES WHERE target=%s;", (node_id))
    else:
        cursor.execute("SELECT * FROM EDGES WHERE source=%s;", (node_id))
    
    edges_ls = cursor.fetchall()

    for edge in edges_ls:

        cursor.execute("SELECT * FROM NODES WHERE id=%s;", (edge['source']))
        source_node = cursor.fetchone()
        cursor.execute("SELECT * FROM NODES WHERE id=%s;", (edge['target']))
        target_node = cursor.fetchone()

        source_node_id = str(source_node["id"])
        source_node_color = source_node["color"]
        target_node_id = str(target_node["id"])

        if (source_node_id not in nodes_by_id):
            parent_nodes.append(
                {
                    'data': 
                    {
                        'id': source_node_id, 
                        'name': source_node["name"], 
                        'size': source_node["child_amount"], 
                        'color': source_node["color"],
                        'admin count': source_node["admin_count"],
                        'country': source_node["country"],
                        'country code': source_node["country_code"],
                        'department': source_node["department"],
                        'last logoff': source_node["last_logoff"],
                        'last logon': source_node["last_logon"],
                        'postal code': source_node["postal_code"],
                        'telephone Nr.': source_node["telephone_nr"],
                        'bad password time': source_node["bad_password_time"],
                        'manager': source_node["manager"],
                        'account name': source_node["account_name"],
                        'last change': source_node["last_change"],
                        'created': source_node["created"]
                    }
                }
            )

        if (target_node_id not in nodes_by_id):
            parent_nodes.append(
                {
                    'data': 
                    {
                        'id': target_node_id, 
                        'name': target_node["name"], 
                        'size': target_node["child_amount"], 
                        'color': target_node["color"],
                        'admin count': target_node["admin_count"],
                        'country': target_node["country"],
                        'country code': target_node["country_code"],
                        'department': target_node["department"],
                        'last logoff': target_node["last_logoff"],
                        'last logon': target_node["last_logon"],
                        'postal code': target_node["postal_code"],
                        'telephone Nr.': target_node["telephone_nr"],
                        'bad password time': target_node["bad_password_time"],
                        'manager': target_node["manager"],
                        'account name': target_node["account_name"],
                        'last change': target_node["last_change"],
                        'created': target_node["created"]
                    }
                }
            )

        parent_edges.append(
            {
                'data': 
                {
                    'source': source_node_id, 
                    'target': target_node_id,
                    'color': source_node_color
                }
            }
        )

        nodes_by_id.append(source_node_id)
        nodes_by_id.append(target_node_id)

        if dir:
            family_lookup(source_node_id, dir, parent_nodes, parent_edges, nodes_by_id)
        else:
            family_lookup(target_node_id, dir, parent_nodes, parent_edges, nodes_by_id)

    return parent_nodes, parent_edges

def node_lookup(node_name):
    cursor.execute("SELECT * FROM NODES WHERE name LIKE %s;", ("%" + node_name + "%"))
    node = cursor.fetchall()

    return node