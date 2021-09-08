import threading

def btdebug( msg ):
    """ Prints a messsage to the screen with the name of the current thread """
    print(f"[{str(threading.currentThread().getName())}] {msg}")
