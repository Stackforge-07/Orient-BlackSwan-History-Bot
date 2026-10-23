from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from langchain_core.documents import Document
from historybot.extraction import chunk_pages
from historybot.qa import Candidate,Pipeline,verify,format_answer
from historybot.config import ConfigError
import historybot.config as config

PASSAGE={'id':'id','text':'The publisher was incorporated in 1948.','metadata':{'pdf_page':2,'printed_page':'','section':''},'score':0.8}
def candidate(**updates):
 values=dict(found=True,answer='1948',evidence_quote='The publisher was incorporated in 1948.',page=2,section=None)
 return Candidate(**dict(values,**updates))
def test_page_metadata_and_stable_chunk_ids():
 page=Document(page_content=('An actual page with words. '*150),metadata={'pdf_page':7,'document_hash':'digest','printed_page':'4','section':'History'})
 a=chunk_pages([page]);b=chunk_pages([page])
 assert len(a)>1 and all(c.metadata['pdf_page']==7 and c.metadata['printed_page']=='4' for c in a)
 assert [c.metadata['chunk_id'] for c in a]==[c.metadata['chunk_id'] for c in b]
def test_fabricated_quote_rejected():
 result=verify('year',candidate(evidence_quote='This was incorporated in 1999.'),[PASSAGE])
 assert format_answer(result)=='Not found'
def test_wrong_page_rejected():
 assert format_answer(verify('year',candidate(page=9),[PASSAGE]))=='Not found'
def test_whitespace_normalized_evidence():
 result=verify('year',candidate(evidence_quote='The publisher\nwas incorporated in 1948.'),[PASSAGE])
 assert result.found and result.page==2
 assert 'not printed/detected' in result.source()
def test_exact_not_found():
 assert format_answer(verify('unknown',candidate(found=False,answer='Any prose'),[PASSAGE]))=='Not found'
def test_missing_key_clear(monkeypatch,tmp_path):
 monkeypatch.setattr(config,'ROOT',tmp_path);monkeypatch.delenv('GOOGLE_API_KEY',raising=False)
 (tmp_path/'.env').write_text('')
 with pytest.raises(ConfigError,match='GOOGLE_API_KEY is not set'):config.load_config()
def pipeline_stub(tmp_path):
 p=Pipeline.__new__(Pipeline);p.config=SimpleNamespace(model='fake');p.cache=tmp_path;p.cache_hits=0;p.max_calls=40;p.calls=0;p.threshold=.5
 result={'question':'year','score':.8,'passages':[PASSAGE]}
 p.retriever=SimpleNamespace(search=lambda q:dict(result,question=q))
 return p,result
def test_disk_cache_prevents_second_generation(tmp_path):
 p,result=pipeline_stub(tmp_path);p.generate=Mock(return_value={'parsed':candidate().model_dump(),'raw':{'content':'mocked'}})
 first=p.answer('year',result);second=p.answer('year',result)
 assert first.found and second.found and second.cached
 assert p.generate.call_count==1 and p.cache_hits==1
def test_max_calls_preflight_and_request_guard(tmp_path):
 p,result=pipeline_stub(tmp_path);p.max_calls=0
 with pytest.raises(ConfigError,match='Planned generation'):p.prepare(['year'])
 with pytest.raises(ConfigError,match='budget exhausted'):p.generate('prompt')
def test_low_relevance_needs_no_generation(tmp_path):
 p,result=pipeline_stub(tmp_path);p.generate=Mock(side_effect=AssertionError('Must not call'))
 result['score']=.1
 assert p.answer('unrelated',result).answer=='Not found'
 p.generate.assert_not_called()
