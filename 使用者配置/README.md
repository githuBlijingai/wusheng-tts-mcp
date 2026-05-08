# 悟声MCP客户端配置

## 📋 前提条件

1. Python 3.8+
2. 安装必要的依赖

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastmcp httpx python-dotenv
```

### 2. 配置你的API Key

复制 `.env.example` 为 `.env`，然后填入你的悟声API Key：

```env
WUSOUND_API_KEY=sk-你的悟声API Key
```

### 3. 获取服务器地址

向MCP服务器管理者获取服务器地址，类似：
- `http://192.168.1.100:8000/sse`
- `http://你的域名.com/sse`

### 4. 配置MCP客户端

#### Claude Desktop

编辑 `~/.claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "wusound": {
      "command": "mcp",
      "args": [
        "client",
        "--server-url",
        "http://服务器地址/sse"
      ],
      "env": {
        "WUSOUND_API_KEY": "你的API Key"
      }
    }
  }
}
```

#### Cursor

在 Settings → MCP Servers 中添加服务器。

## 📡 直接HTTP调用

如果你的MCP客户端不支持远程连接，可以使用REST API方式：

```python
import requests

# 设置服务器地址和你的API Key
BASE_URL = "http://服务器地址"
API_KEY = "你的悟声API Key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 调用工具
response = requests.post(
    f"{BASE_URL}/tools/generate_speech",
    headers=headers,
    json={
        "voice_id": "角色ID",
        "text": "要生成的文本",
        "preset": "balance"
    }
)

print(response.json())
```

## ❓ 常见问题

**Q: 连接失败？**
- 确认服务器地址正确
- 确认端口已开放
- 确认你的API Key有效

**Q: 提示"没有权限"？**
- 检查你的悟声API Key是否有效
- 确认Key有足够的点数

**Q: 如何找到我的API Key？**
- 访问 https://www.wusound.cn/apiKey
- 创建或查看你的API Key
