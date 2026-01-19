# _exts\qa_search_indexer.py

import json
import os
from docutils import nodes
from docutils.core import publish_parts
from sphinx.util.docutils import docutils_namespace
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

# 存储问题和答案的列表
qa_data = []

def rst_to_html(rst_text):
    """
    将 RST 格式的字符串转换为 HTML。
    """
    try:
        # 使用 docutils 将 RST 转换为 HTML
        parts = publish_parts(
            rst_text,
            writer_name='html',
            settings_overrides={
                'output_encoding': 'unicode',
                # 确保图片路径等正确处理
                # 'embed_stylesheet': False,  # 如果不需要内嵌CSS
            }
        )
        # 提取 body 部分的 HTML 内容
        html_body = parts['body']
        return html_body
    except Exception as e:
        logger.error(f"Error converting RST to HTML: {e}")
        # 如果转换失败，返回原始文本
        return rst_text


def on_doctree_read(app: Sphinx, doctree: nodes.document) -> None:
    """
    当 Sphinx 解析完一个文档的 doctree (文档树) 时触发。
    这里查找 qa_data.md 的 doctree，并提取内容。
    """
    global qa_data

    # 获取当前处理的文档名 (例如 'qa_data')
    docname = app.env.docname

    # --- 添加日志 ---
    logger.info(f"Processing document: {docname}")

    # 只处理 qa_data.md 文件
    if docname == 'qa_data':
        logger.info(f"Processing document: {docname}")

        # --- 优化遍历策略 ---
        # 遍历顶级的 section 节点 (对应 Markdown 中的 # 标题)
        for section_node in doctree.traverse(nodes.section):
            # 在每个 section 中查找第一个 title 节点 (对应 # 问题)
            title_nodes = section_node.traverse(nodes.title)
            if not title_nodes:
                continue # 如果 section 没有标题，跳过

            question_node = title_nodes[0] # 取第一个标题作为问题
            question = question_node.astext().strip()

            if not question:
                continue # 如果标题为空，跳过

            # --- 修改：收集原始 RST 文本内容 ---
            answer_rst_text = ""
            # 获取 section 的所有直接子节点
            section_children = list(section_node.children)
            title_index = section_node.index(question_node) # 找到标题在子节点列表中的位置

            # 从标题之后开始查找
            for i in range(title_index + 1, len(section_children)):
                child_node = section_children[i]
                # 如果遇到下一个标题，停止查找答案
                if isinstance(child_node, nodes.title):
                    break
                # 检查是否是内容节点 (段落、列表、代码块等)
                # 使用 child_node.rawsource 可能获取原始源码，但不一定可靠
                # 更可靠的方式是重新构建 RST 文本，但这比较复杂
                # 使用 astext() 获取文本，然后在构建 JSON 前转换为 HTML
                if isinstance(child_node, (nodes.paragraph, nodes.bullet_list, nodes.enumerated_list, nodes.literal_block, nodes.line_block, nodes.definition_list)):
                    # 这里仍然需要原始的 RST 格式来转换
                    # 但是 doctree.nodes 通常不直接提供原始 RST 源码
                    # 一个变通方法是假设 source 文件路径已知，并读取原始内容
                    # 但对于 Sphinx 构建过程，这可能不适用
                    # 更好的方法是使用 Sphinx 的内置转换机制或确保 MyST 解析器正确处理

                    # 这里尝试直接使用 astext 获取文本，但这不会保留 RST 指令
                    # 为了处理 RST 指令，需要获取原始源码
                    # 一个可能的替代方案是直接在 source 文件中处理 RST 图片指令

                    # 由于直接从 doctree 获取原始 RST 可能比较困难，
                    # 可以考虑在 `qa_data.md` 文件中直接使用 HTML 或 MyST 兼容的图片语法
                    # 例如，使用 Markdown 图片语法: ![alt text](path/to/image.png)
                    # 或 MyST 的图片指令，如果 MyST 正确处理的话

                    # 然而，如果 `qa_data.md` 包含 RST 图片指令如 `.. image:: images/51_1.png`
                    # MyST 解析器应该将其转换为 HTML <img> 标签在 doctree 中
                    # 但 `astext()` 会丢失这些 HTML 结构

                    # 一个更直接的方法是：
                    # 1. 从 source 文件中读取原始内容
                    # 2. 找到对应的问题部分
                    # 3. 提取原始 RST/Markdown 内容
                    # 4. 使用 publish_parts 转换

                    # 但这需要知道 source 文件路径和内容结构
                    # 让尝试另一种方式：利用 Sphinx 环境获取源码
                    # app.env 是 Sphinx 环境对象，可能包含源码信息
                    # 但这同样复杂

                    # 最简单且可能最有效的方式是：
                    # 在 `qa_data.md` 中直接使用 Markdown 语法的图片，如：
                    # ![图1](images/51_1.png)
                    # MyST 解析器会将其正确转换为 HTML <img> 标签
                    # 然后 `astext()` 虽然会丢失，但应该使用 `walkabout` 或其他方法获取 HTML 内容
                    # 或者，直接获取节点的 HTML 表示，如果可能的话

                    # 更进一步，可以尝试直接从 doctree 生成 HTML 片段
                    # 这需要一个自定义的 writer 或使用现有的 HTML writer
                    # 但这超出了简单脚本的范围

                    # 回到最初的想法：如果知道 `qa_data.md` 的内容
                    # 并且它包含 RST 图片指令，可以手动读取并转换

                    # 为了简化，假设 `qa_data.md` 中使用的是 Markdown 图片语法
                    # 或者，MyST 已经将 RST 指令转换为了 HTML 结构，只需提取

                    # 尝试直接获取节点的 HTML 表示
                    # 这通常需要一个 writer，但可以尝试 `toctree` 或其他方法
                    # 或者，直接尝试 `astext()` 并手动替换图片路径（如果知道原始格式）

                    # 最后，一个可行的方案是：
                    # 1. 在 `qa_data.md` 中使用 Markdown 语法: ![alt text](images/51_1.png)
                    # 2. MyST 解析器会将其转换为 HTML <img> 标签
                    # 3. 需要一种方法来获取这个 HTML 结构，而不是纯文本

                    # 一个 hacky 的方法是：使用 `publish_parts` 转换 `astext()` 的结果
                    # 但这可能不是最佳，因为 `astext()` 已经丢失了结构
                    # 更好的方法是找到一种方式获取节点的 HTML 版本

                    # 让尝试一个不同的 approach：
                    # 1. 从 app.env 获取原始源码
                    # 2. 定位问题和答案部分
                    # 3. 提取原始 RST/MD
                    # 4. 转换为 HTML

                    # 获取源文件路径
                    source_path = app.env.doc2path(docname)
                    # print(f"Source path: {source_path}") # 调试用

                    # 读取原始源文件
                    with open(source_path, 'r', encoding='utf-8') as f:
                        source_content = f.read()

                    # 简单的分割方法来定位问题和答案
                    # 这种方法依赖于文档结构的稳定性
                    # 寻找当前 section 对应的原始内容
                    # 例如，如果问题是 "## 问题51：..."
                    # 寻找 "## 问题51：" 开始，到下一个 "##" 或文件结束

                    # 使用正则表达式或其他方法来精确提取
                    import re
                    # 构建一个模式来匹配当前问题及其内容
                    # 问题标题可能包含特殊字符，需要转义
                    escaped_question = re.escape(question)
                    # 模式：问题标题 + 任意内容直到下一个顶级标题或文件末尾
                    # 注意：这里假设标题是 Markdown 格式 ##
                    pattern = rf"##\s+{escaped_question}.*?\n((?:(?!##\s).)*)"
                    match = re.search(pattern, source_content, re.DOTALL)

                    if match:
                        raw_answer_content = match.group(1).strip()
                        # print(f"Raw answer content for '{question}': {raw_answer_content}") # 调试用
                        # 现在 raw_answer_content 包含了原始的 RST/MD 内容
                        # 将其转换为 HTML
                        answer_html = rst_to_html(raw_answer_content)
                    else:
                        logger.warning(f"Could not find raw content for question: {question}")
                        answer_html = child_node.astext().strip() + "\n"

                    # 将转换后的 HTML 内容追加
                    answer_rst_text += answer_html

            answer_rst_text = answer_rst_text.strip() # 去除首尾空白

            if answer_rst_text:
                # 确保 question 和 answer_rst_text 不是空字符串或只有空白
                qa_data.append({
                    "question": question,
                    "answer": answer_rst_text # 现在是 HTML 格式
                })
                logger.info(f"  Found Q: {question[:30]}...") # 记录找到的问题开头
            else:
                logger.warning(f"Found question '{question}' but no answer content.")

