from pynput.mouse import Controller, Button

_mouse = Controller()

def mouse_down():
    _mouse.press(Button.left)

def mouse_up():
    _mouse.release(Button.left)
