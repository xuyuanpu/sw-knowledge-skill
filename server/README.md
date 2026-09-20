# SW Knowledge MCP 服务

为 SW 知识库技能提供 Streamable HTTP 工具接入。Python 3.12、官方MCP Python SDK 1.30.0（固定维护分支）、单进程Uvicorn、SQLite持久化。员工凭证为服务端独立生成的随机Bearer令牌，数据库只存SHA256；这是个人令牌模式，不是OAuth授权服务器。

## 能力

- `sw_list_knowledge_bases`：只返回个人已授权的库。
- `sw_search_knowledge`：单库检索，逐条核对文档归属并区分摘要/正文。
- `sw_read_document`：先检查授权库与文档归属，再按页取正文片段。
- `sw_upload_document`：接收Markdown正文及来源，不接受任意路径/URL；稳定编号幂等，SQLite在POST前记录待对账状态，未知结果不重发。
- `sw_get_upload_status`：解析完成后验证本服务上传稿的下载SHA256。

无删除、共享、权限管理或模型管理MCP工具。工具可发现并不意味着有写权限，执行时按当前数据库权限拒绝。新增知识库不会自动加入员工范围。每次请求及每次工具执行重新鉴权；已提交后台的任务不能靠撤销令牌撤回。

## 本地验证

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt pytest pytest-asyncio
.venv/bin/python -m pytest test_gateway.py -q
```

14项测试涵盖鉴权、权限变更/撤销/过期、跨库泄漏阻断、原文结构、幂等与不确定写入对账、下载完整性以及真实ASGI MCP握手/工具调用。

## 部署配置

- `SW_BACKEND_URL`：服务端WeKnora API地址，当前仅本机loopback。
- `SW_BACKEND_KEY_FILE`：仅服务用户可读的后端Key文件，不能放在仓库、日志或员工配置。
- `SW_MCP_DB`：SQLite文件位置，需要服务用户写权限。
- 生产入口`https://ai.skillandwill.com/mcp`；单进程监听Docker桥接172.18.0.1:8643，前端Nginx精确反代，关闭POST重试。
- TLS由现有知识库域名证书负责。MCP强制校验Bearer及Origin，SDK校验Host；限每令牌60请求/分钟，单次工具50秒，入站最多1MB，上传稿最大600KB且200000字符。

本项目`deploy/`中的脚本针对现有SW服务器，不是通用一键安装器。bootstrap.sh首次在线pip解析曾失败，实际部署使用从PyPI下载并逐个校验SHA256的Linux wheels离线安装；依赖版本保持requirements.txt不变。独立Python解释器从同机已安装的3.12.14运行时复制，不修改Hermes的环境。

管理员按Skill内references/admin-guide.md签发、修改、撤销个人令牌；admin.py不会输出明文凭证，只写入600权限的指定新文件。对不再使用的私密交付文件进行受控清理；令牌撤销与删除交付文件是两件事。

## 状态、审计与恢复

SQLite包含principals、uploads、audit。audit仅记录身份ID、工具动作、库/文档ID、结果和时间；不记录Token、查询内容或上传正文。使用SQLite在线backup备份，保留uploads状态；不得清空对账表后盲目重传。后台密钥变更需要重启，员工权限调整与撤销无需重启。

不确定上传保留同一材料编号和参数，查到唯一匹配远端文件才能复用；若上次请求从未到达后端且查无文件，需管理员核实再处理该待对账记录，不提供自动强制重发。已存在旧版上传资料不会自动迁移进本服务的编号台账，首次迁移须核对历史清单。

## 已验证边界

标准MCP SDK客户端通过公网完成合成材料上传、解析、指纹、检索、原文读取、重复复用及权限隔离；并不等于每位员工WorkBuddy客户端已经安装并接通。业务内容仍需人工核对。员工实际名单和按库范围确认后逐人开通，不生成共享万能令牌。
