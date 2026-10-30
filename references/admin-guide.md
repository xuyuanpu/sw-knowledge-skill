# 管理员开通与撤销

## 员工不再需要终端登录

v2通过独立SW MCP服务连接，知识库底层密钥仅存服务器。员工拿到的是单独生成、按库授权的个人MCP令牌，不是WeKnora管理API Key。Skill与连接配置分发两部分：公共安装包不含令牌，私密配置仅交给对应员工。

接入地址：`https://ai.skillandwill.com/mcp`。首版为Bearer个人令牌授权，默认90天；不是OAuth。

## 开通步骤

1. 确认员工代号及可读/可写/可管理范围。write包含read，manage包含write。上传到哪一个现有库须经业务确认，不能因可查询就默认可上传。
2. 在服务器创建仅管理员可读的grants.json：键为已核对库UUID或`tenant:<租户ID>`，值为read、write或manage。UUID授权不自动扩展；tenant授权自动覆盖该租户现有及未来库，服务端逐库核验实际tenant_id，拒绝跨租户。`*`不受支持。单库显式授权优先于租户授权。
3. 管理员在服务器执行以下命令（通过项目受控SSH入口；员工不执行）：

```sh
/opt/sw-kb-mcp/venv/bin/python /opt/sw-kb-mcp/app/admin.py --db /opt/sw-kb-mcp/state/gateway.sqlite3 issue --label 员工代号 --grants /管理员私密目录/grants.json --days 90 --out /管理员私密目录/员工-mcp.json
```

命令只打印人员ID、标签和文件位置，不打印令牌。JSON配置文件含个人令牌，权限为600，通过公司认可的私密渠道只交给本人；不可提交GitHub或群发。

4. 员工按[接入指南](employee-guide.md)添加连接。首次列库核对权限，再以一份已授权材料验证上传和正文检索。
5. 管理员确认只读令牌不能上传、未授权库和跨库文档读取被拒绝。测试成功不是业务内容已审核。

## 调整与撤销

```sh
# 查看ID、标签、权限及有效期（不显示令牌）
/opt/sw-kb-mcp/venv/bin/python /opt/sw-kb-mcp/app/admin.py --db /opt/sw-kb-mcp/state/gateway.sqlite3 list
# 更新范围，下一次调用生效
/opt/sw-kb-mcp/venv/bin/python /opt/sw-kb-mcp/app/admin.py --db /opt/sw-kb-mcp/state/gateway.sqlite3 grant --id 人员ID --grants /管理员私密目录/grants.json
# 撤销：后续请求拒绝；已经被后台接受的上传不会倒退删除
/opt/sw-kb-mcp/venv/bin/python /opt/sw-kb-mcp/app/admin.py --db /opt/sw-kb-mcp/state/gateway.sqlite3 revoke --id 人员ID
```

换发流程：生成新连接、交给本人、撤销旧ID。服务器只保存令牌SHA256，不能查回原始令牌。人员名单和权限未明确时，不预先生成通用全员令牌。

## 运维与验收

服务`sw-kb-mcp.service`，状态及审计库`/opt/sw-kb-mcp/state/gateway.sqlite3`，底层密钥`/opt/sw-kb-mcp/backend.key`。应用仅监听Docker桥接地址172.18.0.1:8643，由现有HTTPS反代访问；不新增公网端口。审计记录人员ID、动作、库/文档ID和结果，不记录正文、问题或令牌。

备份SQLite应使用在线backup或停服后复制。故障恢复同时保留uploads表，不能丢掉待对账记录后重发资料；management_ops表同样保留，防止重复建库。上游密钥轮换需更新服务器文件并重启服务；个人权限和撤销无需重启。服务源码与详细部署记录在GitHub仓库server/及本地项目services/sw-kb-mcp。

## 已知边界

MCP凭证代表个人连接，不冒充WeKnora网页用户。Agent列库、上传、检索权限由本服务独立校验，底层管理API Key不会下发。上传接受整理后的Markdown正文及来源信息，不接受任意URL或服务器文件路径；来源指纹由员工Agent计算，服务端不能据此证明未收到的源件内容真实。

## 完整管理授权

按已确认租户ID设置 `{"tenant:10000":"manage"}`（10000仅为SW当前租户，其他部署须核实）。通过grant更新指定人员，不改其他人员范围。原令牌及有效期不变；客户端刷新MCP工具列表。manage允许改名、正文换版及删除整库和文档；这不包含账户、权限、模型或服务器管理。操作规范见[管理指南](management-guide.md)。
