from cefpython3 import cefpython as cef
import os
import platform
import subprocess
import sys
import pyvirtualcam
import numpy as np
import time
import threading

try:
    from PIL import Image, PILLOW_VERSION
except ImportError:
    print("Error: PIL module not available. To install"
          " type: pip install Pillow")
    sys.exit(1)
    
# Config
URL = "https://www.youtube.com/watch?v=oHg5SJYRHA0"
VIEWPORT_SIZE = (1280, 720)

def command_line_arguments():
    if len(sys.argv) == 4:
        url = sys.argv[1]
        width = int(sys.argv[2])
        height = int(sys.argv[3])
        if url.startswith("http://") or url.startswith("https://"):
            global URL
            URL = url
        else:
            print("Error: Invalid url argument")
            sys.exit(1)
        if width > 0 and height > 0:
            global VIEWPORT_SIZE
            VIEWPORT_SIZE = (width, height)
        else:
            print("Error: Invalid width and height")
            sys.exit(1)

    elif len(sys.argv) > 1:
        print("Error: Expected arguments: url width height")
        sys.exit(1)
   

class LoadHandler(object):
    def OnLoadingStateChange(self, browser, is_loading, **_):
        pass

def drawFrame(browser, run_event):
    time.sleep(2)
    with pyvirtualcam.Camera(width=1280, height=720, fps=20, print_fps=True) as cam:
        print("start camara")
        while run_event.is_set():
            buffer_string = browser.GetUserData("OnPaint.buffer_string")
            if (buffer_string):
                image = Image.frombytes("RGBA", VIEWPORT_SIZE, buffer_string, "raw", "RGBA", 0, 1)
                image = np.array(image).astype("uint8")
                cam.send(image)
                cam.sleep_until_next_frame()

class RenderHandler(object):
    def __init__(self):
        print('start')
        pass

    def GetViewRect(self, rect_out, **_):
        rect_out.extend([0, 0, VIEWPORT_SIZE[0], VIEWPORT_SIZE[1]])
        return True

    def OnPaint(self, browser, element_type, paint_buffer, **_):
        if element_type == cef.PET_VIEW:
            buffer_string = paint_buffer.GetString(mode="rgba", origin="top-left")
            browser.SetUserData("OnPaint.buffer_string", buffer_string)
        
global t,run_event
def endProgram(exctype, value, tb):
    global t,run_event
    print("EXITING");
    run_event.clear()
    t.join()
    cef.QuitMessageLoop()
    browser.CloseBrowser()
    cef.Shutdown()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

try:
    sys.excepthook = endProgram  # To shutdown all CEF processes on error
   
    command_line_arguments()
    settings = {
        "windowless_rendering_enabled": True,
    }
    switches = {
        "disable-gpu": "",
        "disable-gpu-compositing": "",
        "enable-media-stream": "",
        "autoplay-policy":"no-user-gesture-required",
        "enable-begin-frame-scheduling": "",
        "disable-surfaces": "",  # This is required for PDF ext to work
    }
    browser_settings = {
        "windowless_frame_rate": 30,  # Default frame rate in CEF is 30
    }
    cef.Initialize(settings=settings, switches=switches)

    parent_window_handle = 0
    window_info = cef.WindowInfo()
    window_info.SetAsOffscreen(parent_window_handle)
    
    browser = cef.CreateBrowserSync(window_info=window_info, settings=browser_settings, url=URL)
    browser.SetClientHandler(RenderHandler())
    
    browser.SendFocusEvent(True)
    browser.WasResized()
    browser.SetClientHandler(LoadHandler())
    
    run_event = threading.Event()
    run_event.set()
    t = threading.Thread(target=drawFrame, args=(browser,run_event,))
    t.start()
    
    cef.MessageLoop()
    run_event.clear()
    t.join()
    
    cef.QuitMessageLoop()
    browser.CloseBrowser()
    cef.Shutdown()
   
except:
    print('Interrupted')
    run_event.clear()
    t.join()
    
    cef.QuitMessageLoop()
    browser.CloseBrowser()
    cef.Shutdown()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
