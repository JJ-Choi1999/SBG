import numpy as np
from docx import Document
from docx.table import Table


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

def merge_cells_by_value(table: Table, merged_arr: np.ndarray) -> Table:
    """
    合并表格中内容相同的相邻单元格（包括行方向和列方向）
    :param table: 表格对象
    """
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