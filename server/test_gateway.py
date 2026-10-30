import asyncio,hashlib,json,os,tempfile,time
from pathlib import Path
from unittest.mock import patch
import pytest
from core import Store,Gateway,Denied,Failure
KB='11111111-1111-4111-8111-111111111111'
OTHER='22222222-2222-4222-8222-222222222222'
DOC='33333333-3333-4333-8333-333333333333'
CONTENT='## 内容概览\n测试\n## 重点索引\n测试\n## 完整原文\n测试案例保持完整，不能编造。\n## 来源与核对说明\nfixture段落1'
SOURCES=[{'filename':'fixture.md','sha256':hashlib.sha256(CONTENT.encode()).hexdigest(),'locator':'P1'}]
class Fake:
    def __init__(self): self.posts=0;self.calls=[];self.rows=[];self.lose=False;self.body_kb=KB
    async def request(self,method,path,**kw):
        self.calls.append((method,path))
        if path=='/knowledge-bases/'+KB:return {'data':{'id':KB,'name':'试验库'}}
        if path.endswith('/knowledge/file'):
            self.posts+=1
            item={'id':DOC,'knowledge_base_id':KB,'parse_status':'pending','file_name':kw['files']['file'][0],'metadata':json.loads(kw['data']['metadata'])}
            self.rows.append(item)
            if self.lose:raise Failure('network')
            return {'data':item}
        if path.endswith('/knowledge'):return {'data':self.rows,'total':len(self.rows)}
        if path=='/knowledge/'+DOC:return {'data':{'id':DOC,'knowledge_base_id':self.body_kb,'parse_status':'pending','title':'测试'}}
        if path.endswith('/hybrid-search'):return {'data':[{'id':'chunk1','knowledge_id':DOC,'content':'正文','chunk_type':'text'}]}
        if path.startswith('/chunks/'):return {'data':[{'id':'chunk1','content':'正文','chunk_type':'text'}]}
        raise AssertionError(path)
@pytest.fixture
def setup(tmp_path):
    s=Store(tmp_path/'test.db');ident,token=s.issue('test',{KB:'write'})
    return s,s.authenticate('Bearer '+token),Fake(),token
@pytest.mark.asyncio
async def test_upload_idempotent(setup):
    s,p,b,t=setup;g=Gateway(s,b)
    a=await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    c=await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    assert a['id']==c['id']==DOC and c['reused'] and b.posts==1
@pytest.mark.asyncio
async def test_uncertain_reconcile(setup):
    s,p,b,t=setup;g=Gateway(s,b);b.lose=True
    with pytest.raises(Failure):await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    assert (await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES))['reused'] and b.posts==1
@pytest.mark.asyncio
async def test_uncertain_invisible_never_reposts(setup):
    s,p,b,t=setup;g=Gateway(s,b);b.lose=True
    with pytest.raises(Failure):await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    b.rows=[]
    with pytest.raises(Failure):await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    assert b.posts==1
@pytest.mark.asyncio
async def test_conflict(setup):
    s,p,b,t=setup;g=Gateway(s,b)
    await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    with pytest.raises(Failure):await g.upload(p,KB,'MAT-001','不同',CONTENT,SOURCES)
    assert b.posts==1
@pytest.mark.asyncio
async def test_readonly_cannot_write(setup):
    s,p,b,t=setup
    with s.db() as db:db.execute('UPDATE principals SET grants=?',(json.dumps({KB:'read'}),))
    with pytest.raises(Denied):await Gateway(s,b).upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    assert not b.calls
@pytest.mark.asyncio
async def test_other_library_denied_before_backend(setup):
    s,p,b,t=setup
    with pytest.raises(Denied):await Gateway(s,b).search(p,OTHER,'query',3)
    assert not b.calls
@pytest.mark.asyncio
async def test_cross_library_document_denied(setup):
    s,p,b,t=setup;b.body_kb=OTHER
    with pytest.raises(Denied):await Gateway(s,b).document(p,KB,DOC,1)
    assert len(b.calls)==1
@pytest.mark.asyncio
async def test_search_filters_wrong_library(setup):
    s,p,b,t=setup;b.body_kb=OTHER
    assert (await Gateway(s,b).search(p,KB,'query',3))['hits']==[]
@pytest.mark.asyncio
async def test_revoke_immediate(setup):
    s,p,b,t=setup
    with s.db() as db:db.execute('UPDATE principals SET active=0')
    with pytest.raises(Denied):s.authenticate('Bearer '+t)
    with pytest.raises(Denied):await Gateway(s,b).search(p,KB,'query',3)
    assert not b.calls
@pytest.mark.asyncio
async def test_expiry(setup):
    s,p,b,t=setup
    with s.db() as db:db.execute('UPDATE principals SET expires=?',(time.time()-1,))
    with pytest.raises(Denied):s.authenticate('Bearer '+t)
@pytest.mark.asyncio
async def test_no_plaintext_token(setup):
    s,p,b,t=setup
    assert t.encode() not in Path(s.path).read_bytes()
