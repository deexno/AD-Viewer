from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
from datetime import *
import configparser
import pymysql
import random
import codecs
import re
import os

# Initialising all necessary variables from the config.ini file
config = configparser.ConfigParser()
config.readfp(codecs.open(os.getcwd() + "\config.ini", "r", "utf8"))

ad_server = config['AD_INFO']['server']
ad_domain = config['AD_INFO']['domain']
ad_user = config['AD_INFO']['user']
ad_password = config['AD_INFO']['password']

db_server = config['DB_INFO']['server']
db_name = config['DB_INFO']['dbname']
db_user = config['DB_INFO']['user']
db_password = config['DB_INFO']['password']

# Establishing a connection to the database server on which all important information will be stored later on
conn = pymysql.connect(
    host=db_server,
    database=db_name,
    user=db_user,
    password=db_password,
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

def get_info(connection, column_name):
    try:
        return connection.entries[0][column_name].value
    except: 
        return "NO DATA"

def db_cleaning():
    cursor.execute("DELETE FROM EDGES;")
    cursor.execute("DELETE FROM NODES;")
    conn.commit()

def parent_lookup(parents):

    parent = "NO PARENT"

    if parents:
        parent = re.sub(r'^.*?OU=', '', parents[0])

    return parent

def ad_connect():
    
    try:

        # Try to connect to the Active Directory and get all the information about the groups on it.
        server = Server(ad_server, get_info=ALL)
        conn = Connection(server, user="{}\\{}".format(ad_domain, ad_user), password=ad_password, authentication=NTLM, auto_bind=True)
        conn.search("dc={},dc=local".format(ad_domain), "(objectclass=group)", attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])

        print("CONNECTING TO ACTIVE DIRECTORY SUCCESSFUL! CONNECTED.")

        return conn

    except Exception as e:
        print("CONNECTING TO ACTIVE DIRECTORY FAILED! ERROR: {}".format(e))

def node_lookup(node_name, parent_node_name, type):

    # Check if there is already a node with this ID
    cursor.execute("SELECT id FROM NODES WHERE name='{}' and parent_name='{}';".format(node_name, parent_node_name))
    output = cursor.fetchone()

    id = 0

    # If no node with this ID was found, create a new one.
    if (output == None):

        r = lambda: random.randint(0,255)
        color = ('#%02X%02X%02X' % (r(),r(),r()))

        cursor.execute("INSERT INTO NODES (name, type, active, parent_name, color) VALUES (%s, %s, 1, %s, %s);", (node_name, type, parent_node_name, color))
        conn.commit()
        id = node_lookup(node_name, parent_node_name, type)
    else:
        id = output["id"]

    return id

def edge_lookup(parent_id, child_id, display_type):

    cursor.execute("SELECT * FROM EDGES WHERE source='{}' AND target='{}' AND display_type='{}';".format(parent_id, child_id, display_type))
    data = cursor.fetchone()

    if (data == None):
        cursor.execute("INSERT INTO EDGES (source, target, display_type) VALUES (%s, %s, %s);", (parent_id, child_id, display_type))

    conn.commit()
    return parent_id

def group_node_ini(ad_connection):

    try:

        for group in sorted(ad_connection.entries):

            itemname = "[G] " + str(group.name.value)
            parents = [x for x in str(group.distinguishedName.value).split(",") if x.startswith("OU=")]
            parent = parent_lookup(parents)

            item_id = node_lookup(itemname, parent, 1)
            parent_ini(parents, item_id)
            
            try:
                childs = group.member.value
                    
                if (isinstance(childs, str)):
                    childs = [str(group.member.value)]

                child_ini(childs, item_id)

            except Exception as e:
                print("ERROR WHILE READING MEMBERS OF GROUP - PERHAPS THE GROUP HAS NO MEMBERS. ERROR: {}".format(e))

        print("INITIALISING COMPLETE! (GROUP NODES)")

    except Exception as e:
        print("INITIALISING GROUP NODES FAILED! ERROR: {}".format(e))
        
def parent_ini(parents, primar_id):

    i = 0
    parents_parent_name = ""

    for parent in parents:
        
        i = i + 1
        parent_name = "[O] " + re.sub(r'^.*?OU=', '', parent)

        try:
            parents_parent_name = re.sub(r'^.*?OU=', '', parents[i])
        except:
            parents_parent_name = "no parent"

        parent_id = node_lookup(parent_name, parents_parent_name, 2)
        primar_id = edge_lookup(parent_id, primar_id, "group")

