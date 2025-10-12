import json
import re

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Length, Pt, Inches, RGBColor
from docx.text.paragraph import Paragraph

from common.file.document_replace.docx_replace import merge_cells_by_value


class DocxFormatAdjust:

    def __init__(
        self,
        input_docx: str,
        output_docx: str = None,
        is_merge_cells: bool = False,
        format_type: str = 'default',
        header_style: str = 'page_header',
        footer_style: str = 'page_footer',
        page_number_style: str = 'page_number',
        format_map: dict = None,
    ):

        self.__input_docx = input_docx
        self.__output_docx = output_docx
        self.__format_type = format_type
        self.__header_style = header_style
        self.__footer_style = footer_style
        self.__page_number_style = page_number_style
        self.__is_merge_cells = is_merge_cells

        if not self.__output_docx: self.__output_docx = self.__input_docx

        self.__format_map = {'澳門中銀文檔標準模板（2024）': {'Normal': [{'regular': '^关于.*?的汇报.*', 'is_break': 1.0, 'line_spacing': 29.0, 'space_before': 0.5, 'space_after': 0.5, 'zh_font': 'STZhongsong', 'en_font': 'Times New Roman', 'font_size': 20.0, 'is_bold': True, 'is_italic': False}, {'regular': '^汇报部门.*', 'is_break': 1.0, 'line_spacing': 29.0, 'zh_font': 'STKaiti', 'en_font': 'Times New Roman', 'font_size': 16.0, 'is_bold': True}, {'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'FangSong', 'en_font': 'Times New Roman', 'font_size': 16.0, 'is_bold': False}], 'Heading 1': [{'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'SimHei', 'en_font': 'Times New Roman', 'font_size': 16.0}], 'Heading 2': [{'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'STKaiti', 'en_font': 'Times New Roman', 'font_size': 16.0, 'is_bold': True}], 'Heading 3': [{'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'FangSong', 'en_font': 'Times New Roman', 'font_size': 16.0}], 'Heading 4': [{'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'FangSong', 'en_font': 'Times New Roman', 'font_size': 16.0}], 'Body Text Indent 2': [{'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'FangSong', 'en_font': 'Times New Roman', 'font_size': 16.0, 'is_bold': False}], 'Table.Cell Body Text Indent 2': [{'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'FangSong', 'en_font': 'Times New Roman', 'font_size': 16.0, 'is_bold': False}], 'page_header': [{'para_text': '文档密级', 'alignment': 0.0, 'zh_font': 'Kaiti', 'en_font': 'Times New Roman', 'font_size': 18.0}], 'page_footer': [{'para_text': '[文件日期]: 2025-10-10', 'alignment': 0.0, 'zh_font': 'Kaiti', 'en_font': 'Times New Roman', 'font_size': 14.0}], 'page_number': [{'alignment': 1.0, 'zh_font': 'Kaiti', 'en_font': 'Times New Roman', 'font_size': 10.0, 'docx_xml': ['<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:fldChar w:fldCharType="begin" w:dirty="1"/><w:instrText xml:space="preserve"> PAGE </w:instrText><w:fldChar w:fldCharType="separate"/><w:fldChar w:fldCharType="end"/></w:r>', '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:t xml:space="preserve"> / </w:t></w:r><w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:fldChar w:fldCharType="begin" w:dirty="1"/><w:instrText xml:space="preserve"> NUMPAGES </w:instrText><w:fldChar w:fldCharType="separate"/><w:fldChar w:fldCharType="end"/></w:r>']}]}, '行長經營管理專題會觀點摘錄（2025年第X號）': {'Normal': [{'regular': '^\\d{4}-\\d{2}-\\d{2}會議觀點摘錄$', 'is_break': 1.0, 'alignment': 1.0, 'zh_font': 'STZhongsong', 'en_font': 'Times New Roman', 'font_size': 22.0}, {'regular': '（僅供參考，不代表會議決策）', 'is_break': 1.0, 'alignment': 1.0, 'zh_font': 'STZhongsong', 'en_font': 'Times New Roman', 'font_size': 12.0}], 'Table.Cell List Paragraph': [{'alignment': 0.0, 'line_spacing': 29.0, 'zh_font': 'PMingLiU', 'en_font': 'Times New Roman', 'font_size': 16.0}], 'page_number': [{'alignment': 1.0, 'zh_font': 'Kaiti', 'en_font': 'Times New Roman', 'font_size': 10.0, 'docx_xml': ['<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:fldChar w:fldCharType="begin" w:dirty="1"/><w:instrText xml:space="preserve"> PAGE </w:instrText><w:fldChar w:fldCharType="separate"/><w:fldChar w:fldCharType="end"/></w:r>']}]}, '行長經營管理專題會會議紀要（2025年第X號）': {'Normal': [{'regular': '^（\\d{4}年第\\d+號）$', 'is_break': 1.0, 'alignment': 1.0, 'zh_font': 'PMingLiU', 'en_font': 'Times New Roman', 'font_size': 14.0, 'is_bold': True}, {'regular': '^(正文新細(.*?)。)', 'alignment': 3.0, 'line_spacing': 29.0, 'first_line_indent': 2.0, 'zh_font': 'PMingLiU', 'en_font': 'Times New Roman', 'font_size': 16.0}, {'alignment': 3.0, 'line_spacing': 29.0, 'zh_font': 'PMingLiU', 'en_font': 'Times New Roman', 'font_size': 16.0}, {'run_regular': '時間|地點|主持|出席|列席|記錄|議題|內容', 'alignment': 0.0, 'is_bold': True}], 'page_number': [{'alignment': 1.0, 'zh_font': 'Kaiti', 'en_font': 'Times New Roman', 'font_size': 10.0, 'docx_xml': ['<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:fldChar w:fldCharType="begin" w:dirty="1"/><w:instrText xml:space="preserve"> PAGE </w:instrText><w:fldChar w:fldCharType="separate"/><w:fldChar w:fldCharType="end"/></w:r>']}]}}

        print(json.dumps(self.__format_map, ensure_ascii=False, indent=2))

        self.__docx = Document(self.__input_docx)

    def run(self):

        if self.__format_map.get(self.__format_type, {}).get(self.__header_style, []):
            self.format_adjust_header(style_name=self.__header_style)

        if self.__format_map.get(self.__format_type, {}).get(self.__footer_style, []):
            self.format_adjust_footer(style_name=self.__footer_style)

        if self.__format_map.get(self.__format_type, {}).get(self.__page_number_style, []):
            self.format_adjust_page_number(style_name=self.__page_number_style)

        self.format_adjust_paras()
        self.format_adjust_tables()

        self.__docx.save(self.__output_docx)

        return self.__output_docx

    def format_adjust_header(self, style_name: str = 'page_header'):

        for section in self.__docx.sections:
            header = section.header
            if not header.paragraphs:
                header.add_paragraph(text='header_holder')

            for para in header.paragraphs:
                if not para.text: para.text = 'header_holder'
                format_rules = self.__format_map.get(self.__format_type, {}).get(style_name, [])
                if not format_rules: continue
                self.__format_adjust_para(para=para, format_rules=format_rules)

    def format_adjust_footer(self, style_name: str = 'page_footer'):

        for section in self.__docx.sections:
            footer = section.footer
            if not footer.paragraphs:
                footer.add_paragraph(text='footer_holder')

            for para in footer.paragraphs:
                if not para.text: para.text = 'footer_holder'
                format_rules = self.__format_map.get(self.__format_type, {}).get(style_name, [])
                if not format_rules: continue
                self.__format_adjust_para(para=para, format_rules=format_rules)

    def format_adjust_page_number(self, style_name: str = 'page_footer'):

        # 获取所有节
        for section in self.__docx.sections:
            # 获取页脚
            footer = section.footer
            # 清除现有页脚内容
            for paragraph in footer.paragraphs:
                paragraph.clear()

            # 创建新的页脚段落
            p = footer.paragraphs[0]

            format_rules = self.__format_map.get(self.__format_type, {}).get(style_name, [])
            if not format_rules: continue
            self.__format_adjust_para(para=p, format_rules=format_rules, is_filter_null=False)

    def format_adjust_tables(self):
        for table in self.__docx.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        format_rules = self.__format_map.get(self.__format_type, {}).get(
                            f'Table.Cell {para.style.name}', [])
                        if not format_rules: continue
                        self.__format_adjust_para(para=para, format_rules=format_rules)

            if self.__is_merge_cells:
                merge_cells_by_value(table=table)

    def format_adjust_paras(self):
        for para in self.__docx.paragraphs:
            format_rules = self.__format_map.get(self.__format_type, {}).get(para.style.name, [])
            if not format_rules: continue
            self.__format_adjust_para(para=para, format_rules=format_rules)

    def __format_adjust_para(self, para: Paragraph, format_rules: list[dict] = None, is_filter_null: bool = True):

        if not format_rules: return

        is_break: bool = False
        for rule_index, format_rule in enumerate(format_rules):

            if is_break: break

            if is_filter_null and not para.text: continue

            for fr_key, fr_val in format_rule.items():

                if fr_key == 'regular' and fr_val is not None and not re.findall(fr_val, para.text, re.DOTALL): break

                print(f'({rule_index + 1}) para.text: {para.text}, fr_key: {fr_key}, fr_val: {fr_val}')

                run_regular = format_rule.get('run_regular')

                if fr_key == 'line_spacing' and fr_val is not None:
                    para.paragraph_format.line_spacing = Length(fr_val * Length._EMUS_PER_PT)

                if fr_key == 'space_before' and fr_val is not None:
                    para.paragraph_format.space_before = Pt(round(fr_val * 12, 2))

                if fr_key == 'space_after' and fr_val is not None:
                    para.paragraph_format.space_after = Pt(round(fr_val * 12, 2))

                if fr_key == 'first_line_indent' and fr_val is not None:
                    # 0.2 英寸越等于一个字符
                    para.paragraph_format.first_line_indent = Inches(round(fr_val * 0.2, 2))

                if fr_key == 'alignment' and fr_val is not None:
                    para.alignment = fr_val

                if fr_key == 'para_text' and fr_val is not None:
                    para.text = fr_val

                if fr_key == 'is_bold' and fr_val is not None:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        run.bold = fr_val

                if fr_key == 'is_italic' and fr_val is not None:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        run.italic = fr_val

                if fr_key == 'is_underline' and fr_val is not None:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        run.underline = fr_val

                if fr_key == 'zh_font' and fr_val is not None:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        try:
                            # 中文系统字体名
                            run.font.name = fr_val
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), fr_val)
                        except Exception as e:
                            print(f'para.style.name: {para.style.name}, 异常文本: {run.text}')

                if fr_key == 'en_font' and fr_val is not None:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        run.font.name = fr_val

                if fr_key == 'font_size' and fr_val is not None:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        run.font.size = Pt(fr_val)

                if fr_key == 'font_color' and fr_val:
                    for run in para.runs:
                        if run_regular and not re.findall(run_regular, run.text, re.DOTALL): continue
                        run.font.color.rgb = RGBColor(*fr_key)

                if fr_key == 'docx_xml' and fr_val is not None:
                    # 添加页码和总页数域
                    run = para.add_run()
                    # 迭代构建页码和总页数域的XML
                    for xml in fr_val:
                        print(f'xml: {xml}')
                        # 添加xml到docx
                        run._element.append(parse_xml(xml))

                if fr_key == 'is_break' and fr_val is not None:
                    is_break = True

if __name__ == '__main__':
    format_map: dict = {
        'default': {
            'Normal': [
                {
                    'regular': r'^关于.*?的汇报.*'
                },
                {
                    'regular': r'^汇报部门.*'
                },
            ],
            'Heading': [],
            'Body Text Indent 2': []
        }
    }

    # text = f'关于XXX的汇报（华文中宋/STZhongsong 20号，加粗，行距固定值29点/磅，段前段後0.5行）'
    # # text = f'汇报部门（楷体Kaiti/STKaiti 16号加粗，行距固定值29点/磅）'
    # format_rules = format_map['default']['Normal']
    # regular = format_rules[0]['regular']
    # re_result = re.findall(regular, text)
    # print(f'regular:', regular)
    # print(f're_result:', re_result)

    input_docx = r'D:\AiAgent\SBG\common\file\document_format_adjust\行長經營管理專題會觀點摘錄（2025年第X號）.docx'
    output_docx = r'D:\AiAgent\SBG\common\file\document_format_adjust\行長經營管理專題會觀點摘錄（2025年第X號）_1.docx'

    dfa = DocxFormatAdjust(input_docx, output_docx, format_type='行長經營管理專題會觀點摘錄（2025年第X號）')
    dfa.run()

    # text = f'正文新細明體16號，英文及數字Times New Roman，行距固定值29點，首行縮進2字元。'
    # parrten = r'^(正文新細(.*?)。)'
    # print(re.findall(parrten, text, re.DOTALL))