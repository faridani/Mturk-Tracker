# -*- coding: utf-8 -*-

import code
import traceback
import signal

def _debug_callback(sig, frame):
    """Interrupt running process, and provide a python prompt for    
    interactive debugging.
    """
    d = {'_frame': frame}
    d.update(frame.f_globals)
    d.update(frame.f_locals)
    i = code.InteractiveConsole(d)
    message = "Signal recieved: entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def debug_listen():
    signal.signal(signal.SIGUSR1, _debug_callback)
