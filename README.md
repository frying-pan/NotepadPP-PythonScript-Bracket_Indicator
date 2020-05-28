# Bracket_Indicator

PythonScript that highlights the bracket pair () [] {} (and possibly the text inside) containing the active selection/caret

in Notepad++ when the script is run from Notepad++ (with PythonScript plugin installed)

Tested with Notepad++ 7.8.2 64 bits, with PythonScript plugin 1.5.2,

on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)


Features :
  * highlight the pair () [] {} (and possibly the text inside) containing the active selection/caret
  * customizable highlight box style, color, background and outline color 


# Install :

This script can be run at Notepad++ startup (folders below are those of a local installation) : 

* copy the Perso_BracketIndicator_Callback .py script file in :

C:\Users\[username]\AppData\Roaming\Notepad++\plugins\config\PythonScript\scripts

* add "import [Perso_BracketIndicator_Callback (py) script file name without extension]"

to the startup.py file located, for me, under the Notepad++ install folder :

C:\Program Files\Notepad++\plugins\PythonScript\scripts

(I think I had to take ownership of startup.py before being able to write into it)


# Versions :

Perso_BracketIndicator_Callback_v1_0.py
