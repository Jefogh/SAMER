name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      # Use caching to speed up builds
      - name: Get Date
        id: get-date
        run: |
          echo "::set-output name=date::$(/bin/date -u "+%Y%m%d")"
        shell: bash

      - name: Cache Buildozer global directory
        uses: actions/cache@v2
        with:
          path: .buildozer_global
          key: buildozer-global-${{ hashFiles('buildozer.spec') }}

      - uses: actions/cache@v2
        with:
          path: .buildozer
          key: ${{ runner.os }}-${{ steps.get-date.outputs.date }}-${{ hashFiles('buildozer.spec') }}

      # Install dependencies
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt-get install -y \
            build-essential \
            git \
            ffmpeg \
            libsdl2-dev \
            libsdl2-image-dev \
            libsdl2-mixer-dev \
            libsdl2-ttf-dev \
            libportmidi-dev \
            libswscale-dev \
            libavformat-dev \
            libavcodec-dev \
            libunwind-dev \
            zlib1g-dev \
            libopencv-dev \
            libtesseract-dev \
            libleptonica-dev \
            tesseract-ocr \
            zlib1g-dev \
            openssl \
            libgdbm-dev \
            libgdbm-compat-dev \
            liblzma-dev \
            libreadline-dev \
            uuid-dev \
            libgstreamer1.0 \
            gstreamer1.0-plugins-base \
            gstreamer1.0-plugins-good
          sudo apt-get install -y \
            zip \
            unzip \
            autoconf \
            libtool \
            pkg-config \
            libncurses5-dev \
            libncursesw5-dev \
            libtinfo5 \
            cmake \
            libffi-dev \
            libssl-dev \
            automake

      # Set up Java 17 required by Gradle
      - name: Setup Java 17 required by Gradle
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '17'

      # Set up Python
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      # Install pip dependencies
      - name: Install pip dependencies
        run: |
          pip install --upgrade pip
          pip install buildozer cython==0.29.33
          pip install opencv-python-headless numpy httpx tensorflow keras-ocr

      # Clean previous builds to avoid conflicts
      - name: Clean previous builds
        run: buildozer android clean

      # Build with Buildozer and save logs
      - name: Build with Buildozer
        run: |
          yes | buildozer -v android debug 2>&1 | tee build.log

      # Upload the APK artifact
      - name: Upload APK artifact
        uses: actions/upload-artifact@v2
        with:
          name: APK
          path: bin/*.apk

      # Upload Build Log if the build fails
      - name: Upload Build Log
        if: failure()
        uses: actions/upload-artifact@v2
        with:
          name: build-log
          path: build.log
