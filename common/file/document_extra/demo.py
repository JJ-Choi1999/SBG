from docx import Document
from xml.etree import ElementTree as ET
from xml.dom import minidom


def generate_and_pretty_print_xml(docx_path):
    """
    使用 python-docx 生成文档的 XML 结构并格式化打印
    :param docx_path: .docx 文件路径
    """
    doc = Document(docx_path)

    # 获取文档的 XML 元素
    xml_element = doc._element

    # 将 XML 元素转换为字符串
    xml_str = ET.tostring(xml_element, encoding="utf-8")

    # 使用 minidom 格式化 XML
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")

    # 去除多余的空行
    lines = [line for line in pretty_xml.splitlines() if line.strip()]
    print("\n".join(lines))

docx_path = r'D:\AiAgent\SBG\common\file\document_extra\Clearstream FAQs – Clearing mandate for U.S. Treasury securities – U.S.A_.docx'
# with open(docx_path, 'rb') as f:
#     # print(f.read())
#     bd = f.read()
#
# with open(docx_path, 'wb') as f:
#     f.write(bd)

generate_and_pretty_print_xml(docx_path)