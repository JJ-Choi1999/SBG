import re

def contains_chinese_full(text):
    return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df]', text))