def on_build_finished(app: Sphinx, exception):
    """
    当 Sphinx 构建完成后触发。
    将收集到的 QA 数据写入 JSON 文件和 JavaScript 文件。
    """
    global qa_data
    if not qa_data:
        logger.warning("No QA data found during build.")
        return

    # --- 关键修改 1: 将输出目录改为 _static ---
    static_dir = os.path.join(app.outdir, '_static')
    os.makedirs(static_dir, exist_ok=True)  # 确保 _static 目录存在

    # 1. 生成 search_index.json
    json_path = os.path.join(static_dir, 'search_index.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Search index JSON file created successfully at {json_path}")
    except Exception as e:
        logger.error(f"Error writing search index JSON: {e}")

    # 2. 生成 qa_search_index.js (这是浏览器需要的 JS 文件)
    js_path = os.path.join(static_dir, 'qa_search_index.js')
    try:
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write('// Auto-generated QA search index\n')
            f.write('window.qaData = ') # ✅ 修改为 window.qaData
            json.dump(qa_data, f, ensure_ascii=False, indent=2)
            f.write(';\n')
        logger.info(f"QA search index JS file created successfully at {js_path}")
    except Exception as e:
        logger.error(f"Error writing QA search index JS: {e}")

def setup(app: Sphinx) -> dict:
    """
    Sphinx 扩展的入口点。
    """
    # 注册事件处理器
    app.connect('doctree-read', on_doctree_read)
    app.connect('build-finished', on_build_finished)

    # 返回扩展元数据
    return {
        'version': '0.1',
        'parallel_read_safe': True, # 如果扩展不修改全局状态，设为 True
        'parallel_write_safe': True, # 如果扩展只写入自己的输出文件，设为 True
    }