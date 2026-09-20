"""Administrator-only local provisioning. Secrets are written to private files, never printed."""
import argparse,json,os,time
from pathlib import Path
from core import Store,Failure
p=argparse.ArgumentParser();p.add_argument('--db',required=True);sp=p.add_subparsers(dest='cmd',required=True)
a=sp.add_parser('issue');a.add_argument('--label',required=True);a.add_argument('--grants',required=True);a.add_argument('--days',type=int,default=90);a.add_argument('--out',required=True)
a=sp.add_parser('revoke');a.add_argument('--id',required=True)
a=sp.add_parser('grant');a.add_argument('--id',required=True);a.add_argument('--grants',required=True)
sp.add_parser('list');args=p.parse_args();store=Store(args.db)
if args.cmd=='issue':
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    # Open before issuing so a missing/private output cannot strand a secret in stdout.
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        ident,token=store.issue(args.label,json.loads(Path(args.grants).read_text()),args.days)
        payload={'mcpServers':{'sw-knowledge':{'type':'streamableHttp','url':'https://ai.skillandwill.com/mcp','headers':{'Authorization':'Bearer '+token}}}}
        with os.fdopen(fd,'w') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
        print(json.dumps({'id':ident,'label':args.label,'config_file':str(out)},ensure_ascii=False))
    except Exception:out.unlink(missing_ok=True);raise
elif args.cmd=='revoke':
    with store.db() as db:r=db.execute('UPDATE principals SET active=0 WHERE id=?',(args.id,))
    print(json.dumps({'revoked':r.rowcount}))
elif args.cmd=='grant':
    from core import uid
    grants=json.loads(Path(args.grants).read_text())
    for kb,permission in grants.items():
        uid(kb)
        if permission not in ('read','write'):raise Failure('权限无效')
    with store.db() as db:r=db.execute('UPDATE principals SET grants=? WHERE id=?',(json.dumps(grants),args.id))
    print(json.dumps({'updated':r.rowcount}))
else:
    with store.db() as db:rows=db.execute('SELECT id,label,grants,expires,active FROM principals').fetchall()
    print(json.dumps([dict(x) for x in rows],ensure_ascii=False,indent=2))
