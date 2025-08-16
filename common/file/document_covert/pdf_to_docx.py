import os
import filetype

from pdf2docx import Converter

from common.file.file_info import extract_file_type


def pdf_to_docx(pdf_path: str, start_num: int = 0, end_num: int | None = None, docx_path: str | None = None) -> str:
    """
    pdf 转 docx, 输入一个pdf文件地址, 根据[start_num: end_num]转换指定页数的pdf页, 返回转换后的docx文件地址
    :param pdf_path: pdf 文件地址
    :param start_num: 需要转换的pdf起始页(最小位下标为0)
    :param end_num: 需要转换的pdf末尾页(为None表示一直转换到末尾)
    :param docx_path: pdf转换后docx的保存地址, 不填默认为 pdf 同文件夹下生成同名 docx 文件
    :return:
    """
    if not docx_path:
        docx_path = os.path.join(os.path.dirname(pdf_path), f'{os.path.basename(pdf_path)}.docx')

    # 创建转换器对象
    cv = Converter(pdf_path)
    # 执行转换（转换所有页面）
    cv.convert(docx_path, start=start_num, end=end_num)
    # 关闭资源
    cv.close()

    return docx_path

if __name__ == '__main__':
    import json
    pdf_path: str = r"E:\downloads\玄姐AGI-三天训练营\Day1\大模型应用开发项目实战训练营——Agent开发篇.pdf"
    file_type = extract_file_type(pdf_path)
    print(json.dumps(file_type, ensure_ascii=False, indent=2))

    docx_path = pdf_to_docx(pdf_path=pdf_path)
    print(f'docx_path:', docx_path)