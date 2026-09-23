# 员工接入指南

## 一次配置，之后直接说需求

安装「SW 知识库技能」v2.1.0。再由管理员提供你的个人 MCP 连接令牌，或只属于你的私密连接配置文件。各员工使用独立令牌，不共用负责人连接。

在 WorkBuddy 的「插件 → MCP服务器 → 配置MCP」添加远程 Streamable HTTP 服务：

- 名称：SW 知识库 / sw-knowledge
- 地址：`https://ai.skillandwill.com/mcp`
- 认证请求头：`Authorization: Bearer 你的个人令牌`

令牌填在连接配置的凭证字段，不发到对话里。若界面支持JSON配置，可参考包内 `assets/mcp.example.json`，将占位值替换为个人令牌；手动配置时不保留未解析的占位符。不同 WorkBuddy 版本入口可能不同，传输类型选 Streamable HTTP。

若管理员给的是私密JSON配置，可让本机助手将其中 sw-knowledge 条目合并到 `~/.workbuddy/mcp.json`（Windows为用户目录下的.workbuddy/mcp.json），保留其他连接；仅本机文件操作，不将凭证回显到对话、日志或提交GitHub。文件应只对本人可读。此操作不需要手动运行Python或登录命令。

保存并启用连接后，对 WorkBuddy 说：

> 使用 SW 知识库技能，列出我可以访问的知识库及权限。

能返回实际库名和权限才算已连接；仅显示Skill已安装不等于连接成功。服务端已通过标准MCP客户端验证，员工自己的 WorkBuddy 客户端仍需执行这一步确认。

## 日常使用

- “从ACC心得中找一个具体行动案例，保留过程并给出原文来源。”
- “将这个文件夹按分类上传规范整理，先给我清单。”
- “按刚才确认的清单上传到这个库，并检查正文检索。”

Agent会自动读取授权库列表。无需员工填写库UUID、安装Python、运行login或维护connection.json。

首次上传先用一份已授权材料验证；批量执行前核对目标库。查询权限与上传权限独立。

## 连接异常

- 401：令牌过期、撤销或填写错误。请管理员换发，然后更新连接。
- 403或工具提示未授权：管理员调整对应库的read/write权限；不要尝试用管理员Key绕过。
- 429：等待Retry-After或至少60秒，不反复并发调用。
- 解析失败/上传不确定：保留材料编号和文档ID，避免换编号重复上传。

令牌默认90天有效，泄露或离职可单独撤销。移除本机连接不会自动撤销服务器令牌，需要管理员执行撤销。

官方配置说明：https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide
官方连接器格式：https://open.workbuddy.cn/docs/connector

本版为自行添加的私有MCP连接，并未上架WorkBuddy连接器市场，也不是OAuth网页登录授权。

## 后续升级

对WorkBuddy说“检查并更新SW知识库技能，保留个人MCP连接”。无需重新收取安装包，执行[在线更新规范](update-guide.md)。从旧版首次升级时同时提供 https://github.com/xuyuanpu/sw-knowledge-skill 。
