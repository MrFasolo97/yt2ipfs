#!/usr/bin/python37
import requests
import json
import flask
from flask import request
from flask_restful import Api
import ipfshttpclient
import asyncio
import subprocess
import os
import shutil
from waitress import serve
import inspect

IPFS_NODE_ADDR = ""
PORT = -1
API_PATH = ""

try:
    config_file = open("./config.json")
    config = json.load(config_file)
    config_file.close()
    IPFS_NODE_ADDR = config["ipfs_node_address"] or "/ip4/127.0.0.1/tcp/5001"
    YT_API_KEY = config["youtube_api_key"]
    MY_API_KEY = config["my_api_key"]
    API_PATH = config["api_path"] or "/sync_api"
    if API_PATH[-1] == "/":
        print("Fixing API_PATH from", API_PATH, "to", API_PATH[0:-1])
        API_PATH = API_PATH[0:-1]
    PORT = config["server_port"] or 8080
except FileNotFoundError:
    print("Make a config.json file! Check config_example.json if needed.")
    exit(-1)
except KeyError:
    print("Invalid config.json file!")
    exit(-1)
except json.decoder.JSONDecodeError as e:
    print("Error loading config.json file:")
    print(e)
    exit(1)


try:
    ipfs_client = ipfshttpclient.connect(IPFS_NODE_ADDR, session=True)
except ipfshttpclient.exceptions.VersionMismatch as e:
    print("Unable to connect to IPFS Daemon, wrong version!")
    print("\n", "Path of the file to be modified:", inspect.getfile(ipfshttpclient)[0:-11]+"client"+os.sep+"__init__.py")
    print("\n", "For reference see this:",
           "https://github.com/ipfs-shipyard/py-ipfs-http-client/issues/296#issuecomment-905484061")
    print("\n", e)
    exit(-1)
except ipfshttpclient.exceptions.ConnectionError as e:
    print("Unable to connect to IPFS Daemon")
    print(e)
    print("ADDRESS:", IPFS_NODE_ADDR)
    exit(-1)


app = flask.Flask("sync_api")
api = Api(app)


def download_videos(videos_list):
    path = os.path.dirname(os.path.abspath(__file__))
    for video in videos_list:
        os.mkdir(path + os.sep + "dl" + os.sep + video)
        subprocess.run(["youtube-dl", "-f mp4", "-o./dl/%(id)s/%(title)s.%(ext)s",
                        "https://www.youtube.com/watch?v=" + video, "--write-description", "--write-info-json",
                        "--write-annotations", "--write-thumbnail"])


def pin_videos(video_ids):
    global ipfs_client
    path = os.path.dirname(os.path.abspath(__file__))
    r = []
    for video_id in video_ids:
        load_path = path + os.sep + "dl" + os.sep + video_id + os.sep
        added_files = ipfs_client.add(load_path, recursive=True)
        for file_var in added_files:
            ipfs_client.pin.add(file_var["Hash"])
            r.append([file_var["Hash"], file_var["Name"]])
        shutil.rmtree(load_path)
    return r


def get_videos(channel_id, date):
    global YT_API_KEY
    if date is None:
        date = "1970-01-01T00:00:00Z"

    url = "https://www.googleapis.com/youtube/v3/search"
    querystring = {"key": YT_API_KEY, "channelId": channel_id, "type": "video", "order": "date", "maxResults": "50",
                   "publishedAfter": date}
    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)
    return response.text


@app.route(API_PATH+'/get_all_videos', methods=["POST"])
def get_all_videos_from_channel():
    global YT_API_KEY
    global MY_API_KEY
    json_data = request.get_json()
    channel_id = json_data['channel_id']
    if "date" in json_data:
        date = json_data["date"]
    else:
        date = "1970-01-01T00:00:00Z"
    url = "https://www.googleapis.com/youtube/v3/search"
    base_querystring = {"key": YT_API_KEY, "channelId": channel_id, "type": "video", "order": "date",
                        "maxResults": "50", "publishedAfter": date, "nextPageToken": None}
    querystring = base_querystring
    r = {}
    i = 0
    while True:
        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        json_data2 = json.loads(response.text)
        r[i] = json_data2
        if "nextPageToken" in json_data2:
            querystring["pageToken"] = json_data2["nextPageToken"]
        else:
            break
        i = i+1

    return json.dumps(r), 200


@app.route(API_PATH+'/get_videos', methods=["POST"])
async def request_videos():
    global MY_API_KEY
    json_data = request.get_json()
    channel_id = json_data["channel_id"]
    if "date" in json_data:
        date = json_data["date"]
    else:
        date = "1970-01-01T00:00:00Z"
    api_key = json_data["api_key"]
    if api_key == MY_API_KEY:
        r = get_videos(channel_id, date), 200
        return r
    else:
        return '{"status": "error", "error": "api_key not valid!"}', 401


@app.route(API_PATH+'/youtube2ipfs', methods=["POST"])
async def youtube2ipfs():
    json_text = request.get_data()
    json_data = json.loads(json_text)
    if "video_id" in json_data:
        video_id = json_data["video_id"]
    else:
        video_id = None
    if "multiple_video_ids" in json_data:
        multiple_video_ids = json_data["multiple_video_ids"]
    else:
        multiple_video_ids = None
    api_key = json_data["api_key"]
    global MY_API_KEY
    hashes = None
    if api_key == MY_API_KEY:
        if multiple_video_ids is not None:
            download_videos(multiple_video_ids)
            pin_videos(multiple_video_ids)
        if video_id is not None:
            download_videos([video_id])
            hashes = pin_videos([video_id])
        if video_id is None and multiple_video_ids is None:
            return '{"status": "error", "error": "Not OK, at least one of "multiple_video_ids" and "video_id" is ' \
                   'required.', 200
        return json.dumps(hashes), 200
    else:
        return '{"status": "error", "error": "api_key not valid!"}', 401


@app.route(API_PATH)
@app.route("/")
def index():
    f = open("index.html", "r")
    html = f.read()
    f.close()
    return html, 200


loop = asyncio.get_event_loop()
print("Now listening on port", PORT)
if __name__ == "__main__":
    serve(app, port=PORT)
