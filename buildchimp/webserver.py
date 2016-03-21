#!/bin/python

import SimpleHTTPServer
import SocketServer
from threading import Thread, Lock
import os, socket

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

class Webserver():
    def __init__(self):
        self.thread = None
        self.httpd = None
        self.pngPath = None
        self.lock = Lock()
        self.port = None

    def __del__(self):
        self.stop()

    def __str__(self):
        if self.httpd:
            return "Webserver - serving on {}:{}".format(
                   socket.gethostbyname(socket.gethostname()),
                   self.port)
        else:
            return "Webserver - not serving."

    def start_(self):
        TMP_BC = "/tmp/buildchimp_web"
        os.system('mkdir -p "{}"'.format(TMP_BC))
        os.chdir(TMP_BC)
        self.pngPath = TMP_BC + "/screenshot.png"
        open(TMP_BC + "/index.html", "w").write(_HTML)
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        for PORT in range(8000,8100):
            try:
                httpd = SocketServer.TCPServer(("", PORT), Handler)
                self.httpd = httpd
                self.port = PORT
                break
            except SocketServer.socket.error as exc:
                if exc.args[0] != 48: raise
                print('Port {} is already in use, will try another.'.format(PORT))

    def start(self):
        self.start_()
        self.thread = Thread(target = lambda : self.httpd.serve_forever() )
        self.thread.start()
        print(self)

    def stop(self):
        self.lock.acquire()
        try:
            if self.thread and self.httpd:
                self.httpd.shutdown()
                self.thread.join()
                self.httpd = None
                self.thread = None
            self.lock.release()
        except:
            self.lock.release()
            raise
