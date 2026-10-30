# 知识库与文档管理

## 权限与范围

先列库确认permission。read可查询与读取；write增加上传；manage增加改名、换版、删除。UUID授权只覆盖指定库；管理员设置tenant:<已核对租户ID>授权后，该租户现有及未来库自动纳入。空间manage才可创建新库，单库manage不能建库。不能操作其他租户、修改人员权限或服务器配置。

## 创建与修改库

调用sw_create_knowledge_base，选择同空间现有库作为template_knowledge_base_id，提供name、description与稳定request_id。复制模型、分块和存储配置，创建文档库，关闭额外视觉/音频/问题生成功能。结果不确定时先列库对账，同编号重试不会再次建库；不得换编号绕过。sw_update_knowledge_base传完整名称与描述，空描述会清空描述。

## 修改资料

- 标题：sw_list_documents取得准确ID、标题后，用sw_update_document修改。
- 正文：保留原件，按分类规范整理完整修订稿，用新的版本材料编号上传。等待completed及download_sha256_verified=true，检索并读取新版确认正文、案例和来源完整。随后在用户授权换版的范围内，用sw_replace_document传旧文档ID、新文档ID及旧版准确标题。服务端只在同库新版解析和指纹通过时删除旧版。新文档ID会变化，应更新引用记录；不提供原ID原地正文编辑。
- 换版前验证失败：保持旧版，报告新版ID和失败原因，不自动删除业务资料。

## 删除

只有用户明确要求删除具体库/文档，或明确授权范围内的清理时执行。先列库/列文档核对ID和当前名称，库删除须说明会包含全部文档；若原授权已明确涵盖这些影响，不重复询问。sw_delete_knowledge_base须传confirm_name；sw_delete_document须传confirm_title，均与当前值完全一致。这是避免误删的核对参数，不是额外密码。

删除不是回收站操作；先保留需要的本地源件或备份。响应delete_requested代表后端接受请求，再次列库/文档确认已消失。超时或失败先核实结果，不盲目重试、不连带清理其他资料。

## 客户端刷新

服务端授权立即生效，原个人令牌保持有效期。新增工具需WorkBuddy刷新MCP连接或重开会话；Skill通过固定GitHub Release按需更新，不重新分发个人令牌。
