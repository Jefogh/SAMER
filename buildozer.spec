[app]

# باقي الإعدادات كما هي...

# استخدام الإصدار المحدد من NDK (25b أو أحدث)
android.ndk = 25b

# باقي الإعدادات كما هي...


# (str) Title of your application
title = My Captcha Solver

# (str) Package name
package.name = mycaptchasolver

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
source.include_patterns = images/*.png,images/*.jpg,*.json

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow==10.3.0,opencv-python-headless,numpy,httpx,tensorflow==2.4.0,keras-ocr

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
presplash.filename = %(source.dir)s/images/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/images/favicon.png

# (list) Supported orientations
orientation = portrait

# (list) List of permissions required by the app
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 1

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# باقي الإعدادات كما هي...

