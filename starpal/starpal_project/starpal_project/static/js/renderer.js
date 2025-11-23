/**
 * 聊天消息渲染模块
 * 处理Markdown渲染和代码高亮
 */

class MessageRenderer {
    constructor() {
        this.renderDebounceTimer = null;
        this.lastRenderedContent = '';
        this.initializeMarked();
    }

    /**
     * 初始化Marked.js配置
     */
    initializeMarked() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                highlight: (code, language) => {
                    if (language && window.Prism && window.Prism.languages[language]) {
                        return Prism.highlight(code, Prism.languages[language], language);
                    }
                    return code;
                }
            });
        }
    }

    /**
     * 渲染消息内容（支持Markdown和代码高亮）
     * @param {string} content - 原始消息内容
     * @returns {string} 渲染后的HTML
     */
    renderMessageContent(content) {
        if (!content) return '';

        try {
            // 使用marked处理markdown
            let html = marked ? marked.parse(content) : this.simpleMarkdownParse(content);
            
            // 为代码块添加必要的CSS类
            html = this.processCodeBlocks(html);
            
            return html;
        } catch (error) {
            console.error('渲染消息内容失败:', error);
            return this.escapeHtml(content);
        }
    }

    /**
     * 简单的Markdown解析（备用方案）
     * @param {string} content - 内容
     * @returns {string} HTML
     */
    simpleMarkdownParse(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    /**
     * 处理代码块，添加必要的CSS类
     * @param {string} html - HTML内容
     * @returns {string} 处理后的HTML
     */
    processCodeBlocks(html) {
        // 为有语言标识的代码块添加line-numbers类
        html = html.replace(/<pre><code class="language-(\w+)">/g, (match, lang) => {
            return `<pre class="line-numbers language-${lang}"><code class="language-${lang}">`;
        });
        
        // 为无语言标识的代码块添加默认类
        html = html.replace(/<pre><code>/g, 
            '<pre class="line-numbers language-none"><code class="language-none">');
        
        return html;
    }

    /**
     * 转义HTML字符
     * @param {string} text - 文本内容
     * @returns {string} 转义后的文本
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 智能实时渲染（支持流式更新）
     * @param {HTMLElement} element - 目标元素
     * @param {string} fullContent - 完整内容
     */
    smartRealTimeRender(element, fullContent) {
        if (!element) return;

        // 立即更新内容
        element.innerHTML = this.renderMessageContent(fullContent);
        // 实时渲染代码高亮（去除防抖和内容变更判断）
        this.applyCodeHighlighting(element, true);
    }

    /**
     * 应用代码高亮
     * @param {HTMLElement} element - 目标元素
     * @param {boolean} isStreaming - 是否为流式模式
     */
    applyCodeHighlighting(element, isStreaming = false) {
        if (!element) return;

        try {
            // 添加行号到代码块
            this.addLineNumbers(element);
            
            // 应用Prism代码高亮
            if (window.Prism) {
                Prism.highlightAllUnder(element);
            }
        } catch (error) {
            console.error('代码高亮应用失败:', error);
        }
    }

    /**
     * 为代码块添加行号
     * @param {HTMLElement} element - 目标元素
     */
    addLineNumbers(element) {
        const preElements = element.querySelectorAll('pre.line-numbers');
        
        preElements.forEach(pre => {
            // 避免重复添加行号
            if (pre.querySelector('.line-numbers-rows')) {
                return;
            }
            
            const code = pre.querySelector('code');
            if (!code) return;
            
            const lines = code.textContent.split('\n');
            const lineCount = lines.length;
            
            // 创建行号容器
            const lineNumbersRows = document.createElement('span');
            lineNumbersRows.className = 'line-numbers-rows';
            lineNumbersRows.setAttribute('aria-hidden', 'true');
            
            // 添加行号
            for (let i = 0; i < lineCount; i++) {
                const span = document.createElement('span');
                lineNumbersRows.appendChild(span);
            }
            
            pre.appendChild(lineNumbersRows);
        });
    }

    /**
     * 清除防抖定时器
     */
    clearRenderTimer() {
        if (this.renderDebounceTimer) {
            clearTimeout(this.renderDebounceTimer);
            this.renderDebounceTimer = null;
        }
    }

    /**
     * 最终渲染（用于流式传输完成后）
     * @param {HTMLElement} element - 目标元素
     * @param {string} content - 完整内容
     */
    finalRender(element, content) {
        this.clearRenderTimer();
        
        if (element && content) {
            element.innerHTML = this.renderMessageContent(content);
            this.applyCodeHighlighting(element, false);
        }
    }

    /**
     * 创建消息元素（优化：带操作按钮）
     * @param {Object} message - 消息对象
     * @param {Array} messages - 全部消息（用于判断相邻关系）
     * @param {number} idx - 当前消息索引
     * @returns {HTMLElement} 消息DOM元素
     */
    createMessageElement(message, messages = [], idx = 0, showActions = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}`;

        // AI 消息显示头像（左侧）
        if (message.role === 'ai') {
            const avatar = document.createElement('div');
            avatar.className = 'ai-avatar';
            avatar.innerHTML = '<img src="assets/ai-avatar.png" alt="AI" style="width:44px;height:44px;border-radius:50%;object-fit:cover;">';
            messageDiv.appendChild(avatar);
        }

        // 用户消息显示自定义头像（左侧悬浮）
        if (message.role === 'user') {
            const userAvatar = document.createElement('div');
            userAvatar.className = 'user-avatar';
            // 读取本地存储的头像base64，否则用默认图片
            let avatarSrc = localStorage.getItem('userAvatar') || 'assets/user-avatar.png';
            userAvatar.innerHTML = `<img src="${avatarSrc}" alt="用户头像" style="width:44px;height:44px;border-radius:50%;object-fit:cover;">`;
            messageDiv.appendChild(userAvatar);
        }

        const bubble = document.createElement('div');
        bubble.className = `bubble ${message.role}`;
        bubble.innerHTML = this.renderMessageContent(message.content);
        messageDiv.appendChild(bubble);
        this.applyCodeHighlighting(bubble);


        // 操作按钮区域，悬停时显示
        if (showActions) {
            const actions = document.createElement('div');
            actions.className = 'bubble-actions';
            // DeepSeek风格：AI左下，用户右下，按钮组另起一行
            if (message.role === 'user') {
                actions.style.left = 'auto';
                actions.style.right = '6px';
                actions.style.bottom = '-4px';
                actions.style.top = 'auto';
                actions.style.justifyContent = 'flex-end';
            } else if (message.role === 'ai') {
                actions.style.left = '6px';
                actions.style.right = 'auto';
                actions.style.bottom = '-4px';
                actions.style.top = 'auto';
                actions.style.justifyContent = 'flex-start';
            }
            actions.style.position = 'absolute';
            actions.style.display = 'flex';
            actions.style.alignItems = 'center';
            actions.style.gap = '8px';
            actions.style.fontSize = '18px';
            actions.style.opacity = '0';
            actions.style.background = 'rgba(30,30,30,0.92)';
            actions.style.borderRadius = '8px';
            actions.style.boxShadow = '0 2px 8px rgba(0,0,0,0.10)';
            actions.style.padding = '2px 8px';
            actions.style.pointerEvents = 'none';
            actions.style.transition = 'opacity 0.2s';
            actions.style.userSelect = 'none';
            // 悬停/触控时渐显
            bubble.addEventListener('mouseenter', () => {
                actions.style.opacity = '1';
                actions.style.pointerEvents = 'auto';
            });
            bubble.addEventListener('mouseleave', () => {
                actions.style.opacity = '0';
                actions.style.pointerEvents = 'none';
            });
            bubble.addEventListener('touchstart', () => {
                actions.style.opacity = '1';
                actions.style.pointerEvents = 'auto';
            });
            bubble.addEventListener('touchend', () => {
                setTimeout(() => {
                    actions.style.opacity = '0';
                    actions.style.pointerEvents = 'none';
                }, 600);
            });

            // 复制按钮
            const copyBtn = document.createElement('i');
            copyBtn.className = 'ri-file-copy-line action-btn';
            copyBtn.title = '复制';
            copyBtn.style.cursor = 'pointer';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(message.content);
                Utils.showToast('已复制到剪贴板');
            };
            actions.appendChild(copyBtn);

            if (message.role === 'ai') {
                // 重新生成
                const regenBtn = document.createElement('i');
                regenBtn.className = 'ri-refresh-line action-btn';
                regenBtn.title = '重新生成';
                regenBtn.style.cursor = 'pointer';
                regenBtn.onclick = () => {
                    if (typeof window.regenerateAiReply === 'function') {
                        window.regenerateAiReply(idx);
                    }
                };
                actions.appendChild(regenBtn);
                // 点赞
                const likeBtn = document.createElement('i');
                likeBtn.className = 'ri-thumb-up-line action-btn';
                likeBtn.title = '点赞';
                likeBtn.style.cursor = 'pointer';
                likeBtn.onclick = () => {
                    likeBtn.classList.toggle('active');
                    dislikeBtn.classList.remove('active');
                    Utils.showToast(likeBtn.classList.contains('active') ? '已点赞' : '已取消点赞');
                    if (likeBtn.classList.contains('active')) {
                        if (typeof window.sendAiFeedback === 'function') {
                            window.sendAiFeedback('很好');
                        }
                    }
                };
                actions.appendChild(likeBtn);
                // 踩
                const dislikeBtn = document.createElement('i');
                dislikeBtn.className = 'ri-thumb-down-line action-btn';
                dislikeBtn.title = '踩';
                dislikeBtn.style.cursor = 'pointer';
                dislikeBtn.onclick = () => {
                    dislikeBtn.classList.toggle('active');
                    likeBtn.classList.remove('active');
                    Utils.showToast(dislikeBtn.classList.contains('active') ? '已点踩' : '已取消点踩');
                    if (dislikeBtn.classList.contains('active')) {
                        if (typeof window.sendAiFeedback === 'function') {
                            window.sendAiFeedback('不好');
                        }
                    }
                };
                actions.appendChild(dislikeBtn);
            }
            if (message.role === 'user') {
                // 只允许最新一条用户消息有修改按钮
                const isLatestUserMsg = (() => {
                    // 找到所有用户消息的索引
                    const userMsgIndexes = messages
                        .map((msg, i) => msg.role === 'user' ? i : -1)
                        .filter(i => i !== -1);
                    return userMsgIndexes.length > 0 && idx === userMsgIndexes[userMsgIndexes.length - 1];
                })();
                if (isLatestUserMsg) {
                    const editBtn = document.createElement('i');
                    editBtn.className = 'ri-edit-2-line action-btn';
                    editBtn.title = '修改';
                    editBtn.style.cursor = 'pointer';
                    editBtn.onclick = () => {
                        if (typeof window.editUserMessage === 'function') {
                            window.editUserMessage(idx);
                        }
                    };
                    actions.appendChild(editBtn);
                }
            }
            bubble.appendChild(actions);
        }
        return messageDiv;
    }

    /**
     * 创建日期分隔符元素
     * @param {string} date - 日期字符串
     * @returns {HTMLElement} 日期分隔符DOM元素
     */
    createDateSeparator(date) {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'chat-date';
        dateDiv.textContent = date;
        return dateDiv;
    }

    /**
     * 批量渲染消息列表
     * @param {Array} messages - 消息列表
     * @param {HTMLElement} container - 容器元素
     */
    renderMessageList(messages, container, streamingIdx = -1) {
        if (!container) return;
        container.innerHTML = '';
        const groupByDate = {};
        messages.forEach(msg => {
            const date = Utils.formatDate(msg.time);
            if (!groupByDate[date]) groupByDate[date] = [];
            groupByDate[date].push(msg);
        });
        Object.keys(groupByDate)
            .sort()
            .forEach(date => {
                container.appendChild(this.createDateSeparator(date));
                groupByDate[date].forEach((msg, idx) => {
                    // AI流式回复时，最后一条AI消息也显示按钮
                    const showActions = true;
                    container.appendChild(this.createMessageElement(msg, groupByDate[date], idx, showActions));
                });
            });
    }
}

// 创建全局消息渲染器实例
const messageRenderer = new MessageRenderer();

// 导出消息渲染器类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessageRenderer;
}
