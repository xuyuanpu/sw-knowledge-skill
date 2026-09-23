# SW 知识库技能

版本：2.1.0。通过个人授权的MCP连接，让WorkBuddy等Agent整理上传、查询原文并引用知识库。员工不需要Python、终端login或connection.json。

- [从GitHub安装与一句话更新](references/update-guide.md)
- [员工一次接入与日常使用](references/employee-guide.md)
- [分类上传规范](references/content-standard.md)
- [查询与引用规范](references/query-guide.md)
- [管理员按库授权、调整和撤销](references/admin-guide.md)
- [MCP配置示例（不含令牌）](assets/mcp.example.json)

将本仓库链接交给WorkBuddy，说“从最新正式Release安装SW知识库技能”；已安装后说“检查并更新SW知识库技能”。Agent按更新规范下载、校验、备份及替换，个人MCP配置保留。此为按需更新，不是后台自动同步。首次知识库授权仍由管理员单独提供个人MCP连接。服务器地址统一为`https://ai.skillandwill.com/mcp`，Agent自动列出授权库。只查询不等于可上传。技能名称为「SW 知识库技能」，内部标识sw-knowledge-upload保持不变。

支持五个工具：列库、检索、读取文档、上传正文、查看解析状态。资料按类型整理，保留完整案例、原文、源件指纹和引用。上传幂等、解析完成后下载指纹校验，机构确认仍由业务负责人完成。

源码与安装包：https://github.com/xuyuanpu/sw-knowledge-skill

v1个人网页登录脚本保留在历史Release中；v2默认不使用旧登录流程。Skill安装包只包含规范和无凭证配置示例，个人连接另行私密交付。此项目未提交WorkBuddy连接器市场审核，不声称市场已上架或所有员工已接通。
