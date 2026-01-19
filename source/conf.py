# Configuration file for the Sphinx documentation builder.

project = '简易问答系统'
copyright = '2025, CiCi'
author = 'CiCi'
release = '1.0'

# -- General configuration ---------------------------------------------------

import os
import sys
# 将 _exts 目录添加到 Python 模块搜索路径
sys.path.insert(0, os.path.abspath('../_exts'))

extensions = [
'myst_parser',  # 启用 MyST Parser
'qa_search_indexer', # 自创建的扩展
]

templates_path = ['_templates']
exclude_patterns = []
language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------

html_baseurl = 'https://nmxyyt-hub.github.io/simple-qa-system/'

html_theme = 'furo' # 使用 Furo 主题
html_static_path = ['_static']
html_js_files = [
    'lunr.js',      # 先加载 lunr.js
    'qa_search_index.js', # 加载数据
    'qa_search.js', # 再加载自定义搜索脚本
]

# 启用搜索高亮和富文本渲染
html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
}

html_css_files = [
    'css/custom_sidebar.css', # 隐藏图标
    'css/custom_style.css', # 美化样式
]

html_show_sourcelink = False