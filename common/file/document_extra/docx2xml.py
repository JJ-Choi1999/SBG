import os.path

import lxml
from docx import Document
from xml.etree import ElementTree as ET
from xml.dom import minidom

from docx.opc.oxml import BaseOxmlElement
from docx.oxml import CT_Document


def generate_and_pretty_print_xml(docx_path):
    """
    使用 python-docx 生成文档的 XML 结构并格式化打印
    :param docx_path: .docx 文件路径
    """
    doc = Document(docx_path)

    # 获取文档的 XML 元素
    xml_element = doc._element
    doc._element = lxml.etree.fromstring(xml_element.xml)
    print(xml_element.xml)

    # 将 XML 元素转换为字符串
    xml_str = ET.tostring(xml_element, encoding="utf-8")

    # 使用 minidom 格式化 XML
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")

    # 去除多余的空行
    lines = [line for line in pretty_xml.splitlines() if line.strip()]

    with open(os.path.join(os.getcwd(), f'extra.xml'), 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    file_path = os.path.join(
        os.path.dirname(docx_path),
        f'{os.path.splitext(os.path.basename(docx_path))[0]}_1.docx'
    )
    doc.save(file_path)