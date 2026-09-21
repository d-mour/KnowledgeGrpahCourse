"""Чтение фактических экспортов и наполнение учебного RDF-графа.

Только стандартная библиотека и RDFLib. Схема загружается отдельно в notebook.
"""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import json
import re
from rdflib import Namespace, Literal, RDF, XSD

G = Namespace('https://example.org/guitar/')
KINDS = {'GUITAR': 'Guitar', 'PICKUP': 'Pickup', 'BRIDGE': 'Bridge', 'CONTROL': 'Control'}
FIELDS = ['bridge_type', 'component_id', 'control_type', 'guitar_id', 'pickup_type', 'position', 'value']
TEXT_STATUS = 'assistant_self_checked_not_independent'
AUDIO_STATUS = 'technical_preannotation_not_listened'


def unescape(value):
    return re.sub(r'\\(.)', r'\1', value)


def read_text(root, rec):
    """TSV span IDs объединяют токены; координаты дают точную цитату.

    В relation target 1-5[2_6]: Governor = span 2 при токене 1-5,
    Dependent = span 6 на текущем токене. 0 означает однотокенный span.
    """
    gid = rec['guitar_id']
    source = (root / rec['materials']['text']['path']).read_text(encoding='utf-8')
    # В данном корпусе все символы BMP: координаты UTF-16 совпадают с Python.
    if any(ord(c) > 65535 for c in source):
        raise ValueError('Нужен перевод смещений UTF-16 для ' + gid)
    path = f'annotations/text/tsv/{gid}.tsv'
    tsv = (root / path).read_text(encoding='utf-8')
    expected = '#T_SP=webanno.custom.GuitarEntity|' + '|'.join(FIELDS)
    assert expected in tsv, 'Изменился порядок полей TSV'
    rows = [l.split('\t') for l in tsv.splitlines() if l and not l.startswith('#')]
    conllu = [l.split('\t') for l in (root / f'annotations/text/conllu/{gid}.conllu').read_text().splitlines() if l and not l.startswith('#')]
    assert len(rows) == len(conllu)
    mentions, paragraphs, sentences, tokens, pending = {}, {}, {}, [], []
    for row, pos in zip(rows, conllu):
        a, b = map(int, row[1].split('-'))
        sid = row[0].split('-')[0]
        assert pos[1] == source[a:b] and pos[3] == row[4]
        assert all(pos[c] == '_' for c in [2,4,5,6,7,8])
        tokens.append(dict(start=a, end=b, quote=source[a:b], upos=pos[3], local=row[0], sentence=sid))
        if sid not in sentences: sentences[sid] = dict(start=a, end=b)
        sentences[sid]['end'] = b
        match = re.fullmatch(r'(GUITAR|PICKUP|BRIDGE|CONTROL)(?:\[(\d+)\])?', row[11])
        if match:
            key = match[2] or 'token-' + row[0]
            attrs = {f:unescape(re.sub(r'\[\d+\]$', '', v)) for f,v in zip(FIELDS,row[5:12])}
            attrs = {k:v for k,v in attrs.items() if v not in ('*','_')}
            if key not in mentions: mentions[key] = dict(start=a, end=b, attrs=attrs, local=key)
            else:
                assert mentions[key]['attrs'] == attrs
                mentions[key]['end'] = b
        pm = re.fullmatch(r'(heading|body)\[(\d+)\]', row[12])
        if pm:
            if pm[2] not in paragraphs: paragraphs[pm[2]]=dict(start=a,end=b,label=pm[1])
            paragraphs[pm[2]]['end']=b
        if row[13] != '_':
            assert unescape(row[13]) == 'HAS_PART'
            rm = re.fullmatch(r'(\d+-\d+)(?:\[(\d+)_(\d+)\])?', row[14])
            assert rm, row[14]
            governor = rm[2] if rm[2] not in (None, '0') else 'token-' + rm[1]
            dependent = rm[3] if rm[3] not in (None, '0') else 'token-' + row[0]
            pending.append((governor, dependent))
    for m in mentions.values(): m['quote'] = source[m['start']:m['end']]
    for a,b in pending:
        assert mentions[a]['attrs']['value']=='GUITAR'
        assert mentions[b]['attrs']['value']!='GUITAR'
    return dict(gid=gid, path=path, mentions=mentions, relations=pending, tokens=tokens, sentences=sentences, paragraphs=paragraphs)


