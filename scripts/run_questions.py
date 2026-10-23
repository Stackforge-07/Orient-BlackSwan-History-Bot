"""Live evaluation; cache responses and print the call plan before generation."""
import argparse,json
from dataclasses import asdict
from historybot.config import ROOT,ConfigError
from historybot.qa import Pipeline,format_answer
from historybot.questions import ASSIGNMENT,EXTRA,NEGATIVES

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--max-calls',type=int,default=40);args=parser.parse_args()
 cases=ASSIGNMENT+(EXTRA+[(q,'Not found',None) for q in NEGATIVES] if args.all else [])
 pipeline=None
 try:
  pipeline=Pipeline(args.max_calls);prepared=pipeline.prepare([c[0] for c in cases]);rows=[]
  for (q,expected,page),retrieved in zip(cases,prepared):
   answer=pipeline.answer(q,retrieved)
   match=(not answer.found and answer.answer=='Not found') if expected=='Not found' else answer.found and expected.lower() in answer.answer.lower() and answer.page==page
   rows.append(dict(asdict(answer),expected=expected,expected_page=page,matches=match))
   print('\nQUESTION: '+q+'\n'+format_answer(answer)+f'\nMATCHES GROUND TRUTH: {"yes" if match else "no"}',flush=True)
  name='EVALUATION_ALL' if args.all else 'ASSIGNMENT_RESULTS'
  (ROOT/f'docs/{name}.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
  print(f'RESULT: {sum(r["matches"] for r in rows)}/{len(rows)} matched; generation calls={pipeline.calls}; cache hits={pipeline.cache_hits}')
  if not all(r['matches'] for r in rows):raise ConfigError('QA evaluation gate failed; inspect saved results before continuing.')
  return 0
 except ConfigError as exc:print('Error: '+str(exc));return 1
 finally:
  if pipeline:pipeline.close()
if __name__=='__main__':raise SystemExit(main())
