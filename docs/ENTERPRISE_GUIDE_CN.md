# NotebookLM 企业版使用指南

通过命令行（CLI）和 MCP Server 访问 **Gemini Enterprise（NotebookLM Pro）**。

企业版地址：`https://vertexaisearch.cloud.google.com`

## 安装

```bash
# 从源码安装（企业版支持在 feat/enterprise-support 分支）
git clone https://github.com/jacob-bd/notebooklm-mcp-cli.git
cd notebooklm-mcp-cli
git checkout feat/enterprise-support
uv tool install .
```

安装完成后获得两个可执行文件：

| 命令 | 用途 |
|------|------|
| `nlm` | 命令行工具，直接在终端使用 |
| `notebooklm-mcp` | MCP Server，供 AI 助手（Claude、Cursor 等）调用 |

## 认证配置

只需一条命令，粘贴你的企业版地址即可：

```bash
nlm login --url "https://vertexaisearch.cloud.google.com/u/0/home/cid/79e69e06-xxxx-xxxx?hl=en_US"
```

Chrome 会自动打开企业页面。登录你的 Google Workspace 账户后，所有配置（Cookies、组织 ID、Project ID）自动提取并保存。

> 企业版地址在哪里找？登录 Gemini Enterprise 后，浏览器地址栏的 URL 就是。

### 验证

```bash
nlm list notebooks
```

看到你的 Notebook 列表即为成功。后续命令无需再次认证，直到 Cookies 过期。过期后重新运行 `nlm login --url ...` 即可。

## 常用命令

### Notebook 管理

```bash
nlm list notebooks                         # 列出所有 Notebook
nlm create notebook "我的研究项目"           # 创建 Notebook
nlm get notebook <id>                       # 查看 Notebook 详情
nlm describe notebook <id>                  # AI 生成的内容摘要
nlm rename notebook <id> "新标题"           # 重命名
nlm delete notebook <id> --confirm          # 删除（不可撤销）
```

### Source 管理

```bash
nlm list sources <notebook-id>                              # 列出所有 Source
nlm add url <notebook-id> "https://example.com/article"     # 添加网页
nlm add text <notebook-id> "文本内容" --title "标题"          # 添加文本
nlm rename source -n <notebook-id> <source-id> "新名称"     # 重命名
nlm delete source <source-id> --confirm                     # 删除
```

### 对话查询

```bash
nlm chat send <notebook-id> "这篇文章的核心观点是什么？"
```

AI 会基于 Notebook 中的所有 Source 回答问题，并引用来源。

### Studio 内容生成

```bash
nlm studio create <notebook-id> audio --confirm    # 创建播客音频
nlm studio status <notebook-id>                    # 查看生成状态
```

### 协作分享

```bash
nlm share status <notebook-id>                           # 查看分享状态
nlm share invite <notebook-id> colleague@company.com     # 邀请协作者
```

> 注意：企业版不支持公开链接分享，只能通过邮件邀请。

### 笔记

```bash
nlm note create <notebook-id> --title "笔记标题" --content "内容"
nlm note delete <notebook-id> <note-id> --confirm
```

## MCP Server 配置

### Claude Code / Claude Desktop

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "notebooklm-mcp",
      "env": {
        "NOTEBOOKLM_BASE_URL": "https://vertexaisearch.cloud.google.com",
        "NOTEBOOKLM_PROJECT_ID": "你的 Project ID",
        "NOTEBOOKLM_CID": "你的组织 CID"
      }
    }
  }
}
```

> MCP Server 启动时会自动从本地 profile 读取已保存的 Cookies（通过 `nlm login` 保存的），无需在配置中写入 Cookies。

配置完成后，可以用自然语言操作 NotebookLM：

- "列出我所有的 Notebook"
- "创建一个关于机器学习的 Notebook，添加这个 URL 作为来源"
- "根据 Notebook 内容生成一期播客"

### 手动配置（可选）

如果不想用 `nlm login --url`，也可以通过环境变量手动配置：

```bash
export NOTEBOOKLM_BASE_URL="https://vertexaisearch.cloud.google.com"
export NOTEBOOKLM_CID="79e69e06-..."        # 组织 ID
export NOTEBOOKLM_PROJECT_ID="77341597043"  # Project ID
nlm login                                    # 仍需登录提取 Cookies
```

## 企业版与标准版差异

| 特性 | 标准版（免费/Plus） | 企业版 |
|------|-------------------|--------|
| 地址 | `notebooklm.google.com` | `vertexaisearch.cloud.google.com` |
| 单 Notebook 最大 Source 数 | 50 | 300 |
| 公开链接分享 | 支持 | 不支持（仅邮件邀请） |
| 文件上传 | 标准三步协议 | Discovery Engine 两步协议 |
| 音频/视频概览 | 支持 | 支持 |
| 报告（摘要、学习指南等） | 支持 | 支持 |
| 思维导图 | 支持 | 支持 |
| 闪卡 | 支持 | 不支持 |
| 信息图 | 支持 | 不支持 |
| 幻灯片 | 支持 | 不支持 |
| 数据表格 | 支持 | 不支持 |

## 常见问题

### "Authentication expired"

重新运行 `nlm login`。企业版的 Cookie 会定期轮换，CSRF Token 和 Session ID 由工具自动刷新，但基础 Cookie 过期后需要重新登录。

### "API error (code 3)"

请求参数无效。检查 `NOTEBOOKLM_PROJECT_ID` 是否正确设置。在浏览器中打开任意 Notebook，URL 参数 `?project=XXXXX` 中可以找到。

### Notebook 列表为空

- 确认已运行 `nlm login` 且使用正确的 Google Workspace 账户登录
- 确认 `NOTEBOOKLM_CID` 与 URL 中的组织 ID 一致

### 创建 Studio 内容时报 "type not available"

企业版不支持闪卡、信息图、幻灯片和数据表格。支持的类型：音频概览、视频概览、简报文档、学习指南、FAQ、时间线、思维导图。

### 对话查询返回 400 错误

确认所有三个环境变量（`NOTEBOOKLM_BASE_URL`、`NOTEBOOKLM_PROJECT_ID`、`NOTEBOOKLM_CID`）都已正确设置。如果仍有问题，重新运行 `nlm login`。
