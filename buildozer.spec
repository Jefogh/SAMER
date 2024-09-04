[app]
title = My Captcha Solver
package.name = mycaptchasolver
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = images/*.png,images/*.jpg,*.json
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow==10.3.0,opencv-python-headless,numpy,httpx,easyocr
presplash.filename = %(source.dir)s/images/presplash.png
icon.filename = %(source.dir)s/images/favicon.png
orientation = portrait
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.debug_artifact = apk

# Ensure using a specific NDK version
android.ndk = 21d

[buildozer]
log_level = 1  # Use 'info' to reduce log size
warn_on_root = 1
