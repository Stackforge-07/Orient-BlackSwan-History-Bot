"""Screenshot-friendly catalogue CLI."""
import argparse,sys
from historybot.qa import Pipeline,format_answer
from historybot.config import ConfigError

def main():
 p=argparse.ArgumentParser();p.add_argument('question');p.add_argument('--max-calls',type=int,default=40);p.add_argument('--debug',action='store_true');a=p.parse_args()
 pipeline=None
 try:
  pipeline=Pipeline(a.max_calls)
  # A single-question CLI keeps stdout exactly Not found on abstention.
  result=pipeline.retriever.search(a.question)
  needed=int(result['score']>=pipeline.threshold and not pipeline.payload(result)[1].exists())
  print(f'PLAN: {needed} uncached generation calls; max {a.max_calls}.',file=sys.stderr)
  answer=pipeline.answer(a.question,result);print(format_answer(answer))
  if a.debug:
   print('DEBUG:',answer.debug,file=sys.stderr)
   for c in answer.passages: print(f"DEBUG page={c['metadata']['pdf_page']} score={c['score']:.6f}: {c['text']}",file=sys.stderr)
  return 0
 except ConfigError as exc:print('Error: '+str(exc),file=sys.stderr);return 1
 finally:
  if pipeline:pipeline.close()
if __name__=='__main__':raise SystemExit(main())
