import re

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Length, Pt, Inches
from docx.text.paragraph import Paragraph

from common.file.document_replace.docx_replace import merge_cells_by_value


class DocxFormatAdjust:

    def __init__(
        self,
        input_docx: str,
        output_docx: str = None,
        format_type: str = 'default',
        header_style: str = 'page_header',
        footer_style: str = 'page_footer'
    ):

        self.__input_docx = input_docx
        self.__output_docx = output_docx
        self.__format_type = format_type
        self.__header_style = header_style
        self.__footer_style = footer_style

        if not self.__output_docx: self.__output_docx = self.__input_docx

        self.__format_map: dict = {
            'default': {
                'Normal': [
                    {
                        'regular': r'^关于.*?的汇报.*',
                        'line_spacing': 29,
                        'space_before': 0.5,
                        'space_after': 0.5,
                        'zh_font': 'STZhongsong',
                        'font_size': 20,
                        'is_bold': True,
                        'is_italic': False,
                        'is_break': True,
                    },
                    {
                        'regular': r'^汇报部门.*',
                        'line_spacing': 29,
                        'zh_font': 'STKaiti',
                        'font_size': 16,
                        'is_bold': True,
                        'is_break': True,
                    },
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'FangSong',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                        'is_bold': False,
                    }
                ],
                'Heading 1': [
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'SimHei',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                    }
                ],
                'Heading 2': [
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'STKaiti',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                        'is_bold': True,
                    }
                ],
                'Heading 3': [
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'FangSong',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                    }
                ],
                'Heading 4': [
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'FangSong',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                    }
                ],
                'Body Text Indent 2': [
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'FangSong',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                        'is_bold': False,
                    }
                ],
                '[Table.Cell]Body Text Indent 2': [
                    {
                        'line_spacing': 29,
                        'first_line_indent': 2,
                        'zh_font': 'FangSong',
                        'en_font': 'Times New Roman',
                        'font_size': 16,
                        'is_bold': False,
                    }
                ],
                'page_header': [
                    {
                        'para_text': '文档密级',
                        'alignment': WD_PARAGRAPH_ALIGNMENT.LEFT,
                        'font_size': 18,
                        'zh_font': 'Kaiti',
                        'en_font': 'Times New Roman',
                    }
                ],
                'page_footer': [
                    {
                        # 'para_text': '文档密级',
                        'record_page': True,
                        'alignment': WD_PARAGRAPH_ALIGNMENT.CENTER,
                        'font_size': 10,
                        'zh_font': 'Kaiti',
                        'en_font': 'Times New Roman',
                    }
                ],
            }
        }

        self.__docx = Document(self.__input_docx)

    def run(self):

        self.format_adjust_header(style_name=self.__header_style)
        self.format_adjust_footer(style_name=self.__footer_style)
        self.format_adjust_paras()
        self.format_adjust_tables()

        self.__docx.save(self.__output_docx)

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

        for section_index, section in enumerate(self.__docx.sections):
            footer = section.footer
            if not footer.paragraphs:
                footer.add_paragraph(text='footer_holder')

            for para in footer.paragraphs:
                if not para.text: para.text = 'footer_holder'
                format_rules = self.__format_map.get(self.__format_type, {}).get(style_name, [])
                if not format_rules: continue

                if format_rules[0].get('record_page'):
                    format_rules[0]['para_text'] = f'{section_index + 1} / {len(self.__docx.sections)}'

                self.__format_adjust_para(para=para, format_rules=format_rules)

    def format_adjust_tables(self):
        for table in self.__docx.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        format_rules = self.__format_map.get(self.__format_type, {}).get(
                            f'[Table.Cell]{para.style.name}', [])
                        if not format_rules: continue
                        self.__format_adjust_para(para=para, format_rules=format_rules)

            merge_cells_by_value(table=table)

    def format_adjust_paras(self):
        for para in self.__docx.paragraphs:
            format_rules = self.__format_map.get(self.__format_type, {}).get(para.style.name, [])
            if not format_rules: continue
            self.__format_adjust_para(para=para, format_rules=format_rules)

    def __format_adjust_para(self, para: Paragraph, format_rules: list[dict] = None):

        if not format_rules: return

        is_break: bool = False
        for rule_index, format_rule in enumerate(format_rules):

            if is_break: break

            if not para.text: continue

            for fr_key, fr_val in format_rule.items():

                if fr_key == 'regular' and fr_val and not re.findall(fr_val, para.text, re.DOTALL): break

                print(f'({rule_index + 1}) para.text: {para.text}, fr_key: {fr_key}, fr_val: {fr_val}')

                if fr_key == 'line_spacing' and fr_val:
                    para.paragraph_format.line_spacing = Length(fr_val * Length._EMUS_PER_PT)

                if fr_key == 'space_before' and fr_val:
                    para.paragraph_format.space_before = Pt(round(fr_val * 12, 2))

                if fr_key == 'space_after' and fr_val:
                    para.paragraph_format.space_after = Pt(round(fr_val * 12, 2))

                if fr_key == 'first_line_indent' and fr_val:
                    # 0.2 英寸越等于一个字符
                    para.paragraph_format.first_line_indent = Inches(round(fr_val * 0.2, 2))

                if fr_key == 'alignment' and fr_val:
                    para.alignment = fr_val

                if fr_key == 'para_text' and fr_val:
                    para.text = fr_val

                if fr_key == 'is_bold' and fr_val:
                    for run in para.runs:
                        run.bold = True

                if fr_key == 'is_italic' and fr_val:
                    for run in para.runs:
                        run.italic = True

                if fr_key == 'is_underline' and fr_val:
                    for run in para.runs:
                        run.underline = True

                if fr_key == 'zh_font' and fr_val:
                    for run in para.runs:
                        try:
                            # 中文系统字体名
                            run.font.name = fr_val
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), fr_val)
                        except Exception as e:
                            print(f'para.style.name: {para.style.name}, 异常文本: {run.text}')

                if fr_key == 'en_font' and fr_val:
                    for run in para.runs:
                        run.font.name = fr_val

                if fr_key == 'font_size' and fr_val:
                    for run in para.runs:
                        run.font.size = Pt(fr_val)

                if fr_key == 'is_break' and fr_val:
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

    input_docx = r'D:\AiAgent\SBG\test\format_adjust\澳門中銀文檔標準模板（2024）_1.docx'
    output_docx = r'D:\AiAgent\SBG\test\format_adjust\澳門中銀文檔標準模板（2024）_2.docx'

    dfa = DocxFormatAdjust(input_docx, output_docx)
    dfa.run()

    # text = '，首行缩进2字元；全文英文及数字Times New Roman，行距固定值29点/磅，下同。文中结构层次序数依次用“一、”“（一）”“1.”“（1）”标注。）'
    # pattern = r'[\u4e00-\u9fa5]+'
    # print(re.findall(pattern, text, re.DOTALL))
    # # ['首行缩进', '字元', '全文英文及数字', '行距固定值', '点', '磅', '下同', '文中结构层次序数依次用', '一', '一', '标注']
