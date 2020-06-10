# Inspired from brackethighlighter (especially callback events)
# https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/
# https://notepad-plus-plus.org/community/topic/14501/has-a-plugin-like-sublime-plugin-brackethighlighter/

# PythonScript that highlights the bracket pair () [] {} + <> and/or the text between them,
# at the active selection/cursor position, left-most pair in case of mismatch (Notepad++ CALLBACK)

# Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)
# using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7)
# /!\ this file uses TABS for indent /!\ (better read as 4 chars wide tabs)

# (i) limitation : for performance reasons, this script will only highlight a bracket pair if both are on a (partly) visible line
# (i) bracket matching : as for Scintilla this script does NOT care about folding level and folded state for bracket matching
# (i) i_option_limit_highlight=1 : (ADVISED) for files with very long brackets (10000 characters and more) in very long lines,
# this option will highlight no more than a few 1000's characters around the active cursor, saving CPU and app responsiveness

# re-run the script to de-activate/re-activate the whole callback (re-running the script will also apply new *options values*)
# change the *options values* (just below) to choose the style of bracket highlighting when the callback is active

# *options values* *********************************************************************************
# highlight style
s_option_style			= "FULLBOX"		# STRING								: box/underline/text style (allowed values : see below)
t_option_rgb_color		= (255, 0, 0)	# INTEGER TRIPLET (0-255, 0-255, 0-255)	: (Red, Green, Blue) RGB color
i_option_alpha			= 32			# INTEGER 0-255							: box background color intensity (0 : transparent, 255 : opaque)
i_option_outline_alpha	= 48			# INTEGER 0-255							: box outline color intensity (0 : transparent, 255 : opaque)
# AT LEAST 1 of the 2 following options ('highlight brackets' or 'highlight content') must be enabled for highlighting to occur !
i_option_highlight_brackets	= 1	# set to INTEGER 1 to enable option : highlight the brackets () [] {} + <>
i_option_highlight_content	= 1	# set to INTEGER 1 to enable option : AND/OR highlight the text content between the brackets
# miscellaneous options
i_option_limit_highlight	= 1	# set to INTEGER 1 to enable option : (ADVISED) limit content highlighting to a few 1000's chars around cursor
i_option_highlight_angle	= 1	# set to INTEGER 1 to enable option : also highlight <> angle brackets (in addition to () [] {})
i_option_single_line_angle	= 1	# set to INTEGER 1 to enable option : only highlight <> angle brackets when both are on the same line
i_option_toggle_msgbox		= 0	# set to INTEGER 1 to enable option : show a message box when toggling the callback (console messages always occur)

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

i_true	= 1
i_false	= 0

t_option_key = ("S_STYLE", "COL_RGB", "ALPHA", "OUTALPHA", "BRACKETS", "CONTENT", "LIMIT_HL", \
	"ANGLE", "SL_ANGLE", "TOGMBOX")
t_option_value = ( \
	s_option_style.upper(), t_option_rgb_color, i_option_alpha, i_option_outline_alpha, \
	i_option_highlight_brackets, i_option_highlight_content, i_option_limit_highlight, \
	i_option_highlight_angle, i_option_single_line_angle, i_option_toggle_msgbox)
t_option_initdes = ( \
	"Box style", "(Red,Green,Blue)", "Alpha", "Ouline alpha", \
	"Brackets", "Content", "Limit Highlight", "<> Brackets", "Single Line <>", "Toggle message box")

