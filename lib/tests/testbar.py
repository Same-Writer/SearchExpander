from alive_progress import alive_bar, config_handler
import time

config_handler.set_global(length=6, bar='blocks')

with alive_bar(force_tty=True) as bar:
    while True:
        for i in range(300):
            time.sleep(.01)
            bar()
        print("what happens now?")