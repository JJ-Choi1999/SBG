import ast

import pandas as pd
import json

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING

excel_path = r"C:\Users\Lenovo\Downloads\格式調整規則.xlsx"
# 读取 Excel 文件
df = pd.read_excel(excel_path)

zh2en_map= {
    '段落正則': 'regular',
    '段落跳出': 'is_break',
    '段落文本': 'para_text',
    '文本块正则': 'run_regular',
    '水平對齊': 'alignment',
    '行距(倍數)': 'line_spacing_rule',
    '行距(磅)': 'line_spacing',
    '段前(磅)': 'space_before',
    '段後(磅)': 'space_after',
    '首行縮進(字符)': 'first_line_indent',
    '中文字體': 'zh_font',
    '英文字體': 'en_font',
    '字號': 'font_size',
    '字體顔色': 'font_color',
    '是否粗體': 'is_bold',
    '是否斜體': 'is_italic',
    '是否下劃綫': 'is_underline',
    '頁碼xml列表': 'docx_xml'
}

multiple_map = {
    1: 0,
    1.5: 1,
    2: 2,
    'at_least': 3,
    'exactly': 4,
    'multiple': 5
}

# 初始化结果字典
result = {}

# 动态获取列 C 到列 G 的列名（假设列 A 是第 0 列，列 B 是第 1 列）
columns_c_to_g = df.columns[2:18]  # 索引 2 到 6，共 5 列

# 遍历每一行
for _, row in df.iterrows():
    a_val = row['模板名']  # 假设列名为 "列A"
    b_val = row['樣式名']  # 假设列名为 "列B"

    # 如果 a_val 未在 result 中，则初始化
    if a_val not in result:
        result[a_val] = {}

    # 如果 b_val 未在 result[a_val] 中，则初始化为空列表
    if b_val not in result[a_val]:
        result[a_val][b_val] = []

    # 构建包含列 C 到 G 的字典
    sub_dict = {}
    for col in columns_c_to_g:
        if pd.isna(row[col]): continue

        sub_key = zh2en_map.get(col, col)
        sub_val = row[col]

        if sub_key in ['is_bold', 'is_italic', 'is_underline']:
            sub_val = True if row[col] else False

        if sub_key in ['docx_xml']:
            sub_val = ast.literal_eval(sub_val)

        if sub_key == 'line_spacing_rule':
            sub_val = multiple_map[sub_val]

        sub_dict[sub_key] = sub_val

    # 添加到列表中
    result[a_val][b_val].append(sub_dict)

print(result)