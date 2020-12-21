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
# /!\ AT LEAST 1 of the 2 following options ('highlight brackets' or 'highlight content') must be enabled for highlighting to occur !
i_option_highlight_brackets	= 1	# set to INTEGER 1 to enable option : highlight the (non-empty) brackets () [] {} + optional <>
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
	# -1	: (NOT advised, some performance impact with many short lines) brackets search without document lines limit
	# >= 0	: limit brackets search to this number of document lines before and after the caret/middle of active selection(last in multi-selection)
			# (so 0 will search only within the active document line, 50-100 document lines before/after the caret line are reasonable values)
			# (note : a single document line can appear as multiple displayed lines when Notepad++ option 'Word wrap' is enabled)
# highlight style for BRACKETS
s_option_style_br			= "FULLBOX"		# STRING, NOT case-sensitive			: box/underline/text decoration (allowed values : see below)
t_option_rgb_color_br		= (0, 128, 0)	# INTEGER TRIPLET (0-255, 0-255, 0-255)	: (Red, Green, Blue) RGB color
i_option_alpha_br			= 64			# INTEGER 0-255							: box background color intensity (0 : transparent, 255 : opaque)
i_option_outline_alpha_br	= 255			# INTEGER 0-255							: box outline color intensity (0 : transparent, 255 : opaque)
# highlight style for CONTENT
s_option_style_con			= "FULLBOX"		# STRING, NOT case-sensitive			: box/underline/text decoration (allowed values : see below)
t_option_rgb_color_con		= (255, 0, 0)	# INTEGER TRIPLET (0-255, 0-255, 0-255)	: (Red, Green, Blue) RGB color
i_option_alpha_con			= 24			# INTEGER 0-255							: box background color intensity (0 : transparent, 255 : opaque)
i_option_outline_alpha_con	= 24			# INTEGER 0-255							: box outline color intensity (0 : transparent, 255 : opaque)
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
		# predefined	: "CONTAINER", "IME", "IME_MAX", "MAX"

# script declarations ******************************************************************************
from Npp import *

s_script_name	= "Bracket Indicator"
s_callback_name	= "Indicator Callback"

s_controleditscript	= "(hold CTRL while starting the script to edit its options in Notepad++)"
s_reruntogglecb		= "Re-run the script to toggle the whole callback"
s_willapplynewopt	= "This will also apply new *options values* saved in the script file"
s_nofreeindicators	= "no free indicator numbers for brackets/content highlighting could be found"

s_editorprop_prefix			= "BRACKETINDICATORCB_"
s_editorprop_cb_reg			= s_editorprop_prefix + "CB_REGISTERED"
s_editorprop_cb_on			= s_editorprop_prefix + "CB_ON"
s_editorprop_indic_num_br	= s_editorprop_prefix + "INDIC_NUM_BR"
s_editorprop_indic_num_con	= s_editorprop_prefix + "INDIC_NUM_CON"

s_option_style_br	= s_option_style_br.upper().strip()		# upper-case, without spaces around indicator style
s_option_style_con	= s_option_style_con.upper().strip()	# upper-case, without spaces around indicator style

t_option_key = ("BRACKETS", "CONTENT", "ANGLE", "SL_ANGLE", "TOGMBOX", "LIM_CHARS", "LIM_LINES", "", \
	"S_STYLE_BR", "COL_RGB_BR", "ALPHA_BR", "OUTALPHA_BR", "", \
	"S_STYLE_CON", "COL_RGB_CON", "ALPHA_CON", "OUTALPHA_CON")
t_option_value = ( \
	i_option_highlight_brackets, i_option_highlight_content, \
	i_option_highlight_angle, i_option_single_line_angle, i_option_toggle_msgbox, \
	i_option_limit_search_chars_around_caret, i_option_limit_search_lines_around_caret, "", \
	s_option_style_br, t_option_rgb_color_br, i_option_alpha_br, i_option_outline_alpha_br, "", \
	s_option_style_con, t_option_rgb_color_con, i_option_alpha_con, i_option_outline_alpha_con)
t_option_initdes = ( \
	"Brackets", "Content", "<> Brackets", "Single line <>", "Toggle message box", "Search chars around caret", "Search lines around caret", "", \
	"Brackets style", "Brackets coloring (Red,Green,Blue)", "Brackets alpha", "Brackets outline alpha", "", \
	"Content style", "Content coloring (Red,Green,Blue)", "Content alpha", "Content outline alpha")

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

