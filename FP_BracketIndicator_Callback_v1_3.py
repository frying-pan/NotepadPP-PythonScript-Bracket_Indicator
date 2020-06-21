# Inspired from brackethighlighter (especially callback events)
# https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/
# https://notepad-plus-plus.org/community/topic/14501/has-a-plugin-like-sublime-plugin-brackethighlighter/

# PythonScript that highlights the bracket pair () [] {} + optional <>, and/or the content between them,
# around the caret or the active selection, left-most pair in case of mismatch (Notepad++ CALLBACK)

# Tested with Notepad++ 7.8.2 64 bits, on Windows 8.1 64 bits (NOT tested with Notepad++ 32 Bits but should be compatible)
# using PythonScript plugin 1.5.2 from https://github.com/bruderstein/PythonScript/releases/ (based on python 2.7)
# /!\ this file uses TABS for indent /!\ (better read as 4 chars wide tabs)
# check update at https://github.com/frying-pan

# (i) brackets matching : this script will match brackets even in different folding level/folded lines/hidden lines,
	# but both brackets must be of the same style
# (i) performance : default options will limit highlight to a limited range around the caret/middle of active selection

# re-run the script to de-activate/re-activate the whole callback (re-running the script will also apply new *options values*)
# hold CONTROL while starting the script to edit it in Notepad++, and setup the *options values* (just below)

# *options values* *********************************************************************************
# highlight style
s_option_style			= "FULLBOX"		# STRING, NOT case-sensitive			: box/underline/text style (allowed values : see below)
t_option_rgb_color		= (255, 0, 0)	# INTEGER TRIPLET (0-255, 0-255, 0-255)	: (Red, Green, Blue) RGB color
i_option_alpha			= 24			# INTEGER 0-255							: box background color intensity (0 : transparent, 255 : opaque)
i_option_outline_alpha	= 48			# INTEGER 0-255							: box outline color intensity (0 : transparent, 255 : opaque)
# AT LEAST 1 of the 2 following options ('highlight brackets' or 'highlight content') must be enabled for highlighting to occur !
i_option_highlight_brackets	= 1	# set to INTEGER 1 to enable option : highlight the brackets () [] {} + optional <>
i_option_highlight_content	= 1	# set to INTEGER 1 to enable option : AND/OR highlight the content between the brackets
# miscellaneous options
i_option_highlight_angle	= 1	# set to INTEGER 1 to enable option : also highlight <> angle brackets (in addition to () [] {})
i_option_single_line_angle	= 1	# set to INTEGER 1 to enable option : only highlight <> angle brackets when both are on the same line
i_option_toggle_msgbox		= 0	# set to INTEGER 1 to enable option : show a message box when toggling the callback (console messages always occur)
# limit highlight (both options are applied simultaneously)
i_option_limit_search_chars_around_caret = 4000	# set to INTEGER -1 or > 0, see values below :
	# -1	: (NOT advised, SERIOUS PERFORMANCE IMPACT with very long lines) brackets search without characters limit
	# > 0	: limit brackets search to this number of characters before and after the caret/middle of active selection(last in multi-selection)
			# (so 0 would NOT search anything and is NOT allowed, 2000-10000 characters before/after the caret are reasonable values)
i_option_limit_search_lines_around_caret = 50	# set to INTEGER -1 or >= 0, see values below :
	# -1	: (NOT advised, some performance impact with many short lines) brackets search without lines limit
	# >= 0	: limit brackets search to this number of document lines before and after the caret/middle of active selection(last in multi-selection)
			# (so 0 will search only within the active document line, 50-100 document lines before/after the caret are reasonable values)
			# (note : a single document line can appear as multiple displayed lines when Notepad++ option 'Word wrap' is enabled)

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
i_deflimit_chars = 4000
i_deflimit_lines = 50
i_nolimit_search = -1

s_option_style = s_option_style.upper() # upper-case indicator style
if i_option_limit_search_chars_around_caret == 0: # limit search to 0 char is NOT allowed
	i_option_limit_search_chars_around_caret = i_deflimit_chars

t_option_key = ("S_STYLE", "COL_RGB", "ALPHA", "OUTALPHA", "BRACKETS", "CONTENT", \
	"ANGLE", "SL_ANGLE", "TOGMBOX", "LIM_CHARS", "LIM_LINES")
