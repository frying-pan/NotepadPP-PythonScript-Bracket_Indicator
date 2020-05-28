# Inspired from brackethighlighter (especially callback events)
# https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/
# https://notepad-plus-plus.org/community/topic/14501/has-a-plugin-like-sublime-plugin-brackethighlighter/

# PythonScript that highlights the bracket pair () [] {} (and possibly the text inside)
# containing the active selection/caret, left-most pair in case of mismatch (Notepad++ CALLBACK)

# Tested with Notepad++ 7.8.2 64 bits, with PythonScript plugin 1.5.2
# on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)
# /!\ this file uses TABS for indent /!\ (better read as 4 chars wide tabs)

# (i) limitation : for performance reasons, only highlights bracket pairs which are both visible (on screen),
# however line wrapping will cause highlight to occur when a bracket is off-screen but on a partially visible document line

# re-run the script to de-activate/re-activate the whole callback (re-running the script will also apply new *options values*)
# change the *options values* (just below) to choose the style of bracket highlighting when the callback is active

# *options values* *********************************************************************************
s_option_style			= "FULLBOX"		# STRING								: box/underline/text style (allowed values : see below)
t_option_rgb_color		= (255, 0, 255)	# INTEGER TRIPLET (0-255, 0-255, 0-255)	: (Red, Green, Blue) RGB color
i_option_alpha			= 24			# INTEGER 0-255							: box background coloring intensity (0 is transparent, 255 is opaque)
i_option_outline_alpha	= 48			# INTEGER 0-255							: box outline coloring intensity (0 is transparent, 255 is opaque)
i_option_get_content	= 1 # set to INTEGER 1 to enable option : also highlight content of bracket, otherwise only the () [] {}
i_option_toggle_msgbox	= 0 # set to INTEGER 1 to enable option : show a message box when toggling the callback (console messages always occur)

# allowed STRING s_option_style values :
	# box			: "BOX", "STRAIGHTBOX", "FULLBOX", "ROUNDBOX", "DOTBOX"
	# under line	: "PLAIN", "COMPOSITIONTHIN", "COMPOSITIONTHICK"
	# under wavy	: "SQUIGGLE", "SQUIGGLELOW", "SQUIGGLEPIXMAP"
	# under broken	: "DASH", "DOTS", "DIAGONAL", "TT"
	# middle line	: "STRIKE"
	# text color	: "TEXTFORE"
	# no highlight	: "HIDDEN"
	# start point	: "POINT", "POINTCHARACTER"
	# gradient		: "GRADIENT", "GRADIENTCENTRE"
	# reserved		: "CONTAINER", "IME", "IME_MAX", "MAX"

# script declarations ******************************************************************************
from Npp import *

s_script_name	= "Bracket Indicator"
s_callback_name	= "Indicator Callback"

s_controleditscript	= "(hold CTRL while starting the script to edit its options in Notepad++)"
s_reruntogglecb		= "Re-run the script to toggle the whole callback"
s_willapplynewopt	= "This will also apply new *options values* saved in the script file"
s_nofreeindicator	= "no free indicator number for bracket highlighting could be found"

s_editorprop_prefix		= "BRACKETINDICATORCB_"
s_editorprop_cb_reg		= s_editorprop_prefix + "CB_REGISTERED"
s_editorprop_cb_on		= s_editorprop_prefix + "CB_ON"
s_editorprop_indic_num	= s_editorprop_prefix + "INDIC_NUM"

t_option_key = ("S_STYLE", "COL_R", "COL_G", "COL_B", "ALPHA", "OUTALPHA", "CONTENT", "TOGMBOX")
t_option_value = (
	s_option_style.upper(), t_option_rgb_color[0], t_option_rgb_color[1], t_option_rgb_color[2], \
	i_option_alpha, i_option_outline_alpha, i_option_get_content, i_option_toggle_msgbox)
