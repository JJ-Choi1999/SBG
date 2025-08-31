import os

from docx2markdown_custom import docx_to_markdown_custom
from docx2markdown import docx_to_markdown

def docx_to_md1(docx_path: str, md_path: str = None) -> str:
    pass

def docx_to_md(docx_path: str, md_path: str = None) -> str:
    if not md_path:
        file_name = os.path.splitext(os.path.basename(docx_path))[0]
        md_path = os.path.join(os.path.dirname(docx_path), f'{file_name}.md')

    try:
        docx_to_markdown(docx_path, md_path)
    except:
        return ''

    return md_path