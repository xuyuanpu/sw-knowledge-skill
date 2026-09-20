"""Run on SW server only; back up both template and generated config, test before reload."""
from pathlib import Path
import subprocess,datetime
base=Path('/opt/sw-kb-mcp/backups')/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');base.mkdir(parents=True)
template=Path('/opt/WeKnora/config/frontend-tls.conf.template')
current=subprocess.check_output(['docker','exec','WeKnora-frontend','cat','/etc/nginx/conf.d/default.conf']).decode()
original=template.read_text();(base/'template.conf').write_text(original);(base/'generated.conf').write_text(current)
block='''    # SW MCP: independent employee authentication, no POST retries.
    location = /mcp {
        client_max_body_size 1m;
        proxy_pass http://172.18.0.1:8643/mcp;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        proxy_next_upstream off;
        proxy_connect_timeout 5s;
        proxy_read_timeout 180s;
        proxy_send_timeout 60s;
    }

'''
def patch(s):
    if 'location = /mcp {' in s:raise RuntimeError('MCP route already exists; inspect rather than duplicate')
    marker='    # 前端静态文件'
    assert marker in s
    return s.replace(marker,block+marker,1)
new=patch(current);template.write_text(patch(original));out=base/'new-generated.conf';out.write_text(new)
try:
    subprocess.run(['docker','cp',str(out),'WeKnora-frontend:/etc/nginx/conf.d/default.conf'],check=True)
    subprocess.run(['docker','exec','WeKnora-frontend','nginx','-t'],check=True)
    subprocess.run(['docker','exec','WeKnora-frontend','nginx','-s','reload'],check=True)
except Exception:
    template.write_text(original)
    subprocess.run(['docker','cp',str(base/'generated.conf'),'WeKnora-frontend:/etc/nginx/conf.d/default.conf'],check=True)
    raise
print('PROXY_ENABLED backup='+str(base))
