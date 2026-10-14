[app]

# (str) Title of your application
title = Attendance System

# (str) Package name
package.name = attendancesystem

# (str) Package domain (needed for android packaging)
package.domain = org.attendance

# (str) Source files to include
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js,db,json

# (list) Application requirements
requirements = python3,flask,sqlite3,jinja2,werkzeug,click,itsdangerous

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android arch to build for
android.archs = arm64-v8a

p4a.branch = master
