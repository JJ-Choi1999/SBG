import json
import re

from common.utils.re_util import contains_chinese_full

filter_texts = [
    '必需分析项目(请列出异常数值该项目位置)'
]

def md_replace(md_text: str):
    md_text = re.sub(r'\d+\.\s*', '', md_text)
    md_text = re.sub(r'\[XXXX(.*?)\]', '', md_text)
    md_text = re.sub(r'【(.*?)】', '', md_text)
    md_text = md_text.lstrip('#').replace('-', '').replace('**', '')
    md_text = md_text.strip(' ')

    return md_text

def recursion_title(md_texts: list[str], text_index: int):

    title_text = ''
    for i in range(text_index - 1, -1, -1):
        md_text = md_texts[i]
        if md_text.strip().find('#') == 0:
            title_text = md_text.replace('#', '').replace(':', '')
            break

    print(md_replace(title_text.strip(' ')))
    if md_replace(title_text.strip(' ')) in filter_texts: return ''

    return title_text + ','

# def extra_md_prompts(company_name: str, md_texts: list[str]):
#     prompts = []
#     for text_index, md_text in enumerate(md_texts):
#         md_text = md_text.strip()
#         if not md_text.find('- ') == 0: continue
#
#         if md_text and text_index and not contains_chinese_full(md_text):
#             md_text = md_replace(md_texts[text_index-1].strip(' '))
#         else:
#             md_text = md_replace(f'{recursion_title(md_texts, text_index)}{md_text}')
#
#         prompts.append(f'{company_name}, {md_text}'[:-1])
#
#     return prompts

def extra_md_prompts(company_name: str, md_path: str) -> tuple[list[str], list[dict]]:

    md_prompts = []
    md_prompts_maps = []

    with open(md_path, 'r', encoding='utf-8') as f:
        md_texts = f.readlines()
        for line_index, line in enumerate(md_texts):
            md_text = line.lstrip(' ')
            if not md_text.find('- ') == 0: continue

            if md_text and line_index and not contains_chinese_full(md_text):
                md_text = md_replace(md_texts[line_index - 1].strip(' '))
            else:
                md_text = md_replace(f'{recursion_title(md_texts, line_index)}{md_text}')

            md_prompt = f'{company_name}, {md_text}'[:-1]
            md_prompts.append(md_prompt)
            md_prompts_maps.append({
                md_prompt: {
                    'line_index': line_index,
                    'line': line
                }
            })

    return md_prompts, md_prompts_maps

if __name__ == '__main__':
    md_path = r'D:\AiAgent\SBG\common\file\document_recursion\征信报告模板.md'
    # with open(md_path, 'r', encoding='utf-8') as f:
    #     text = f.read()
    #
    # md_texts = list(filter(lambda x: x, text.split('\n')))
    company_name = '借款人[智谱华章]'
    # prompts = extra_md_prompts(
    #     company_name=company_name,
    #     md_texts=md_texts
    # )
    # import json
    # print(f'prompts:\n', json.dumps(prompts, ensure_ascii=False, indent=2))

    md_prompts = []
    md_prompts_maps = []
    with open(md_path, 'r', encoding='utf-8') as f:
        md_texts = f.readlines()
        for line_index, line in enumerate(md_texts):
            md_text = line.lstrip(' ')
            if not md_text.find('- ') == 0: continue

            if md_text and line_index and not contains_chinese_full(md_text):
                md_text = md_replace(md_texts[line_index - 1].strip(' '))
            else:
                md_text = md_replace(f'{recursion_title(md_texts, line_index)}{md_text}')

            md_prompt = f'{company_name}, {md_text}'[:-1]

            format_example = ''.join(re.compile(r'格式参考:(.*?)').findall(line))
            print(f'format_example:', format_example)
            md_prompts.append(md_prompt)
            md_prompts_maps.append({
                md_prompt: {
                    'line_index': line_index,
                    'line': line,
                    'format_example': format_example
                }
            })

    print(f'md_prompts:', json.dumps(md_prompts, ensure_ascii=False, indent=2))
    print(f'=' * 100)
    print(f'md_prompts_maps:', json.dumps(md_prompts_maps, ensure_ascii=False, indent=2))
