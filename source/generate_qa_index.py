import os
import json
from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer

def rst_to_html(rst_text):
    """将 RST 文本转换为 HTML"""
    writer = Writer()
    parts = publish_parts(
        source=rst_text,
        writer=writer,
        settings_overrides={
            'initial_header_level': 2,
            'output_encoding': 'utf-8',
        }
    )
    return parts['html_body']

def extract_qa_data():
    """提取问答数据并转换为 HTML"""
    qa_data_path = os.path.join(os.getcwd(), 'qa_data.md')
    if not os.path.exists(qa_data_path):
        raise FileNotFoundError(f"文件未找到: {qa_data_path}")
    
    with open(qa_data_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    qa_list = []
    current_question = None
    current_answer = []

    for line in lines:
        if line.startswith('## 问题'):
            if current_question is not None:
                # ✅ 转换 RST 为 HTML
                answer_html = rst_to_html('\n'.join(current_answer))
                qa_list.append({
                    'question': current_question.strip(),
                    'answer': answer_html
                })
            current_question = line.strip()
            current_answer = []
        else:
            current_answer.append(line)

    if current_question:
        # ✅ 转换最后一个答案为 HTML
        answer_html = rst_to_html('\n'.join(current_answer))
        qa_list.append({
            'question': current_question.strip(),
            'answer': answer_html
        })

    return qa_list

if __name__ == '__main__':
    try:
        qa_data = extract_qa_data()
        
        js_file = os.path.join(os.getcwd(), '_static', 'qa_search_index.js')
        os.makedirs(os.path.dirname(js_file), exist_ok=True)
        
        # ✅ 必须使用 window.qaData = 
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write('window.qaData = ')  # ✅ 正确的全局变量
            f.write(json.dumps(qa_data, ensure_ascii=False, indent=2))
            f.write(';')  # ✅ 分号
            
        print("✅ qa_search_index.js 生成成功！")
        print(f"位置: {js_file}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()