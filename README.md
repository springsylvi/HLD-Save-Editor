# HLD Save Editor
A tool for editing save files for Hyper Light Drifter.
## Usage
Compatible with any version of Python 3. Invoke with `python edit.py [save_num]` to open a save file (specify python3 on Mac). Typing `help` will list all available commands. The fields used in save files are described in `save_format.txt`.
## Config
Configuration options are available through modifying `config.ini`. All options should be under the section `[main]`. The following options are available:

path:  
   	The path to the folder containing the game's save files. This option is required.
    By default, this is
    `/Users/[username]/Library/Application Support/com.HeartMachine.HyperLightDrifter`
    on Mac and `C:\Users\[username]\AppData\Local\HyperLightDrifter` on Windows. 

macros:  
    Not yet implemented.
