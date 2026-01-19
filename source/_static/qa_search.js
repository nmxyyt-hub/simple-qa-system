// qa_search.js - 修正版（异步等待数据，全屏搜索界面）- 增加调试
(function () {
    'use strict';

    // ✅ 异步等待 window.qaData 加载完成
    function waitForQaData() {
        return new Promise((resolve) => {
            if (window.qaData) {
                console.log('✅ window.qaData 已存在:', window.qaData.length, 'items');
                resolve(window.qaData);
                return;
            }

            let attempts = 0;
            const maxAttempts = 100;

            const checkData = () => {
                attempts++;
                if (window.qaData) {
                    console.log('✅ window.qaData 已加载:', window.qaData.length, 'items');
                    resolve(window.qaData);
                } else if (attempts < maxAttempts) {
                    setTimeout(checkData, 100);
                } else {
                    console.error('❌ 超时：window.qaData 未加载');
                    resolve(null);
                }
            };

            checkData();
        });
    }

    function renderQAItem(item) {
        console.log('--- renderQAItem called for item:', item.question); // 新增调试日志
        const div = document.createElement('div');
        div.className = 'qa-result-item';
        div.style.marginBottom = '20px';
        div.style.padding = '10px';
        div.style.border = '1px solid #eee';
        div.style.borderRadius = '4px';

        const questionEl = document.createElement('h3');
        questionEl.textContent = item.question;
        questionEl.style.marginTop = '0';

        const answerEl = document.createElement('div');
        answerEl.innerHTML = item.answer;

        console.log('✅ Original answer HTML:', item.answer);
        console.log('✅ Answer element before fix:', answerEl.innerHTML);

        // ✅ 修正图片路径
        const images = answerEl.querySelectorAll('img');
        console.log('✅ Found images:', images.length);

        images.forEach((img, index) => {
            let originalSrc = img.getAttribute('src');
            console.log(`✅ Image ${index} original src:`, originalSrc);

            if (originalSrc && !originalSrc.startsWith('_static/')) {
                if (originalSrc.startsWith('images/')) {
                    img.src = '_static/' + originalSrc;
                    console.log(`✅ Fixed image ${index} src to:`, img.src);
                } else {
                    img.src = '_static/images/' + originalSrc;
                    console.log(`✅ Fixed image ${index} src to:`, img.src);
                }
            }
        });

        console.log('✅ Answer element after fix:', answerEl.innerHTML);

        div.appendChild(questionEl);
        div.appendChild(answerEl);
        return div;
    }

    async function performSearch(query) {
        console.log('--- performSearch called with query:', query); // 新增调试日志
        const resultsContainer = document.getElementById('qa-search-results');
        if (!resultsContainer) {
            console.warn('No element with id="qa-search-results" found.');
            return;
        }

        // 清空之前的结果
        resultsContainer.innerHTML = '';

        if (!query.trim()) {
            resultsContainer.innerHTML = '<p>请输入搜索关键词</p>';
            return;
        }

        // ✅ 等待数据加载完成
        const data = await waitForQaData();
        if (!data) {
            resultsContainer.innerHTML = '<p>数据加载失败，请刷新页面重试。</p>';
            return;
        }

        const matches = data.filter(item =>
            item.question.toLowerCase().includes(query.toLowerCase()) ||
            item.answer.toLowerCase().includes(query.toLowerCase())
        );

        console.log('✅ Search matches:', matches.length, matches); // 打印匹配项

        if (matches.length === 0) {
            resultsContainer.innerHTML = '<p>未找到相关问答。</p>';
            return;
        }

        matches.forEach(item => {
            console.log('--- Adding match to results:', item.question); // 新增调试日志
            const el = renderQAItem(item);
            resultsContainer.appendChild(el);
        });
    }

    function init() {
        console.log('--- init function called'); // 新增调试日志
        // 查找用于放置搜索界面的容器 (例如在 index.rst 中创建的 div)
        const container = document.getElementById('search-box-container');
        if (!container) {
            console.error('❌ 未找到 ID 为 "search-box-container" 的容器元素。');
            return;
        }

        // 检查是否已经初始化过（防止重复初始化）
        if (container.querySelector('#full-screen-search-input')) {
            console.warn('--- Search UI already exists, skipping init.');
            return;
        }

        // --- 创建全屏搜索界面 ---
        container.style.width = '100%';
        container.style.maxWidth = '800px'; // 可选：限制最大宽度
        container.style.margin = '0 auto'; // 居中
        container.style.padding = '20px';
        // container.style.border = '1px solid #ccc'; // 可选：边框

        // 创建搜索输入框
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.id = 'full-screen-search-input';
        searchInput.placeholder = '请输入您的问题...';
        searchInput.style.width = 'calc(100% - 110px)'; // 减去按钮的宽度和一些边距
        searchInput.style.padding = '10px';
        searchInput.style.fontSize = '16px';
        searchInput.style.border = '1px solid #ccc';
        searchInput.style.borderRadius = '4px';
        searchInput.style.marginBottom = '10px';

        // 创建搜索按钮
        const searchButton = document.createElement('button');
        searchButton.id = 'full-screen-search-button';
        searchButton.textContent = '搜索';
        searchButton.style.padding = '10px 15px';
        searchButton.style.fontSize = '16px';
        searchButton.style.marginLeft = '10px';
        searchButton.style.border = '1px solid #ccc';
        searchButton.style.borderRadius = '4px';
        searchButton.style.cursor = 'pointer';
        searchButton.style.backgroundColor = '#f5f5f5';

        // 创建结果显示区域
        const resultsContainer = document.createElement('div');
        resultsContainer.id = 'qa-search-results';
        resultsContainer.style.marginTop = '20px';
        resultsContainer.style.minHeight = '200px'; // 给结果区域一个最小高度

        // 将元素添加到容器
        container.appendChild(searchInput);
        container.appendChild(searchButton);
        container.appendChild(resultsContainer);

        // --- 添加事件监听器 ---

        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            console.log('--- Input event triggered'); // 新增调试日志
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                await performSearch(e.target.value);
            }, 300); // 300ms 防抖
        });

        searchButton.addEventListener('click', async (e) => {
            console.log('--- Click event triggered'); // 新增调试日志
            e.preventDefault(); // 阻止默认表单提交行为（如果有的话）
            await performSearch(searchInput.value);
        });

        // 也可以让回车键触发搜索
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchButton.click(); // 模拟点击搜索按钮
            }
        });
    }

    // 等待 DOM 加载完成后再初始化
    if (document.readyState === 'loading') {
        console.log('--- Waiting for DOMContentLoaded'); // 新增调试日志
        document.addEventListener('DOMContentLoaded', init);
    } else {
        console.log('--- DOM already loaded, calling init now'); // 新增调试日志
        init();
    }
})();