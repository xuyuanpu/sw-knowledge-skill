# 回退本次MCP接入

只停用新增MCP入口，不回滚知识库业务数据或HTTPS证书。

1. 在服务器使用`/opt/sw-kb-mcp/backups/20260920-173000/`中的template.conf和generated.conf，先与当前配置比较；如其后有其他改动，仅移除本次`location = /mcp`，不能覆盖他人的新配置。
2. 恢复模板`/opt/WeKnora/config/frontend-tls.conf.template`及容器`/etc/nginx/conf.d/default.conf`，执行`docker exec WeKnora-frontend nginx -t`，通过后`nginx -s reload`。
3. `systemctl disable --now sw-kb-mcp.service`。
4. 保留`/opt/sw-kb-mcp/state/`、服务端key和备份供恢复；不能把停止MCP误当作删除上传资料。
