"""Hybrid retrieval with cached query embeddings; no answer knowledge here."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
import chromadb
from chromadb.config import Settings
from historybot.config import ROOT,ConfigError,load_config,validate_models
from historybot.embedding_runtime import GeminiEmbeddings

STOP=set('a an the what which who where when how is are was were in on at for of to with this that it me do does my can i and book textbook current price'.split())
def terms(text): return set(re.findall(r'[a-z0-9]+',text.lower()))-STOP

class Retriever:
 def __init__(self,verify_models=True):
  self.config=load_config()
  if not self.config.pdf_path.is_file(): raise ConfigError('PDF missing. Place History_2024-25.pdf in data/.')
  manifest=ROOT/'chroma_db/manifest.json'
  if not manifest.is_file(): raise ConfigError('Chroma index missing or incomplete. Run python -m historybot.ingest.')
  if verify_models: validate_models(self.config)
  self.manifest=json.loads(manifest.read_text())
  if self.manifest['embedding_model']!=self.config.embedding_model: raise ConfigError('Embedding model differs from the indexed model.')
  self.client=chromadb.PersistentClient(path=str(ROOT/'chroma_db'),settings=Settings(anonymized_telemetry=False))
  self.collection=self.client.get_collection(self.manifest['collection'])
  if self.collection.count()!=self.manifest['chunks']: raise ConfigError('Index count does not match its completed manifest.')
  records=self.collection.get(include=['documents','metadatas'])
  self.chunks=[{'id':i,'text':t,'metadata':m} for i,t,m in zip(records['ids'],records['documents'],records['metadatas'])]
  self.embeddings=GeminiEmbeddings(self.config)
  self.cache=ROOT/'cache/query_embeddings';self.cache.mkdir(parents=True,exist_ok=True)
 def search(self,question,k=8):
  digest=hashlib.sha256((self.config.embedding_model+'\0'+question).encode()).hexdigest()
  path=self.cache/(digest+'.json')
  if path.exists(): vector=json.loads(path.read_text())
  else:
   vector=self.embeddings.embed_query(question);path.write_text(json.dumps(vector))
  hits=self.collection.query(query_embeddings=[vector],n_results=k,include=['documents','metadatas','distances'])
  merged={}
  scores=[]
  for i,t,m,d in zip(hits['ids'][0],hits['documents'][0],hits['metadatas'][0],hits['distances'][0]):
   score=1/(1+float(d));scores.append(score)
   merged[i]={'id':i,'text':t,'metadata':m,'score':score,'lexical':0}
  keywords=terms(question)
  ranked=sorted(self.chunks,key=lambda c:(-len(keywords & terms(c['text'])),c['metadata']['pdf_page']))
  for c in ranked[:4]:
   overlap=len(keywords & terms(c['text']))
   if overlap:
    item=merged.setdefault(c['id'],dict(c,score=0.0,lexical=0))
    item['lexical']=overlap
  passages=sorted(merged.values(),key=lambda c:(c['metadata']['pdf_page'],-c['score']))
  return {'question':question,'score':max(scores,default=0),'passages':passages}
 def close(self): self.embeddings.close()
