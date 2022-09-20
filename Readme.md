# BeatEditor for BoxVR

Tool to edit beat data(JSON file) for Training Mode(Custom song import function) in [BoxVR(Steam Version)](https://store.steampowered.com/app/641960/BOXVR/).

## Notice 

I wrote this tool for (only) me. If you can edit track data with this tool, you should think you are lucky. 

This tool and I don't promise it is useful for you.

You can only use this tool at your own risk.

## Description

This tool can:

* Edit beat data in a track data file(JSON) for Training mode in BoxVR.
	* change beat action(punch/duck/dodge) in any time zone.
	* change beat timing.

## Demo

T.B.D.

I will upload a demo movie to youtube soon.

## VS.

As far as I know, There isn't any tool that is competitive to this in OSS.

## Installation

You can choose two installation methods depending on your environment.

### 1. Stand-alone executable(Recommend)

1. Download a zip file in Releases.
2. Unzip the zip file.
3. Execute BeatEditor.exe.

### 2. Python script

If you choose this method, You must prepare a python3 environment on your PC.

1. Clone this repository to your local PC.
2. Run this command if libraries that this tool depends on didn't install in your python environment.
```
pip install -r requirements.txt
```
3. Run beatEditor.py
```
python beatEditor.py
```

## Usage

Check [manual page](doc/manual.md).

## Support 

No support.

However, you can open an issue to share your problem. If you do so, It is beneficial to share information that can use in analysis problems for the author(me) and other users.

For example, your environment, detailed situation problem occurred, original/edit track data and music relates a track data.

## dependency

This tool depends on this software. Thanks to the authors and contributors.

* [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
