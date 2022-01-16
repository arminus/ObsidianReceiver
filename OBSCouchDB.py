import couchdb
import binascii
import time
import yaml
import re

class OBSCouchDB:
    """Handle all connections and updates to the Obsidian livesync CouchDB
    
    sets init_ok to false and puts error into error_msg if something goes wrong
    ...

    Attributes
    ----------
    db: chouchdb.database
        the database found at the configured URL
    init_ok: bool
        set to False if something went wrong during __init__
    error_msg:
        any error message
    http_code:
        http response code
    target_doc_id: str
        the ID of the target document, e.g. MyFolder/MyDocument
    target_doc: couchdb.document
        the actual document for target_doc_id
    trace: bool
        print trace messages

    Methods
    -------
    add_content(content : str)
        add content to the defined target_doc_id
    get_last_child()
        Test methoid only: return the last child of target_doc
    delete_last_child()
        Test methoid only: delete the (previously added) last child of target_doc
    """

    db = None
    init_ok = True
    error_msg = ""
    http_code = 200
    target_doc = None
    target_doc_id = None
    trace = False

    def __init__(self, the_target_doc_id = ""):
        """
        Parameters
        ----------
        the_target_doc_id: str, optional
            override the target_doc_id (fully qualified name of the "receiver" .md file) as defined in CouchDB.yaml
        """

        try:
            with open("obsidian_conf/CouchDB.yaml", "r") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print("Cannot read obsidian_conf/CouchDB.yaml")
            exit(-1)

        dbname = config["couchdb"]["dbname"]        # CouchDB DB name
        username = config["couchdb"]["username"]    # CouchDB DB username
        password = config["couchdb"]["password"]    # CouchDB DB password
        couchdb_url = config["couchdb"]["url"]      # CouchDB DB address, e.g. https://couchdb.my.domain.com/obs/

        # the fully qualified name of the "receiver" .md file, e.g. 0-WorkInProgress/CouchDB-Test.md
        if ( the_target_doc_id != ""):
            self.target_doc_id = the_target_doc_id
        else:
            self.target_doc_id = config["obsidian"]["target_doc_id"]
        if not re.match(r'.*\.md$', self.target_doc_id):
            self.target_doc_id += ".md";

        # SSL issues:
        # https://www.reddit.com/r/learnpython/comments/q5fffb/windows_python_397_urllib_and_dst_root_ca_x3_lets/ - no effect ?
        # https://forum.micropython.org/viewtopic.php?t=11201

        # https://gist.github.com/marians/8e41fc817f04de7c4a70 - This is an unofficial manual for the couchdb Python module
        url = re.sub(r'^(http[s]?://)(.*)', r'\1'+username+':'+password+'@'+r'\2', couchdb_url)
        try:
            couch = couchdb.Server(url)
            self.db = couch[dbname]
        except:
            self.error_msg = f"Could not connect to {couchdb_url}"
            self.http_code = 500
            self.init_ok = False
        try:
            self.target_doc = self.db[self.target_doc_id]
        except:
            self.error_msg = f"Could not retreive document with id {self.target_doc_id}"
            self.http_code = 404
            self.init_ok = False

    def add_content(self, content : str):
        """Add content to the defined target_doc_id

        Parameters
        ----------
        content: str
            The content to be added
        """

        try:
            unique_content = content + str(round(time.time_ns()/1000000))
            checksum = '%08X' % (binascii.crc32(unique_content.encode('utf-8')) & 0xffffffff)
            new_id = "h:"+checksum.lower()

            content += "\n"
            self.db[new_id] = {'data': content, 'type': 'leaf'}
            if self.trace:
                print(f"Created new document {new_id}")

            children = self.target_doc["children"]

            # update the target doc
            self.target_doc["mtime"] = round(time.time_ns()/1000000)
            self.target_doc["children"] = children + [new_id]
            self.target_doc["size"] = self.target_doc["size"] + len(content)
            self.db[self.target_doc_id] = self.target_doc

            if self.trace:
                print(f"Updated {self.target_doc_id}")
        except Exception as e:
            self.error_msg = e.__class__
            return ""

        return f"Appended content to {self.target_doc_id}"

    def get_last_child(self):
        """ Test Method

        return the last child of target_doc
        """
        cid = self.target_doc["children"][-1]
        return self.db[cid]

    def delete_last_child(self):
        """ Test Method
        
        delete the (previously added) last child of target_doc
        """
        children = self.target_doc["children"]
        cid = children[-1]
        del self.db[cid]
        if self.trace:
            print(f"Deleted {cid}")
        del children[-1]
        self.target_doc["children"] = children
        if self.trace:
            print(f"Updated {self.target_doc_id}")

        return True
