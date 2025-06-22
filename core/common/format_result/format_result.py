import re
from typing import Iterator, Any, List, Tuple

from langchain_core.documents import Document
from langchain_core.messages import AIMessage


def output_stream(agent_stream: Iterator[dict[str, Any] | Any], chat_id: str, enable_print: bool = True) -> list:
    """
    输出对话流
    :param agent_stream: 
    :param chat_id:
    :param enable_print: 是否开启打印
    :return: 
    """
    messages: list = []

    for stream_mode, chunk in agent_stream:
        # 记录打印完成的结果
        if stream_mode == 'updates':
            if 'agent' in chunk:
                msg = chunk.get('agent', {}).get('messages', [])[-1]
                messages.append(msg.model_copy(update={"id": chat_id}))

            if 'tools' in chunk:
                msg = chunk.get('tools', {}).get('messages', [])[-1]
                messages.append(msg.model_copy(update={"id": chat_id}))

        # 记录自定义内容
        if stream_mode == 'custom':
            messages.append(
                AIMessage(content=chunk, id=chat_id, additional_kwargs={'msg_type': 'custom'})
            )

        # 不打印工具调用信息(防止泄密)
        if stream_mode == 'messages':
            if chunk[-1].get('langgraph_triggers', ()) == ('branch:to:tools',):
                if enable_print: print(f'Tools 调用中...')
                continue
            if enable_print: print(chunk[0].text(), end="", flush=True)

    if enable_print: print()
    return messages

# [todo] 该方法要封装到对应 pydantic 输出结果类中
def vector_results(docs: list) -> list[dict]:
    vec_results = []
    for i, doc in enumerate(docs):
        print(f'可信度: {round(doc[1], 3)}', '检索内容:', doc[0].page_content, 'DOC Metadata:', doc[0].metadata, '\n\n')
        vec_results.append({
            'score': doc[1],
            'content': doc[0].page_content
        })

    return vec_results

# [todo] 该方法要封装到对应 pydantic 输出结果类中
def transform_rerank_texts(vector_results: list[dict]) -> list[str]:
    rerank_texts = []
    for vector_result in vector_results:
        if not vector_result.get('content'): continue
        rerank_texts.append(vector_result.get('content'))

    return rerank_texts

def transform_rerank_results(rerank_results: list):
    """
    将rerank 返回格式统一为 xembedding 在 weaviate 处理完成后的格式
    :param rerank_results:
    :return:
    """
    vec_results = []
    for rerank_result in rerank_results:
        vec_results.append({
            'score': rerank_result.get('relevance_score'),
            'content': rerank_result.get('document', {}).get('text', '')
        })
    return vec_results

# [todo] 该方法要封装到对应 pydantic 输出结果类中
def get_rerank_contents(rerank_results: list[dict]) -> list[str]:
    rerank_contents = []
    results = rerank_results.get('results', {})

    for result in results:
        text = result.get('document', {}).get('text', '')
        if not text: continue
        rerank_contents.append(text)

    return rerank_contents


def extract_tags(text: str, tag: str) -> list[str]:
    """
    提取标签内容, 输入需要提取的内容, 按照标签提取, 把所有提取到的内容返回一个 list
    :param text: 需要提取标签的文本
    :param tag: 需要提取的标签
    :return:
    """
    pattern = f'<{tag}>(.*?)</{tag}>'
    pattern = r'' + pattern + r''
    # 使用 re.findall 查找所有匹配的内容
    return re.findall(pattern, text, re.DOTALL)

def format_search_refer(search_refer: dict[str, list[str]]):
    """
    格式化知识库/网页搜索参考
    :param search_refer: 搜索参考, 格式: {'需求1': ['需求1关联搜索1', '需求1关联搜索2', ...], ...}
    :return: 返回以下格式字符串:
        需求1:
            1) 需求1关联搜索1
            2) 需求1关联搜索2
            ...
        ...
    """
    format_text = ''
    index = 0
    for key, value in search_refer.items():
        format_text += f'\n\t{index+1}) {key}:'
        for i, item in enumerate(value):
            format_text += f'\n\t\t{index+1}.{i+1}) {item}'
        index += 1

    return format_text