def child_ini(childs, item_id):
    
    # Try to connect to the Active Directory and get all the information about the groups on it.
    server = Server(ad_server, get_info=ALL)
    ad_conn = Connection(server, user="{}\\{}".format(ad_domain, ad_user), password=ad_password, authentication=NTLM, auto_bind=True)

    for child in childs:
            
        childs_parents = [x for x in str(child).split(",") if "OU=" in x]
        child_name = re.sub(r'^.*?CN=', '', [x for x in str(child).split(",") if "CN=" in x][0])
        child_name_with_prefix = "[U] " + child_name

        ad_conn.search("dc={},dc=local".format(ad_domain), "(&(objectClass=person)(displayName={}))".format(child_name), attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])

        primar_id = node_lookup(child_name_with_prefix, "NO PARENT", 3)

        all_mail = get_info(ad_conn, "msExchShadowProxyAddresses")

        if (all_mail != "NO DATA"):

            all_mail = ""

            for mail in get_info(ad_conn, "msExchShadowProxyAddresses"):
                all_mail = all_mail + "/" + mail

        manager = "NO MANAGER"

        try:
            manager = str([x for x in str(get_info(ad_conn, "manager")).split(",") if "CN=" in x][0]).replace("CN=", "")
            manager_id = node_lookup("[U] " + manager, "-", 3)

            edge_lookup(manager_id, primar_id, "user")
        except:
            pass

        cursor.execute(
            "UPDATE NODES SET admin_count='{}', country='{}', country_code='{}', department='{}', last_logoff='{}', last_logon='{}', logon_count='{}', main_mail='{}', mobile='{}', all_mail='{}', postal_code='{}', telephone_nr='{}', bad_password_time='{}', manager='{}', account_name='{}', last_change='{}', created='{}' WHERE id = {};".format(
                get_info(ad_conn, "adminCount"), get_info(ad_conn, "co"), get_info(ad_conn, "countryCode"), get_info(ad_conn, "department"), get_info(ad_conn, "lastLogoff"), get_info(ad_conn, "lastLogon"), 
                get_info(ad_conn, "logonCount"), get_info(ad_conn, "mail"), get_info(ad_conn, "mobile"), all_mail, get_info(ad_conn, "postalCode"), 
                get_info(ad_conn, "telephoneNumber"), get_info(ad_conn, "badPasswordTime"), manager, get_info(ad_conn, "sAMAccountName"), get_info(ad_conn, "whenChanged"), get_info(ad_conn, "whenCreated"), primar_id
            )
        )

        conn.commit()

        edge_lookup(item_id, primar_id, "group")

        i = 0

        for parent in childs_parents:
                
            i = i + 1
            parents_parent_name = ""

            try:
                parents_parent_name = re.sub(r'^.*?OU=', '', childs_parents[i])
            except:
                parents_parent_name = "no parent"

            parent_name = "[O] " + re.sub(r'^.*?OU=', '', parent)
            parent_id = node_lookup(parent_name, parents_parent_name, 2)

            primar_id = edge_lookup(parent_id, primar_id, "group")

def node_revision():
    
    try:
        cursor.execute("SELECT id from NODES;")
        NODES = cursor.fetchall()

        for item in NODES:
            id = item["id"]

            cursor.execute("SELECT COUNT(*) as child_amount FROM EDGES WHERE source={} OR target={};".format(id, id))
            child_amount = cursor.fetchone()["child_amount"]
            
            cursor.execute("UPDATE NODES SET child_amount = {} WHERE id = {};".format(child_amount, id))

        conn.commit()

        print("REVISIONING COMPLETE! (NODES)")
    except Exception as e:
        print("REVISIONING NODES FAILED! ERROR: {}".format(e))

    try:
        cursor.execute("SELECT * from NODES;")
        NODES = cursor.fetchall()

        for item in NODES:
            id = item["id"]

            if (item["child_amount"] == 0 and item["active"] == 1):
                cursor.execute("UPDATE NODES SET active = 0 WHERE id = {};".format(id))
                print("THE NODE {} HAS BEEN DEACTIVATED BECAUSE IT HAS NOT FOUND A CONNECTION TO A NODE AND THERE IS NONE BELOW IT.".format(item["name"]))

        conn.commit()
    except  Exception as e:
        print("DEACTIVATION OF UNUSED NODES FAILED! ERROR: {}".format(e))
