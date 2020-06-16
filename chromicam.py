## Install:https://github.com/CatxFish/obs-virtual-cam/releases
### THEN run the following, if OBS is not installed.
# regsvr32 /n /i:1 "obs-virtualcam\bin\32bit\obs-virtualsource.dll"
# regsvr32 /n /i:1 "obs-virtualcam\bin\64bit\obs-virtualsource.dll"
### AND FINALLY..
## pip install -r requirements.txt
# python3 chromicam.py https://www.youtube.com/watch?v=oHg5SJYRHA0 1280 720 30

from cefpython3 import cefpython as cef
import os
import sys
import pyvirtualcam
import numpy as np
import time
import threading

    
# Config
URL = "https://www.youtube.com/watch?v=oHg5SJYRHA0"
VIEWPORT_SIZE = (1280, 720)
FRAMERATE = 30

def command_line_arguments():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if url.startswith("http://") or url.startswith("https://"):
            global URL
            URL = url
        else:
            print("Error: Invalid url argument")
            sys.exit(1)
    if len(sys.argv) > 3:
        width = int(sys.argv[2])
        height = int(sys.argv[3])
        if width > 0 and height > 0:
            global VIEWPORT_SIZE
            VIEWPORT_SIZE = (width, height)
        else:
            print("Error: Invalid width and height")
            sys.exit(1)
    if len(sys.argv) > 4:
        global FRAMERATE
        FRAMERATE = int(sys.argv[4])
        
   

class LoadHandler(object):
    def OnLoadingStateChange(self, browser, is_loading, **_):
        pass

def drawFrame(browser, run_event, camera_ready):
    time.sleep(2)
    with pyvirtualcam.Camera(width=VIEWPORT_SIZE[0], height=VIEWPORT_SIZE[1], delay=0, fps=20, print_fps=True) as cam:
        print("Initializing OBS-VirtualCam..")
        while run_event.is_set():
            camera_ready.wait()
            buffer_string = browser.GetUserData("OnPaint.buffer_string")
            if (buffer_string):
                cam.send(np.frombuffer(buffer_string, dtype=np.uint8, count=(VIEWPORT_SIZE[0]*VIEWPORT_SIZE[1]*4)).reshape((VIEWPORT_SIZE[0],VIEWPORT_SIZE[1],4)))
                
                camera_ready.clear()
                #cam.sleep_until_next_frame()

class RenderHandler(object):
    def __init__(self):
        print('Starting to Render Frames')
        pass

    def GetViewRect(self, rect_out, **_):
        rect_out.extend([0, 0, VIEWPORT_SIZE[0], VIEWPORT_SIZE[1]])
        return True

    def OnPaint(self, browser, element_type, paint_buffer, **_):
        global camera_ready
        if element_type == cef.PET_VIEW:
            buffer_string = paint_buffer.GetString(mode="rgba", origin="top-left")
            browser.SetUserData("OnPaint.buffer_string", buffer_string)
            camera_ready.set();
        
global t,run_event, camera_ready

def endProgram(exctype, value, tb):
    global t, run_event, camera_ready
    print("EXITING");
    run_event.clear()
    camera_ready.set()
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
    
    camera_ready = threading.Event()
    camera_ready.set()
    
    browser = cef.CreateBrowserSync(window_info=window_info, settings=browser_settings, url=URL)
    browser.SetClientHandler(RenderHandler())
    
    browser.SendFocusEvent(True)
    browser.WasResized()
    browser.SetClientHandler(LoadHandler())
    
    run_event = threading.Event()
    run_event.set()
    
    t = threading.Thread(target=drawFrame, args=(browser,run_event,camera_ready,))
    t.start()
    
    cef.MessageLoop()
    run_event.clear()
    camera_ready.set()
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
