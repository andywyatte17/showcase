#!/bin/python

import SimpleHTTPServer
import SocketServer
from multiprocessing import Process, Queue
import os, socket
import copy
import time

_HTML = '''<html>
<head>
<script>
function reloadImage() {
   var now = new Date();
   document.images['screenshot'].src = 'screenshot.png?' + now.getTime();
   // Start new timer (1 min)
   timeoutID = setTimeout('reloadImage()', 30000);
}
</script>
</head>
<body onload="reloadImage()">
Below is a screenshot of buildchimp. It will automatically refresh every 30 seconds.
<img id="screenshot" src="screenshot.png"/>
</body>
</html>'''


def serve(webserver, q_process_to_main):
    os.system('mkdir -p "{}"'.format(webserver.basepath))
    os.chdir(webserver.basepath)
    open(webserver.basepath + "/index.html", "w").write(_HTML)
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = None
    port = None
    for PORT in range(8000,8100):
        try:
            httpd = SocketServer.TCPServer(("", PORT), Handler)
            port = PORT
            break
        except SocketServer.socket.error as exc:
            if exc.args[0] != 48: raise
            print('Port {} is already in use, will try another.'.format(PORT))
    if httpd:
        q_process_to_main.put('Webserver - serving on <a href="{0}:{1}">{0}:{1}</a>'.format(
               socket.gethostbyname(socket.gethostname()), port))
        httpd.serve_forever()
    else:
        q_process_to_main.put("Webserver - couldn't start.")

class Webserver():
    def __init__(self):
        TMP_BC = "/tmp/buildchimp_web"
        self.q_process_to_main = Queue()
        self.basepath = TMP_BC
        self.process = None
        self.pngPath = TMP_BC + "/screenshot.png"
        self.serving_string = False

    def __del__(self):
        self.stop()

    def __str__(self):
        if not self.serving_string:
            try:
                self.serving_string = self.q_process_to_main.get_nowait()
            except: pass
        return self.serving_string if self.servingstring else ""

    def start(self):
        self_copy = copy.copy(self)
        self.process = Process(target = serve, args = (self_copy, self.q_process_to_main) )
        self.process.start()

    def stop(self):
        if self.process:
            self.process.terminate()

    def wait_on_msg(self, timeout=10):
        try:
            got = self.q_process_to_main.get(block=True, timeout=timeout)
            return got
        except:
            return None
