*Chromicam* uses CEF (Chromium Embedded Framework) and OBS-Virtualcam (along with the very awesome pyvirtualcam lib) to create a live video output device that mirrors a website.  This application can be run minimized, in the background, which frees up desktop screen space versus the alternative of screen capturing.

![image](https://user-images.githubusercontent.com/2575698/84745620-d6a57b80-af82-11ea-8137-7e01dd188004.png)
Pre-built Windows Binary  [can be found here](https://obs.ninja/chromicam_win.zip)

You'll need to install this also: https://obsproject.com/forum/resources/obs-virtualcam.949/

if OBS is not installed, you can force the install of the driver with this:
```
regsvr32 /n /i:1 "obs-virtualcam\bin\32bit\obs-virtualsource.dll"
regsvr32 /n /i:1 "obs-virtualcam\bin\64bit\obs-virtualsource.dll"
```
Running with the compiled version:
```
chromicam.exe https://www.youtube.com/watch?v=oHg5SJYRHA0 1280 720 30
```


If you want to run Chromicam from source, you will need Python3 and then you can do:

```
pip install -r requirements.txt
```
```
python3 chromicam.py https://www.youtube.com/watch?v=oHg5SJYRHA0 1280 720 30
```


Stop OBS Virtual Cam before using with this tool if its already in use. 
(Stop it in OBS if using it there, for example)

If it crashes, deactive and reaactivate OBS Virtualcam (via its OBS device settings works)
Also double check to make sure its not already in use by OBS or other app.

This app will use the first OBS Virtualcam; others install are ignored.

There will not be any video output unless the content is dynamic; it will update on scene changes.

Default is up to 30fps