def read_images(root):
    regions = []
    for task in json.loads((root/'annotations/images/label_studio.json').read_text()):
        annotations = [a for a in task['annotations'] if not a.get('was_cancelled')]
        assert len(annotations)==1, 'Нужен явный выбор итоговой аннотации'
        byid = defaultdict(list)
        for result in annotations[0]['result']: byid[result['id']].append(result)
        for rid, results in byid.items():
            rects = [r for r in results if r['type']=='rectanglelabels']
            assert len(rects)==1
            rect=rects[0]; v=rect['value']; attrs={}
            for r in results:
                if r['type']=='textarea': attrs[r['from_name']]=r['value']['text'][0]
                if r['type']=='choices': attrs[r['from_name']]=r['value']['choices'][0]
            assert attrs['guitar_id']==task['data']['guitar_id']
            assert '_group_' not in attrs.get('component_id','')
            w,h=rect['original_width'],rect['original_height']
            regions.append(dict(gid=attrs['guitar_id'],material=task['data']['material_id'],path=task['data']['image_path'],local=rid,kind=v['rectanglelabels'][0],attrs=attrs,width=w,height=h,
                xPx=Decimal(str(v['x']))*w/100,yPx=Decimal(str(v['y']))*h/100,
                widthPx=Decimal(str(v['width']))*w/100,heightPx=Decimal(str(v['height']))*h/100,
                rotation=Decimal(str(v.get('rotation',0)))))
    return regions


def read_audio(root, rec):
    gid=rec['guitar_id']; path=f'annotations/audio/{gid}.TextGrid'
    text=(root/path).read_text(encoding='utf-8')
    result=[]
    for block in re.split(r'\n\s*item \[\d+\]:',text)[1:]:
        layer=re.search(r'name = "([^"]+)"',block)[1]
        for index, start, end, label in re.findall(r'intervals \[(\d+)\]:\s*xmin = ([\d.eE+-]+)\s*xmax = ([\d.eE+-]+)\s*text = "((?:[^"]|"")*)"',block):
            result.append(dict(gid=gid,path=path,layer=layer,start=Decimal(start),end=Decimal(end),label=label.replace('""','"'),local=f'{layer}/intervals[{index}]'))
    assert {r['layer'] for r in result}=={'phrase','event','pickup_setting','coil_mode'}
    return result


def lit(graph, subject, prop, value):
    datatype = XSD.boolean if isinstance(value,bool) else XSD.integer if isinstance(value,int) else XSD.decimal if isinstance(value,(float,Decimal)) else XSD.string
    graph.add((subject,G[prop],Literal(value,datatype=datatype)))


def entity(graph, identifier, kind):
    node=G[identifier];graph.add((node,RDF.type,G[kind]));lit(graph,node,'identifier',identifier)
    if kind in ('Pickup','Bridge','Control'): graph.add((node,RDF.type,G.Component))
    return node


def annotation(graph, identifier, kind, material, path, local, status, status_source):
    node=entity(graph,identifier,kind);graph.add((node,RDF.type,G.Annotation));graph.add((node,G.inMaterial,G[material]))
    for p,v in [('exportPath',path),('sourceLocalId',local),('verificationStatus',status),('statusSource',status_source)]:lit(graph,node,p,v)
    return node


