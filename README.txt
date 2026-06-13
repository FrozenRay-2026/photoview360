PhotoView360
============

A QGIS plugin that instantly opens a 360-degree panoramic image in your
browser by clicking a feature in a vector layer.
The viewer is powered by A-Frame (https://aframe.io/) and requires no
additional installation.

Plugin directory:
    C:/Users/katzc/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/photoview360


Requirements
------------
  - QGIS        : 3.0 or later
  - Python      : 3.x (bundled with QGIS)
  - Browser     : Chrome / Edge / Firefox (A-Frame compatible)
  - Image format: JPEG / PNG (equirectangular 360-degree images recommended)


Installation
------------
  1. Copy the photoview360 directory to your QGIS plugin folder:
       C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\

  2. Open QGIS and go to:
       Plugins -> Manage and Install Plugins

  3. Enable PhotoView360.


Usage
-----

  1. Open the dialog
     Click the PhotoView360 icon in the toolbar, or go to:
       Plugins -> PhotoView360 -> PhotoView360

  2. Configure the layer and path
     Select a vector layer containing photo locations in "Photo Layer".
     Then choose how to specify the image path:

     Mode 1 - Full path via attribute field:
       Select a field that stores the absolute path to the image
       (e.g. C:\photos\IMG_001.jpg).

     Mode 2 - Filename via attribute field:
       Select a field that stores the filename (e.g. IMG_001.jpg)
       and specify the image folder separately.
       Check "Include subfolders" to search recursively.

  3. Select a location and open the viewer
     - Click "Select photo location" to activate the tool
       (the button will appear pressed).
     - Click a feature on the map -- the browser opens automatically
       with the 360-degree viewer.
     - The selected feature is highlighted in red on the map.


Viewer Controls
---------------
  Drag          : Rotate view
  Mouse wheel   : Zoom in / out (follows cursor direction)


Language Toggle
---------------
  Click the "English / Japanese" button at the top-right of the dialog
  to switch the UI language instantly.


How It Works
------------
  - Feature clicks are detected via QgsMapToolIdentify.
  - A local HTTP server (Python standard library) is started for the
    image folder and serves images via localhost.
  - The image is rendered as a sphere using A-Frame's <a-sky> component.
  - The server is reused as long as the folder remains the same;
    the port is assigned automatically by the OS.


File Structure
--------------
  photoview360/
  +-- __init__.py
  +-- photoview360.py            Main plugin logic
  +-- photoview360_dialog.py     Dialog UI (built entirely in code)
  +-- resources.py               Compiled resources
  +-- icon.png                   Toolbar icon
  +-- metadata.txt               Plugin metadata
  +-- README.html                This document (HTML version)
  +-- README.txt                 This document (plain text)


Changelog
---------
  0.2 - Added filename mode with folder browser and subfolder search
      - Added JP/EN language toggle in dialog
      - Auto-deactivate select tool on mode switch
      - Improved dialog layout with resize support
  0.1 - Initial release


Author & License
----------------
  Author : Rei Ito <katzchen.th@gmail.com>
  License: GNU GPL v2 or later

  For more information on PyQGIS development, see:
  http://www.qgis.org/pyqgis-cookbook/index.html