t_option_value = ( \
	s_option_style, t_option_rgb_color, i_option_alpha, i_option_outline_alpha, \
	i_option_highlight_brackets, i_option_highlight_content, \
	i_option_highlight_angle, i_option_single_line_angle, i_option_toggle_msgbox, \
	i_option_limit_search_chars_around_caret, i_option_limit_search_lines_around_caret)
t_option_initdes = ( \
	"Box style", "(Red,Green,Blue)", "Alpha", "Ouline alpha", \
	"Brackets", "Content", "<> Brackets", "Single line <>", "Toggle message box", "Search chars around caret", "Search lines around caret")

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
	def __init__(self, \
			s_script_name, dic_styles, i_deflimit_chars, i_deflimit_lines, i_nolimit_search, \
			i_option_on, s_editorprop_cb_on, dic_editorprop):
		import re
		self.re = re

		# class const
		self.INVALID_POSITION = -1 # Scintilla character position constant
		# script params
		self.script_name	= s_script_name
		self.dic_styles		= dic_styles
		self.deflimit_chars	= i_deflimit_chars
		self.deflimit_lines	= i_deflimit_lines
		self.nolimit_search	= i_nolimit_search
		self.option_on		= i_option_on
		self.editorprop_cb_on		= s_editorprop_cb_on
		self.editorprop_s_style		= dic_editorprop["S_STYLE"]
		self.editorprop_col_rgb		= dic_editorprop["COL_RGB"]
		self.editorprop_alpha		= dic_editorprop["ALPHA"]
		self.editorprop_outalpha	= dic_editorprop["OUTALPHA"]
		self.editorprop_brackets_on	= dic_editorprop["BRACKETS"]
		self.editorprop_content_on	= dic_editorprop["CONTENT"]
		self.editorprop_angle_on	= dic_editorprop["ANGLE"]
		self.editorprop_sl_angle_on	= dic_editorprop["SL_ANGLE"]
		self.editorprop_limit_chars	= dic_editorprop["LIM_CHARS"]
		self.editorprop_limit_lines	= dic_editorprop["LIM_LINES"]
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
		def _SetOneEditorIndicatorOptions( \
				i_indicator_number, indicator_style, rgb_color_tup, alpha, outline_alpha, draw_under_text, curedit):
			curedit.indicSetStyle			(i_indicator_number, indicator_style)	# INDICATORSTYLE
			curedit.indicSetFore			(i_indicator_number, rgb_color_tup)		# (r,g,b) integers tuple
			curedit.indicSetAlpha			(i_indicator_number, alpha)				# integer
			curedit.indicSetOutlineAlpha	(i_indicator_number, outline_alpha)		# integer
			curedit.indicSetUnder			(i_indicator_number, draw_under_text)	# boolean
		def _IsRGBTuple(t_rgb_color):
			if type(t_rgb_color) != type(()): return False
			if len(t_rgb_color) != 3: return False
			i_red = t_rgb_color[0]; i_green = t_rgb_color[1]; i_blue = t_rgb_color[2]
			if (type(i_red) != type(0) or type(i_green) != type(0) or type(i_blue) != type(0)): return False
			if i_red	< 0 or i_red	> 255: return False
			if i_green	< 0 or i_green	> 255: return False
			if i_blue	< 0 or i_blue	> 255: return False
			return True
		def _IsUByteInteger(t_ubyte_int):
			if (t_ubyte_int < 0 or t_ubyte_int > 255): return False
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
		if not(_IsRGBTuple(t_rgb_color)):
			b_has_error= True
		if (not(_IsUByteInteger(i_alpha)) or not(_IsUByteInteger(i_outalpha))):
			b_has_error= True
		if b_has_error:
			s_error_msg = "/!\\ User options error, check your highlight style options values..."
			print "\t" + s_error_msg
			notepad.messageBox(s_error_msg, self.script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

		for curedit in (editor, editor1, editor2):
			if b_has_error:
				_SetOneEditorIndicatorOptions( \
					i_indicator_number, self.dic_styles["HIDDEN"], (0, 0, 0), 0, 0, True, curedit)
			else:
				_SetOneEditorIndicatorOptions( \
					i_indicator_number, indicator_style, t_rgb_color, i_alpha, i_outalpha, True, curedit)

	def RegCallback(self):
		# our CallBack functions
		def _CBS_BracketInd_Modified(args):
			self.lastmodtype_hack = args['modificationType']
		def _CBS_BracketInd_UpdateUI(args):
			# hack, look for "16400" [== (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER)] in code :
			# https://notepad-plus-plus.org/community/topic/12360/vi-simulator-how-to-highlight-a-word/28
			if ( \
					args['updated'] == UPDATE.CONTENT and \
					self.lastmodtype_hack == (MODIFICATIONFLAGS.CHANGEINDICATOR | MODIFICATIONFLAGS.USER)):
				return
			_CheckBrackets()
		def _CB_BracketInd_BufferActivated(args):
			_CheckBrackets()

		def _CheckBrackets():
			# range must be : i_min < i_start <= i_end < i_max, [i_start, i_end] is typically the current selection
			def _MatchingBrackets_OutRange_InRange(curedit, i_start, i_end, i_min, i_max, b_angle, b_sl_angle):
				# dic_charstyle_datas : indexes in value = [fw count, bk count, bk pos]; counter add/sub
				c_fw = 0; c_bk = 1; bk_pos = 2; i_open = 1; i_close = -1
				def _Make_Match_Datas(dic_close_open, s_open, s_sep, o_match, i_style):
					s_cur_char = o_match.group(0)
					i_br_dir = i_open if (s_cur_char in s_open) else i_close
					s_open_char = s_cur_char if (i_br_dir == i_open) else dic_close_open[s_cur_char]
					s_charstyle = s_open_char + s_sep + str(i_style)
					return (i_br_dir, s_cur_char, s_open_char, s_charstyle)
				def _Set_Counter(dic_charstyle_datas, s_charstyle, i_br_dir, i_counter):
					if not(s_charstyle in dic_charstyle_datas.keys()):
						dic_charstyle_datas[s_charstyle] = [0, 0, None]
					if dic_charstyle_datas[s_charstyle] is None: # this charstyle was killed
						return
					if i_counter is None: # in selection (forward) search
						if (i_br_dir == i_close and dic_charstyle_datas[s_charstyle][c_fw] <= 0):
							dic_charstyle_datas[s_charstyle][c_bk] += i_br_dir # trick : un-matched_closing are sent to bk count
						else:
							dic_charstyle_datas[s_charstyle][c_fw] += i_br_dir # opening and matched_closing are kept in fw count
					else: # forward after selection, or backward search
						dic_charstyle_datas[s_charstyle][i_counter] += i_br_dir
				def _Valid_Angle(curedit, pattern_newline, s_open_char, b_angle, b_sl_angle, i_left, i_right):
					if s_open_char != "<": return True
					if not(b_angle and b_sl_angle): return True
					s_text = curedit.getTextRange(i_left + 1, i_right)
					if pattern_newline.search(s_text) is None: return True
					return False

				if (i_min < 0): i_min = 0
				if (i_max > curedit.getTextLength()): i_max = curedit.getTextLength()
				if (i_min >= i_start or i_start > i_end or i_end >= i_max): return None

				s_pattern_brackets = "\(\)\[\]\{\}"
				if b_angle: s_pattern_brackets = s_pattern_brackets + "\<\>"
				s_pattern_brackets = "[" + s_pattern_brackets + "]"
				pattern_brackets	= self.re.compile(s_pattern_brackets)
				pattern_newline		= self.re.compile("[\r\n]")

				s_open = "([{"
				if b_angle: s_open = s_open + "<"
				dic_close_open = {")" : "(", "]" : "[", "}" : "{"}
				if b_angle: dic_close_open[">"] = "<"

				s_sep = ":"; dic_charstyle_datas = {} # {(openchar + s_sep + style_number) : [fw count, bk count, bk pos]}
				i_chunk_base = 128 # search in chunks to limit getTextRange string size, chunks double up each time

				s_charstyle_fw = None

				b_exit_while = False
				i_chunk = i_chunk_base
				i_offset = 0
				# search all selection (trick : un-matched_closing are sent to bk count instead of fw count),
				# and after selection stop at [first un-matched closing charstyle]
				while True: # forward search from i_start, i_offset >= 0, i_chunk > 0
					s_text = curedit.getTextRange(i_start + i_offset, min(i_start + i_offset + i_chunk, i_max))
					for o_match in pattern_brackets.finditer(s_text):
						i_pos_fw = i_start + i_offset + o_match.start()
						i_br_dir, s_cur_char, s_open_char, s_charstyle_fw = \
							_Make_Match_Datas(dic_close_open, s_open, s_sep, o_match, curedit.getStyleAt(i_pos_fw))

						if i_pos_fw < i_end: # in selection
							_Set_Counter(dic_charstyle_datas, s_charstyle_fw, i_br_dir, None)
							#print "DEBUG : in sel. : " + s_cur_char + " at " + str(i_pos_fw) + " " + str(dic_charstyle_datas[s_charstyle_fw])
						else: # after selection
							_Set_Counter(dic_charstyle_datas, s_charstyle_fw, i_br_dir, c_fw)
							#print "DEBUG : after sel. : " + s_cur_char + " at " + str(i_pos_fw) + " " + str(dic_charstyle_datas[s_charstyle_fw])
							# [first un-matched closing charstyle] found, EXIT while and search backward
							if dic_charstyle_datas[s_charstyle_fw][c_fw] == i_close:
								b_exit_while = True
								break
					if b_exit_while: break

					i_offset = i_offset + i_chunk
					if i_start + i_offset >= i_max: break
					i_chunk = i_chunk * 2
				if s_charstyle_fw is None:
					return None # NO bracket after start of selection
				if dic_charstyle_datas[s_charstyle_fw][c_fw] != i_close:
					return None # NO [first un-matched closing charstyle] after end of selection

				i_chunk = i_chunk_base
				i_offset = 0
				# search backward from start of selection to i_min, but stop if matching [first un-matched closing charstyle],
				# record bk count, and remember bk pos for future forward match
				while True: # backward search from i_start, i_offset <= 0, i_chunk > 0
					s_text = curedit.getTextRange(max(i_start + i_offset - i_chunk, i_min), i_start + i_offset)
					s_text = s_text[::-1] # reverse text for regex
					for o_match in pattern_brackets.finditer(s_text):
						i_pos_bk = i_start + i_offset - o_match.end()
						i_br_dir, s_cur_char, s_open_char, s_charstyle_bk = \
							_Make_Match_Datas(dic_close_open, s_open, s_sep, o_match, curedit.getStyleAt(i_pos_bk))

						_Set_Counter(dic_charstyle_datas, s_charstyle_bk, i_br_dir, c_bk)
						#print "DEBUG : backward : " + s_cur_char + " at " + str(i_pos_bk) + " " + str(dic_charstyle_datas[s_charstyle_bk])
						if dic_charstyle_datas[s_charstyle_bk] is None: continue # this charstyle was killed

						if dic_charstyle_datas[s_charstyle_bk][c_bk] == i_open:
							if s_charstyle_bk == s_charstyle_fw:
								if _Valid_Angle(curedit, pattern_newline, s_open_char, b_angle, b_sl_angle, i_pos_bk, i_pos_fw):
									return (i_pos_bk, i_pos_fw) # match OK, RETURN
								dic_charstyle_datas[s_charstyle_bk] = None # kill this <> charstyle
							elif (dic_charstyle_datas[s_charstyle_bk][bk_pos] is None): # if no bk pos yet
								# remember bk pos for future forward match
								dic_charstyle_datas[s_charstyle_bk][bk_pos] = i_pos_bk

					i_offset = i_offset - i_chunk
					if i_start + i_offset <= i_min: break
					i_chunk = i_chunk * 2
				# kill s_charstyle_fw since not matched backward from i_start to i_min
				if not(dic_charstyle_datas[s_charstyle_fw] is None):
					dic_charstyle_datas[s_charstyle_fw] = None

				i_chunk = i_chunk_base
				i_offset = i_pos_fw + 1 - i_start
				# search from [first un-matched closing charstyle] + 1 to i_max, and check if any un-matched closing charstyle
				# matches an opening charstyle saved by the backward search in dic_charstyle_datas[s_charstyle_fw][bk_pos]
				while True: # forward search from (first un-matched)i_pos_fw + 1, i_offset >= 0, i_chunk > 0
					s_text = curedit.getTextRange(i_start + i_offset, min(i_start + i_offset + i_chunk, i_max))
					for o_match in pattern_brackets.finditer(s_text):
						i_pos_fw = i_start + i_offset + o_match.start()
						i_br_dir, s_cur_char, s_open_char, s_charstyle_fw = \
							_Make_Match_Datas(dic_close_open, s_open, s_sep, o_match, curedit.getStyleAt(i_pos_fw))

						_Set_Counter(dic_charstyle_datas, s_charstyle_fw, i_br_dir, c_fw)
						#print "DEBUG : forward : " + s_cur_char + " at " + str(i_pos_fw) + " " + str(dic_charstyle_datas[s_charstyle_fw])
						if dic_charstyle_datas[s_charstyle_fw] is None: continue # this charstyle was killed

						# un-matched closing charstyle found, check for a previously remembered bk pos or kill it
						if dic_charstyle_datas[s_charstyle_fw][c_fw] == i_close:
							i_pos_bk = dic_charstyle_datas[s_charstyle_fw][bk_pos]
							if not(i_pos_bk is None):
								if _Valid_Angle(curedit, pattern_newline, s_open_char, b_angle, b_sl_angle, i_pos_bk, i_pos_fw):
									return (i_pos_bk, i_pos_fw) # match OK, RETURN
							dic_charstyle_datas[s_charstyle_fw] = None # kill this charstyle

					i_offset = i_offset + i_chunk
					if i_start + i_offset >= i_max: break
					i_chunk = i_chunk * 2

				return None

			def _CanSkip_Or_ClearLastRange(curedit, i_start, i_end, b_content):
				if curedit.indicatorValueAt(self.indicator_number, 0) != 0:
					i_cur_start = 0 # if 1st highlight begins at 0 indicatorEnd() would give the end of 1st highlight
				else:
					i_cur_start = curedit.indicatorEnd(self.indicator_number, 0) # indeed gives start of 1st highlight
				i_cur_end = curedit.indicatorEnd(self.indicator_number, i_cur_start) # end of 1st highlight
				if b_content:
					if (i_cur_end != 0 and i_cur_start == i_start and i_cur_end == i_end):
						#print "DEBUG : " + "Content skip, no highlight change"
						return True
					if i_cur_end != 0:
						#print "DEBUG : " + "Content clear : [" + str(i_cur_start) + ":" + str(i_cur_end) + "]"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(i_cur_start, i_cur_end - i_cur_start)
					else:
						#print "DEBUG : " + "Content clear ALL, should NOT happen"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(0, curedit.getTextLength())
				else:
					i_cur_start2	= curedit.indicatorEnd(self.indicator_number, i_cur_end) # start of 2nd highlight
					i_cur_end2		= curedit.indicatorEnd(self.indicator_number, i_cur_start2) # end of 2nd highlight
					if (i_cur_end != 0 and i_cur_start == i_start and i_cur_start2 == i_end):
						#print "DEBUG : " + "Bracket skip, no highlight change"
						return True
					if i_cur_end != 0:
						#print "DEBUG : " + "Bracket clear : [" + str(i_cur_start) + ":" + str(i_cur_end2) + "]"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(i_cur_start, i_cur_end2 - i_cur_start)
					else:
						#print "DEBUG : " + "Bracket clear ALL, should NOT happen"
						curedit.setIndicatorCurrent(self.indicator_number)
						curedit.indicatorClearRange(0, curedit.getTextLength())
				return False

			def _Clear_Whole_Doc():
				curedit.setIndicatorCurrent(self.indicator_number)
				curedit.indicatorClearRange(0, curedit.getTextLength())
				self.had_range = False

			if console.editor.getProperty(self.editorprop_cb_on) != str(self.option_on):
				return

			# 'highlight brackets', 'highlight content' options
			b_brackets	= (console.editor.getProperty(self.editorprop_brackets_on)	== str(self.option_on))
			b_content	= (console.editor.getProperty(self.editorprop_content_on)	== str(self.option_on))
			if (not(b_brackets) and not(b_content)):
				return

			curedit = editor

			# check if a new BufferID has been activated
			i_bufferid = notepad.getCurrentBufferID()
			if self.last_buffid != i_bufferid:
				self.last_buffid = i_bufferid
				_Clear_Whole_Doc()

			i_min = 0
			i_max = curedit.getTextLength()
			i_sel_start	= curedit.getSelectionStart()
			i_sel_end	= curedit.getSelectionEnd()

			# 'limit search chars', 'limit search lines' options
			try:	i_limit_search_chars = int(console.editor.getProperty(self.editorprop_limit_chars))
			except:	i_limit_search_chars = self.deflimit_chars
			try:	i_limit_search_lines = int(console.editor.getProperty(self.editorprop_limit_lines))
			except:	i_limit_search_lines = self.deflimit_lines
			if i_limit_search_chars < self.nolimit_search: i_limit_search_chars = self.deflimit_chars
			if i_limit_search_lines < self.nolimit_search: i_limit_search_lines = self.deflimit_lines

			if (i_limit_search_chars != self.nolimit_search or i_limit_search_lines != self.nolimit_search):
				i_doc_lines = curedit.getLineCount

				# getFirstVisibleLine() and linesOnScreen() give display line (NOT document line)
				i_vis_dis_line_first	= curedit.getFirstVisibleLine()
				i_vis_dis_line_last		= i_vis_dis_line_first + curedit.linesOnScreen()
				# partially vertically-truncated last visible line is included so NO (-1) to linesOnScreen()

				i_doc_line_min = curedit.docLineFromVisible(i_vis_dis_line_first)	# should be in limit
				i_doc_line_max = curedit.docLineFromVisible(i_vis_dis_line_last)	# can be scrolled off limit
				if i_doc_line_min < 0: i_doc_line_min = 0							# min doc line index is 0
				if i_doc_line_max >= i_doc_lines: i_doc_line_max = i_doc_lines - 1	# max doc line index is (i_doc_lines - 1)
				i_mined_vis = curedit.positionFromLine(i_doc_line_min)				# min is mined (start of line)
				i_maxed_vis = curedit.getLineEndPosition(i_doc_line_max)			# max is maxed (end of line, before cr/lf)
				if i_mined_vis == self.INVALID_POSITION : i_mined_vis = 0						# just in case, should not happen
				if i_maxed_vis == self.INVALID_POSITION : i_maxed_vis = curedit.getTextLength()	# just in case, should not happen

				i_middle_pos = int((i_sel_start + i_sel_end) / 2)

				if i_limit_search_chars != self.nolimit_search:
					#if		i_maxed_vis < (i_middle_pos - i_limit_search_chars):	print "DEBUG : off chars range limit before"
					#elif	i_mined_vis > (i_middle_pos + i_limit_search_chars):	print "DEBUG : off chars range limit after"
					if (i_maxed_vis < (i_middle_pos - i_limit_search_chars) or i_mined_vis > (i_middle_pos + i_limit_search_chars)):
						if self.had_range: _Clear_Whole_Doc()
						return # i_middle_pos to visible area exceed i_limit_search_chars, no need to highlight

					i_min = max(i_min, i_middle_pos - i_limit_search_chars)
					i_max = min(i_max, i_middle_pos + i_limit_search_chars)
				if i_limit_search_lines != self.nolimit_search:
					i_doc_line_min = curedit.lineFromPosition(i_middle_pos) - i_limit_search_lines	# can be calculated off limit
					i_doc_line_max = curedit.lineFromPosition(i_middle_pos) + i_limit_search_lines	# can be calculated off limit
					if i_doc_line_min < 0: i_doc_line_min = 0										# min doc line index is 0
					if i_doc_line_max >= i_doc_lines: i_doc_line_max = i_doc_lines - 1				# max doc line index is (i_doc_lines - 1)
					i_mined_from_lines = curedit.positionFromLine(i_doc_line_min)					# min is mined (start of line)
					i_maxed_from_lines = curedit.getLineEndPosition(i_doc_line_max)					# max is maxed (end of line, before cr/lf)
					if i_mined_from_lines == self.INVALID_POSITION : i_mined_from_lines = 0							# just in case, should not happen
					if i_maxed_from_lines == self.INVALID_POSITION : i_maxed_from_lines = curedit.getTextLength()	# just in case, should not happen

					#if		i_maxed_vis < i_mined_from_lines:						print "DEBUG : off lines range limit before"
					#elif	i_mined_vis > i_maxed_from_lines:						print "DEBUG : off lines range limit after"
					if (i_maxed_vis < i_mined_from_lines or i_mined_vis > i_maxed_from_lines):
						if self.had_range: _Clear_Whole_Doc()
						return # i_middle_pos to visible area exceed i_limit_search_lines, no need to highlight

					i_min = max(i_min, i_mined_from_lines)
					i_max = min(i_max, i_maxed_from_lines)

			# 'angle', 'single line angle' options
			b_angle		= (console.editor.getProperty(self.editorprop_angle_on)		== str(self.option_on))
			b_sl_angle	= (console.editor.getProperty(self.editorprop_sl_angle_on)	== str(self.option_on))

			t_brackets = _MatchingBrackets_OutRange_InRange(curedit, i_sel_start, i_sel_end, i_min, i_max, b_angle, b_sl_angle)
			if t_brackets is None:
				if self.had_range: _Clear_Whole_Doc()
				return

			i_start	= t_brackets[0]
			i_end	= t_brackets[1]
			if not(b_brackets): i_start += 1
			elif b_content: i_end += 1

			if self.had_range: # return, or clear last highlight range(s)
				if _CanSkip_Or_ClearLastRange(curedit, i_start, i_end, b_content):
					return

			if b_content: # with content, with or without brackets (highlight 1 range)
				if i_end > i_start:
					curedit.setIndicatorCurrent(self.indicator_number)
					curedit.indicatorFillRange(i_start, i_end - i_start)
					self.had_range = True
				else:
					self.had_range = False
			else: # brackets only (highlight 2 ranges of 1 char long)
				curedit.setIndicatorCurrent(self.indicator_number)
				curedit.indicatorFillRange(i_start, 1)
				curedit.indicatorFillRange(i_end, 1)
				self.had_range = True

		if self.cb_done:
			return None

		curedit = editor

		# try to pick an unused indicator number : from INDICATORNUMBERS.CONTAINER(8) to (INDICATORNUMBERS.IME - 1)(31)
		# skip the first 2 of them, just in case they are used but their flags/styles/colors are still 0
		self.indicator_number = None
		for i in range(INDICATORNUMBERS.CONTAINER + 2, INDICATORNUMBERS.IME):
			# indicators flag and styles seems to default to 0 before being set, so this one could be unused
			if (curedit.indicGetFlags(i) == 0 and curedit.indicGetStyle(i) == 0 and curedit.indicGetHoverStyle(i) == 0):
				# indicators fore colors seems to default to black (0, 0, 0) before being set, so (hopefully) this one is really unused
				if (curedit.indicGetFore(i) == (0, 0, 0) and curedit.indicGetHoverFore(i) == (0, 0, 0)):
					self.indicator_number = i
					break
		if self.indicator_number is None:
			return None

		self.SetIndicatorOptions(self.indicator_number)

		# install callback 1, should be sync to ensure it is fired before UPDATEUI (avoids constant UPDATEUI when a doc is cloned)
		editor.callbackSync(_CBS_BracketInd_Modified, [SCINTILLANOTIFICATION.MODIFIED])
		# install callback 2, sync avoids flicker and other delay glitches
		editor.callbackSync(_CBS_BracketInd_UpdateUI, [SCINTILLANOTIFICATION.UPDATEUI])
		# install callback 3, to synchronize or update highlight of cloned documents
		notepad.callback(_CB_BracketInd_BufferActivated, [NOTIFICATION.BUFFERACTIVATED])

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
	o_bracketindicator_cb = C_BracketIndicator_CB( \
								s_script_name, dic_styles, i_deflimit_chars, i_deflimit_lines, i_nolimit_search, \
								i_true, s_editorprop_cb_on, dic_editorprop)

	if console.editor.getProperty(s_editorprop_cb_reg) != str(i_true):
		# register the callbacks on SCINTILLANOTIFICATION.UPDATEUI, SCINTILLANOTIFICATION.MODIFIED, NOTIFICATION.BUFFERACTIVATED
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
