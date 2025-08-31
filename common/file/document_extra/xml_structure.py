from lxml import etree

import lxml

xml_path = r'/test_files/extra.xml'
with open(xml_path, 'r', encoding='utf-8') as f:
    data = f.read()

root = etree.fromstring(data)
print(f'root:', root.tag)
print(len(root.findall('p')))
# for subchild in root.xpath('//child[@id="1"]/subchild'):
#     print(subchild.text)  # 输出 Content A