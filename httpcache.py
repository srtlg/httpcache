#! /usr/bin/python3

# A simple HTTP proxy which does caching of requests.
# "Inspired" by: https://gist.github.com/justinmeiners/24dcf5904490b621220bed643651f681
# but updated with
#
# - a clean exit on signal allowing it to be easily popped by another script using subprocess
# - tcp socket reuse to avoid the tcp socket already in use if popped often
# - a cache directory to avoid a lot of files just being in the middle
# 
# use it by getting 'http://localhost:8000/www.kernel.org' to get http://www.kernel.org 
# duplicate the class+tcpserver and listen on another port for your https needs (alter line 40 in the duplicate);
# it will share the cache

import http.server
import socketserver
import urllib.request
import shutil
import os
import sys
import hashlib
import signal
import argparse


CEND = '\33[0m'
CYELLOW = '\33[33m'

if sys.platform.startswith('win32'):
    os.system('')

parser = argparse.ArgumentParser()
parser.add_argument('port', type=int, default=8000, nargs='?', help='port to listen on, default 8000')
parser.add_argument('-c', '--cache-dir', default='./cache/', help='location of cache files, default ./cache')
parser.add_argument('-b', '--bind', default='127.0.0.1', help='bind address, default 127.0.0.1')
args = parser.parse_args()

cache_base = args.cache_dir
httpd = None


def exit_gracefully(sig, stack):
    # print("received sig %d, quitting" % (sig))
    httpd.server_close()
    exit()


class CacheHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        m = hashlib.new("sha1", usedforsecurity=False)
        m.update(self.path.encode("utf-8"))
        cache_filename = cache_base + m.hexdigest() + ".cached"

        if not os.path.exists(cache_filename):
            self.log_message(CYELLOW + 'downloading %s' + CEND, self.path)
            with open(cache_filename + ".temp", "wb") as output:
                req = urllib.request.Request(self.path)
                for k in self.headers:
                    if k not in ["Host"]:
                        req.add_header(k, self.headers[k])
                resp = urllib.request.urlopen(req)
                shutil.copyfileobj(resp, output)
                os.rename(cache_filename + ".temp", cache_filename)

        with open(cache_filename, "rb") as cached:
            self.send_response(200)
            self.end_headers()
            shutil.copyfileobj(cached, self.wfile)


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer((args.bind, args.port), CacheHandler)
if not os.path.exists(cache_base):
    os.mkdir(cache_base)

httpd.serve_forever()
