from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import tempfile
import os
import os.path

import threading


class TestFTPServer(object):
    class FTPThread(threading.Thread):
        def __init__(self, server, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.server = server

        def run(self):
            try:
                self.server.serve_forever()
            except OSError:
                pass

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.temp_dir, "dir1"))
        with open(os.path.join(self.temp_dir, "file1.txt"), 'w') as f:
            f.write("Test")
        with open(os.path.join(self.temp_dir, "file2.txt"), 'w') as f:
            f.write("Test")

        authorizer = DummyAuthorizer()
        authorizer.add_user("username1", "password1", self.temp_dir, perm='elradfmwMT')
        handler = FTPHandler
        handler.authorizer = authorizer
        self.server = FTPServer(("127.0.0.1", 2121), handler)
        self.server_thread = TestFTPServer.FTPThread(server = self.server)

    def clean_temp_dir(self):
        os.remove(os.path.join(self.temp_dir, "file1.txt"))
        os.remove(os.path.join(self.temp_dir, "file2.txt"))
        if os.path.exists(os.path.join(self.temp_dir, "file3.txt")):
            os.remove(os.path.join(self.temp_dir, "file3.txt"))
        os.rmdir(os.path.join(self.temp_dir, "dir1"))
        os.rmdir(self.temp_dir)

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.close_all()
        self.server_thread.join()
        self.clean_temp_dir()