1.实例化客户端
```python
import os
from mem0 import MemoryClient

os.environ["MEM0_API_KEY"] = "your-api-key"

client = MemoryClient()
```
2.添加回忆
```python
messages = [
    {"role": "user", "content": "Thinking of making a sandwich. What do you recommend?"},
    {"role": "assistant", "content": "How about adding some cheese for extra flavor?"},
    {"role": "user", "content": "Actually, I don't like cheese."},
    {"role": "assistant", "content": "I'll remember that you don't like cheese for future recommendations."}
]
client.add(messages, user_id="alex")
```
3.找回记忆
3.1搜索用户记忆
```python
# Example showing location and preference-aware recommendations
query = "I'm craving some pizza. Any recommendations?"
filters = {
    "AND": [
        {
            "user_id": "alex"
        }
    ]
}
client.search(query, version="v2", filters=filters)
```
3.2获取用户全部记忆
```python
filters = {
   "AND": [
      {
         "user_id": "alex"
      }
   ]
}

all_memories = client.get_all(version="v2", filters=filters, page=1, page_size=50)
```
4.更新记忆
4.1更新记忆
```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

memory_id = "your_memory_id"
client.update(
    memory_id=memory_id,
    text="Updated memory content about the user",
    metadata={"category": "profile-update"}
)
```
4.2批量更新记忆
```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

update_memories = [
    {"memory_id": "id1", "text": "Watches football"},
    {"memory_id": "id2", "text": "Likes to travel"}
]

response = client.batch_update(update_memories)
print(response)
```
Tips  技巧
You can update both text and metadata in the same call.
您可以在同一调用中更新文本和元数据 。
Use batchUpdate when you’re applying similar corrections at scale.
当您大规模应用类似的更正时，请使用 batchUpdate。
If memory is marked immutable, it must first be deleted and re-added.
如果内存被标记为不可变 ，则必须先删除并重新添加它。
Combine this with feedback mechanisms (e.g., user thumbs-up/down) to self-improve memory.
将其与反馈机制（例如，用户竖起大拇指/竖起大拇指）相结合，以自我提升记忆。

5.删除记忆
5.1.按id删除记忆
```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

memory_id = "your_memory_id"
client.delete(memory_id=memory_id)
```
5.2.批量删除多个记忆
```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

delete_memories = [
    {"memory_id": "id1"},
    {"memory_id": "id2"}
]

response = client.batch_delete(delete_memories)
print(response)
```
5.3 通过过滤器删除记忆（例如，user_id）
```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")

# Delete all memories for a specific user
client.delete_all(user_id="alice")
```
您还可以按其他参数进行筛选，例如：
agent_id
run_id
metadata (as JSON string)
元数据 （作为 JSON 字符串）