@pytest.mark.asyncio
async def test_structure_rejected(setup):
    s,p,b,t=setup
    with pytest.raises(Failure):await Gateway(s,b).upload(p,KB,'MAT-001','测试','only summary',SOURCES)
    assert b.posts==0

def test_http_mcp_contract(tmp_path,monkeypatch):
    from starlette.testclient import TestClient
    key=tmp_path/'key';key.write_text('fixture-secret')
    monkeypatch.setenv('SW_MCP_DB',str(tmp_path/'http.db'));monkeypatch.setenv('SW_BACKEND_KEY_FILE',str(key))
    import server
    _,token=server.STORE.issue('read',{KB:'read'});server.GATEWAY.backend=Fake()
    headers={'Authorization':'Bearer '+token,'Accept':'application/json, text/event-stream','Host':'ai.skillandwill.com'}
    with TestClient(server.app) as c:
        assert c.post('/mcp',json={}).status_code==401
        assert c.post('/mcp',headers={**headers,'Origin':'https://evil.test'},json={}).status_code==403
        init=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
        assert init.status_code==200 and init.json()['result']['serverInfo']['name']=='sw_knowledge_mcp'
        tools=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':2,'method':'tools/list'}).json()['result']['tools']
        assert len(tools)==12
        assert all(t['annotations']['destructiveHint'] for t in tools if 'delete' in t['name'] or 'replace' in t['name'])
        call=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'sw_list_knowledge_bases','arguments':{}}}).json()['result']
        assert not call.get('isError') and '试验库' in str(call)
        denied=c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'sw_upload_document','arguments':{'knowledge_base_id':KB,'material_id':'MAT-001','title':'测试','content':CONTENT,'sources':SOURCES}}}).json()['result']
        assert denied['isError'] and server.GATEWAY.backend.posts==0

@pytest.mark.asyncio
async def test_completed_download_integrity(setup):
    s,p,b,t=setup;g=Gateway(s,b)
    await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    original=b.request
    async def completed(method,path,**kwargs):
        result=await original(method,path,**kwargs)
        if path=='/knowledge/'+DOC:result['data']['parse_status']='completed'
        return result
    b.request=completed
    async def good(_):return hashlib.sha256(CONTENT.encode()).hexdigest()
    b.download_sha=good
    assert (await g.status(p,KB,DOC))['download_sha256_verified']
    async def bad(_):return 'wrong'
    b.download_sha=bad
    with pytest.raises(Failure):await g.status(p,KB,DOC)

@pytest.mark.asyncio
async def test_hermes_eight_field_card_only_in_pending_library(setup):
    s,p,b,t=setup;pending='7dc09343-76ef-486b-9697-3cdf1d6d31d1'
    heads=['建议选题','热点背景','适合谁看','为什么值得做','具体切入角度','依据与使用边界','待人工确认与下一步','当前状态']
    card='\n'.join('## '+h+'\n具体内容' for h in heads)+'\n外部报道支持；内部资料支持；观点与我们的推演；待人工审核；未获发布授权'
    with s.db() as db:db.execute('UPDATE principals SET grants=?',(json.dumps({KB:'write',pending:'write'}),))
    b.body_kb=pending
    original=b.request
    async def with_pending(method,path,**kwargs):
        if path=='/knowledge-bases/'+pending:return {'data':{'id':pending,'name':'待审库'}}
        return await original(method,path,**kwargs)
    b.request=with_pending
    with pytest.raises(Failure):await Gateway(s,b).upload(p,pending,'SW-TOPIC-test-v2','测试',card,SOURCES)
    p['label']='hermes-agent'
    with pytest.raises(Failure):await Gateway(s,b).upload(p,KB,'SW-TOPIC-test-v2','测试',card,SOURCES)
    with pytest.raises(Failure):await Gateway(s,b).upload(p,pending,'SW-TOPIC-test-v2','测试',card.replace('## 当前状态','## 缺失状态'),SOURCES)
    result=await Gateway(s,b).upload(p,pending,'SW-TOPIC-test-v2','测试',card,SOURCES)
    assert result['id']==DOC and b.posts==1

class TenantFake(Fake):
    def __init__(self):
        super().__init__();self.catalog={KB:{'id':KB,'name':'现有库','tenant_id':10000}}
    async def request(self,method,path,**kw):
        if path=='/knowledge-bases':return {'data':list(self.catalog.values())}
        if path.startswith('/knowledge-bases/') and path.split('/')[-1] in self.catalog:
            return {'data':self.catalog[path.split('/')[-1]]}
        return await super().request(method,path,**kw)

def tenant_principal(s,grant='write'):
    _,token=s.issue('space-admin',{'tenant:10000':grant})
    return s.authenticate('Bearer '+token)

@pytest.mark.asyncio
async def test_future_library_automatically_authorized(setup):
    s,_,_,_=setup;p=tenant_principal(s);b=TenantFake();g=Gateway(s,b)
    assert len((await g.libraries(p))['knowledge_bases'])==1
    b.catalog[OTHER]={'id':OTHER,'name':'以后新建','tenant_id':10000}
    assert len((await g.libraries(p))['knowledge_bases'])==2
    assert await g.authorize(p,OTHER,True)=='write'

