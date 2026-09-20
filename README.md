# SW 知识库技能

版本：1.1.0。适用于WorkBuddy等能执行本机Python脚本的桌面助手。

员工使用同一知识库网址，通过自己的账号连接，并上传到获准接收库。链路为：WorkBuddy → Skill内脚本 → SW AI HTTPS API → 员工接收库。无需MCP服务、服务器SSH或共享管理员Key。

- [员工安装、登录与日常使用](references/employee-guide.md)
- [管理员开通账号、库与权限验收](references/admin-guide.md)
- [查询、调用与引用规范](references/query-guide.md)
- [内容整理与测试标准](references/content-standard.md)
- [Skill执行入口](SKILL.md)

按规范保留完整案例、原文与来源，先生成锁定指纹的计划，再按用户授权上传。脚本支持单批1–50份、逐文件解析等待、下载指纹核对、断点对账及正文/自动摘要分离的检索检查。不提供删除、覆盖、共享或模型配置功能。

运行环境：Python 3.10+，仅标准库。Windows使用`py -3`，macOS/Linux通常使用`python3`。网页登录的凭证不会自动传给Skill，需本人在终端隐藏输入密码一次；会话过期重新登录。

## 分发

将同级的`sw-knowledge-upload-workbuddy-v1.1.0.zip`交给获准员工，由员工在WorkBuddy的技能页面上传启用。包不含connection.json、实际员工账号、JWT、API Key、源材料和服务器脚本。将assets中的接入配置示例复制到员工自己的固定目录，填写经管理员核对的库信息；不要修改示例后重新打包给所有人。

`release-manifest.json`包含包内文件的SHA256。更新版本后重新验证包内容，员工自己的接入配置和本机会话不随Skill升级覆盖。

## 当前验证范围

- Skill格式校验通过。
- 上传与查询工具16项模拟测试通过，覆盖重复上传、跨状态复用、源/稿变化、丢失响应后的恢复、不确定写入时停止、账号绑定、权限失败、独立查询的来源输出/无结果/未配置库拦截和Summary不得冒充正文。
- 上传、认证与权限路由已按线上镜像revision核对；公开接口的无认证响应另有项目验证记录。
- 尚未用员工个人账号完成真实登录上传，尚未在员工Windows/WorkBuddy环境安装验收；这些要在管理员分配账号与接收库后执行。不把单元测试当作生产员工链路通过。

## GitHub 分发

仓库：https://github.com/xuyuanpu/sw-knowledge-skill

安装包见仓库 Releases。当前仓库为私有，访问者需获授 GitHub 仓库访问权限；也可由管理员直接分发 ZIP。GitHub 权限与知识库账号权限独立。为兼容已有安装与个人会话，内部标识继续使用 `sw-knowledge-upload`，中文名称统一为「SW 知识库技能」。
