# 悟声MCP服务器

[![License](https://img.shields.io/github/license/yourusername/wusound-mcp)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-0.1.0%2B-blue)](https://github.com/modelcontextprotocol/fastmcp)

基于悟声语音合成API的Model Context Protocol (MCP) 服务器，支持SSE传输协议，可让AI助手（如Claude Desktop、Cursor等）调用悟声的高质量语音合成服务。

## 🌟 特性

- ✅ **多用户支持**：每个调用者可使用自己的API Key
- ✅ **SSE传输**：支持Server-Sent Events协议
- ✅ **远程调用**：可在局域网或互联网中远程调用
- ✅ **完整工具集**：支持账户、语音角色、语音生成等全部功能
- ✅ **易于部署**：简单配置即可运行
- ✅ **安全可靠**：API Key由调用方提供，避免密钥泄露风险

## 📦 支持的工具

| 工具名 | 功能描述 |
|--------|----------|
| `get_account_info` | 获取当前用户账户信息 |
| `get_voice_list` | 获取可用语音角色列表 |
| `get_voice_detail` | 获取指定语音角色详细信息 |
| `generate_speech` | 生成语音文件 |
| `create_voice` | 创建自定义语音角色 |
| `get_voice_styles` | 获取语音角色风格列表 |
| `add_voice_style` | 为语音角色添加新风格 |
| `delete_voice_style` | 删除语音角色风格 |
| `get_voice_share_id` | 获取语音角色分享ID |
| `add_voice_by_share` | 通过分享ID添加语音角色 |
| `get_generation_tasks` | 获取语音生成任务列表 |
| `get_generation_task_detail` | 获取语音生成任务详情 |
| `delete_generation_task` | 删除语音生成任务 |
| `upload_voice_conversion_audio` | 上传音色转换音频 |
| `create_voice_clone` | 创建语音克隆角色 |
| `delete_voice` | 删除语音角色 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
# 启动多用户版本（推荐）
python wusound_mcp_multiuser.py

# 或指定端口和IP
python wusound_mcp_multiuser.py 8000 0.0.0.0
```

### 3. 配置客户端

在支持MCP的客户端（如Claude Desktop、Cursor）中添加以下配置：
 
```{
  "mcpServers": {
    "wusound": {
      "url": "http://127.0.0.1:8000/sse",
      "env": {
        "X_API_KEY": " xxxx"
      }
    }
  }
}

## 🔑 API Key 使用说明

### 多用户版特点
每个工具的第一个参数都是 `X_API_KEY`，使用者调用时需要传入自己的悟声API Key。
 

### 获取API Key
1. 访问 [悟声官网](https://www.wusound.cn/apiKey)
2. 创建新的API Key
3. 在调用MCP工具时填入

## 📋 使用示例

### 查看账户信息
```bash
工具: get_account_info
参数: {"api_key": "sk-xxx"}
```

### 获取角色列表
```bash
工具: get_voice_list
参数: {"api_key": "sk-xxx", "show_market": true}
```

### 生成语音
```bash
工具: generate_speech
参数: {
    "api_key": "sk-xxx",
    "voice_id": "角色ID",
    "text": "你好，这是测试",
    "preset": "balance"
}
```

## 🛠️ 部署指南

### 本地部署
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务器
python wusound_mcp_multiuser.py
```

### 远程部署
参考 [远程调用配置指南](REMOTE_SETUP.md)

### Docker部署
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "wusound_mcp_multiuser.py"]
```

## 📞 技术支持
+86 13710688743
### 常见问题
- **连接失败**：确认服务器IP和端口正确，防火墙开放端口
- **认证失败**：检查API Key是否正确
- **服务器未运行**：确保服务器已启动并显示相关信息

### 日志查看
```bash
# 启动时查看日志
python wusound_mcp_multiuser.py

# 或重定向到文件
python wusound_mcp_multiuser.py > server.log 2>&1 &
```

## 📝 注意事项

1. **API Key安全**：每个用户使用自己的API Key，避免密钥泄露
2. **网络配置**：确保服务器端口在防火墙中开放
3. **版本兼容**：确保Python版本 >= 3.8
4. **资源限制**：注意服务器资源使用情况

## 🤝 贡献

欢迎提交Issue和Pull Request来改进此项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢 [悟声](https://www.wusound.cn/) 提供高质量的语音合成服务，以及 [FastMCP](https://github.com/modelcontextprotocol/fastmcp) 项目提供的MCP框架支持。
