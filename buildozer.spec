[app]

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
# تحديد المكتبات الضرورية فقط لتقليل حجم البناء
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow==10.3.0,opencv-python-headless,numpy,httpx,easyocr

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
presplash.filename = %(source.dir)s/images/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/images/favicon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (list) List of permissions required by the app
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# تقليل عدد المعماريات لدعمها فقط حيث تتركز أغلب الأجهزة الحديثة على arm64-v8a و armeabi-v7a
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# Use a specific NDK version for compatibility
android.ndk = 21d

# Exclude unnecessary files from being included in the APK to reduce its size
android.include_exts = .so

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
# تقليل مستوى السجلات لتقليل حجم ملف السجل
log_level = 1

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# Specify extra arguments to python-for-android to optimize the build process
p4a.extra_args = --arch=armeabi-v7a --arch=arm64-v8a --requirements=python3,kivy,kivymd,pillow,opencv-python-headless,numpy,httpx,easyocr

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

#    --------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as an option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
# [app]
# source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
# [app:source.exclude_patterns]
# license
# data/audio/*.wav
# data/images/original/*
#

#    --------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
# [app@demo]
# title = My Application (demo)
#
# [app:source.exclude_patterns@demo]
# images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
# buildozer --profile demo android debug
