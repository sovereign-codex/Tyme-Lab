"""Synthetic native-API responses; no live workspace, credentials, or requests."""
from copy import deepcopy
import hashlib
import json
import subprocess
import sys
from types import SimpleNamespace

import pytest
from adapters.tyme_notion_rest_provider_v0 import (
    API_VERSION, NotionReadTransport, NotionRESTProvider, ProviderError,
    _scope_ref_for_expected_bot, _transport_profile,
)

ROOT = "10000000-0000-4000-8000-000000000001"
CHILD = "10000000-0000-4000-8000-000000000002"
OTHER = "10000000-0000-4000-8000-000000000003"
BOT = "10000000-0000-4000-8000-000000000004"
CURSOR = "10000000-0000-4000-8000-000000000005"
TEXT = '# Body\r\n\tΩ é\n```xml\n<page url="outsider">not membership</page>\n```\n'

def block(identity, kind="child_page"):
    return {"object":"block","id":identity,"parent":{"type":"page_id","page_id":ROOT},"type":kind,kind:{}}

def metadata(identity):
    return {"object":"page","id":identity,"in_trash":False,
            "parent":({"type":"workspace","workspace":True} if identity==ROOT else {"type":"page_id","page_id":ROOT}),
            "last_edited_time":"2026-01-01T00:00:00Z",
            "properties":{"title":{"type":"title","title":[{"plain_text":"Fixture"}]}}}

class Native:
    def __init__(self):
        self.calls=[]; self.meta={i:metadata(i) for i in (ROOT,CHILD)}
        self.markdown={i:{"object":"page_markdown","id":i,"markdown":TEXT,"truncated":False,"unknown_block_ids":[]} for i in (ROOT,CHILD)}
        self.batches={None:{"object":"list","results":[block(CHILD)],"has_more":False,"next_cursor":None}}
        self.transform=lambda path,body:body
    def get_json(self,path,params=None,*,timeout_seconds):
        assert timeout_seconds>0; self.calls.append((path,deepcopy(params),timeout_seconds))
        if path=="/v1/users/me": value={"object":"user","type":"bot","id":BOT}
        elif path.endswith("/children"): value=self.batches[(params or {}).get("start_cursor")]
        elif path.endswith("/markdown"): value=self.markdown[path.split("/")[-2]]
        else: value=self.meta[path.split("/")[-1]]
        return self.transform(path,deepcopy(value))

def provider(native=None,**kwargs): return NotionRESTProvider(native or Native(),ROOT,**kwargs)

def test_native_membership_and_markdown():
    n=Native(); p=provider(n)
    listing=p.list_child_pages(ROOT,cursor=None,timeout_seconds=5)
    assert listing["items"]==[{"page_id":CHILD,"parent_page_id":ROOT}]
    assert p.get_page(CHILD,timeout_seconds=5)["content"]==TEXT

def test_pagination_and_recheck():
    n=Native()
    n.batches[None]={"object":"list","results":[],"has_more":True,"next_cursor":CURSOR}
    n.batches[CURSOR]={"object":"list","results":[block(CHILD)],"has_more":False,"next_cursor":None}
    p=provider(n)
    assert p.list_child_pages(ROOT,cursor=None,timeout_seconds=5)["has_more"] is True
    assert p.list_child_pages(ROOT,cursor=CURSOR,timeout_seconds=5)["has_more"] is False
    assert p.list_child_pages(ROOT,cursor=None,timeout_seconds=5)["has_more"] is True

@pytest.mark.parametrize("key,value",[("truncated",True),("truncated",None),("unknown_block_ids",None),("unknown_block_ids",[OTHER])])
def test_markdown_gaps_not_complete(key,value):
    n=Native(); n.markdown[ROOT][key]=value
    assert provider(n).get_page(ROOT,timeout_seconds=5)["content_complete"] is False

def test_moved_child_rejected():
    n=Native(); p=provider(n); p.list_child_pages(ROOT,cursor=None,timeout_seconds=5)
    n.meta[CHILD]["parent"]["page_id"]=OTHER
    with pytest.raises(ProviderError): p.get_page(CHILD,timeout_seconds=5)

@pytest.mark.parametrize("trash",[None,True,0,"false"])
def test_trash_must_be_false(trash):
    n=Native(); n.meta[ROOT]["in_trash"]=trash
    with pytest.raises(ProviderError): provider(n).get_page(ROOT,timeout_seconds=5)

def test_archived_alias_optional():
    n=Native(); assert provider(n).get_page(ROOT,timeout_seconds=5)["content_complete"]
    n.meta[ROOT]["archived"]=True
    with pytest.raises(ProviderError): provider(n).get_page(ROOT,timeout_seconds=5)

def test_scope_identity_is_bot_id():
    assert provider().connection_scope_ref=="notion-bot:"+BOT

