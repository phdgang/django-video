import pp
import os
import sys

class Job:
    def __init__(self, job_server, function, depfuncs=(), modules=(), globals=None):
        self.job_server = job_server
        self.function = function
        self.depfuncs = depfuncs
        self.modules = modules
        self.globals = globals

    def schedule(self, args, callback=None, callbackargs=()):
        self.job_server.submit(self.function, depfuncs=self.depfuncs,
                               modules=self.modules, globals=self.globals,
                               callback=callback, callbackargs=callbackargs,
                               args=args)