dic_styles = { \
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
	def __init__(self, s_script_name, dic_styles, i_option_on, s_editorprop_cb_on, dic_editorprop):
		import re
		self.re = re

		# class const
		self.INVALID_POSITION = -1 # Scintilla character position constant
		self.max_vis_col = 200 # supposed max visible columns ('limit highlight' option)
		# script params
		self.script_name	= s_script_name
		self.dic_styles		= dic_styles
		self.option_on		= i_option_on
		self.editorprop_cb_on		= s_editorprop_cb_on
		self.editorprop_s_style		= dic_editorprop["S_STYLE"]
		self.editorprop_col_rgb		= dic_editorprop["COL_RGB"]
		self.editorprop_alpha		= dic_editorprop["ALPHA"]
		self.editorprop_outalpha	= dic_editorprop["OUTALPHA"]
		self.editorprop_brackets_on	= dic_editorprop["BRACKETS"]
		self.editorprop_content_on	= dic_editorprop["CONTENT"]
		self.editorprop_limit_hl_on	= dic_editorprop["LIMIT_HL"]
		self.editorprop_angle_on	= dic_editorprop["ANGLE"]
		self.editorprop_sl_angle_on	= dic_editorprop["SL_ANGLE"]
		# instance state datas
		self.cb_done			= False
		self.lastmodtype_hack	= None
		self.last_buffid		= notepad.getCurrentBufferID()
		self.had_range			= False

	def Ugly_ClearAllBuffersHighlights(self, i_indicator_number):
		i_act_bufferid = notepad.getCurrentBufferID()
		lst_files_infos = notepad.getFiles()
		for t_file_infos in lst_files_infos:
			notepad.activateBufferID(t_file_infos[1])
			curedit = editor
			curedit.setIndicatorCurrent(i_indicator_number)
			curedit.indicatorClearRange(0, curedit.getTextLength())
		notepad.activateBufferID(i_act_bufferid)

	def Ugly_ForceUpdateUI(self):
		i_act_bufferid = notepad.getCurrentBufferID()
		notepad.new()	
		notepad.close()
		notepad.activateBufferID(i_act_bufferid)

	def SetIndicatorOptions(self, i_indicator_number):
		def SetOneEditorIndicatorOptions( \
				i_indicator_number, indicator_style, rgb_color_tup, alpha, outline_alpha, draw_under_text, curedit):
			curedit.indicSetStyle			(i_indicator_number, indicator_style)	# INDICATORSTYLE
			curedit.indicSetFore			(i_indicator_number, rgb_color_tup)		# (r,g,b) integers tuple
			curedit.indicSetAlpha			(i_indicator_number, alpha)				# integer
			curedit.indicSetOutlineAlpha	(i_indicator_number, outline_alpha)		# integer
			curedit.indicSetUnder			(i_indicator_number, draw_under_text)	# boolean
		def IsRGBTuple(t_rgb_color):
			if type(t_rgb_color) != type(()):return False
			if len(t_rgb_color) != 3:return False
			i_red = t_rgb_color[0]; i_green = t_rgb_color[1]; i_blue = t_rgb_color[2]
			if (type(i_red) != type(0) or type(i_green) != type(0) or type(i_blue) != type(0)):return False
			if i_red	< 0 or i_red	> 255:return False
			if i_green	< 0 or i_green	> 255:return False
			if i_blue	< 0 or i_blue	> 255:return False
			return True
		def IsUByteInteger(t_ubyte_int):
			if (t_ubyte_int < 0 or t_ubyte_int > 255):return False
			return True

		# 'style', 'RGB color', 'background alpha', 'outline alpha' options
		b_has_error= False
		try:
			indicator_style	= self.dic_styles[console.editor.getProperty(self.editorprop_s_style)]
			t_rgb_color		= eval(console.editor.getProperty(self.editorprop_col_rgb))
			i_alpha			= int(console.editor.getProperty(self.editorprop_alpha))
			i_outalpha		= int(console.editor.getProperty(self.editorprop_outalpha))
		except:
			b_has_error= True
		if not(IsRGBTuple(t_rgb_color)):
			b_has_error= True
		if (not(IsUByteInteger(i_alpha)) or not(IsUByteInteger(i_outalpha))):
			b_has_error= True
		if b_has_error:
			s_error_msg = "/!\\ User options error, check your highlight style options values..."
			print "\t" + s_error_msg
			notepad.messageBox(s_error_msg, self.script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

		for curedit in (editor, editor1, editor2):
			if b_has_error:
				SetOneEditorIndicatorOptions( \
					i_indicator_number, self.dic_styles["HIDDEN"], (0, 0, 0), 0, 0, True, curedit)
			else:
				SetOneEditorIndicatorOptions( \
					i_indicator_number, indicator_style, t_rgb_color, i_alpha, i_outalpha, True, curedit)

	def RegCallback(self):
		# our CallBack functions
		def CBS_BracketInd_Modified(args):
			self.lastmodtype_hack = args['modificationType']
		def CBS_BracketInd_UpdateUI(args):
			# hack, look for "16400" [== (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER)] in code :
			# https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/28
			if ( \
					args['updated'] == UPDATE.CONTENT and \
					self.lastmodtype_hack == (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER)):
				return
			CheckBrackets()
		def CB_BracketInd_BufferActivated(args):
			CheckBrackets()

		def CheckBrackets():
			def MatchingBrackets_OutRange_InRange(curedit, i_start, i_end, i_min, i_max, b_angle, b_sl_angle):
				if (i_start <= i_min or i_end >= i_max):
					return None

				pattern_newline = self.re.compile("[\r\n]")
				s_pattern_close_brackets = "\)\]\}"
				if b_angle: s_pattern_close_brackets = s_pattern_close_brackets + "\>"
				s_pattern_close_brackets = "[" + s_pattern_close_brackets + "]"
				pattern_close_brackets = self.re.compile(s_pattern_close_brackets)

				i_chunk = 256

				i_left	= None
				i_right	= None
				i_offset = 0
				while True:
					s_text = curedit.getTextRange(i_end + i_offset, min(i_end + i_offset + i_chunk, i_max))
					for o_match in pattern_close_brackets.finditer(s_text):
						i_pos_close	= i_end + i_offset + o_match.start()
						i_pos_open	= curedit.braceMatch(i_pos_close, 0)
						if (i_pos_open != self.INVALID_POSITION and i_pos_open < i_start and i_pos_open >= i_min):
							b_ignore = False
							if (b_angle and b_sl_angle):
								if o_match.group(0) == ">":
									s_single_line = curedit.getTextRange(i_pos_open + 1, i_pos_close)
									if not(pattern_newline.search(s_single_line) is None):
										b_ignore = True
							if not(b_ignore):
								i_left	= i_pos_open
								i_right	= i_pos_close
								break
					if (not(i_left is None) and not(i_right is None)): break

					i_offset = i_offset + i_chunk
					if i_end + i_offset >= i_max: break
					i_chunk = i_chunk * 2
				if ((i_left is None) or (i_right is None)):
					return None
				return (i_left, i_right)

			def CanSkip_Or_ClearLastRange(curedit, i_start, i_end, b_content):
				if b_content:
					i_cur_start	= curedit.indicatorEnd(self.indicator_number, 0)
					i_cur_end	= curedit.indicatorEnd(self.indicator_number, i_cur_start)
					if (i_cur_end != 0 and i_cur_start == i_start and i_cur_end == i_end):
						#print "DEBUG : " + "Content skip"
						return True
					if i_cur_end != 0:
						#print "DEBUG : " + "Content clear"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(i_cur_start, i_cur_end - i_cur_start)
					else:
						#print "DEBUG : " + "Content clear ALL, should NOT happen"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(0, curedit.getTextLength())
				else:
					i_cur_start		= curedit.indicatorEnd(self.indicator_number, 0)
					i_cur_end		= curedit.indicatorEnd(self.indicator_number, i_cur_start)
					i_cur_start2	= curedit.indicatorEnd(self.indicator_number, i_cur_end)
					i_cur_end2		= curedit.indicatorEnd(self.indicator_number, i_cur_start2)
					if (i_cur_end != 0 and i_cur_start == i_start and i_cur_start2 == i_end):
						#print "DEBUG : " + "Bracket skip"
						return True
					if i_cur_end != 0:
						#print "DEBUG : " + "Bracket clear"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(i_cur_start, i_cur_end2 - i_cur_start)
					else:
						#print "DEBUG : " + "Bracket clear ALL, should NOT happen"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(0, curedit.getTextLength())
				return False

			if console.editor.getProperty(self.editorprop_cb_on) != str(self.option_on):
				return

			# 'highlight brackets', 'highlight content' options
			b_brackets	= (console.editor.getProperty(self.editorprop_brackets_on)	== str(self.option_on))
			b_content	= (console.editor.getProperty(self.editorprop_content_on)	== str(self.option_on))
			if (not(b_brackets) and not(b_content)):
				return

			curedit = editor

			i_bufferid = notepad.getCurrentBufferID()
			if self.last_buffid != i_bufferid:
				self.last_buffid	= i_bufferid
				self.had_range		= False
				curedit.setIndicatorCurrent(self.indicator_number)
				curedit.indicatorClearRange(0, curedit.getTextLength())

			i_lines_on_screen = curedit.linesOnScreen()
			i_vis_line_first = curedit.getFirstVisibleLine()
			i_vis_line_last = i_vis_line_first + i_lines_on_screen - 1
			i_min = curedit.positionFromLine(curedit.docLineFromVisible(i_vis_line_first))
			i_max = curedit.getLineEndPosition(curedit.docLineFromVisible(i_vis_line_last))
			if i_min == self.INVALID_POSITION: i_min = 0
			if i_max == self.INVALID_POSITION: i_max = curedit.getTextLength()

			# 'angle', 'single line angle' options
			b_angle		= (console.editor.getProperty(self.editorprop_angle_on)		== str(self.option_on))
			b_sl_angle	= (console.editor.getProperty(self.editorprop_sl_angle_on)	== str(self.option_on))
			t_brackets = MatchingBrackets_OutRange_InRange( \
							curedit, curedit.getSelectionStart(), curedit.getSelectionEnd(), i_min, i_max, b_angle, b_sl_angle)

			if t_brackets is None:
				if self.had_range:
					curedit.setIndicatorCurrent(self.indicator_number)
					curedit.indicatorClearRange(0, curedit.getTextLength())
					self.had_range = False
				return

			i_start	= t_brackets[0]
			i_end	= t_brackets[1]
			if not(b_brackets): i_start += 1
			elif b_content: i_end += 1

			# 'limit highlight' option
			b_limit_hl = (console.editor.getProperty(self.editorprop_limit_hl_on) == str(self.option_on))

			# optimized for very long brackets content (10000 characters and more) if 'limit highlight' option is enabled
			if (b_limit_hl and b_content):
				i_extend_bidir = ((i_lines_on_screen + 1) * self.max_vis_col)
				i_hl_limit_free_room = self.max_vis_col

				i_cur_pos = curedit.getCurrentPos()

				if self.had_range: # return, or clear last highlight range for update
					i_cur_start	= curedit.indicatorEnd(self.indicator_number, 0)
					i_cur_end	= curedit.indicatorEnd(self.indicator_number, i_cur_start)
					if (i_cur_end != 0 and i_cur_start == i_start and i_cur_end == i_end):
						#print "DEBUG : " + "Limit skip FULL"
						return
					elif (i_cur_end != 0 and i_cur_start >= i_start and i_cur_end <= i_end):
						if ( \
								(i_cur_start	== i_start	or i_cur_start	<= (i_cur_pos - i_extend_bidir)) and \
								(i_cur_end		== i_end	or i_cur_end	>= (i_cur_pos + i_extend_bidir))):
							#print "DEBUG : " + "Limit skip part"
							return
					if i_cur_end != 0:
						#print "DEBUG : " + "Limit clear"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(i_cur_start, i_cur_end - i_cur_start)
					else:
						#print "DEBUG : " + "Limit clear ALL, should NOT happen"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(0, curedit.getTextLength())
				i_start	= max(i_start, i_cur_pos - i_extend_bidir - i_hl_limit_free_room)
				i_end	= min(i_end, i_cur_pos + i_extend_bidir + i_hl_limit_free_room)
				if i_end > i_start:
					curedit.setIndicatorCurrent(self.indicator_number)
					curedit.indicatorFillRange(i_start, i_end - i_start)
					self.had_range = True
				else:
					self.had_range = False
			# NOT optimized for very long brackets content : with content (with or without brackets)
			elif b_content:
				if self.had_range: # return, or clear last highlight range for update
					if CanSkip_Or_ClearLastRange(curedit, i_start, i_end, b_content):
						return
				if i_end > i_start:
					curedit.setIndicatorCurrent(self.indicator_number)
					curedit.indicatorFillRange(i_start, i_end - i_start)
					self.had_range = True
				else:
					self.had_range = False
			# NO content, brackets only (highlight 2 ranges of 1 char long)
			elif b_brackets:
				if self.had_range: # return, or clear last 2 highlight ranges for update
					if CanSkip_Or_ClearLastRange(curedit, i_start, i_end, b_content):
						return
				curedit.setIndicatorCurrent(self.indicator_number)
				curedit.indicatorFillRange(i_start, 1)
				curedit.indicatorFillRange(i_end, 1)
				self.had_range = True

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

		# install callback 1, should be sync to ensure it is fired before UPDATEUI (avoids constant UPDATEUI when a doc is cloned)
		editor.callbackSync(CBS_BracketInd_Modified, [SCINTILLANOTIFICATION.MODIFIED])
		# install callback 2, sync avoids flicker and other delay glitches
		editor.callbackSync(CBS_BracketInd_UpdateUI, [SCINTILLANOTIFICATION.UPDATEUI])
		# install callback 3, to synchronize or update highlight of cloned documents
		notepad.callback(CB_BracketInd_BufferActivated, [NOTIFICATION.BUFFERACTIVATED])

		self.cb_done = True
		return self.indicator_number
# end of class

# Main() code **************************************************************************************
def Main():
	print "[" + s_script_name + " starts] " + s_controleditscript

	# options formatting
	s_opt_info = ""
	dic_editorprop = {}
	for i in range(0, len(t_option_key)):
		console.editor.setProperty(s_editorprop_prefix + t_option_key[i], str(t_option_value[i]))
		v_opt_value = t_option_value[i]
		if type(v_opt_value) == type(""):
			v_opt_value = chr(34) + v_opt_value + chr(34)
		elif type(v_opt_value) == type(()):
			v_opt_value = str(v_opt_value).replace(", ", ",")
		else:
			v_opt_value = str(v_opt_value)
		s_opt_info = s_opt_info + t_option_initdes[i] + "=" + v_opt_value + ", "
		dic_editorprop[t_option_key[i]] = s_editorprop_prefix + t_option_key[i]
	s_opt_info = s_opt_info[:-2]
	if ( \
			console.editor.getProperty(dic_editorprop["BRACKETS"]) != str(i_true) and \
			console.editor.getProperty(dic_editorprop["CONTENT"]) != str(i_true)):
		s_opt_warn = "\n" + "\t" + "/!\\ Both brackets and content highlighting are disabled, NO highlight will be done"
	else:
		s_opt_warn = ""

	# create an instance of the callback class, and populate object properties with script and Console variables
	o_bracketindicator_cb = C_BracketIndicator_CB(s_script_name, dic_styles, i_true, s_editorprop_cb_on, dic_editorprop)

	if console.editor.getProperty(s_editorprop_cb_reg) != str(i_true):
		# register the callbacks on SCINTILLANOTIFICATION.UPDATEUI, SCINTILLANOTIFICATION.MODIFIED and NOTIFICATION.BUFFERACTIVATED
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
			print \
				"\t" + s_callback_name + " registered and activated [indicator number=" + str(i_indicator_number) + "]" + \
				" (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
			print "\t" + s_opt_info + s_opt_warn
		return

	if console.editor.getProperty(s_editorprop_cb_on) != str(i_true):
		console.editor.setProperty(s_editorprop_cb_on, str(i_true))

		o_bracketindicator_cb.SetIndicatorOptions(int(console.editor.getProperty(s_editorprop_indic_num)))
		o_bracketindicator_cb.Ugly_ForceUpdateUI()
		print "\t" + s_callback_name + " re-activated (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info + s_opt_warn
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_callback_name + " re-activated" + "\n\n" + \
				s_reruntogglecb + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n") + s_opt_warn.replace("\t", "\n").replace(", ", ",\n") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_cb_on, str(i_false))

		o_bracketindicator_cb.Ugly_ClearAllBuffersHighlights(int(console.editor.getProperty(s_editorprop_indic_num)))
		print "\t" + s_callback_name + " DE-ACTIVATED /!\\ (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info + s_opt_warn
		print "\t" + "(Bracket highlightings have been cleared from all opened documents)"
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_callback_name + " DE-ACTIVATED /!\\" + "\n\n" + \
				s_reruntogglecb + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n") + s_opt_warn.replace("\t", "\n").replace(", ", ",\n") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

Main()