i_true	= 1
i_false	= 0
i_deflimit_chars = 4000
i_deflimit_lines = 50
i_nolimit_search = -1

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
		self.editorprop_brackets_on	= dic_editorprop["BRACKETS"]
		self.editorprop_content_on	= dic_editorprop["CONTENT"]
		self.editorprop_angle_on	= dic_editorprop["ANGLE"]
		self.editorprop_sl_angle_on	= dic_editorprop["SL_ANGLE"]
		self.editorprop_limit_chars	= dic_editorprop["LIM_CHARS"]
		self.editorprop_limit_lines	= dic_editorprop["LIM_LINES"]
		self.editorprop_s_style_br		= dic_editorprop["S_STYLE_BR"]
		self.editorprop_col_rgb_br		= dic_editorprop["COL_RGB_BR"]
		self.editorprop_alpha_br		= dic_editorprop["ALPHA_BR"]
		self.editorprop_outalpha_br		= dic_editorprop["OUTALPHA_BR"]
		self.editorprop_s_style_con		= dic_editorprop["S_STYLE_CON"]
		self.editorprop_col_rgb_con		= dic_editorprop["COL_RGB_CON"]
		self.editorprop_alpha_con		= dic_editorprop["ALPHA_CON"]
		self.editorprop_outalpha_con	= dic_editorprop["OUTALPHA_CON"]
		# instance state datas
		self.cb_done			= False
		self.lastmodtype_hack	= None
		self.getoptions			= True
		self.bufferid_last		= notepad.getCurrentBufferID()
		self.had_range_br		= False
		self.had_range_con		= False

	def Ugly_UpdateVisTabsHighlight(self):
		i_act_view = notepad.getCurrentView()
		if notepad.isSingleView():
			i_act_index = notepad.getCurrentDocIndex(i_act_view)
			notepad.new()
			notepad.close()
			notepad.activateIndex(i_act_view, i_act_index)
		else:
			i_act_index_0	= notepad.getCurrentDocIndex(0)
			i_act_index_1	= notepad.getCurrentDocIndex(1)
			if i_act_view == 0:
				notepad.activateIndex(1, i_act_index_1)
				notepad.activateIndex(0, i_act_index_0)
			else:
				notepad.activateIndex(0, i_act_index_0)
				notepad.activateIndex(1, i_act_index_1)

	def Ugly_ClearAllTabsHighlights(self, i_indic_num_br, i_indic_num_con):
		def _Clear_All_Tabs(i_indic_num_br, i_indic_num_con):
			lst_files_infos = notepad.getFiles()
			for t_file_infos in lst_files_infos:
				notepad.activateIndex(t_file_infos[3], t_file_infos[2])
				curedit = editor
				curedit.setIndicatorCurrent(i_indic_num_br)
				curedit.indicatorClearRange(0, curedit.getTextLength())
				curedit.setIndicatorCurrent(i_indic_num_con)
				curedit.indicatorClearRange(0, curedit.getTextLength())

		i_act_view = notepad.getCurrentView()
		if notepad.isSingleView():
			i_act_index = notepad.getCurrentDocIndex(i_act_view)
			_Clear_All_Tabs(i_indic_num_br, i_indic_num_con)
			notepad.activateIndex(i_act_view, i_act_index)
		else:
			i_act_index_0	= notepad.getCurrentDocIndex(0)
			i_act_index_1	= notepad.getCurrentDocIndex(1)
			_Clear_All_Tabs(i_indic_num_br, i_indic_num_con)
			if i_act_view == 0:
				notepad.activateIndex(1, i_act_index_1)
				notepad.activateIndex(0, i_act_index_0)
			else:
				notepad.activateIndex(0, i_act_index_0)
				notepad.activateIndex(1, i_act_index_1)
		self.had_range_br	= False
		self.had_range_con	= False

	def SetIndicatorsOptions(self, i_indic_num_br, i_indic_num_con):
		def _SetOneEditorIndicatorOptions(curedit, i_indic_num, indicator_style, t_rgb_color, i_alpha, i_outline_alpha):
			curedit.indicSetStyle			(i_indic_num, indicator_style)	# INDICATORSTYLE
			curedit.indicSetFore			(i_indic_num, t_rgb_color)		# (red,green,blue) integers tuple
			curedit.indicSetAlpha			(i_indic_num, i_alpha)			# integer
			curedit.indicSetOutlineAlpha	(i_indic_num, i_outline_alpha)	# integer
			curedit.indicSetUnder			(i_indic_num, True)				# boolean (draw under text)
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

		# brackets/content : 'style', 'RGB color', 'background alpha', 'outline alpha' options
		for (s_editorprop_s_style, s_editorprop_col_rgb, s_editorprop_alpha, s_editorprop_outalpha, i_indic_num) in \
				((self.editorprop_s_style_br, self.editorprop_col_rgb_br, self.editorprop_alpha_br, self.editorprop_outalpha_br, i_indic_num_br), \
				(self.editorprop_s_style_con, self.editorprop_col_rgb_con, self.editorprop_alpha_con, self.editorprop_outalpha_con, i_indic_num_con)):
			b_has_error= False
			try:
				indicator_style	= self.dic_styles[console.editor.getProperty(s_editorprop_s_style)]
				t_rgb_color		= eval(console.editor.getProperty(s_editorprop_col_rgb))
				i_alpha			= int(console.editor.getProperty(s_editorprop_alpha))
				i_outalpha		= int(console.editor.getProperty(s_editorprop_outalpha))
			except:
				b_has_error= True
			else:
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
					_SetOneEditorIndicatorOptions(curedit, i_indic_num, self.dic_styles["HIDDEN"], (0, 0, 0), 0, 0)
				else:
					_SetOneEditorIndicatorOptions(curedit, i_indic_num, indicator_style, t_rgb_color, i_alpha, i_outalpha)

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
			self.getoptions = True
			_CheckBrackets()

		def _CheckBrackets():
			def _Get_Search_Ranges(curedit):
				i_min = 0
				i_max = curedit.getTextLength()
				i_sel_start	= curedit.getSelectionStart()
				i_sel_end	= curedit.getSelectionEnd()

				if (self.i_limit_search_chars != self.nolimit_search or self.i_limit_search_lines != self.nolimit_search):
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
					if i_mined_vis == self.INVALID_POSITION : i_mined_vis = 0						# just in case,
					if i_maxed_vis == self.INVALID_POSITION : i_maxed_vis = curedit.getTextLength()	# but should NOT happen

					i_middle_pos = int((i_sel_start + i_sel_end) / 2)

					if self.i_limit_search_chars != self.nolimit_search:
						#if		i_maxed_vis < (i_middle_pos - self.i_limit_search_chars):	print "DEBUG : off chars range limit before"
						#elif	i_mined_vis > (i_middle_pos + self.i_limit_search_chars):	print "DEBUG : off chars range limit after"
						if (i_maxed_vis < (i_middle_pos - self.i_limit_search_chars) or i_mined_vis > (i_middle_pos + self.i_limit_search_chars)):
							return None # i_middle_pos to visible area exceed self.i_limit_search_chars, no need to highlight

						i_min = max(i_min, i_middle_pos - self.i_limit_search_chars)
						i_max = min(i_max, i_middle_pos + self.i_limit_search_chars)
					if self.i_limit_search_lines != self.nolimit_search:
						i_doc_line_min = curedit.lineFromPosition(i_middle_pos) - self.i_limit_search_lines	# can be calculated off limit
						i_doc_line_max = curedit.lineFromPosition(i_middle_pos) + self.i_limit_search_lines	# can be calculated off limit
						if i_doc_line_min < 0: i_doc_line_min = 0										# min doc line index is 0
						if i_doc_line_max >= i_doc_lines: i_doc_line_max = i_doc_lines - 1				# max doc line index is (i_doc_lines - 1)
						i_mined_from_lines = curedit.positionFromLine(i_doc_line_min)					# min is mined (start of line)
						i_maxed_from_lines = curedit.getLineEndPosition(i_doc_line_max)					# max is maxed (end of line, before cr/lf)
						if i_mined_from_lines == self.INVALID_POSITION : i_mined_from_lines = 0							# just in case,
						if i_maxed_from_lines == self.INVALID_POSITION : i_maxed_from_lines = curedit.getTextLength()	# but should NOT happen

						#if		i_maxed_vis < i_mined_from_lines:						print "DEBUG : off lines range limit before"
						#elif	i_mined_vis > i_maxed_from_lines:						print "DEBUG : off lines range limit after"
						if (i_maxed_vis < i_mined_from_lines or i_mined_vis > i_maxed_from_lines):
							return None # i_middle_pos to visible area exceed self.i_limit_search_lines, no need to highlight

						i_min = max(i_min, i_mined_from_lines)
						i_max = min(i_max, i_maxed_from_lines)
				return (i_sel_start, i_sel_end, i_min, i_max)

			# ranges must be : i_min < i_start <= i_end < i_max, [i_start, i_end] is typically the current selection
			def _MatchingBrackets_OutRange_InRange(curedit, i_start, i_end, i_min, i_max, b_angle, b_sl_angle):
				# dic_charstyle_datas : indexes in value = [fw count, bk count, bk pos]; counter add/sub
				c_fw = 0; c_bk = 1; bk_pos = 2; i_open = 1; i_close = -1
				def _Make_Match_Datas(dic_close_open, s_open, o_match, i_style):
					s_sep = ":"
					s_cur_char = o_match.group(0)
					i_br_dir = i_open if (s_cur_char in s_open) else i_close
					s_open_char = s_cur_char if (i_br_dir == i_open) else dic_close_open[s_cur_char]
					s_charstyle = s_open_char + s_sep + str(i_style)
					return (i_br_dir, s_cur_char, s_open_char, s_charstyle)
				def _Create_CharStyle_If_Needed(dic_charstyle_datas, s_charstyle):
					if s_charstyle in dic_charstyle_datas.keys(): return
					dic_charstyle_datas[s_charstyle] = [0, 0, None]
				def _Update_CharStyle_Counter(dic_charstyle_datas, s_charstyle, i_br_dir, i_counter):
					if i_counter is None: # in selection (forward) search
						if (i_br_dir == i_close and dic_charstyle_datas[s_charstyle][c_fw] <= 0):
							dic_charstyle_datas[s_charstyle][c_bk] += i_br_dir # TRICK : un-matched_closing are sent to bk count
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

				dic_charstyle_datas = {} # {(openchar + s_sep + style_number) : [fw count, bk count, bk pos]}
				i_chunk_base = 128 # search in chunks to limit getTextRange string size, chunks double up each time

				s_charstyle_fw = None

				b_exit_while = False
				i_chunk = i_chunk_base
				i_offset = 0
				# search all selection (TRICK : un-matched_closing in selection are sent to bk count instead of fw count),
				# and after selection stop at [first un-matched closing charstyle]
				while True: # forward search from i_start, i_offset >= 0, i_chunk > 0
					s_text = curedit.getTextRange(i_start + i_offset, min(i_start + i_offset + i_chunk, i_max))
					for o_match in pattern_brackets.finditer(s_text):
						i_pos_fw = i_start + i_offset + o_match.start()
						i_br_dir, s_cur_char, s_open_char, s_charstyle_fw = \
							_Make_Match_Datas(dic_close_open, s_open, o_match, curedit.getStyleAt(i_pos_fw))

						_Create_CharStyle_If_Needed(dic_charstyle_datas, s_charstyle_fw)
						if i_pos_fw < i_end: # in selection
							_Update_CharStyle_Counter(dic_charstyle_datas, s_charstyle_fw, i_br_dir, None)
							#print "DEBUG : in sel. : " + s_cur_char + " at " + str(i_pos_fw) + " " + str(dic_charstyle_datas[s_charstyle_fw])
						else: # after selection
							_Update_CharStyle_Counter(dic_charstyle_datas, s_charstyle_fw, i_br_dir, c_fw)
							#print "DEBUG : after sel. : " + s_cur_char + " at " + str(i_pos_fw) + " " + str(dic_charstyle_datas[s_charstyle_fw])
							# [first un-matched closing charstyle] found (un-matched closing after selection), EXIT while and search backward
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
							_Make_Match_Datas(dic_close_open, s_open, o_match, curedit.getStyleAt(i_pos_bk))

						_Create_CharStyle_If_Needed(dic_charstyle_datas, s_charstyle_bk)
						if dic_charstyle_datas[s_charstyle_bk] is None: continue # this <> charstyle was killed, skip it
						if not(dic_charstyle_datas[s_charstyle_bk][bk_pos] is None): continue # already has a bk pos, skip it
						_Update_CharStyle_Counter(dic_charstyle_datas, s_charstyle_bk, i_br_dir, c_bk)
						#print "DEBUG : backward : " + s_cur_char + " at " + str(i_pos_bk) + " " + str(dic_charstyle_datas[s_charstyle_bk])

						if dic_charstyle_datas[s_charstyle_bk][c_bk] == i_open:
							if s_charstyle_bk == s_charstyle_fw:
								if _Valid_Angle(curedit, pattern_newline, s_open_char, b_angle, b_sl_angle, i_pos_bk, i_pos_fw):
									return (i_pos_bk, i_pos_fw) # match OK, RETURN
								dic_charstyle_datas[s_charstyle_bk] = None # kill this <> charstyle quickly (avoid more newline checks)
							else: # remember bk pos (un-matched opening before selection) for future forward match
								dic_charstyle_datas[s_charstyle_bk][bk_pos] = i_pos_bk

					i_offset = i_offset - i_chunk
					if i_start + i_offset <= i_min: break
					i_chunk = i_chunk * 2
				# kill all s_charstyle without bk pos (so that they will be skipped forward)
				for s_charstyle in dic_charstyle_datas.keys():
					if not(dic_charstyle_datas[s_charstyle] is None):
						if dic_charstyle_datas[s_charstyle][bk_pos] is None:
							dic_charstyle_datas[s_charstyle] = None

				i_chunk = i_chunk_base
				i_offset = i_pos_fw + 1 - i_start
				# search from [first un-matched closing charstyle] + 1 to i_max, and check if any un-matched closing charstyle
				# matches the opening charstyle saved by the backward search in dic_charstyle_datas[s_charstyle_fw][bk_pos]
				while True: # forward search from (first un-matched)i_pos_fw + 1, i_offset >= 0, i_chunk > 0
					s_text = curedit.getTextRange(i_start + i_offset, min(i_start + i_offset + i_chunk, i_max))
					for o_match in pattern_brackets.finditer(s_text):
						i_pos_fw = i_start + i_offset + o_match.start()
						i_br_dir, s_cur_char, s_open_char, s_charstyle_fw = \
							_Make_Match_Datas(dic_close_open, s_open, o_match, curedit.getStyleAt(i_pos_fw))

						if not(s_charstyle_fw in dic_charstyle_datas.keys()): continue # this charstyle does NOT exist, skip it
						if dic_charstyle_datas[s_charstyle_fw] is None: continue # this charstyle was killed, skip it
						_Update_CharStyle_Counter(dic_charstyle_datas, s_charstyle_fw, i_br_dir, c_fw)
						#print "DEBUG : forward : " + s_cur_char + " at " + str(i_pos_fw) + " " + str(dic_charstyle_datas[s_charstyle_fw])

						# un-matched closing charstyle found, match it with the previously remembered bk pos
						if dic_charstyle_datas[s_charstyle_fw][c_fw] == i_close:
							i_pos_bk = dic_charstyle_datas[s_charstyle_fw][bk_pos]
							if _Valid_Angle(curedit, pattern_newline, s_open_char, b_angle, b_sl_angle, i_pos_bk, i_pos_fw):
								return (i_pos_bk, i_pos_fw) # match OK, RETURN
							dic_charstyle_datas[s_charstyle_fw] = None # kill this <> charstyle quickly (avoid more newline checks)

					i_offset = i_offset + i_chunk
					if i_start + i_offset >= i_max: break
					i_chunk = i_chunk * 2

				return None

			def _Match_Or_Clear_LastRange(curedit, i_start, i_end, i_indic_num, b_brackets_or_content):
				if curedit.indicatorValueAt(i_indic_num, 0) != 0:
					i_cur_start = 0 # if 1st highlight begins at 0 indicatorEnd() would give the end of 1st highlight
				else:
					i_cur_start = curedit.indicatorEnd(i_indic_num, 0) # otherwise indeed gives start of 1st highlight
				i_cur_end = curedit.indicatorEnd(i_indic_num, i_cur_start) # end of 1st highlight
				if i_cur_end == 0: return False # highlight was removed by text edition
				if b_brackets_or_content:
					i_cur_start2	= curedit.indicatorEnd(i_indic_num, i_cur_end) # start of 2nd highlight
					i_cur_end2		= curedit.indicatorEnd(i_indic_num, i_cur_start2) # end of 2nd highlight
					i_cur_startoff	= curedit.indicatorEnd(i_indic_num, i_cur_end2) # unexpected highlight if <> curedit.getTextLength()
					if i_cur_startoff != curedit.getTextLength():
						#print "DEBUG : Brackets " + "clear WHOLE DOC, should NOT happen : [" + \
						#	str(i_cur_end) + "(end)==0 OR " + str(i_cur_startoff) + "(startoff)<>" + str(curedit.getTextLength()) + "(TextLength)]"
						curedit.setIndicatorCurrent(i_indic_num)
						curedit.indicatorClearRange(0, curedit.getTextLength())
					elif (i_cur_start == i_start and i_cur_end == i_start + 1 and i_cur_start2 == i_end - 1 and i_cur_end2 == i_end):
						#print "DEBUG : Brackets " + "skip, no highlight change"
						return True
					else:
						#print "DEBUG : Brackets " + "clear range : [" + \
						#	str(i_cur_start) + "(start)>" + str(i_cur_end) + "(end) & " + str(i_cur_start2) + "(start2)>" + str(i_cur_end2) + "(end2)]"
						curedit.setIndicatorCurrent(i_indic_num)
						curedit.indicatorClearRange(i_cur_start, i_cur_end - i_cur_start)
						curedit.indicatorClearRange(i_cur_start2, i_cur_end2 - i_cur_start2)
				else:
					i_cur_startoff	= curedit.indicatorEnd(i_indic_num, i_cur_end) # unexpected highlight if <> curedit.getTextLength()
					if i_cur_startoff != curedit.getTextLength():
						#print "DEBUG : Content " + "clear WHOLE DOC, should NOT happen : [" + \
						#	str(i_cur_end) + "(end)==0 OR " + str(i_cur_startoff) + "(startoff)<>" + str(curedit.getTextLength()) + "(TextLength)]"
						curedit.setIndicatorCurrent(i_indic_num)
						curedit.indicatorClearRange(0, curedit.getTextLength())
					elif (i_cur_start == i_start and i_cur_end == i_end):
						#print "DEBUG : Content " + "skip, no highlight change"
						return True
					else:
						#print "DEBUG : Content " + "clear range : [" + \
						#	str(i_cur_start) + "(start)>" + str(i_cur_end) + "(end)]"
						curedit.setIndicatorCurrent(i_indic_num)
						curedit.indicatorClearRange(i_cur_start, i_cur_end - i_cur_start)
				return False

			if console.editor.getProperty(self.editorprop_cb_on) != str(self.option_on):
				return

			if self.getoptions:
				self.getoptions = False
				self.b_brackets	= (console.editor.getProperty(self.editorprop_brackets_on)	== str(self.option_on))
				self.b_content	= (console.editor.getProperty(self.editorprop_content_on)	== str(self.option_on))
				self.b_angle	= (console.editor.getProperty(self.editorprop_angle_on)		== str(self.option_on))
				self.b_sl_angle	= (console.editor.getProperty(self.editorprop_sl_angle_on)	== str(self.option_on))
				try:	self.i_limit_search_chars = int(console.editor.getProperty(self.editorprop_limit_chars))
				except:	self.i_limit_search_chars = self.deflimit_chars
				try:	self.i_limit_search_lines = int(console.editor.getProperty(self.editorprop_limit_lines))
				except:	self.i_limit_search_lines = self.deflimit_lines
				if (self.i_limit_search_chars < self.nolimit_search or self.i_limit_search_chars == 0):
					self.i_limit_search_chars = self.deflimit_chars
				if self.i_limit_search_lines < self.nolimit_search:
					self.i_limit_search_lines = self.deflimit_lines

			if (not(self.b_brackets) and not(self.b_content)):
				return

			curedit = editor

			# check if a new BufferID has been activated : force clear whole highlights in new active buffer and forget them
			bufferid_cur = notepad.getCurrentBufferID()
			if bufferid_cur != self.bufferid_last:
				self.bufferid_last = bufferid_cur
				curedit.setIndicatorCurrent(self.indic_num_br)
				curedit.indicatorClearRange(0, curedit.getTextLength())
				curedit.setIndicatorCurrent(self.indic_num_con)
				curedit.indicatorClearRange(0, curedit.getTextLength())
				self.had_range_br	= False
				self.had_range_con	= False

			t_ranges = _Get_Search_Ranges(curedit)
			if t_ranges is None: # visible area is outside highlight limits : no highlights update needed
				return
			i_sel_start, i_sel_end, i_min, i_max = t_ranges

			t_brackets = _MatchingBrackets_OutRange_InRange(curedit, i_sel_start, i_sel_end, i_min, i_max, self.b_angle, self.b_sl_angle)
			if t_brackets is None: # no brackets found around selection (within highlight limits) : clear last highlights and forget them
				if self.had_range_br:
					_Match_Or_Clear_LastRange(curedit, 0, 0, self.indic_num_br, True)
					self.had_range_br = False
				if self.had_range_con:
					_Match_Or_Clear_LastRange(curedit, 0, 0, self.indic_num_con, False)
					self.had_range_con = False
				return

			i_full_start	= t_brackets[0]
			i_full_end		= t_brackets[1] + 1

			if (self.had_range_br and self.b_brackets):
				b_canskip_br = _Match_Or_Clear_LastRange(curedit, i_full_start, i_full_end, self.indic_num_br, True)
			else:
				b_canskip_br = (not(self.had_range_br) and not(self.b_brackets))
			if (self.had_range_con and self.b_content):
				b_canskip_con = _Match_Or_Clear_LastRange(curedit, i_full_start + 1, i_full_end - 1, self.indic_num_con, False)
			else:
				b_canskip_con = (not(self.had_range_con) and not(self.b_content))
			if (b_canskip_br and b_canskip_con): return # skip if highlights did NOT change

			self.had_range_br	= False
			self.had_range_con	= False
			if i_full_end - i_full_start <= 2: return # skip new empty brackets, previous were cleared and forgot

			if self.b_brackets: # brackets (highlight 2 ranges of 1 char long)
				curedit.setIndicatorCurrent(self.indic_num_br)
				curedit.indicatorFillRange(i_full_start, 1)
				curedit.indicatorFillRange(i_full_end - 1, 1)
				self.had_range_br = True
			if self.b_content: # content (highlight 1 range)
				curedit.setIndicatorCurrent(self.indic_num_con)
				curedit.indicatorFillRange(i_full_start + 1, (i_full_end - 1) - (i_full_start + 1))
				self.had_range_con = True

		if self.cb_done:
			return None, None

		curedit = editor

		# try to pick 2 unused indicator numbers : from INDICATORNUMBERS.CONTAINER(8) to (INDICATORNUMBERS.IME - 1)(31)
		# skip the first 4 of them and then loop, just in case the firsts are used but their flags/styles/colors are still 0
		self.indic_num_br	= None
		self.indic_num_con	= None
		for i in range(0, INDICATORNUMBERS.IME - INDICATORNUMBERS.CONTAINER):
			i_num = ((i + 4) % (INDICATORNUMBERS.IME - INDICATORNUMBERS.CONTAINER)) + INDICATORNUMBERS.CONTAINER
			# indicators flag and styles seems to default to 0 before being set, so this one could be unused
			if (curedit.indicGetFlags(i_num) == 0 and curedit.indicGetStyle(i_num) == 0 and curedit.indicGetHoverStyle(i_num) == 0):
				# indicators fore colors seems to default to black (0, 0, 0) before being set, so (hopefully) this one is really unused
				if (curedit.indicGetFore(i_num) == (0, 0, 0) and curedit.indicGetHoverFore(i_num) == (0, 0, 0)):
					self.indic_num_br = i_num
					break
		for i in range(0, INDICATORNUMBERS.IME - INDICATORNUMBERS.CONTAINER):
			i_num = ((i + 4) % (INDICATORNUMBERS.IME - INDICATORNUMBERS.CONTAINER)) + INDICATORNUMBERS.CONTAINER
			# indicators flag and styles seems to default to 0 before being set, so this one could be unused
			if (curedit.indicGetFlags(i_num) == 0 and curedit.indicGetStyle(i_num) == 0 and curedit.indicGetHoverStyle(i_num) == 0):
				# indicators fore colors seems to default to black (0, 0, 0) before being set, so (hopefully) this one is really unused
				if (curedit.indicGetFore(i_num) == (0, 0, 0) and curedit.indicGetHoverFore(i_num) == (0, 0, 0)):
					if i_num != self.indic_num_br:
						self.indic_num_con = i_num
						break
		if (self.indic_num_br or self.indic_num_con) is None:
			return None, None

		self.SetIndicatorsOptions(self.indic_num_br, self.indic_num_con)

		# install callback 1, should be sync to ensure it is fired before UPDATEUI (avoids constant UPDATEUI when a doc is cloned)
		editor.callbackSync(_CBS_BracketInd_Modified, [SCINTILLANOTIFICATION.MODIFIED])
		# install callback 2, sync avoids flicker and other delay glitches
		editor.callbackSync(_CBS_BracketInd_UpdateUI, [SCINTILLANOTIFICATION.UPDATEUI])
		# install callback 3, to synchronize or update highlight of cloned documents, and refresh options
		notepad.callback(_CB_BracketInd_BufferActivated, [NOTIFICATION.BUFFERACTIVATED])

		self.cb_done = True
		return self.indic_num_br, self.indic_num_con
