# Bracket_Indicator

PythonScript that highlights the bracket pair () [] {} + optional <>, and/or the content between them,

around the caret or the active selection, left-most pair in case of mismatch (Notepad++ CALLBACK)

Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)

using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7).


Features :
* highlight the bracket pair () [] {} + optional <> and/or the text between them containing the caret/active selection
* 2 configurable indicators style for the brackets and their content (shape, background color, outline color)
* follow Scintilla bracket matching rule (brackets must be of the same style)
* highlight can be de-activated/re-activated/reconfigured by re-rerunning the script
* performance : default options will limit highlight to a limited range around the caret/middle of active selection


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
* removed dependency to FP__Lib_Edit.py, FP_BracketIndicator_Callback is now a single file script
* added option : only highlight <> angle brackets when they are on the same line, to limit unwanted matches

FP_BracketIndicator_Callback_v1_3.py
* performance : changed the range of bracket search around the caret to a maximum of characters and document lines
* performance : replaced the built-in braceMatch() function by a custom search function that accepts a limited range of search

FP_BracketIndicator_Callback_v1_4.py
* minor esthetic and performance update

FP_BracketIndicator_Callback_v1_5.py
* added option : use 2 different highlights for the brackets and their content
* bug fix : some issues in highlights clearing/updating
