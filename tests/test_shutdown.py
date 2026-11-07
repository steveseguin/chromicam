"""Offline lifecycle regressions. Run: python -m unittest discover -s tests -v.

The complete application runs in a child process, with real Python threads,
Events and NumPy. Only CEF, the virtual camera and the startup delay are stubbed.
No browser or virtual-camera device is required.
"""

import os
from pathlib import Path
import runpy
import subprocess
import sys
import threading
import types
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parents[1] / "chromicam.py"


def run_scenario(source, scenario):
    real_event = threading.Event
    waiting_for_paint = real_event()
    worker_sent_frame = real_event()
    events = []
    threads = []
    cleanup = []
    observed_scenarios = []
    real_thread = threading.Thread

    class ObservedEvent:
        def __init__(self):
            self.event = real_event()
            self.is_camera_ready = not events
            events.append(self)

        def is_set(self):
            return self.event.is_set()

        def set(self):
            self.event.set()

        def clear(self):
            self.event.clear()

        def wait(self, timeout=None):
            if self.is_camera_ready and not self.event.is_set():
                waiting_for_paint.set()
            return self.event.wait(timeout)

    class ObservedThread(real_thread):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            threads.append(self)

    class Browser:
        def GetUserData(self, key):
            assert key == "OnPaint.buffer_string"
            return bytes(1280 * 720 * 4)

        def SetClientHandler(self, handler):
            pass

        def SendFocusEvent(self, focus):
            pass

        def WasResized(self):
            pass

        def CloseBrowser(self):
            assert threads and not threads[0].is_alive(), "closed browser before joining worker"
            cleanup.append("browser.close")

    class Camera:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            cleanup.append("camera.close")

        def send(self, frame):
            worker_sent_frame.set()

    class WindowInfo:
        def SetAsOffscreen(self, handle):
            pass

    def message_loop():
        assert worker_sent_frame.wait(2), "worker did not send its first frame"
        assert waiting_for_paint.wait(2), "worker did not wait for another paint"
        observed_scenarios.append(scenario)
        if scenario == "interrupt":
            raise KeyboardInterrupt()
        if scenario == "error":
            raise RuntimeError("simulated message-loop failure")
        assert scenario == "normal"

    def verify_cleanup():
        assert observed_scenarios == [scenario], "scenario did not reach the blocked worker"
        assert len(threads) == 1 and not threads[0].is_alive()
        assert cleanup == ["camera.close", "cef.quit", "browser.close", "cef.shutdown"], cleanup
        print("SHUTDOWN_OK", flush=True)

    def exit_process(code):
        assert code == 0
        verify_cleanup()
        real_exit(code)

    cef = types.SimpleNamespace(
        Initialize=lambda **kwargs: None,
        WindowInfo=WindowInfo,
        CreateBrowserSync=lambda **kwargs: Browser(),
        MessageLoop=message_loop,
        QuitMessageLoop=lambda: cleanup.append("cef.quit"),
        Shutdown=lambda: cleanup.append("cef.shutdown"),
    )
    modules = {
        "cefpython3": types.SimpleNamespace(cefpython=cef),
        "pyvirtualcam": types.SimpleNamespace(Camera=Camera),
    }
    real_exit = os._exit
    sys.argv = [str(source)]
    with mock.patch.dict(sys.modules, modules), \
            mock.patch.object(threading, "Event", ObservedEvent), \
            mock.patch.object(threading, "Thread", ObservedThread), \
            mock.patch("time.sleep", lambda seconds: None), \
            mock.patch.object(os, "_exit", exit_process):
        runpy.run_path(str(source), run_name="__main__")
    verify_cleanup()


class ShutdownTests(unittest.TestCase):
    def check_shutdown(self, scenario):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--scenario", str(SOURCE), scenario],
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SHUTDOWN_OK", result.stdout, result.stdout + result.stderr)

    def test_normal_close_with_worker_waiting(self):
        self.check_shutdown("normal")

    def test_ctrl_c_with_worker_waiting(self):
        self.check_shutdown("interrupt")

    def test_message_loop_error_with_worker_waiting(self):
        self.check_shutdown("error")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scenario":
        run_scenario(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
