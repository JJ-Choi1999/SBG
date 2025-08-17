from docx import Document

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

if __name__ == '__main__':
    # 示例：替换段落中的 "旧文字" 为 "新文字"
    replace_paragraph_text("example.docx", "旧文字", "新文字")
    # 示例：替换表格中的 "旧文字" 为 "新文字"
    replace_table_text("example.docx", "旧文字", "新文字")