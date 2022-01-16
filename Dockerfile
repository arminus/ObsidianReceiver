FROM python:3.9-bullseye

# change according to your location
ENV TZ=Europe/Berlin

WORKDIR /root

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /root/obsidian_conf
# maybe not copy this ? 
COPY obsidian_conf/CouchDB.yaml ./obsidian_conf
COPY OBSCouchDB.py .
COPY test_add2couchdb.py .
COPY server.py .
COPY start_server.sh .

RUN chmod a+x ./start_server.sh

ENTRYPOINT [ "/root/start_server.sh" ]  
  