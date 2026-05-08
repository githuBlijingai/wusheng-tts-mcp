# 悟声MCP服务器 - 远程调用配置指南

## 📋 概述

本服务器支持SSE（Server-Sent Events）模式，允许局域网或远程机器通过HTTP连接调用MCP工具。

## 🚀 服务器端部署

### 1. 在服务器上启动

```bash
cd 悟声mcp
pip install -r requirements.txt

# 启动服务器（默认监听所有网卡）
python wusound_mcp.py

# 或指定端口和IP
python wusound_mcp.py 8080 0.0.0.0
```

### 2. 配置环境变量

可以修改 `.env` 文件：

```env
WUSOUND_API_KEY=sk-你的API密钥
WUSOUND_API_BASE_URL=https://v1.wusound.cn
MCP_HOST=0.0.0.0              # 监听所有网卡
MCP_PORT=8000                 # 端口
```

### 3. 确保防火墙开放

```bash
# Windows防火墙
netsh advfirewall firewall add rule name="MCP Server" dir=in action=allow protocol=tcp localport=8000

# 或在防火墙设置中手动开放 8000 端口
```

## 🔗 远程客户端配置

### Claude Desktop（远程）

编辑 `~/.claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "wusound-remote": {
      "command": "node",
      "args": [
        "/path/to/@modelcontextprotocol/server-sse/dist/index.js",
        "http://服务器IP:8000/sse"
      ]
    }
  }
}
```

### Cursor（远程）

在 Cursor 设置中添加 MCP Server：

```json
{
  "mcpServers": {
    "wusound-remote": {
      "command": "node",
      "args": [
        "/path/to/@modelcontextprotocol/server-sse/dist/index.js",
        "http://服务器IP:8000/sse"
      ]
    }
  }
}
```

### 其他MCP客户端

对于不支持URL直接配置的MCP客户端，需要使用 MCP SSE Proxy 工具：

```bash
npx @modelcontextprotocol/server-sse http://服务器IP:8000/sse
```

## 🌐 局域网访问示例

假设服务器IP是 `192.168.1.100`，端口是 `8000`：

### 验证服务器是否可访问

```bash
# 测试SSE端点（应该返回SSE流）
curl http://192.168.1.100:8000/sse

# 测试MCP能力端点
curl http://192.168.1.100:8000/capabilities
```

### 完整的Claude Desktop配置示例

```json
{
  "mcpServers": {
    "wusound-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse",
        "http://192.168.1.100:8000/sse"
      ]
    }
  }
}
```

### 使用Python httpx直接调用

```python
import httpx

def call_mcp_tool(server_url: str, tool_name: str, arguments: dict):
    """直接通过HTTP调用MCP服务器的工具"""
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{server_url}/v1/mcp/tools/{tool_name}",
            json={"arguments": arguments}
        )
        return response.json()

# 使用示例
result = call_mcp_tool(
    "http://192.168.1.100:8000",
    "generate_speech",
    {
        "voice_id": "角色ID",
        "text": "你好，这是测试"
    }
)
```

## 🔒 安全建议

### 1. 使用Nginx反向代理+SSL

```nginx
server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

### 2. 添加API Key认证

可以修改服务器代码添加简单的认证：

```python
# 在 wusound_mcp.py 中添加
from functools import wraps

API_SECRET = os.getenv('MCP_API_SECRET', '')

def require_auth(original_func):
    @wraps(original_func)
    def wrapper(*args, **kwargs):
        # 从请求头获取认证信息
        # 验证API Key
        pass
    return wrapper
```

### 3. 限制IP访问

```nginx
# 只允许特定IP段访问
allow 192.168.0.0/16;
allow 10.0.0.0/8;
deny all;
```

## 🐳 Docker部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "wusound_mcp.py"]
```

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  wusound-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - WUSOUND_API_KEY=sk-你的API密钥
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
    restart: unless-stopped
```

启动：

```bash
docker-compose up -d
```

## 📝 快速启动检查清单

- [ ] 服务器上安装Python依赖
- [ ] 配置 `.env` 文件中的API Key
- [ ] 启动MCP服务器
- [ ] 确认防火墙开放端口
- [ ] 测试局域网访问
- [ ] 在客户端配置远程MCP服务器

## ❓ 常见问题

**Q: 连接超时怎么办？**
- 检查服务器是否运行
- 确认防火墙端口开放
- 验证IP地址和端口正确

**Q: 如何查看服务器日志？**
- 服务器启动后会显示实时日志
- 可以重定向到文件：`python wusound_mcp.py > server.log 2>&1 &`

**Q: 支持多少并发连接？**
- FastMCP基于HTTP，支持多客户端连接
- 建议配合Nginx实现负载均衡

**Q: 如何更新服务器？**
- 修改代码后重启服务即可
- 使用systemd管理可实现平滑重启
