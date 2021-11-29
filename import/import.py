import import_lib

import_lib.db_cleaning()
ad_connection = import_lib.ad_connect()
import_lib.group_node_ini(ad_connection)
import_lib.node_revision()