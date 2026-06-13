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

# PhotoView360

ベクタレイヤ上のフィーチャをクリックするだけで、
360度パノラマ画像をWebブラウザで瞬時に表示できるQGISプラグインです。

ビューアには **A-Frame** を使用しており、
追加ソフトウェアのインストールは必要ありません。

---

## 動作環境

- QGIS : 3.0以降
- Python : 3.x（QGISに同梱）
- ブラウザ : Chrome / Edge / Firefox（A-Frame対応）
- 画像形式 : JPEG / PNG（正距円筒図法の360度画像を推奨）

---

## インストール

1. `photoview360` フォルダをQGISのプラグインフォルダへコピーします。

```
C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

2. QGISを起動します。

```
プラグイン
  ↓
プラグインの管理とインストール
```

3. PhotoView360 を有効にします。

---

## 使用方法

### 1. ダイアログを開く

ツールバーの PhotoView360 アイコンをクリックするか、

```
プラグイン
  ↓
PhotoView360
  ↓
PhotoView360
```

を選択します。

---

### 2. レイヤと画像パスを設定する

「Photo Layer」で写真の撮影地点を格納したベクタレイヤを選択します。

画像パスの指定方法は2種類あります。

#### モード1：属性フィールドでフルパスを指定

画像の絶対パスを格納したフィールドを選択します。

例：

```
C:\photos\IMG_001.jpg
```

#### モード2：属性フィールドでファイル名を指定

画像ファイル名を格納したフィールドを選択します。

例：

```
IMG_001.jpg
```

画像フォルダを別途指定します。

「サブフォルダを含む」をチェックすると、
サブフォルダも再帰的に検索します。

---

### 3. 撮影地点を選択する

- 「撮影地点を選択」をクリックして有効化します。
- 地図上のフィーチャをクリックすると、
  ブラウザが自動的に起動して360度ビューアを表示します。
- 選択したフィーチャは赤色でハイライト表示されます。

---

## ビューア操作

|操作|機能|
|---|---|
|ドラッグ|視点を回転|
|マウスホイール|ズームイン／ズームアウト|

---

## 言語切替

ダイアログ右上の

**English / 日本語**

ボタンで表示言語を即座に切り替えられます。

---

## 動作の仕組み

- QgsMapToolIdentify によるフィーチャ選択
- Python標準ライブラリでローカルHTTPサーバを起動
- localhost経由で画像を配信
- A-Frame の `<a-sky>` コンポーネントで球面表示
- 同じフォルダならサーバを再利用
- ポート番号はOSが自動割り当て

---

## ファイル構成

```
photoview360/
├── __init__.py
├── photoview360.py
├── photoview360_dialog.py
├── resources.py
├── icon.png
├── metadata.txt
├── README.html
└── README.txt
```

---

## 更新履歴

### Version 0.2

- ファイル名指定モードを追加
- フォルダ選択機能を追加
- サブフォルダ検索機能を追加
- 日本語／英語切替を追加
- モード切替時の自動解除
- ダイアログのリサイズ対応

### Version 0.1

- 初回リリース

---

## 作者

Rei Ito

---

## ライセンス

GNU GPL v2 以降


