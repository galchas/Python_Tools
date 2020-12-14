import time
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

# Set delay, iterations = (how much clicks), run the app, point the mouse cursor on the point you want to click at and click 's'
delay = 2
button = Button.left
start_stop_key = KeyCode(char='s')
exit_key = KeyCode(char='e')
iterations = 100 # 0 for forever


class ClickMouse(threading.Thread):
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.with_iterations = False
        self.program_running = True
        self.i = 1
        if iterations > 0:
            self.with_iterations=True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                mouse.click(self.button)
                print('iteration {}'.format(self.i))
                time.sleep(self.delay)
                self.i += 1
                if self.with_iterations and self.i >= iterations:
                    self.running = False
                    print('End of Iterations!')
            time.sleep(0.1)


mouse = Controller()
click_thread = ClickMouse(delay, button)
click_thread.start()


def on_press(key):
    if key == start_stop_key:
        print('Starting...')
        if click_thread.running:
            click_thread.stop_clicking()
        else:
            click_thread.start_clicking()
    elif key == exit_key:
        print('exit')
        click_thread.exit()
        listener.stop()


with Listener(on_press=on_press) as listener:
    listener.join()
