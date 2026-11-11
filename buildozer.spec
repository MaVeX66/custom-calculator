[app]
title = Custom Calculator
package.name = customcalculator
package.domain = org.customcalc
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json
version = 1.0
requirements = python3,kivy,plyer,android
orientation = portrait
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 31
android.accept_sdk_license = True
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
