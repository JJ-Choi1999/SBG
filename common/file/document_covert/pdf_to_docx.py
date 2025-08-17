import os
import fitz

from pdf2docx import Converter

from common.file.file_info import extract_file_type, extract_file_path


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
        docx_path = os.path.join(os.path.dirname(pdf_path), f'{os.path.splitext(os.path.basename(pdf_path))[0]}.docx')

    # 创建转换器对象
    cv = Converter(pdf_path)
    cv.default_settings['multi_processing'] = True
    # 执行转换（转换所有页面）
    cv.convert(docx_path, start=start_num, end=end_num)
    # 关闭资源
    cv.close()

    return docx_path

def convert_pdf_images_to_rgb(pdf_path, output_pdf_path):
    with fitz.open(pdf_path) as doc:
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                # 使用 PIL 转换为 RGB 格式
                from PIL import Image
                from io import BytesIO
                pil_img = Image.open(BytesIO(image_data))
                pil_img = pil_img.convert("RGB")  # 强制转为 RGB
                pil_img.save(f"temp_{xref}.jpg", "JPEG")  # 保存为 JPEG（RGB 格式）
        doc.save(output_pdf_path)  # 保存为新 PDF

    return output_pdf_path

if __name__ == '__main__':
    import json
    pdf_path: str = r"C:\Users\Lenovo\Downloads\esunfhc_annual_2024.pdf"
    # pdf_path = r"E:\downloads\玄姐AGI-三天训练营\Day1\大模型应用开发项目实战训练营——Agent开发篇.pdf"
    # pdf_path = r'D:\AiAgent\SBG\common\file\document_covert\output_rgb_converted.pdf'
    file_type_info = extract_file_type(pdf_path)
    file_path_info = extract_file_path(pdf_path)
    print(json.dumps(file_type_info, ensure_ascii=False, indent=2))
    print(json.dumps(file_path_info, ensure_ascii=False, indent=2))

    steps = []
    for i in range(0, 200, 5):
        steps.append(i)

    # for i in range(len(steps) - 1):
    #     print(f'[{steps[i]}: {steps[i+1]}]')
    #     start_num = steps[i]
    #     end_num = steps[i+1]
    #     docx_path = os.path.join(
    #         file_path_info.get('file_dir'),
    #         f'{os.path.splitext(file_path_info.get('file_name'))[0]}_{start_num}_{end_num}.docx'
    #     )
    #     convert_path = pdf_to_docx(
    #         pdf_path=pdf_path,
    #         start_num=start_num,
    #         end_num=end_num
    #     )
    #     print(f'docx_path:', docx_path, ', convert_path:', convert_path)

    # output_pdf_path = os.path.join(os.path.dirname(pdf_path), f'output_{os.path.basename(pdf_path)}')
    convert_path = pdf_to_docx(
        pdf_path=pdf_path,
        start_num=0,
        end_num=5
    )