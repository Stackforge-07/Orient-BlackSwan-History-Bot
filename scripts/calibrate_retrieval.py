"""Calibrate using vector scores and verified labels only; zero generation calls."""
import json
from historybot.config import ROOT
from historybot.retrieval import Retriever
from historybot.questions import ASSIGNMENT,NEGATIVES,EXTRA

def main():
 cases=[(q,a!='Not found',p) for q,a,p in ASSIGNMENT+EXTRA]+[(q,False,None) for q in NEGATIVES]
 print(f'PLAN: {len(cases)} retrievals; at most {len(cases)} uncached query-embedding calls; 0 generation calls.',flush=True)
 r=Retriever();rows=[]
 try:
  for q,found,page in cases:
   result=r.search(q)
   rows.append({'question':q,'answerable':found,'expected_page':page,'score':result['score'],
                'retrieved_pages':sorted({c['metadata']['pdf_page'] for c in result['passages']})})
   print(f"{result['score']:.6f} | answerable={found} | {q}",flush=True)
 finally:r.close()
 threshold=min(row['score'] for row in rows if row['answerable'])-1e-6
 positives=[x for x in rows if x['answerable']];negatives=[x for x in rows if not x['answerable']]
 report={'threshold':threshold,'score_definition':'1 / (1 + Chroma L2 distance)',
         'method':'Highest threshold retaining all seven verified positives; no LLM calls.',
         'positive_recall':sum(x['score']>=threshold for x in positives),'positive_count':len(positives),
         'negative_bypasses':sum(x['score']<threshold for x in negatives),'negative_count':len(negatives),'rows':rows}
 (ROOT/'docs/RETRIEVAL_CALIBRATION.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
 if any(x['expected_page'] not in x['retrieved_pages'] for x in positives): raise SystemExit('GATE FAIL: a verified positive source page was not retrieved.')
 print('RETRIEVAL GATE PASS: all seven verified positive pages retrieved.')
if __name__=='__main__':main()
