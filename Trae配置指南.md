# Trae MCP 配置 - HTTP模式

## 📋 说明

如果你需要在另一台机器的Trae中使用悟声MCP服务器，有两种方式：

## 方式1: 通过HTTP REST API调用

这是最简单的方式，不需要MCP客户端支持！

### 服务器端（你）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动REST API服务器
python wusound_api.py

# 服务器会显示:
# API文档: http://0.0.0.0:8000/docs
# 服务器地址: http://0.0.0.0:8000
```

### Trae中的使用

在Trae的AI配置或插件中调用HTTP API：

```python
import requests

# 配置
BASE_URL = "http://你的服务器IP:8000"
API_KEY = "使用者的悟声API Key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 生成语音示例
response = requests.post(
    f"{BASE_URL}/generate/speech",
    headers=headers,
    json={
        "voice_id": "角色ID",
        "text": "要生成的文本",
        "preset": "balance"
    }
)

result = response.json()
print(result['audio_url'])
```

### 查看API文档

启动服务器后，访问：http://你的服务器IP:8000/docs

会有完整的Swagger UI文档！

## 方式2: 使用MCP CLI桥接

### 服务器端（你）

启动MCP SSE服务器：

```bash
python wusound_mcp_multiuser.py 8000 0.0.0.0
```

### Trae配置

在Trae的MCP配置文件（通常是项目根目录的`.trae/mcp.json`或全局配置）中添加：

```json
{
  "mcpServers": {
    "wusound": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse",
        "http://你的服务器IP:8000/sse"
      ]
    }
  }
}
```

**注意**：这种方式需要Trae支持MCP协议。

## 🆚 对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| HTTP REST API | 任何客户端都能用，文档完整 | 需要写代码调用 |
| MCP CLI桥接 | 可以直接在AI对话中使用 | 需要客户端支持MCP |

## 📝 推荐

**如果Trae支持MCP**，使用方式2更方便。

**如果Trae只支持HTTP API**，使用方式1，写一个简单的封装。

## 🔧 获取API文档

服务器启动后访问：
- Swagger UI: http://IP:8000/docs
- ReDoc: http://IP:8000/redoc
- OpenAPI JSON: http://IP:8000/openapi.json
