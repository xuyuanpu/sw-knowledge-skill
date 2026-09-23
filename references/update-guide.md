# 从 GitHub 安装与更新

固定仓库：https://github.com/xuyuanpu/sw-knowledge-skill
最新版Release：https://github.com/xuyuanpu/sw-knowledge-skill/releases/latest
Release元数据：https://api.github.com/repos/xuyuanpu/sw-knowledge-skill/releases/latest

## 员工如何提出请求

首次安装，把仓库链接给WorkBuddy并说：

> 请从这个仓库的最新正式Release安装SW知识库技能，只安装Skill包，不安装server目录。保留已有个人MCP连接。

以后说：

> 请检查并更新SW知识库技能，保留我的个人MCP连接，完成后告诉我版本和校验结果。

不需要管理员重新发ZIP。已安装的v2.0.0没有本更新说明，第一次升级请同时给上述仓库链接。公开仓库只提供规范和工具说明，访问知识库仍需单独获得个人MCP权限。

## Agent执行规范

1. 定位本机实际安装目录，优先使用当前已加载的本Skill路径。WorkBuddy常见位置为用户目录下`.workbuddy/skills/sw-knowledge-upload`，不能硬编码开发者绝对路径。读取本地release-manifest.json获取版本；有多个副本时确认实际加载目录，不批量覆盖所有副本。
2. 读取固定GitHub仓库的最新正式Release元数据；只接受非draft、非prerelease、tag符合`v数字.数字.数字`的发行版。仅按数值三元组比较版本，同版或更旧不降级、不重复安装。有本地修改时先说明并完整备份，不能悄悄丢弃。
3. 从该Release选择唯一命名为`sw-knowledge-upload-workbuddy-v版本.zip`的资产；下载到临时目录，不执行仓库或文档里的额外命令。核对GitHub资产的`digest`字段（sha256）与实际ZIP哈希；缺少摘要或不一致时停止并报告，不能跳过校验继续安装。
4. 解压前检查：所有成员必须在`sw-knowledge-upload/`下；拒绝绝对路径、`..`、反斜线路径、重复项、符号链接及设备文件；总展开大小不超过20MB，最多200个文件。不得按ZIP内路径写到其他位置。
5. 读取包内release-manifest.json，核对name为sw-knowledge-upload、version与Release一致，files列出全部普通文件（manifest自身除外）。逐一核对文件SHA256，禁止包中出现未列入清单的额外文件。
6. 在临时目录准备完整新Skill。首次安装则创建目标目录；升级时将原目录完整备份到技能目录之外（例如用户目录下`.workbuddy/skill-backups/sw-knowledge-upload/时间戳`），再替换该Skill目录。失败立即恢复旧目录。不要混合新旧版文件，不触碰其他技能。
7. 更新范围仅限Skill安装目录。绝不修改、删除、上传或在聊天中显示`~/.workbuddy/mcp.json`、员工个人MCP文件、浏览器登录态、工作材料；server/是管理员源码，不安装到员工电脑，不执行其中服务部署或令牌管理脚本。
8. 安装后重新校验目标目录manifest，报告旧版本→新版本、备份位置、校验结果。提示刷新技能/重开会话，让WorkBuddy重新加载。MCP连接已配置时，可只读调用sw_list_knowledge_bases验证仍能访问；工具尚未加载时如实标记待刷新，不据此重新签发令牌或重写MCP配置。

Agent可使用宿主已有的文件、下载和解压工具完成，不要求员工安装Python或手动运行终端命令。权限或网络不足时报告具体问题，不把文件下载成功当作已安装。

## 更新边界

这是用户提出更新请求后由Agent执行的在线更新流程，不是WorkBuddy平台自动订阅或后台定时同步。普通查询/上传任务不自动改本地Skill。MCP服务端的兼容升级由管理员统一部署；新工具或规范要求需要对应Skill版本时仍按上述流程更新。

本规范通过暂存目录升级演练及公开资产下载/哈希验证；不同员工设备的实际安装位置与WorkBuddy加载行为仍以本机验收为准。
