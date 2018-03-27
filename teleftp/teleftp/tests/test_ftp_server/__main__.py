from teleftp.tests.test_ftp_server import TestFTPServer
import time


server = TestFTPServer()

try:
    server.start()
    time.sleep(1)
    a = input("Running (port 2121). Press return to stop.")
finally:
    server.stop()