t_option_initdes = ("Box style", "Red", "Green", "Blue", "Alpha", "Ouline alpha", "Bracket content", "Toggle message box")

i_true	= 1
i_false	= 0

dic_styles = {
	"BOX"				: INDICATORSTYLE.BOX,
	"STRAIGHTBOX"		: INDICATORSTYLE.STRAIGHTBOX,
	"FULLBOX"			: INDICATORSTYLE.FULLBOX,
	"ROUNDBOX"			: INDICATORSTYLE.ROUNDBOX,
	"DOTBOX"			: INDICATORSTYLE.DOTBOX,
	"PLAIN"				: INDICATORSTYLE.PLAIN,
	"COMPOSITIONTHIN"	: INDICATORSTYLE.COMPOSITIONTHIN,
	"COMPOSITIONTHICK"	: INDICATORSTYLE.COMPOSITIONTHICK,
	"SQUIGGLE"			: INDICATORSTYLE.SQUIGGLE,
	"SQUIGGLELOW"		: INDICATORSTYLE.SQUIGGLELOW,
	"SQUIGGLEPIXMAP"	: INDICATORSTYLE.SQUIGGLEPIXMAP,
	"DASH"				: INDICATORSTYLE.DASH,
	"DOTS"				: INDICATORSTYLE.DOTS,
	"DIAGONAL"			: INDICATORSTYLE.DIAGONAL,
	"TT"				: INDICATORSTYLE.TT,
	"STRIKE"			: INDICATORSTYLE.STRIKE,
	"TEXTFORE"			: INDICATORSTYLE.TEXTFORE,
	"HIDDEN"			: INDICATORSTYLE.HIDDEN,
	"POINT"				: INDICATORSTYLE.POINT,
	"POINTCHARACTER"	: INDICATORSTYLE.POINTCHARACTER,
	"GRADIENT"			: INDICATORSTYLE.GRADIENT,
	"GRADIENTCENTRE"	: INDICATORSTYLE.GRADIENTCENTRE,
	"CONTAINER"			: INDICATORSTYLE.CONTAINER,
	"IME"				: INDICATORSTYLE.IME,
	"IME_MAX"			: INDICATORSTYLE.IME_MAX,
	"MAX"				: INDICATORSTYLE.MAX}

