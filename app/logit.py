
from time import time
import sys

class logit:
    def __init__(self,debug=False):
        self.debug = debug
    def execute(self,msg,src='fEVR'):
        def to_stderr(*a):
            print(*a, file=sys.stderr)
        self.logtime = "{:.4f}".format(time())
        logentry = f"{self.logtime} {str(msg)}"
        if self.debug:
            to_stderr(f"[ {src:15}] {logentry}")