# end of class

# Main() code **************************************************************************************
def Main():
	print "[" + s_script_name + " starts] " + s_controleditscript

	# options formatting
	s_opt_info = ""
	dic_editorprop = {}
	for i in range(0, len(t_option_key)):
		if t_option_key[i] == "":
			s_opt_info = s_opt_info + "\n\t"
			continue
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
		i_indic_num_br, i_indic_num_con = o_bracketindicator_cb.RegCallback()
		if (i_indic_num_br or i_indic_num_con) is None:
			console.writeError("\t" + s_callback_name + " registering FAILED /!\\ [" + s_nofreeindicators + "]" + "\n")
			console.show()
			notepad.messageBox(s_callback_name + " registering FAILED /!\\" + "\n\n" + s_nofreeindicators, \
				s_script_name, MESSAGEBOXFLAGS.ICONSTOP)
		else:
			console.editor.setProperty(s_editorprop_cb_reg, str(i_true))
			console.editor.setProperty(s_editorprop_cb_on, str(i_true))
			console.editor.setProperty(s_editorprop_indic_num_br, str(i_indic_num_br))
			console.editor.setProperty(s_editorprop_indic_num_con, str(i_indic_num_con))
			o_bracketindicator_cb.Ugly_UpdateVisTabsHighlight()
			print \
				"\t" + s_callback_name + " registered and activated [indicator numbers=" + str(i_indic_num_br) + "," + str(i_indic_num_con) + "]" + \
				" (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
			print "\t" + s_opt_info + s_opt_warn
		return

	if console.editor.getProperty(s_editorprop_cb_on) != str(i_true):
		console.editor.setProperty(s_editorprop_cb_on, str(i_true))

		o_bracketindicator_cb.SetIndicatorsOptions( \
			int(console.editor.getProperty(s_editorprop_indic_num_br)), int(console.editor.getProperty(s_editorprop_indic_num_con)))
		o_bracketindicator_cb.Ugly_UpdateVisTabsHighlight()
		print "\t" + s_callback_name + " re-activated (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info + s_opt_warn
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_callback_name + " re-activated" + "\n\n" + \
				s_reruntogglecb + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n").replace("\t", "") + s_opt_warn.replace("\t", "\n").replace(", ", ",\n") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONINFORMATION)
	else:
		console.editor.setProperty(s_editorprop_cb_on, str(i_false))

		o_bracketindicator_cb.Ugly_ClearAllTabsHighlights( \
			int(console.editor.getProperty(s_editorprop_indic_num_br)), int(console.editor.getProperty(s_editorprop_indic_num_con)))
		print "\t" + s_callback_name + " DE-ACTIVATED /!\\ (" + s_reruntogglecb + ". " + s_willapplynewopt + ")"
		print "\t" + s_opt_info + s_opt_warn
		print "\t" + "(Bracket highlightings have been cleared from all opened documents)"
		if str(i_option_toggle_msgbox) == str(i_true):
			notepad.messageBox( \
				s_callback_name + " DE-ACTIVATED /!\\" + "\n\n" + \
				s_reruntogglecb + "\n" + s_willapplynewopt + "\n\n" + \
				s_opt_info.replace(", ", "\n").replace("\t", "") + s_opt_warn.replace("\t", "\n").replace(", ", ",\n") + "\n\n" + \
				s_controleditscript, \
				s_script_name, MESSAGEBOXFLAGS.ICONEXCLAMATION)

Main()