class C_BracketIndicator_CB():
	# class constructor
	def __init__(self, dic_styles, i_option_on, s_editorprop_cb_on, dic_editorprop):
		from Perso__Lib_Edit import C_Find_OutRange
		self.o_find_outrange = C_Find_OutRange()

		self.INVALID_POSITION = -1

		self.cb_done			= False
		self.lastmodtype_hack	= None
		self.dic_styles	= dic_styles
		self.option_on	= i_option_on
		self.editorprop_cb_on		= s_editorprop_cb_on
		self.editorprop_s_style		= dic_editorprop["S_STYLE"]
		self.editorprop_col_red		= dic_editorprop["COL_R"]
		self.editorprop_col_green	= dic_editorprop["COL_G"]
		self.editorprop_col_blue	= dic_editorprop["COL_B"]
		self.editorprop_alpha		= dic_editorprop["ALPHA"]
		self.editorprop_outalpha	= dic_editorprop["OUTALPHA"]
		self.editorprop_content_on	= dic_editorprop["CONTENT"]

	def ClearAllHighlighting(self, i_indicator_number):
		for curedit in (editor, editor1, editor2):
			curedit.setIndicatorCurrent(i_indicator_number)
			curedit.indicatorClearRange(0, curedit.getTextLength())

	def SetIndicatorOptions(self, i_indicator_number):
		def SetOneEditorIndicatorOptions( \
				i_indicator_number, indicator_style, rgb_color_tup, alpha, outline_alpha, draw_under_text, curedit):
			curedit.indicSetStyle			(i_indicator_number, indicator_style)	# INDICATORSTYLE
			curedit.indicSetFore			(i_indicator_number, rgb_color_tup)		# (r,g,b) integers tuple
			curedit.indicSetAlpha			(i_indicator_number, alpha)				# integer
			curedit.indicSetOutlineAlpha	(i_indicator_number, outline_alpha)		# integer
			curedit.indicSetUnder			(i_indicator_number, draw_under_text)	# boolean

		for curedit in (editor, editor1, editor2):
			# 'style', 'RGB color', 'background alpha', 'outline alpha' options
			try:
				indicator_style	= self.dic_styles[console.editor.getProperty(self.editorprop_s_style)]
				t_rgb_color		= ( \
					int(console.editor.getProperty(self.editorprop_col_red)), \
					int(console.editor.getProperty(self.editorprop_col_green)), \
					int(console.editor.getProperty(self.editorprop_col_blue)))
				i_alpha			= int(console.editor.getProperty(self.editorprop_alpha))
				i_outalpha		= int(console.editor.getProperty(self.editorprop_outalpha))
			except:
				# default to transparent box rimmed in "pale violet red 2"
				SetOneEditorIndicatorOptions( \
					i_indicator_number, INDICATORSTYLE.STRAIGHTBOX, (238, 121, 159), 0, 255, True, curedit)
			else:
				# 'style', 'RGB color', 'background alpha', 'outline alpha' options
				SetOneEditorIndicatorOptions( \
					i_indicator_number, indicator_style, t_rgb_color, i_alpha, i_outalpha, True, curedit)

	def RegCallback(self):
		# our 2 CallBack functions
		def CBS_BracketInd_UpdateUI(args):
			if console.editor.getProperty(self.editorprop_cb_on) != str(self.option_on):
				return

			# hack, look for "16400" [== (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER)] in code :
			# https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/28
			if ( \
					args['updated'] == UPDATE.CONTENT and \
					self.lastmodtype_hack == (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER)):
				return

			editor.setIndicatorCurrent(self.indicator_number)
			editor.indicatorClearRange(0, editor.getTextLength())

			i_vis_line_first = editor.getFirstVisibleLine()
			i_vis_line_last = i_vis_line_first + editor.linesOnScreen() - 1
			i_min = editor.positionFromLine(editor.docLineFromVisible(i_vis_line_first))
			i_max = editor.positionFromLine(editor.docLineFromVisible(i_vis_line_last) + 1)
			if i_min == self.INVALID_POSITION: i_min = 0
			if i_max == self.INVALID_POSITION: i_max = editor.getTextLength()

			i_sel_start	= editor.getSelectionStart()
			i_sel_end	= editor.getSelectionEnd()

			t_brackets = self.o_find_outrange.RE_MatchingBrackets_OutRange_InRange( \
													editor, i_sel_start, i_sel_end, i_min, i_max)
			if not(t_brackets is None):
				i_pos_open	= t_brackets[0]
				i_pos_close	= t_brackets[1]
				# 'highlight bracket content' option
				if console.editor.getProperty(self.editorprop_content_on) == str(self.option_on):
					editor.indicatorFillRange(i_pos_open, i_pos_close - i_pos_open + 1)
				else:
					editor.indicatorFillRange(i_pos_open, 1)
					editor.indicatorFillRange(i_pos_close, 1)

		def CB_BracketInd_Modified(args):
			self.lastmodtype_hack = args['modificationType']
		# end of 2 callbacks

		if self.cb_done:
			return None

		# try to pick an unused indicator number : from INDICATORNUMBERS.CONTAINER(8) to (INDICATORNUMBERS.IME - 1)(31)
		# skip the first 2 of them, just in case they are used but their flags/styles/colors are still 0
		self.indicator_number = None
		for i in range(INDICATORNUMBERS.CONTAINER + 2, INDICATORNUMBERS.IME):
			# indicators flag and styles seems to default to 0 before being set, so this one could be unused
			if (editor.indicGetFlags(i) == 0 and editor.indicGetStyle(i) == 0 and editor.indicGetHoverStyle(i) == 0):
				# indicators fore colors seems to default to black (0, 0, 0) before being set, so (hopefully) this one is really unused
				if (editor.indicGetFore(i) == (0, 0, 0) and editor.indicGetHoverFore(i) == (0, 0, 0)):
					self.indicator_number = i
					break
		if (self.indicator_number is None):
			return None

		self.SetIndicatorOptions(self.indicator_number)

		# install callback 1 (Sync avoid flicker when scrolling)
		editor.callbackSync(CBS_BracketInd_UpdateUI, [SCINTILLANOTIFICATION.UPDATEUI])
		# install callback 2 (avoid constant UPDATEUI when a doc is cloned)
		editor.callbackSync(CB_BracketInd_Modified, [SCINTILLANOTIFICATION.MODIFIED])

		self.cb_done = True
		return self.indicator_number
