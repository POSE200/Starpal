# Starpal
StarPal - AI Intelligent Chat Assistant Based on Long-Term Memory

一、项目简介

在快节奏的现代社会中，人们对情感陪伴的需求日益凸显，却常面临社交时间碎片化、情感支持不及时等问题。当前市场上的聊天工具多局限于单次对话响应，缺乏对用户长期需求的深度理解，情感交互生硬、个性化不足，难以提供持续、贴心的陪伴体验。
本项目基于长期记忆技术，创新打造智能聊天陪伴助手，通过融合情感识别算法、自然语言处理技术与个性化长期记忆系统，构建 “感知 - 记忆 - 回应” 一体化陪伴体系。
本项目核心功能包括：个性化长期记忆（为用户建立专属记忆空间，记录重要信息、过往关键事件、偏好习惯等）；情感识别与回应（依托自然语言处理和情感分析技术，识别用户对话中的情感倾向并给出对应回应）；个性化聊天（基于用户历史数据调整话题方向，避免模式化对话）。

该助手可广泛服务于需要情感陪伴的年轻群体、独居人士、高压职场人等，通过持续的智能交互，填补情感陪伴缺口。同时，其技术架构可扩展至教育、心理健康等领域，为合作伙伴提供定制化陪伴解决方案，推动 AI 技术在情感交互场景的深度落地，真正实现 “让陪伴更懂你” 的核心价值。

<img width="975" height="1139" alt="image" src="https://github.com/user-attachments/assets/00366a31-eeaf-475b-a5f1-8a3d20a6921f" />


二.🚀 项目部署与运行指南
本项目基于 MySQL + 大模型 API，通过简单的配置即可快速启动并使用。请按照以下步骤完成环境配置与运行。
📁 一、打开项目

# 克隆或进入项目目录

'''python
cd your_project_directory
'''

确保已成功打开项目根目录。

🗄 二、数据库配置（MySQL）

打开项目中的配置文件（如 config.py / .env / settings.yaml，以项目实际为准），修改数据库相关配置项：

'''python
DB_TYPE=mysql
DB_HOST=127.0.0.1        # 数据库服务器地址
DB_PORT=3306             # MySQL 默认端口
DB_NAME=your_database    # 数据库名
DB_USER=your_username    # MySQL 用户名
DB_PASSWORD=your_password # MySQL 密码
'''


📌 注意事项

请确保 MySQL 服务已启动

数据库已创建且用户拥有访问权限

🧠 三、MEM0 与大模型 API 配置

继续在配置文件中修改以下内容：
'''python
# MEM0 配置
MEM0_API_KEY=your_mem0_api_key

# DashScope 配置
DASHSCOPE_API_KEY=your_dashscope_api_key

# 大模型 API 地址
AI_API_BASE=https://your-llm-api-base-url
'''

🔑 密钥获取说明


MEM0_API_KEY：可前往 mem0 官方网站 注册并获取


DASHSCOPE_API_KEY：在 阿里云 DashScope 控制台 获取

🐍 四、环境配置

1️⃣ 创建虚拟环境（推荐）
'''python
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
'''

2️⃣ 安装依赖

进入项目根目录后执行：
'''python
pip install -r requirements.txt
'''

▶️ 五、运行项目
启动后端服务
'''python
python app.py
'''


确保控制台未报错，服务成功启动。

打开前端页面

直接在浏览器中打开：

login.html


即可开始使用系统 🎉

✅ 常见问题（FAQ）

依赖安装失败？
请确认 Python 版本符合 requirements.txt 要求

数据库连接失败？
检查 MySQL 是否启动、账号密码是否正确

API 调用失败？
确认 API Key 是否填写正确，API 地址是否可访问



 




 
