#!/bin/bash
APP_NAME="Quakler.app"
mkdir -p "$APP_NAME/Contents/MacOS"
mkdir -p "$APP_NAME/Contents/Resources"
cp VideoToolbox.py "$APP_NAME/Contents/Resources/"
cp LICENSE "$APP_NAME/Contents/Resources/LICENSE.txt"
clang -O3 -o "$APP_NAME/Contents/MacOS/applet" applet.c
cat << 'PLIST' > "$APP_NAME/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>applet</string>
    <key>CFBundleIdentifier</key>
    <string>com.peneloperose.quakler</string>
    <key>CFBundleName</key>
    <string>Quakler</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2026 Penelope Rose. All rights reserved.</string>
</dict>
</plist>
PLIST
echo "Quakler built successfully!"