@pytest.mark.asyncio
async def test_tenant_grant_cannot_cross_spaces(setup):
    s,_,_,_=setup;p=tenant_principal(s);b=TenantFake();g=Gateway(s,b)
    b.catalog[OTHER]={'id':OTHER,'name':'其他空间','tenant_id':20000}
    assert len((await g.libraries(p))['knowledge_bases'])==1
    with pytest.raises(Denied):await g.search(p,OTHER,'query',3)
    with pytest.raises(Denied):await g.upload(p,OTHER,'MAT-001','测试',CONTENT,SOURCES)
    assert b.posts==0

@pytest.mark.asyncio
async def test_missing_tenant_metadata_fails_closed(setup):
    s,_,_,_=setup;p=tenant_principal(s);b=TenantFake();g=Gateway(s,b)
    b.catalog[KB].pop('tenant_id')
    assert (await g.libraries(p))['knowledge_bases']==[]
    with pytest.raises(Denied):await g.authorize(p,KB,True)

@pytest.mark.asyncio
async def test_space_readonly_cannot_upload(setup):
    s,_,_,_=setup;p=tenant_principal(s,'read');b=TenantFake();g=Gateway(s,b)
    assert await g.authorize(p,KB)=='read'
    with pytest.raises(Denied):await g.upload(p,KB,'MAT-001','测试',CONTENT,SOURCES)
    assert b.posts==0

@pytest.mark.asyncio
async def test_explicit_read_override_and_revocation(setup):
    s,_,_,_=setup;p=tenant_principal(s);b=TenantFake();g=Gateway(s,b)
    with s.db() as db:db.execute('UPDATE principals SET grants=? WHERE id=?',(json.dumps({'tenant:10000':'write',KB:'read'}),p['id']))
    assert (await g.libraries(p))['knowledge_bases'][0]['permission']=='read'
    with pytest.raises(Denied):await g.authorize(p,KB,True)
    with s.db() as db:db.execute('UPDATE principals SET active=0 WHERE id=?',(p['id'],))
    with pytest.raises(Denied):await g.libraries(p)

@pytest.mark.asyncio
async def test_fixed_principals_do_not_gain_future_scope(setup):
    s,p,_,_=setup;b=TenantFake();g=Gateway(s,b)
    b.catalog[OTHER]={'id':OTHER,'name':'新增','tenant_id':10000}
    assert len((await g.libraries(p))['knowledge_bases'])==1
    with pytest.raises(Denied):await g.authorize(p,OTHER,True)

def test_invalid_wildcards_rejected(setup):
    from core import validate_grants
    for scope in ['*','tenant:*','tenant:0','tenant:-1','tenant:10000/other']:
        with pytest.raises(Failure):validate_grants({scope:'write'})

@pytest.mark.asyncio
@pytest.mark.parametrize('grant',['read','write'])
async def test_management_denies_non_managers(setup,grant):
    s,_,_,_=setup;p=tenant_principal(s,grant);b=TenantFake();g=Gateway(s,b)
    for method,args in [(g.delete_library,(KB,'现有库')),(g.update_library,(KB,'新名','说明')),(g.create_library,(KB,'新库','说明','CREATE-1')),(g.delete_document,(KB,DOC,'测试')),(g.update_document,(KB,DOC,'新名')),(g.replace_document,(KB,DOC,OTHER,'测试'))]:
        with pytest.raises(Denied):await method(p,*args)

@pytest.mark.asyncio
async def test_manage_scoped_and_confirmations(setup):
    s,_,_,_=setup;p=tenant_principal(s,'manage');b=TenantFake();g=Gateway(s,b)
    b.catalog[OTHER]={'id':OTHER,'name':'其他空间','tenant_id':20000}
    assert await g.authorize(p,KB,True)=='manage'
    with pytest.raises(Denied):await g.delete_library(p,OTHER,'其他空间')
    with pytest.raises(Failure):await g.delete_library(p,KB,'错误名字')
    with pytest.raises(Failure):await g.delete_document(p,KB,DOC,'错误标题')
    with pytest.raises(Failure):await g.replace_document(p,KB,OTHER,DOC,'测试')
    assert not any(m=='DELETE' for m,_ in b.calls)

@pytest.mark.asyncio
async def test_fixed_manage_cannot_create_space_library(setup):
    s,_,_,_=setup;_,t=s.issue('fixed',{KB:'manage'});p=s.authenticate('Bearer '+t)
    with pytest.raises(Denied):await Gateway(s,TenantFake()).create_library(p,KB,'新库','说明','CREATE-2')

@pytest.mark.asyncio
async def test_uncertain_creation_never_reposts(setup):
    s,_,_,_=setup;p=tenant_principal(s,'manage');b=TenantFake();g=Gateway(s,b);original=b.request;posts=[]
    async def request(method,path,**kw):
        if method=='POST': posts.append(path);raise Failure('timeout')
        return await original(method,path,**kw)
    b.request=request
    for _ in range(2):
        with pytest.raises(Failure):await g.create_library(p,KB,'新库','说明','CREATE-3')
    assert len(posts)==1
