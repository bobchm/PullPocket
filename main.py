from pocket import Pocket, PocketException
import requests
from urllib.parse import urlparse
import os
import pdfkit
import html2text
import json


def name_from_url(url):
    if url[-1] == '/':
        url = url[:-1]
    o = urlparse(url)
    path = o.path
    head_tail = os.path.split(path)
    return head_tail[1]


def dump_tag(pkt, tag, urldict):
    matches = pkt.get(tag=tag, state="all")
    urllist = []
    if matches:
        if not os.path.isdir(tag):
            os.mkdir(tag)
            os.mkdir(os.path.join(tag, "pdf"))
            os.mkdir(os.path.join(tag, "html"))
            os.mkdir(os.path.join(tag, "text"))
        sub_list = matches[0]['list']
        for match in sub_list.items():
            match = match[1]
            url = match['resolved_url']
            urllist.append(url)
            print(f"{url}\n")
            fname = name_from_url(url)

            urlmissing = False
            htmltext = None
            pname = os.path.join(tag, "html", fname) + ".html"
            if not os.path.exists(pname):
                try:
                    r = requests.get(url, allow_redirects=True)
                    if r.status_code == 200:
                        htmltext = str(r.content, 'UTF-8')
                        with open(pname, "w", encoding='utf8') as fo:
                            fo.write(htmltext)
                    else:
                        urlmissing = True
                except requests.ConnectionError:
                    print("Connection error\n")
                    urlmissing = True

            if not urlmissing:
                pname = os.path.join(tag, "text", fname) + ".txt"
                if not os.path.exists(pname):
                    if not htmltext:
                        try:
                            r = requests.get(url, allow_redirects=True)
                            if r.status_code == 200:
                                htmltext = str(r.content, 'UTF-8')
                            else:
                                urlmissing = True
                        except requests.ConnectionError:
                            print("Connection error\n")
                            urlmissing = True
                    if htmltext:
                        with open(pname, "w", encoding='utf8') as fo:
                            h = html2text.HTML2Text()
                            h.ignore_links = True
                            txt = h.handle(htmltext)
                            fo.write(txt)

            if not urlmissing:
                pname = os.path.join(tag, "pdf", fname) + ".pdf"
                if not os.path.exists(pname):
                    try:
                        options = {
                            'quiet': ''
                        }
                        pdfkit.from_url(url, pname, options=options)
                    except:
                        print("PDFkit error occurred\n")
    urldict[tag] = urllist


p = Pocket(
 consumer_key='92012-eed59ea9253b3c580d01447a',
 access_token='16751f51-3306-eb9c-66d0-ca57fb'
)

urldict = {}
if os.path.exists('tagdict.json'):
    with open('tagdict.json') as json_file:
        urldict = json.load(json_file)

dump_tag(p, "practice", urldict)
dump_tag(p, "lisp", urldict)

with open('tagdict.json', 'w') as json_file:
    json.dump(urldict, json_file)