# end of class

# Main() code **************************************************************************************
def Main():
	print "[" + s_script_name + " starts] " + s_controleditscript

	s_opt_info = ""
	dic_editorprop = {}
	for i in range(0, len(t_option_key)):
		console.editor.setProperty(s_editorprop_prefix + t_option_key[i], str(t_option_value[i]))
		v_opt_value = t_option_value[i]
		v_opt_value = (chr(34) + v_opt_value + chr(34)) if (type(v_opt_value) == type("")) else str(v_opt_value)
		s_opt_info = s_opt_info + t_option_initdes[i] + "=" + v_opt_value + ", "
		dic_editorprop[t_option_key[i]] = s_editorprop_prefix + t_option_key[i]
	s_opt_info = s_opt_info[:-2]

	# create an instance of the callback class, and populate object properties with script and Console variables
	o_bracketindicator_cb = C_BracketIndicator_CB(dic_styles, i_true, s_editorprop_cb_on, dic_editorprop)

	if console.editor.getProperty(s_editorprop_cb_reg) != str(i_true):
		# register the callbacks on SCINTILLANOTIFICATION.UPDATEUI and SCINTILLANOTIFICATION.MODIFIED
		i_indicator_number = o_bracketindicator_cb.RegCallback()

		if i_indicator_number is None:
			console.writeError("\t" + s_callback_name + " registering FAILED /!\\ [" + s_nofreeindicator + "]" + "\n")
			console.show()
			notepad.messageBox(s_callback_name + " registering FAILED /!\\" + "\n\n" + s_nofreeindicator, \
				s_script_name, MESSAGEBOXFLAGS.ICONSTOP)
		else:
			console.editor.setProperty(s_editorprop_cb_reg, str(i_true))
			console.editor.setProperty(s_editorprop_cb_on, str(i_true))
			console.editor.setProperty(s_editorprop_indic_num, str(i_indicator_number))

			editor.setSelectionMode(editor.getSelectionMode())	# force manual UPDATEUI to happen
			print \
				"\t" + s_callback_name + " registered and activated [indicator number=" + str(i_indicator_number) + "]" + \
				" (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
			print "\t" + s_opt_info
		return

	if console.editor.getProperty(s_editorprop_cb_on) != str(i_true):
		console.editor.setProperty(s_editorprop_cb_on, str(i_true))

		o_bracketindicator_cb.SetIndicatorOptions(int(console.editor.getProperty(s_editorprop_indic_num)))
		editor.setSelectionMode(editor.getSelectionMode())	# force manual UPDATEUI to happen
		print "\t" + s_callback_name + " re-activated (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_callback_name + " re-activated" + "\n\n" + \
				s_reruntogglecb + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_cb_on, str(i_false))

		o_bracketindicator_cb.ClearAllHighlighting(int(console.editor.getProperty(s_editorprop_indic_num)))
		print "\t" + s_callback_name + " DE-ACTIVATED /!\\ (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_callback_name + " DE-ACTIVATED /!\\" + "\n\n" + \
				s_reruntogglecb + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

Main()
