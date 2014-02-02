#!/usr/local/bin/python2.7
import requests
import httplib
import json
import os
from datetime import date
from ID3 import *

channels = [ 
 "4DDSat",  # davidecks (house)
# "4TVThu",  # tribe vibes (hip hop)
# "4HOPWed",  # house of pain (house of pain)
# "4ZSSun", # zimmerservice service (mixed)
# "4LBFri", # la boum deluxe (electro)
# "4LRMon", # liquid radio (ambient)
# "4HSTue", # high spirits (House, Soul und Breaks)
]

download = "http://loopstream01.apa.at/?channel=fm4&ua=flash&id="


# patch httplib read function so it does catch an
# icomplete read (end of mp3 stream ends usually
# with 218 bytes only, returns partial data then
def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial
    return inner
httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)

for chan in channels:
    url = "http://audioapi.orf.at/fm4/json/2.0/playlist/" + chan
    resp = requests.get(url=url)
    data = resp.content
    var = json.loads(data)

    try:
        stream_size =  len(var["streams"])
    except KeyError:
        continue
    
    # multiple parts
    if stream_size > 1:
        stream_part=1

    for stream in var["streams"]:
        try:
            title = var["title"]
            print title
        except KeyError:
            if chan == "4HOPWed":
                title = "FM4 House of Pain"
            elif chan == "4DDSat":
                title = "FM4 DaviDecks"
            elif chan == "4TVThu":
                title = "FM4 Tribe Vibes"
            elif chan == "4ZSSun":
                title = "FM4 Zimmerservice"

        try:
           day = var["day"]
        except KeyError:
           day=str(date.today()).replace("-","") 

        if stream_size > 1:
            file = title.replace(" ", "_") + "_" + str(day) + "_teil_" + str(stream_part) +".mp3"
        else:
            file = title.replace(" ", "_") + "_" + str(day) +".mp3"

        stream =  stream["loopStreamId"]

        if not os.path.exists(file):
            r = requests.get(url=download+stream, stream=True)
            print "Downloading: " + download+stream
            print "File: " + file
            with open(file, "wb") as fh:
                for block in r.iter_content(256):
                    if not block:
                        print "error downloading"
                        break

                    fh.write(block)
            fh.close
            id = ID3(file)
            id["ARTIST"] = "FM4"
            if stream_size > 1:
                id["TITLE"] = str(var["day"]) + "_" + str(stream_part)
                stream_part=stream_part+1
            else:
                id["TITLE"] = str(var["day"])
            id["ALBUM"] = var["title"]
            id.write
        else:
            print "skipping: " + file
            if stream_size > 1:
                stream_part=stream_part+1

    # todo - merge downloaded parts via mp3wrap and tag accordingly
    if (stream_size + 1) == stream_part:
        if not os.path.exists(file + ".merged"):
            print "all parts dowloaded, not yet merged, merge"
                
