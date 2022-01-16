from OBSCouchDB import OBSCouchDB
from fastapi import FastAPI, Request, Response, status
from typing import Optional
import datetime
import yaml
import json
# import urllib.parse

# default or configured timestamp format
ts_format = ""
try:
    with open("obsidian_conf/CouchDB.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    ts_format = config["obsidian"]["timestamp_format"]
except:
    # for now
    pass
if not ts_format or ts_format == "":
    ts_format = "%Y-%m-%d %H:%M:%S"

app = FastAPI()

@app.get("/")
async def index():
    return "Call this with a PUT request on /obsput and your content in the body"

@app.put("/obsput", status_code=200)
async def obsput(request: Request, response: Response, doc_id: Optional[str] = "", timestamp: Optional[str] = "", type: Optional[str] = ""):
    content_type = request.headers['content-type']
    body = await request.body()
    if not body:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "No content provided!"
    else:
        # handle body with both application/json { "data": "my content "} body as well as a plaintext
        if content_type == "application/json":
            try:
                data = json.loads(body)
                content = data['data']
            except:
                return "Bad content provided!"
        else:
            content = str(body,'UTF-8')

        print(f"content: {content}")

        obsCdb = OBSCouchDB(doc_id)
        if (not obsCdb.init_ok):
            response.status_code = obsCdb.http_code
            return obsCdb.error_msg
        else:
            content = format_content(content, timestamp, type)
            result = obsCdb.add_content(content)
            if result == "":
                response.status_code = obsCdb.http_code
                return obsCdb.error_msg
            else:
                response.status_code = status.HTTP_201_CREATED
                return result

def format_content(content, timestamp, type):
    """Format the provided content

    supported type : str - list|checkbox

    returns content : str
    """
    if timestamp and timestamp.lower() == "true":
        now = datetime.datetime.now()
        content = "*" + now.strftime(ts_format) + "* " + content
    if type:
        type = type.lower()
        if type == "list":
            content = "- " + content;
        if type == "checkbox":
            content = "- [ ] " + content;
    return content            
