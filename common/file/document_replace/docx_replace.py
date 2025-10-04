import numpy as np
import xml.etree.ElementTree as ET

from docx import Document
from docx.table import Table, _Cell


def replace_paragraph_text(docx_path, old_text, new_text):
    docx = Document(docx_path)
    for para in docx.paragraphs:
        if old_text in para.text:
            para.text = para.text.replace(old_text, new_text)
    # doc.save("updated_" + doc_path)
    docx.save(docx_path)

    return docx_path

def replace_table_text(docx_path, old_text, new_text):
    docx = Document(docx_path)
    for table in docx.tables:
        for row in table.rows:
            for cell in row.cells:
                if old_text in cell.text:
                    cell.text = cell.text.replace(old_text, new_text)
    # doc.save("updated_" + doc_path)
    docx.save(docx_path)

    return docx_path

def is_merged_cell(cell: _Cell):
    """
    判断单元格是否为合并单元格（横向或纵向）
    """
    # 获取单元格的 XML 元素
    xml_cell = cell._element
    xml_str = ET.tostring(xml_cell, encoding='utf-8').decode('utf-8')

    # 检查是否有横向合并（w:gridSpan）
    if ':gridSpan' in xml_str:
        return True

    # 检查是否有纵向合并（w:merge）
    if ':vMerge' in xml_str:
        return True

    return False

def merge_cells_by_value(table: Table) -> Table:
    """
    合并表格中内容相同的相邻单元格（包括行方向和列方向）
    :param table: 表格对象
    """
    # 初始化合并矩阵
    merged_arr = np.zeros((len(table.rows), len(table.columns)), dtype=bool)

    # 记录合并矩阵, 需要合并单元格信息
    for row_index, row in enumerate(table.rows):
        for cell_index, cell in enumerate(row.cells):
            # 记录需要合并的单元格
            is_merge = is_merged_cell(cell)
            if is_merge:
                merged_arr[row_index, cell_index] = is_merge

    # 首先处理行方向的合并
    for col_index in range(len(table.columns)):
        start_row = 0
        while start_row < len(table.rows):
            current_value = table.cell(start_row, col_index).text.strip()
            end_row = start_row

            while end_row + 1 < len(table.rows) and table.cell(end_row + 1, col_index).text.strip() == current_value:
                end_row += 1

            if start_row != end_row and merged_arr[start_row, col_index] and merged_arr[end_row, col_index]:
                # print(f'行合并, 左单元格: [{start_row}, {col_index}], 右单元格: [{end_row}, {col_index}]')
                source_text = table.cell(start_row, col_index).text
                table.cell(start_row, col_index).merge(table.cell(end_row, col_index))
                table.cell(start_row, col_index).text = source_text

            start_row = end_row + 1

    # 然后处理列方向的合并
    for row_index in range(len(table.rows)):
        start_col = 0
        while start_col < len(table.columns):
            current_value = table.cell(row_index, start_col).text
            end_col = start_col

            while end_col + 1 < len(table.columns) and table.cell(row_index, end_col + 1).text == current_value:
                end_col += 1

            if start_col != end_col and merged_arr[row_index, start_col] and merged_arr[row_index, end_col]:
                # print(f'列合并, 左单元格: [{row_index}, {start_col}], 右单元格: [{row_index}, {end_col}]')
                source_text = table.cell(row_index, start_col).text
                table.cell(row_index, start_col).merge(table.cell(row_index, end_col))
                table.cell(row_index, end_col).text = source_text

            start_col = end_col + 1

    return table

if __name__ == '__main__':
    # # 示例：替换段落中的 "旧文字" 为 "新文字"
    # replace_paragraph_text("example.docx", "旧文字", "新文字")
    # # 示例：替换表格中的 "旧文字" 为 "新文字"
    # replace_table_text("example.docx", "旧文字", "新文字")

    docx_path = r"C:\Users\Lenovo\Desktop\esunfhc_annual_2024.docx"
    docx = Document(docx_path)
    for para in docx.paragraphs:
        print(f'para.text:', para.text)

    for table in docx.tables:
        for row in table.rows:
            for cell in row.cells:
                print(f'cell.text:', cell.text)