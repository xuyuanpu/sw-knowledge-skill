# 员工接入指南

## 你需要拿到什么

找知识库管理员拿到四项：

1. `sw-knowledge-upload-workbuddy-v1.1.0.zip`。
2. 本人的知识库账号或邀请（知识库账号与WorkBuddy账号是两回事）。
3. 接收库名称、库ID及工作空间ID（如果需要切换工作空间）。
4. 一份按本人接收库填写的`connection.json`，里面只有库ID、库名和可选空间ID，没有密码。

统一网站：https://ai.skillandwill.com 。每个人不需要申请新域名或单独搭服务器；同一网站通过个人账号识别身份。不要互用账号或把管理员API Key发给员工。此包不依赖MCP，也不需要在WorkBuddy填写模型API Key来连接知识库；现有知识库的解析/向量模型由管理员配置。

## 安装Skill

WorkBuddy → 技能 → 添加技能 → 上传技能，选择ZIP，检查通过后启用。新建任务并选择只包含待处理材料的本地工作目录，按客户端提示授权读取该目录。

如果企业策略禁用个人安装，请管理员通过企业Skill管理分发，不绕过客户端限制。

官方安装依据：[WorkBuddy技能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)。本包已制作，但不代表已替所有员工安装或完成企业分发。

## 首次连接（本人操作一次）

1. 浏览器打开SW AI，以本人账号登录，确认能看到分配的接收库。没有账号先联系管理员；注册入口可能受系统设置控制，不保证自行注册就能进入团队库。
2. 本机需Python 3.10+。在终端运行`python3 --version`；Windows可运行`py -3 --version`。没有时安装Python官方发行版，并重新打开WorkBuddy。
3. 将connection.json放在员工自己的固定目录，独立于Skill安装目录和共享材料文件夹；升级Skill不会覆盖它。
4. 在终端进入解压的Skill目录，运行：

```sh
python3 scripts/kb_upload.py --profile "/你的目录/connection.json" login
python3 scripts/kb_upload.py --profile "/你的目录/connection.json" doctor
```

Windows将`python3`替换成`py -3`，使用自己的Windows路径。邮箱和密码由本人在终端输入，密码不回显。不要把密码发在WorkBuddy对话里，也不要让助手替你输入。

脚本只向固定的SW HTTPS域名发送登录请求；不会保存密码或返回的租户API Key。短期个人会话存于本机用户目录`.sw-knowledge-upload/<配置路径摘要>/session.json`，受本机用户权限限制。不要打开、截屏、上传或同步这个目录。更换电脑需重新登录；到期出现401时再次login。需退出时运行同样命令，将login改为logout。

5. doctor应显示本人的用户ID、空间ID和配置的库名。只读成功还不代表有上传权限；首次用一份已授权的真实内部材料走完整流程，核对文件可见性与写入权限后再做批量。

## 每次交给WorkBuddy的话

```text
使用SW知识库上传Skill。
接入配置是：[我本机的connection.json路径]。
把[材料文件或文件夹]按规范整理，保留完整案例和原文，上传到[接收库名称]。
本次授权整理和新增上传，不替换现有资料。
先展示文件数、目标库和待核项，然后继续执行上传与检索验证。
不要读取或输出我的会话文件、密码和API Key；凭证只允许上传脚本内部使用。
```

WorkBuddy会创建一个独立批次目录，建议结构：

```text
本次批次/
  originals/           原件（不改动）
  files/               整理后Markdown
  batch.json           来源与目标清单
  upload-plan.json     锁定文件指纹的上传计划
  upload-state.json    上传ID、解析及检索进度
  source-ledger.json   源段落去向/排除理由
  review.md            问答抽测和待核项
```

原件、实名对应表和私密校对台账留本地；脚本只上传计划中明确的Markdown及最小来源元数据。由WorkBuddy读取原稿可能涉及该工具本身的云处理政策，按公司批准的材料范围使用，不因知识库“内部”就自动允许上传所有敏感资料。

## 常见情况

- **看不到库/403**：发给管理员库名、用户ID、错误码，不发密码。先整理本地资料，不换用管理员账号。
- **401**：本人重新login；移动connection.json后，其配置路径对应的本机会话不同，也需重新登录。
- **中断**：使用原upload-plan.json和upload-state.json恢复；别删进度重来。若显示post_pending但服务端找不到，先让管理员对账。若残留`.lock`，先确认上一次进程确已结束，再移除该锁，不能在进程仍运行时移除。
- **同编号不同正文**：单独做换版计划，不能覆盖旧稿。新版用明确版本编号，旧稿是否移出检索由负责人处理。
- **解析成功却只有摘要命中**：保留报告，标检索待复核。自动Summary不是正文；不要为了通过测试把摘要写回原稿。

本机connection.json中的库清单是防误操作设置，不是安全权限边界。真正的权限由服务器执行。

## 日常查询与取材

除上传外，可以让WorkBuddy“在已配置的知识库查询某个问题并给出原文来源”。执行方法及引用规则见[查询与调用规范](query-guide.md)。查询只要求目标库可读，不能据此推断可上传。
