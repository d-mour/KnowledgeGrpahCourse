"""Проверка итоговых экспортов ЛР3. Только стандартная библиотека Python 3."""
from pathlib import Path
from collections import Counter
from io import BytesIO
import json, re, zipfile, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'annotations/text'
UPOS = set('ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X'.split())
XID = '{http://www.omg.org/XMI}id'
FIELDS = {
 'GUITAR': {'guitar_id'},
 'PICKUP': {'component_id','position','pickup_type'},
 'BRIDGE': {'component_id','bridge_type'},
 'CONTROL': {'component_id','control_type'},
}
VALUES = {
 'position': {'bridge','middle','neck','unknown'},
 'pickup_type': {'humbucker','single_coil','p90','unknown'},
 'bridge_type': {'fixed','vibrato','unknown'},
 'control_type': {'volume','tone','bass_contour','selector','unknown'},
}
def local(x): return x.tag.rsplit('}',1)[-1]
def validate():
 out={}
 with zipfile.ZipFile(A/'inception_project.zip') as archive:
  assert len([n for n in archive.namelist() if n.startswith('source/') and not n.endswith('/')])==10
  for i in range(1,11):
   gid=f'GTR{i:03}'
   text=(ROOT/f'data/text/{gid}.txt').read_text(encoding='utf-8')
   assert archive.read(f'source/{gid}.txt').decode('utf-8')==text
   with zipfile.ZipFile(BytesIO(archive.read(f'annotation/{gid}.txt/admin.zip'))) as z:
    root=ET.fromstring(z.read('admin.xmi'))
   nodes=list(root);byid={x.get(XID):x for x in nodes if x.get(XID)}
   sofa=next(x for x in nodes if local(x)=='Sofa')
   assert sofa.get('sofaString')==text, (gid,'text')
   assert all(ord(ch)<65536 for ch in text), 'UTF-16 conversion required for non-BMP'
   tokens=sorted((x for x in nodes if local(x)=='Token'),key=lambda x:int(x.get('begin')))
   entities=sorted((x for x in nodes if local(x)=='GuitarEntity'),key=lambda x:int(x.get('begin')))
   relations=[x for x in nodes if local(x)=='HasPart']
   starts={int(x.get('begin')) for x in tokens};ends={int(x.get('end')) for x in tokens}
   previous=0;stable={}
   for e in entities:
    a,b=int(e.get('begin')),int(e.get('end'));kind=e.get('value')
    assert previous<=a<b<=len(text) and a in starts and b in ends,(gid,'span',a,b)
    previous=b
    for f in FIELDS[kind]:assert e.get(f),(gid,f,a)
    for f,vals in VALUES.items():
     if e.get(f):assert e.get(f) in vals and f in FIELDS[kind],(gid,f)
    if kind=='GUITAR':assert e.get('guitar_id')==gid
    else:
     cid=e.get('component_id');assert cid.startswith(gid+'_'+kind+'_')
     attrs=tuple((f,e.get(f)) for f in sorted(FIELDS[kind]-{'component_id'}))
     assert stable.setdefault(cid,attrs)==attrs,(gid,'inconsistent component',cid)
   pairs=set()
   for r in relations:
    source=byid[r.get('Governor')];target=byid[r.get('Dependent')]
    assert source.get('value')=='GUITAR' and target.get('value') in {'PICKUP','BRIDGE','CONTROL'}
    assert r.get('value')=='HAS_PART'
    pair=(r.get('Governor'),r.get('Dependent'));assert pair not in pairs;pairs.add(pair)
   assert len(relations)==sum(e.get('value')!='GUITAR' for e in entities)
   rows=[ln.split('\t') for ln in (A/f'conllu/{gid}.conllu').read_text().splitlines() if ln and not ln.startswith('#')]
   assert len(rows)==len(tokens)
   for row,t in zip(rows,tokens):
    assert len(row)==10 and row[3] in UPOS,(gid,'CoNLL-U',row)
    assert row[1]==text[int(t.get('begin')):int(t.get('end'))]
    assert row[3]==byid[t.get('pos')].get('coarseValue')
    assert all(row[c]=='_' for c in [2,4,5,6,7,8]),(gid,'invented fields')
   tsv=(A/f'tsv/{gid}.tsv').read_text();assert tsv.startswith('#FORMAT=WebAnno TSV 3.3')
   trows=[ln.split('\t') for ln in tsv.splitlines() if ln and not ln.startswith('#')]
   assert len(trows)==len(tokens)
   # Each entity is recovered by a TSV span ID, or token ID for a single-token span.
   spans={};edges=set()
   for row,t in zip(trows,tokens):
    a,b=map(int,row[1].split('-'));assert (a,b)==(int(t.get('begin')),int(t.get('end')))
    label=row[11];m=re.fullmatch(r'(GUITAR|PICKUP|BRIDGE|CONTROL)(?:\[(\d+)\])?',label)
    if m:
     key=m[2] or row[0];attrs=tuple(re.sub(r'\[\d+\]$','',v).replace('\\_','_') for v in row[5:12])
     if key not in spans:spans[key]=[a,b,m[1],attrs]
     else:spans[key][1]=b;assert spans[key][3]==attrs
    if row[13]!='_':
     assert row[13]=='HAS\\_PART';edges.add((row[0],row[14]))
   assert len(spans)==len(entities) and len(edges)==len(relations),(gid,'TSV count')
   for actual,e in zip(sorted(spans.values()),entities):
    assert actual[:3]==[int(e.get('begin')),int(e.get('end')),e.get('value')]
    for v,f in zip(actual[3],['bridge_type','component_id','control_type','guitar_id','pickup_type','position','value']):assert v==('*' if not e.get(f) else e.get(f)),(gid,'TSV feature',f)
   n=Counter(e.get('value') for e in entities)
   n.update(tokens=len(tokens),relations=len(relations),paragraphs=sum(local(x)=='Paragraph' for x in nodes),sentences=sum(local(x)=='Sentence' for x in nodes))
   assert n['paragraphs']==3
   out[gid]=dict(n)
 return out
if __name__=='__main__':
 result=validate()
 for gid,n in result.items():print(gid,json.dumps(n,ensure_ascii=False))
 print('TOTAL',json.dumps(dict(sum((Counter(n) for n in result.values()),Counter())),ensure_ascii=False))
 print('PASS: 10 документов; исходники, POS, границы, признаки и HAS_PART согласованы с архивом и экспортами.')
