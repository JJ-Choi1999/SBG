from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE

from common.file.document_covert.pdf_to_docx import pdf_to_docx


def extra_paragraph(docx_path):
    para_texts = []
    docx = Document(docx_path)
    for para in docx.paragraphs:
        para_text = ''
        for run in para.runs:
            para_text += run.text
        # para_texts.append(para.text)
        para_texts.append(para_text)

    return para_texts

def extra_table(docx_path):
    cell_texts = []
    docx = Document(docx_path)
    for table in docx.tables:
        for row in table.rows:
            for cell in row.cells:
                cell_texts.append(cell.text)

    return cell_texts

if __name__ == '__main__':

    import json

    # pdf_path = r'D:\AiAgent\SBG\common\file\document_extra\Clearstream FAQs – Clearing mandate for U.S. Treasury securities – U.S.A_.pdf'
    # docx_path = pdf_to_docx(pdf_path)
    # # print(f'docx_path:', docx_path)
    docx_path = r'D:\AiAgent\SBG\common\file\document_extra\Clearstream FAQs – Clearing mandate for U.S. Treasury securities – U.S.A_.docx'
    # # para_texts = extra_paragraph(docx_path)
    # #
    # # print(json.dumps(para_texts, ensure_ascii=False, indent=2))
    #
    docx = Document(docx_path)
    for para in docx.paragraphs:
        print(para.text)