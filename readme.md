windows binary can be found at: https://obs.ninja/chromicam_win.zip

You'll need to install: https://obsproject.com/forum/resources/obs-virtualcam.949/

if OBS is not installed.
```
regsvr32 /n /i:1 "obs-virtualcam\bin\32bit\obs-virtualsource.dll"
regsvr32 /n /i:1 "obs-virtualcam\bin\64bit\obs-virtualsource.dll"
```

```
pip install -r requirements.txt
```

```
python3 chromicam.py https://obs.ninja/?view=xxxxx 1280 720
```


Stop OBS Virtual Cam before using with this tool if its already in use. 
(Stop it in OBS if using it there, for example)

usage:
chromicam https://obs.ninja/?view=xxx 1280 720 30

or just chromicam.exe to test.

If it crashes, deactive and reaactivate OBS Virtualcam (via its OBS device settings works)
Also double check to make sure its not already in use by OBS or other app.

This app will use the first OBS Virtualcam; others install are ignored.

There will not be any video output unless the content is dynamic; it will update on scene changes.

Default is up to 30fps
