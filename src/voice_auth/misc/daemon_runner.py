from daemon.runner import DaemonRunner
import os

class App(object):
    def __init__(self, worker, name=None, pidfile_path=None, pidfiles_path='/var/run', files_preserve=None):
        if not pidfile_path:
            if not name:
                import sys
                name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            pidfile_path = os.path.join(pidfiles_path, '%s.pid' % name)

        null_path = '/dev/null'
        self.stdin_path = null_path
        self.stdout_path = null_path
        self.stderr_path = null_path
        
        self.pidfile_path = pidfile_path
        self.pidfile_timeout = 0
        
        self.files_preserve = files_preserve
        
        self.run = worker

    def do_action(self):
        r = DaemonRunner(self)
        r.daemon_context.files_preserve = self.files_preserve
        r.do_action()