def test_transport_profile_covers_full_r1_envelope():
    from adapters.tyme_notion_live_read_v0 import AcquisitionLimits
    limits=AcquisitionLimits()
    profile=_transport_profile(limits)
    expected=1+3*(1+limits.max_children)+2*limits.max_listing_pages
    assert profile["max_calls"]==expected==320
    assert profile["max_calls"]>1+3*(1+40)+2*limits.max_listing_pages
    assert profile["min_interval"]*(profile["max_calls"]-1) <= limits.max_elapsed_seconds*0.80

def test_wrong_bot_rejected_before_page_acquisition():
    n=Native()
    with pytest.raises(ProviderError,match="bot_identity_mismatch"):
        provider(n,expected_bot_id=OTHER)
    assert [call[0] for call in n.calls]==["/v1/users/me"]

def test_expected_scope_is_independent_input():
    assert _scope_ref_for_expected_bot(BOT)=="notion-bot:"+BOT

def test_cli_requires_expected_bot_id(tmp_path):
    target=tmp_path/"capture"
    result=subprocess.run(
        [sys.executable,"-m","adapters.tyme_notion_rest_provider_v0",
         "--root",ROOT,"--output-dir",str(target)],
        text=True,capture_output=True,
    )
    assert result.returncode==2
    assert "--expected-bot-id" in result.stderr
    assert not target.exists()

def test_merged_r1_interop(tmp_path):
    from adapters.tyme_notion_live_read_v0 import acquire_notion_snapshot
    from adapters.tyme_institutional_discovery_snapshot_v0 import write_acquisition_bundle, read_acquisition_bundle
    p=provider(); bundle=acquire_notion_snapshot(ROOT,p,connection_scope_ref=p.connection_scope_ref)
    assert bundle["acquisition_status"]=="complete"
    target=tmp_path/"bundle.json"; write_acquisition_bundle(bundle,target)
    assert read_acquisition_bundle(target,expected_manifest_sha256=bundle["manifest_sha256"])==bundle

def test_unknown_markdown_stays_partial():
    from adapters.tyme_notion_live_read_v0 import acquire_notion_snapshot
    n=Native(); del n.markdown[ROOT]["truncated"]
    p=provider(n); bundle=acquire_notion_snapshot(ROOT,p,connection_scope_ref=p.connection_scope_ref)
    assert bundle["acquisition_status"]=="partial"

class Response:
    def __init__(self,raw=b'{"object":"user"}',status=200,headers=None):
        self.raw=raw; self.pos=0; self.status=status
        self.headers={"Content-Type":"application/json","Content-Length":str(len(raw))}
        if headers: self.headers.update(headers)
    def getheader(self,k,d=None): return self.headers.get(k,d)
    def read1(self,n):
        c=self.raw[self.pos:self.pos+n]; self.pos+=len(c); return c

class Connections:
    def __init__(self,response): self.response=response; self.calls=[]
    def __call__(self,host,*,timeout):
        owner=self
        class C:
            sock=SimpleNamespace(settimeout=lambda value:None)
            def request(self,method,path,headers): owner.calls.append((method,path,headers))
            def getresponse(self): return owner.response
            def close(self): pass
        return C()

def transport(response=None,**kwargs):
    c=Connections(response or Response())
    return NotionReadTransport("synthetic-token",connection_factory=c,min_interval=0,**kwargs),c

def test_transport_get_only_and_pinned():
    client,c=transport(Response('{"text":"Ω"}'.encode("utf-8")))
    assert client.get_json("/v1/users/me",timeout_seconds=1)=={"text":"Ω"}
    assert c.calls[0][0]=="GET" and c.calls[0][2]["Notion-Version"]==API_VERSION

@pytest.mark.parametrize("path",["https://evil.example/v1/users/me","//evil.example","/v1/search","/v1/pages/../users/me"])
def test_transport_route_allowlist(path):
    client,c=transport()
    with pytest.raises(ProviderError): client.get_json(path,timeout_seconds=1)
    assert not c.calls

@pytest.mark.parametrize("status",[301,302,401,403,404,429,500])
def test_no_redirect_or_retry(status):
    client,c=transport(Response(b'private',status=status))
    with pytest.raises((ProviderError,PermissionError)): client.get_json("/v1/users/me",timeout_seconds=1)
    assert len(c.calls)==1 and "private" not in json.dumps(client.retained_evidence())

def test_response_budget_and_duplicate_json():
    client,_=transport(Response(b'123456789',headers={"Content-Length":"9"}),max_response_bytes=4)
    with pytest.raises(ProviderError): client.get_json("/v1/users/me",timeout_seconds=1)
    client,_=transport(Response(b'{"x":1,"x":2}'))
    with pytest.raises(ProviderError): client.get_json("/v1/users/me",timeout_seconds=1)
