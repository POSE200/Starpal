"""
AI聊天服务模块 - 通义千问
集成Mem0长期记忆功能
"""
import json
import time
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from mem0 import MemoryClient
from backend.config.config import Config

class AIService:
    """AI聊天服务类 - 基于阿里云通义千问，集成Mem0长期记忆"""
    
    def __init__(self):
        """初始化AI服务"""
        try:
            # 验证配置
            if not Config.AI_API_KEY or Config.AI_API_KEY == 'sk-your-dashscope-api-key-here':
                print("警告: 请在.env文件中配置正确的DASHSCOPE_API_KEY")
            
            print(f"初始化通义千问AI服务...")
            print(f"API Base: {Config.AI_API_BASE}")
            print(f"Model: {Config.AI_MODEL_NAME}")
            
            self.llm = ChatOpenAI(
                base_url=Config.AI_API_BASE,
                api_key=Config.AI_API_KEY,
                model=Config.AI_MODEL_NAME,
                streaming=True,
                temperature=1,  # 适中的创造性
                max_tokens=8000,  # 限制响应长度
            )
            # 用户对话记忆管理 {username_chatid: memory}
            self.user_memories = {}
            # 用户系统提示词管理 {username_chatid: system_prompt}
            self.user_system_prompts = {}
            # 默认系统提示词
            self.default_system_prompt = Config.DEFAULT_SYSTEM_PROMPT
            # 系统级提示词（预设，不可被用户修改）
            self.system_level_prompt = Config.SYSTEM_LEVEL_PROMPT
            
            # 初始化Mem0长期记忆客户端
            if Config.MEM0_ENABLED:
                try:
                    print(f"初始化Mem0长期记忆服务...")
                    if not Config.MEM0_API_KEY or Config.MEM0_API_KEY == 'your-mem0-api-key-here':
                        print("警告: 请在.env文件中配置正确的MEM0_API_KEY")
                    
                    self.mem0_client = MemoryClient(api_key=Config.MEM0_API_KEY)
                    self.mem0_enabled = True
                    print(f"Mem0长期记忆服务初始化成功")
                except Exception as e:
                    print(f"Mem0长期记忆初始化失败: {e}")
                    self.mem0_enabled = False
            else:
                print("Mem0长期记忆服务已禁用")
                self.mem0_enabled = False
                
            print("通义千问AI服务初始化成功")
            
        except Exception as e:
            print(f"AI服务初始化失败: {e}")
            raise
    
    def set_system_prompt(self, username, chat_id, system_prompt=None):
        """
        设置用户对话的系统提示词
        
        Args:
            username: 用户名
            chat_id: 对话ID
            system_prompt: 系统提示词，如果为None则不使用用户级提示词
        """
        key = f"{username}__{chat_id}"
        # 存储用户提供的提示词，可以为None
        self.user_system_prompts[key] = system_prompt
    
    def get_system_prompt(self, username, chat_id):
        """
        获取用户对话的系统提示词
        
        Args:
            username: 用户名
            chat_id: 对话ID
            
        Returns:
            str: 系统提示词，如果没有设置则返回None
        """
        key = f"{username}__{chat_id}"
        return self.user_system_prompts.get(key, None)
    
    def get_user_memory(self, username, chat_id):
        """
        获取用户对话记忆
        
        Args:
            username: 用户名
            chat_id: 对话ID
            
        Returns:
            ConversationBufferMemory: 对话记忆对象
        """
        key = f"{username}__{chat_id}"
        if key not in self.user_memories:
            self.user_memories[key] = ConversationBufferMemory(return_messages=True)
        return self.user_memories[key]
    
    def chat_stream(self, message, username, chat_id, system_prompt=None):
        """
        流式聊天生成器
        
        Args:
            message: 用户消息
            username: 用户名
            chat_id: 对话ID
            system_prompt: 可选的系统提示词，如果提供则会覆盖当前设置
            
        Yields:
            str: 流式响应数据
        """
        try:
            # 获取用户记忆
            memory = self.get_user_memory(username, chat_id)
            
            # 如果提供了新的系统提示词，则更新
            if system_prompt is not None:
                self.set_system_prompt(username, chat_id, system_prompt)
            
            # 添加用户消息到记忆
            memory.chat_memory.add_user_message(message)
            
            full_reply = ""
            
            # 获取当前系统提示词
            current_system_prompt = self.get_system_prompt(username, chat_id)
            
            # 从Mem0获取相关长期记忆
            long_term_memories = ""
            if self.mem0_enabled:
                try:
                    user_id = username
                    # 构建高级过滤条件，优化v2版本搜索
                    current_time = int(time.time())
                    one_month_ago = current_time - (30 * 24 * 60 * 60)  # 30天前的时间戳
                    
                    # 构建高级过滤器，采用v2版本的完整功能
                    filters = {
                        "AND": [
                            {"user_id": user_id},
                            # 可选：增加时间过滤，优先考虑较近的记忆
                            {"OR": [
                                # 查找明确标记为重要的记忆
                                {"metadata.importance": {"gte": "high"}},
                                # 或者较新的记忆
                                {"created_at": {"gte": one_month_ago}}
                            ]}
                        ]
                    }
                    
                    # 使用v2版本的高级搜索功能
                    search_results = self.mem0_client.search(
                        query=message,
                        version="v2",
                        filters=filters,
                        limit=Config.MEM0_MEMORY_LIMIT,
                        output_format="v1.1"
                    )
                    
                    # 格式化长期记忆为文本，增加可读性和相关度显示
                    if search_results and "results" in search_results and search_results["results"]:
                        memories = search_results["results"]
                        long_term_memories = "用户的历史信息和偏好:\n"
                        for i, mem in enumerate(memories):
                            # 提取相关度分数（如果有）
                            relevance = mem.get('relevance_score', '')
                            relevance_str = f"[相关度: {relevance:.2f}] " if relevance else ""
                            
                            # 提取记忆创建时间
                            created_time = mem.get('created_at', '')
                            time_str = f"({created_time}) " if created_time else ""
                            
                            # 添加格式化的记忆条目
                            long_term_memories += f"{i+1}. {relevance_str}{time_str}{mem['memory']}\n"
                except Exception as e:
                    print(f"获取Mem0长期记忆失败: {str(e)}")
                    long_term_memories = ""
            
            # 构建消息列表，先添加系统级提示词（不可修改），再添加用户级提示词
            messages = []
            # 系统级提示词（必须的）
            if self.system_level_prompt:
                messages.append(SystemMessage(content=self.system_level_prompt))
            # 用户级提示词（可选的）
            if current_system_prompt:
                messages.append(SystemMessage(content=current_system_prompt))
            
            # 添加长期记忆（如果有）
            if long_term_memories:
                messages.append(SystemMessage(content=f"以下是用户的历史信息，请在回答时考虑这些信息：\n{long_term_memories}"))
            
            # 添加对话历史
            messages.extend(memory.buffer_as_messages)
            
            # 流式生成响应
            for chunk in self.llm.stream(messages):
                content = chunk.content
                if content:
                    full_reply += content
                    yield f"data: {json.dumps({'reply': content}, ensure_ascii=False)}\n\n"
            
            # 将完整的AI响应添加到记忆中
            if full_reply:
                memory.chat_memory.add_ai_message(full_reply)
                
                # 将对话添加到Mem0长期记忆
                if self.mem0_enabled:
                    try:
                        # 构建消息列表
                        mem0_messages = [
                            {"role": "user", "content": message},
                            {"role": "assistant", "content": full_reply}
                        ]
                        
                        # 准备元数据，增强v2搜索能力
                        metadata = {
                            "chat_id": chat_id,
                            "timestamp": int(time.time()),
                            "importance": self._estimate_importance(message, full_reply),
                            "context": self._extract_context_keywords(message, full_reply)
                        }
                        
                        # 添加到Mem0，带有丰富的元数据
                        self.mem0_client.add(
                            mem0_messages, 
                            user_id=username,
                            metadata=metadata
                        )
                    except Exception as e:
                        print(f"添加到Mem0长期记忆失败: {str(e)}")
                
        except Exception as e:
            error_msg = f"AI服务错误: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
    
    def clear_user_memory(self, username, chat_id):
        """
        清除用户对话记忆和系统提示词
        
        Args:
            username: 用户名
            chat_id: 对话ID
        """
        key = f"{username}__{chat_id}"
        if key in self.user_memories:
            del self.user_memories[key]
        if key in self.user_system_prompts:
            del self.user_system_prompts[key]
            
    def clear_long_term_memory(self, username):
        """
        清除用户的Mem0长期记忆
        
        Args:
            username: 用户名
        """
        if self.mem0_enabled:
            try:
                # 使用v2版本API删除指定用户的所有记忆
                filters = {"AND": [{"user_id": username}]}
                self.mem0_client.delete_all(user_id=username, filters=filters, version="v2")
                return True, "已清除用户的长期记忆"
            except Exception as e:
                print(f"清除Mem0长期记忆失败: {str(e)}")
                return False, f"清除长期记忆失败: {str(e)}"
        else:
            return False, "Mem0长期记忆服务未启用"
    
    def get_memory_count(self):
        """
        获取当前内存中的对话记忆数量
        
        Returns:
            int: 记忆数量
        """
        return len(self.user_memories)
        
    def get_long_term_memories(self, username, limit=10):
        """
        获取用户的长期记忆
        
        Args:
            username: 用户名
            limit: 返回的记忆数量限制
            
        Returns:
            dict: 记忆列表及状态信息
        """
        if not self.mem0_enabled:
            return {"success": False, "message": "Mem0长期记忆服务未启用", "memories": []}
            
        try:
            # 构建高级查询条件（v2版本）
            filters = {
                "AND": [
                    {"user_id": username}
                ]
            }
            
            # 使用高级查询功能
            response = self.mem0_client.get_all(
                version="v2", 
                filters=filters, 
                page=1, 
                page_size=limit,
                output_format="v1.1",
                sort_by="created_at",
                sort_order="desc"  # 最新的记忆优先
            )
            
            # 如果结果包含元数据，增强返回的记忆信息
            if response and "items" in response:
                memories = response["items"]
                enhanced_memories = []
                
                for mem in memories:
                    # 添加元数据和格式化的时间信息
                    enhanced_mem = {
                        "id": mem.get("id"),
                        "memory": mem.get("memory", ""),
                        "created_at": mem.get("created_at"),
                        "updated_at": mem.get("updated_at"),
                        "importance": "未知"
                    }
                    
                    # 提取元数据中的重要性信息
                    if "metadata" in mem and mem["metadata"]:
                        metadata = mem["metadata"]
                        if "importance" in metadata:
                            enhanced_mem["importance"] = metadata["importance"]
                    
                    enhanced_memories.append(enhanced_mem)
                
                return {"success": True, "message": "成功获取长期记忆", "memories": enhanced_memories}
            
            return {"success": True, "message": "成功获取长期记忆", "memories": response}
        except Exception as e:
            print(f"获取Mem0长期记忆失败: {str(e)}")
            return {"success": False, "message": f"获取长期记忆失败: {str(e)}", "memories": []}
    
    def update_long_term_memory(self, memory_id, new_text, metadata=None):
        """
        更新特定的长期记忆
        
        Args:
            memory_id: 记忆ID
            new_text: 新的记忆内容
            metadata: 可选的元数据
            
        Returns:
            tuple: (成功状态, 消息)
        """
        if not self.mem0_enabled:
            return False, "Mem0长期记忆服务未启用"
            
        try:
            # 如果没有提供元数据，获取现有元数据并增强它
            if metadata is None:
                try:
                    # 获取现有记忆
                    existing_memory = self.mem0_client.get(memory_id=memory_id)
                    existing_metadata = existing_memory.get('metadata', {}) if existing_memory else {}
                    
                    # 更新元数据
                    metadata = existing_metadata.copy()
                    metadata['updated_at'] = int(time.time())
                    metadata['last_modified'] = 'user_edit'
                    
                    # 估计重要性（如果之前没有设置）
                    if 'importance' not in metadata:
                        metadata['importance'] = 'high'  # 用户手动编辑的记忆通常比较重要
                except Exception as e:
                    print(f"获取现有记忆元数据失败: {str(e)}")
                    metadata = {
                        'updated_at': int(time.time()),
                        'last_modified': 'user_edit',
                        'importance': 'high'
                    }
            
            # 使用v2版本API更新记忆
            self.mem0_client.update(
                memory_id=memory_id,
                text=new_text,
                metadata=metadata,
                version="v2"
            )
            return True, "成功更新长期记忆"
        except Exception as e:
            print(f"更新Mem0长期记忆失败: {str(e)}")
            return False, f"更新长期记忆失败: {str(e)}"
    
    def delete_long_term_memory(self, memory_id):
        """
        删除特定的长期记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            tuple: (成功状态, 消息)
        """
        if not self.mem0_enabled:
            return False, "Mem0长期记忆服务未启用"
            
        try:
            self.mem0_client.delete(memory_id=memory_id, version="v2")
            return True, "成功删除长期记忆"
        except Exception as e:
            print(f"删除Mem0长期记忆失败: {str(e)}")
            return False, f"删除长期记忆失败: {str(e)}"
    
    def _estimate_importance(self, user_message, ai_reply):
        """
        评估对话的重要性，用于记忆优先级排序
        
        Args:
            user_message: 用户消息
            ai_reply: AI回复
            
        Returns:
            str: 重要性级别 'low', 'medium', 或 'high'
        """
        # 重要性信号词
        high_importance_signals = [
            '记住', '不要忘记', '重要', '必须', '请记住', 
            '我的信息', '我的地址', '我的喜好', '我的偏好',
            '电话', '邮箱', '地址', '生日', '重要日期'
        ]
        
        # 检查信号词出现
        combined_text = (user_message + ' ' + ai_reply).lower()
        for signal in high_importance_signals:
            if signal in combined_text:
                return 'high'
        
        # 消息长度也是重要性的一个指标
        if len(user_message) > 100 or len(ai_reply) > 300:
            return 'medium'
            
        return 'low'
    
    def _extract_context_keywords(self, user_message, ai_reply):
        """
        从对话中提取上下文关键词，用于增强搜索
        
        Args:
            user_message: 用户消息
            ai_reply: AI回复
            
        Returns:
            list: 关键词列表
        """
        # 简单的关键词提取逻辑
        combined_text = (user_message + ' ' + ai_reply).lower()
        
        # 常见的中文停用词
        stop_words = ['的', '了', '和', '是', '在', '我', '有', '你', '我们', '他', '她', '它', '这', '那', '都']
        
        # 分词并过滤
        words = []
        for word in combined_text.replace(',', ' ').replace('.', ' ').replace('?', ' ').replace('!', ' ').split():
            if len(word) > 1 and word not in stop_words:
                words.append(word)
        
        # 返回最多10个关键词
        return words[:10]
# 创建全局AI服务实例
ai_service = AIService()
