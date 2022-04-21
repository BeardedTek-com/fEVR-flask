
from time import time

class logit:
    def __init__(self,logfile="/var/www/logs/debug.log",debug=False):
        self.logfile = logfile
        self.debug = debug
    def execute(self,msg,src='fEVR'):
        self.logtime = "{:.4f}".format(time())
        logentry = f"{self.logtime} {str(msg)}"
        self.to_stderr(f"[ {src:15}] {logentry}")
    def to_stderr(self, *a):
        import sys
        print(*a, file=sys.stderr)
