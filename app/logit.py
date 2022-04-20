
from time import time
from os import environ

class logit:
    def __init__(self,logfile="/var/www/logs/debug.log",debug=False):
        self.logfile = logfile
        self.debug = False
        if environ.get('FEVR_DEBUG', 'false').lower() == "true" or debug == True:
            self.debug = True

    def execute(self,msg,src='fEVR',level='debug',logpath='/var/www/logs'):
        self.logtime = "{:.4f}".format(time())
        self.logfile = f"{logpath}/{level}.log"
        logentry = f"{self.logtime} {str(msg)}"
        self.to_stderr(f"[ {src:15}] {logentry}")
    def to_stderr(self, *a):
        import sys
        print(*a, file=sys.stderr)