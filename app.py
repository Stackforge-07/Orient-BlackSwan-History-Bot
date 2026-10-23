"""Local catalogue interface. Run: streamlit run app.py."""
from __future__ import annotations
import html,json
from dataclasses import asdict
import streamlit as st
from historybot.config import ROOT,ConfigError,load_config
from historybot.qa import Pipeline
from historybot.questions import ASSIGNMENT

st.set_page_config(page_title='Orient BlackSwan History Bot',page_icon='📚',layout='wide')
st.markdown('''<style>
html,body,[class*="css"],p,label,input,button{font-size:16px} .stApp{background:#f4f6f3}
.block-container{max-width:1120px;padding-top:2.6rem;padding-bottom:3rem}
h1{color:#123f35;letter-spacing:-1.1px;line-height:1.12!important;font-size:clamp(2rem,4vw,3.1rem)!important}
.eyebrow{font-size:.85rem;letter-spacing:.16em;font-weight:700;color:#456258;margin-bottom:.65rem}
.subtitle{font-size:1.1rem;color:#435b53;max-width:740px;margin:1rem 0 1.8rem}
.result-card{border:1px solid #c2d3c8;border-left:5px solid #146b58;background:#fff;border-radius:16px;padding:1.5rem;margin:1rem 0;overflow-wrap:anywhere;word-break:break-word}
.result-card.abstain{background:#edf1ed;border-left-color:#65766c}
.result-question{font-size:1rem;color:#465c52;margin:0 0 .8rem}.result-answer{font-size:1.85rem;font-weight:700;line-height:1.3;color:#143e32;margin:.4rem 0 1rem}
.source-badge{display:inline-block;padding:.4rem .65rem;background:#dfede5;color:#214f40;border-radius:8px;font-size:.92rem;max-width:100%;white-space:normal;overflow-wrap:anywhere}
.empty{border:1px dashed #98b5a5;border-radius:16px;padding:1.7rem;color:#435b53;background:#fbfcfa}
button{min-height:44px!important;white-space:normal!important}button:focus-visible,input:focus-visible{outline:3px solid #9a6100!important;outline-offset:3px}
[data-testid="stDataFrame"]{max-width:100%;overflow-x:auto}pre,code,blockquote{white-space:pre-wrap!important;overflow-wrap:anywhere!important}
@media(max-width:768px){.block-container{padding:1.4rem 1rem!important}[data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:.4rem!important}[data-testid="stColumn"]{width:100%!important;min-width:0!important}button{width:100%!important}.result-card{padding:1.1rem}.result-answer{font-size:1.5rem}}
@media(max-width:390px){h1{font-size:1.9rem!important}.block-container{padding-left:.8rem!important;padding-right:.8rem!important}}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="eyebrow">HISTORY · 2024–25 CATALOGUE</div>',unsafe_allow_html=True)
st.title('Orient BlackSwan History Bot')
st.markdown('<p class="subtitle">Answers come only from the catalogue, with page references and evidence you can check.</p>',unsafe_allow_html=True)

if 'history' not in st.session_state:st.session_state.history=[]
if 'question' not in st.session_state:st.session_state.question=''

def choose(question):
 st.session_state.question=question;st.session_state.pending=question

def pipeline():
 if '_pipeline' not in st.session_state:st.session_state['_pipeline']=Pipeline(max_calls=40)
 return st.session_state['_pipeline']

def show_answer(item):
 found=item['found'];kind='' if found else ' abstain'
 question=html.escape(item['question']);answer=html.escape(item['answer'])
 source=''
 if found:
  printed=item['printed_page'] or 'not printed/detected'
  label=f"Page {item['page']} (printed {printed}) - {item['section'] or 'section not specified'}"
  source='<span class="source-badge">'+html.escape(label)+'</span>'
 else:source='<p>The catalogue does not contain this information.</p>'
 st.markdown(f'<section class="result-card{kind}" data-result-card="true"><p class="result-question">{question}</p><div class="result-answer">{answer}</div>{source}</section>',unsafe_allow_html=True)
 if found:
  with st.expander('Evidence from the catalogue'):st.write(item['evidence_quote'])
 if show_passages:
  with st.expander('Retrieved passages'):
   for c in item['passages']:
    st.caption(f"PDF page {c['metadata']['pdf_page']} · retrieval score {c['score']:.3f}")
    st.text(c['text'])

with st.sidebar:
 st.header('Your catalogue companion')
 with st.expander('How it works',expanded=True):
  st.markdown('**1. Search** the catalogue using meaning and keywords.\n\n**2. Answer** using only the retrieved passages.\n\n**3. Verify** the quote and page before showing a source.')
 show_passages=st.toggle('Show retrieved passages',value=False)
 with st.expander('Document details'):
  try:
   manifest=json.loads((ROOT/'chroma_db/manifest.json').read_text());config=load_config()
   st.write('91 PDF pages · 90 text-bearing pages');st.write(f"{manifest['chunks']} indexed chunks")
   st.caption('Answers: '+config.model);st.caption('Embeddings: '+manifest['embedding_model'])
  except (ConfigError,OSError,ValueError):st.info('Complete the local setup to view document details.')
 st.caption('“Not found” means the catalogue does not supply a verified answer. It is not a web search.')

st.subheader('Try a catalogue question')
columns=st.columns(2)
for index,(question,_,_) in enumerate(ASSIGNMENT):
 with columns[index%2]:st.button(question,key=f'example-{index}',on_click=choose,args=(question,),use_container_width=True)
with st.form('ask-form'):
 question=st.text_input('Your question',key='question',placeholder='Ask about a book, a price, or the publisher…')
 submitted=st.form_submit_button('Ask',type='primary',use_container_width=True)
run_all=st.button('Run the 5 assignment questions',use_container_width=True)
request=st.session_state.pop('pending',None)
if submitted:request=question.strip()
try:
 if run_all:
  with st.spinner('Searching the catalogue and verifying five answers…'):
   p=pipeline();questions=[row[0] for row in ASSIGNMENT];prepared=p.prepare(questions)
   items=[asdict(p.answer(q,r)) for q,r in zip(questions,prepared)]
   st.session_state.history=items+st.session_state.history
   st.session_state.batch=[{'Question':x['question'],'Answer':x['answer'],'PDF page':str(x['page']) if x['page'] else '—'} for x in items]
 elif request:
  with st.spinner('Searching the catalogue and checking the evidence…'):
   p=pipeline();prepared=p.prepare([request]);item=asdict(p.answer(request,prepared[0]))
   st.session_state.history.insert(0,item)
 elif submitted:st.info('Enter a question about the catalogue to get started.')
except ConfigError as exc:st.error(str(exc))
except Exception:st.error('The answer could not be loaded. Please check the local setup and try again.')
if st.session_state.get('batch'):
 st.subheader('Assignment results');st.dataframe(st.session_state.batch,hide_index=True,use_container_width=True)
if st.session_state.history:
 st.subheader('Your answers')
 for item in st.session_state.history[:20]:show_answer(item)
else:
 st.markdown('<div class="empty"><strong>A source for every supported answer.</strong><br>Choose an example above or type your own question. The bot will say “Not found” when the catalogue does not supply the answer.</div>',unsafe_allow_html=True)