def populate(graph, records, texts, images, audio):
    """Признаки детали остаются на наблюдении: конфликт не затирает источник."""
    for rec in records:
        gu=entity(graph,rec['guitar_id'],'Guitar');lit(graph,gu,'name',rec['model'])
        for key in ['version','review_author','review_date','checked_on','audio_mapping','recording_chain','limitations']:
            if key in rec:lit(graph,gu,key,rec[key])
        lit(graph,gu,'sourceUrl',rec['source_url']);lit(graph,gu,'exportPath','data/manifest.json')
        for modality, details in rec['materials'].items():
            cls,rel={'text':('TextMaterial','describes'),'image':('ImageMaterial','depicts'),'audio':('AudioMaterial','demonstrates')}[modality]
            m=entity(graph,details['material_id'],cls);graph.add((m,RDF.type,G.Material));graph.add((m,G[rel],gu))
            for key,value in details.items():
                if key=='material_id':continue
                lit(graph,m,'sourceUrl' if key=='source_url' else key,value)
            lit(graph,m,'exportPath','data/manifest.json')
    for doc in texts:
        gid=doc['gid'];mid=gid+'_TXT01'; nodes={}
        for key,m in doc['mentions'].items():
            n=annotation(graph,f'{mid}/mention/{m["start"]}-{m["end"]}','TextMention',mid,doc['path'],key,TEXT_STATUS,'annotations/text/README.md'); nodes[key]=n
            for p,v in [('startChar',m['start']),('endChar',m['end']),('quote',m['quote']),('label',m['attrs']['value'])]:lit(graph,n,p,v)
            attrs=m['attrs'];target=attrs.get('component_id',attrs.get('guitar_id'));kind='ComponentGroup' if '_group_' in target else KINDS[attrs['value']]
            obj=entity(graph,target,kind);graph.add((n,G.refersTo,obj));graph.add((obj,G.evidence,n))
            for p in ('position','pickup_type','bridge_type','control_type'):
                if p in attrs:lit(graph,n,p,attrs[p])
        for source,target in doc['relations']:
            graph.add((nodes[source],G.hasPartMention,nodes[target]))
            guitar=graph.value(nodes[source],G.refersTo);component=graph.value(nodes[target],G.refersTo)
            rel=G.hasComponentGroup if (component,RDF.type,G.ComponentGroup) in graph else G.hasPart
            graph.add((guitar,rel,component))
        unit_nodes={}
        for cls,items in [('Sentence',doc['sentences']),('Paragraph',doc['paragraphs'])]:
            for key,u in items.items():
                n=annotation(graph,f'{mid}/{cls.lower()}/{u["start"]}-{u["end"]}',cls,mid,doc['path'],key,TEXT_STATUS,'annotations/text/README.md');unit_nodes[(cls,key)]=n
                lit(graph,n,'startChar',u['start']);lit(graph,n,'endChar',u['end'])
                if 'label' in u:lit(graph,n,'label',u['label'])
        for t in doc['tokens']:
            n=annotation(graph,f'{mid}/token/{t["start"]}-{t["end"]}','Token',mid,doc['path'],t['local'],TEXT_STATUS,'annotations/text/README.md')
            for p,v in [('startChar',t['start']),('endChar',t['end']),('quote',t['quote']),('upos',t['upos'])]:lit(graph,n,p,v)
            lit(graph,n,'sourceLocator',f'annotations/text/conllu/{gid}.conllu#sentence={t["sentence"]};token={t["local"].split("-")[1]}')
            graph.add((n,G.inSentence,unit_nodes[('Sentence',t['sentence'])]))
            for key,p in doc['paragraphs'].items():
                if p['start']<=t['start'] and t['end']<=p['end']:graph.add((n,G.inParagraph,unit_nodes[('Paragraph',key)]))
    for r in images:
        n=annotation(graph,f'{r["material"]}/region/{r["local"]}','ImageRegion',r['material'],'annotations/images/label_studio.json',r['local'],TEXT_STATUS,'annotations/images/README.md')
        for p in ('xPx','yPx','widthPx','heightPx','width','height','rotation'):lit(graph,n,p,r[p])
        lit(graph,n,'coordinateSystem','pixels; origin=top-left');lit(graph,n,'label',r['kind'])
        target=r['attrs'].get('component_id',r['gid']);obj=entity(graph,target,KINDS[r['kind']]);graph.add((n,G.depicts,obj));graph.add((obj,G.evidence,n))
        if 'position' in r['attrs']:lit(graph,n,'position',r['attrs']['position'])
        if r['kind']!='GUITAR':graph.add((G[r['gid']],G.hasPart,obj))
    for r in audio:
        # Пустые интервалы phrase сохраняются для обратимости, но не считаются фразами.
        mid=r['gid']+'_AUD01';n=annotation(graph,f'{mid}/{r["layer"]}/{r["start"]}-{r["end"]}','AudioInterval',mid,r['path'],r['local'],AUDIO_STATUS,'annotations/audio/README.md')
        for p in ('start','end','layer','label'):lit(graph,n,p,r[p])
        if r['layer']=='pickup_setting' and r['label']!='unknown':
            # Только предварительные кандидаты. Поиск по позиции внутри той же модели,
            # с явно размеченной индивидуальной деталью и рамкой; + разбивается на две позиции.
            for position in r['label'].split('+'):
                candidates={G[x['attrs']['component_id']] for x in images if x['gid']==r['gid'] and x['kind']=='PICKUP' and x['attrs'].get('position')==position}
                if len(candidates)==1:graph.add((n,G.candidateComponent,next(iter(candidates))))
    return graph


def counts(graph):
    classes=['Guitar','Material','Component','Pickup','ComponentGroup','TextMention','Token','Sentence','Paragraph','ImageRegion','AudioInterval']
    result={c:len(set(graph.subjects(RDF.type,G[c]))) for c in classes}
    result['triples']=len(graph)
    result['hasPartMention']=len(list(graph.triples((None,G.hasPartMention,None))))
    result['usesComponent']=len(list(graph.triples((None,G.usesComponent,None))))
    result['candidateComponent']=len(list(graph.triples((None,G.candidateComponent,None))))
    result['nonempty_phrase']=sum(1 for n in graph.subjects(G.layer,Literal('phrase',datatype=XSD.string)) if str(graph.value(n,G.label)))
    return result
