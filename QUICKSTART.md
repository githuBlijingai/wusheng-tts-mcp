# 悟声MCP服务器 - 快速入门

## 📦 两个版本说明

### 版本1: 单用户版 (`wusound_mcp.py`)
- API Key配置在服务器端
- 所有用户共享同一个API Key
- 适合你自己使用，或信任的用户共用一个账户

### 版本2: 多用户版 (`wusound_mcp_multiuser.py`) ✅ 推荐
- API Key由每个调用者提供
- 用户使用自己的API Key
- 适合分发给多人使用

## 🚀 快速开始

### 服务器端（你）

```bash
cd 悟声mcp
pip install -r requirements.txt

# 启动多用户版本
python wusound_mcp_multiuser.py

# 或指定端口
python wusound_mcp_multiuser.py 8000 0.0.0.0
```

### 客户端配置（使用者）

使用者需要在Claude Desktop或Cursor中配置：

```json
{
  "mcpServers": {
    "wusound": {
      "command": "python",
      "args": [
        "/绝对路径/wusound_mcp_multiuser.py",
        "8000",
        "服务器IP"
      ]
    }
  }
}
```

## 🔑 关于API Key

### 多用户版的特点
每个工具的第一个参数都是 `api_key`，使用者调用时需要传入自己的悟声API Key。

例如：
```python
# 使用者调用时
generate_speech(
    api_key="sk-使用者自己的Key",
    voice_id="角色ID",
    text="要生成的文本"
)
```

### 使用者如何获取API Key
1. 访问 https://www.wusound.cn/apiKey
2. 创建新的API Key
3. 在调用MCP工具时填入

## 📋 使用示例

### 1. 查看账户信息
```
工具: get_account_info
参数: {"api_key": "sk-xxx"}
```

### 2. 获取角色列表
```
工具: get_voice_list
参数: {"api_key": "sk-xxx", "show_market": true}
```

### 3. 生成语音
```
工具: generate_speech
参数: {
    "api_key": "sk-xxx",
    "voice_id": "角色ID",
    "text": "你好，这是测试",
    "preset": "balance"
}
```

## 🛠️ 常见问题

**Q: 连接失败？**
- 确认服务器IP和端口正确
- 确认防火墙开放端口

**Q: 提示认证失败？**
- 检查API Key是否正确
- 确认API Key有权限

**Q: 如何确认服务器在运行？**
- 启动时会显示：
  ```
  悟声MCP服务器 (多用户版)
  服务器地址: http://0.0.0.0:8000
  SSE端点: http://0.0.0.0:8000/sse
  ```

## 📞 技术支持

如有问题，检查：
1. Python版本 >= 3.8
2. 依赖已安装：`pip install -r requirements.txt`
3. 端口未被占用
4. 防火墙已开放端口
