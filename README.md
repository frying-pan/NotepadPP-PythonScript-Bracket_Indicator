# Bracket_Indicator

PythonScript that highlights the bracket pair () [] {} + <> and/or the text between them,

at the active selection/cursor position, left-most pair in case of mismatch (Notepad++ CALLBACK)

Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)

using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7).


Features :
* highlight the bracket pair () [] {} + <> and/or the text between them containing the active selection/caret
* configurable indicator style (shape, background color, outline color)
* follow Scintilla bracket matching rule
* highlight can be de-activated/re-activated/reconfigured by re-rerunning the script
* for performance reasons : will only hightlight brackets if both are on screen (but possibly hidden/folded)
* glitch : when code is folded/unfolded bracket highlight will not update immediately if brackets get in/out of screen view


# Install :

This script can be run at Notepad++ startup (folders below are those of a local installation) : 

* copy the FP_BracketIndicator_Callback .py script file in :

C:\Users\[username]\AppData\Roaming\Notepad++\plugins\config\PythonScript\scripts

* add "import [FP_BracketIndicator_Callback (py) script file name without extension]"

to the startup.py file located, for me, under the Notepad++ install folder :

C:\Program Files\Notepad++\plugins\PythonScript\scripts

(I think I had to take ownership of startup.py before being able to write into it)


# Versions :

FP_BracketIndicator_Callback_v1_0.py
* requires the library FP__Lib_Edit.py included in the same folder

FP_BracketIndicator_Callback_v1_1.py
* significant performance update, especially for very long brackets in very long lines (1000's of characters long)
* added <> angle brackets highlight as an option

FP_BracketIndicator_Callback_v1_2.py
* removed dependancy to FP__Lib_Edit.py, FP_BracketIndicator_Callback is now a single file script
* added option : only highlight <> angle brackets when they are on the same line, to limit unwanted matchings
