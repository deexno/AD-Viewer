FROM ubuntu:latest
RUN apt-get update && apt install git -y && apt install python3 -y && apt install pip -y && apt install cron -y
RUN git clone https://github.com/deexno/ACTIVE-DIRECTORY-VIEWER.git
RUN pip3 install ldap3 configparser dash plotly colour flask pymysql dash_cytoscape
RUN echo "00 01,13 * * * cd /ACTIVE-DIRECTORY-VIEWER/; /usr/bin/python3 /ACTIVE-DIRECTORY-VIEWER/import.py" >> /var/spool/cron/crontabs/root

############################################################################
#         REPLACE THE FOLLOWING LINES WITH YOUR SPECIFIC CONFIG            #
############################################################################
RUN echo "[AD_INFO]" > /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "server = SERVER" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "domain = DOMAIN" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "user = USERNAME" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "password = PASSWORD" >> /ACTIVE-DIRECTORY-VIEWER/config.ini

RUN echo "[DB_INFO]" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "server = SERVER" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "dbname = DB_NAME" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "user = USER" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
RUN echo "password = PASSWORD" >> /ACTIVE-DIRECTORY-VIEWER/config.ini
############################################################################

WORKDIR /ACTIVE-DIRECTORY-VIEWER
RUN /usr/bin/python3 /ACTIVE-DIRECTORY-VIEWER/import.py

CMD /usr/bin/python3 /ACTIVE-DIRECTORY-VIEWER/index.py
