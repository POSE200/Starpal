/**
 * API 通信模块
 * 处理与后端的所有HTTP请求
 */

class ApiClient {
    constructor(baseUrl = 'http://127.0.0.1:5000') {
        this.baseUrl = baseUrl;
    }

    /**
     * 通用API请求方法
     * @param {string} endpoint - API端点
     * @param {Object} data - 请求数据
     * @param {string} method - HTTP方法
     * @returns {Promise} API响应
     */
    async request(endpoint, data = null, method = 'POST') {
        try {
            const config = {
                method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            // 添加认证头（如果用户已登录）
            const currentUser = localStorage.getItem('currentUser');
            if (currentUser) {
                config.headers['Authorization'] = `Bearer ${currentUser}`;
            }

            if (data && method !== 'GET') {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseUrl}${endpoint}`, config);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || '请求失败');
            }

            return await response.json();
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }

    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} 登录结果
     */
    async login(username, password) {
        return await this.request('/api/login', { username, password });
    }

    /**
     * 用户注册
     * @param {string} name - 姓名
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise} 注册结果
     */
    async register(name, username, password) {
        return await this.request('/api/register', { name, username, password });
    }

    /**
     * 修改密码
     * @param {string} username - 用户名
     * @param {string} oldpwd - 原密码
     * @param {string} newpwd - 新密码
     * @returns {Promise} 修改结果
     */
    async changePassword(username, oldpwd, newpwd) {
        return await this.request('/api/change_password', { username, oldpwd, newpwd });
    }

    /**
     * 发起聊天（流式响应）
     * @param {string} message - 消息内容
     * @param {string} username - 用户名
     * @param {string} chatId - 对话ID
     * @param {string} systemPrompt - 系统提示词（可选）
     * @param {AbortSignal} signal - 中断信号
     * @returns {Response} 流式响应
     */
    async chatStream(message, username, chatId, systemPrompt = null, signal = null) {
        const requestData = {
            message,
            username,
            chat_id: chatId
        };

        // 如果提供了系统提示词，则添加到请求数据中
        if (systemPrompt !== null) {
            requestData.system_prompt = systemPrompt;
        }

        const config = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        };
        
        // 添加认证头
        if (username) {
            config.headers['Authorization'] = `Bearer ${username}`;
        }

        if (signal) {
            config.signal = signal;
        }

        return await fetch(`${this.baseUrl}/api/chat`, config);
    }

    /**
     * 清除对话记忆
     * @param {string} username - 用户名
     * @param {string} chatId - 对话ID
     * @returns {Promise} 清除结果
     */
    async clearMemory(username, chatId) {
        return await this.request('/api/clear_memory', { username, chat_id: chatId });
    }

    /**
     * 设置系统提示词
     * @param {string} username - 用户名
     * @param {string} chatId - 对话ID
     * @param {string} systemPrompt - 系统提示词（传null则使用默认值）
     * @returns {Promise} 设置结果
     */
    async setSystemPrompt(username, chatId, systemPrompt) {
        return await this.request('/api/set_system_prompt', {
            username,
            chat_id: chatId,
            system_prompt: systemPrompt
        });
    }

    /**
     * 获取当前系统提示词
     * @param {string} username - 用户名
     * @param {string} chatId - 对话ID
     * @returns {Promise} 包含系统提示词的响应
     */
    async getSystemPrompt(username, chatId) {
        return await this.request('/api/get_system_prompt', {
            username,
            chat_id: chatId
        });
    }

    /**
     * 获取服务状态
     * @returns {Promise} 服务状态
     */
    async getHealth() {
        return await this.request('/health', null, 'GET');
    }

    /**
     * 获取用户的长期记忆
     * @param {number} limit - 返回记忆数量限制
     * @returns {Promise} 长期记忆列表
     */
    async getLongTermMemories(limit = 10) {
        return await this.request(`/api/memory/long-term?limit=${limit}`, null, 'GET');
    }

    /**
     * 更新特定的长期记忆
     * @param {string} memoryId - 记忆ID
     * @param {string} text - 新的记忆内容
     * @param {Object} metadata - 可选的元数据
     * @returns {Promise} 更新结果
     */
    async updateLongTermMemory(memoryId, text, metadata = null) {
        const data = { text };
        if (metadata) {
            data.metadata = metadata;
        }
        return await this.request(`/api/memory/long-term/${memoryId}`, data, 'PUT');
    }

    /**
     * 删除特定的长期记忆
     * @param {string} memoryId - 记忆ID
     * @returns {Promise} 删除结果
     */
    async deleteLongTermMemory(memoryId) {
        return await this.request(`/api/memory/long-term/${memoryId}`, null, 'DELETE');
    }

    /**
     * 清除所有长期记忆
     * @returns {Promise} 清除结果
     */
    async clearLongTermMemories() {
        return await this.request('/api/memory/long-term', null, 'DELETE');
    }
}

// 创建全局API客户端实例
const apiClient = new ApiClient();

// 导出API客户端（用于模块化使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiClient;
}
