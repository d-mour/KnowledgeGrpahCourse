#!/usr/bin/env python3
"""Conservative waveform preannotation, NOT listening or musical analysis.
Requires numpy. Existing TextGrids are never overwritten. --stats reads saved files.
"""
from pathlib import Path
import argparse, json, re, wave
import numpy as np
ROOT = Path(__file__).resolve().parents[1]

def read_grid(path):
    s=path.read_text(encoding='utf-8')
    tiers={}
    for block in re.split(r'    item \[\d+\]:\n',s)[1:]:
        name=re.search(r'name = "(.*?)"',block)[1]
        tiers[name]=[(float(a),float(b),t.replace('""','"')) for a,b,t in re.findall(r'intervals \[\d+\]:\s+xmin = ([\d.e+-]+)\s+xmax = ([\d.e+-]+)\s+text = "(.*?)"',block)]
    return tiers

def write_grid(path,d,tiers):
    lines=['File type = "ooTextFile"','Object class = "TextGrid"','', 'xmin = 0',f'xmax = {d:.15g}','tiers? <exists>', 'size = 4','item []:']
    for i,(name,intervals) in enumerate(tiers.items(),1):
        lines += [f'    item [{i}]:','        class = "IntervalTier"',f'        name = "{name}"','        xmin = 0',f'        xmax = {d:.15g}',f'        intervals: size = {len(intervals)}']
        for j,(a,b,t) in enumerate(intervals,1):
            lines += [f'        intervals [{j}]:',f'            xmin = {a:.15g}',f'            xmax = {b:.15g}',f'            text = "{t}"']
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def preannotate(wav):
    with wave.open(str(wav)) as w:
        sr=w.getframerate(); n=w.getnframes(); ch=w.getnchannels()
        assert w.getsampwidth()==2
        x=np.frombuffer(w.readframes(n),dtype='<i2').reshape(-1,ch).astype(float)/32768
    d=n/sr; hop=441
    # Maximum channel RMS: stereo phase cancellation cannot create false silence.
    rms=np.array([np.sqrt(np.mean(x[i:i+hop]**2,axis=0)).max() for i in range(0,n,hop)])
    db=20*np.log10(np.maximum(rms,1e-12))
    threshold=max(-55.,min(-40.,float(np.percentile(db,95))-30.))
    quiet=db<threshold
    edges=np.flatnonzero(np.diff(np.r_[False,quiet,False])).reshape(-1,2)
    pauses=[]
    for a,b in edges:
        # Keep 350 ms after sound, 30 ms before next onset. No short tail chopping.
        start=0. if a==0 else round(a*.01+.35,3)
        end=d if b==len(rms) else round(b*.01-.03,3)
        if end-start>=.2: pauses.append((start,end))
    events=[]; cur=0.
    for a,b in pauses:
        if a>cur: events.append((cur,a,'playing'))
        events.append((a,b,'pause'));cur=b
    if cur<d:events.append((cur,d,'playing'))
    # Only longer silence separates candidate musical phrases; brief gaps stay inside.
    separators=[(a,b) for a,b in pauses if b-a>=.6 or a==0 or b==d]
    phrases=[];cur=0.;idx=0
    for a,b in separators+[(d,d)]:
        if a>cur:idx+=1;phrases.append((cur,a,f'phrase_{idx:03}'))
        if b>a:phrases.append((a,b,''))
        cur=b
    settings=[]
    for a,b,e in events:
        cuts=sorted({a,b}|({t for t in (16.,34.) if a<t<b} if wav.stem=='GTR004' else set()))
        for l,r in zip(cuts,cuts[1:]):
            label='unknown'
            if wav.stem=='GTR004' and e=='playing': label='bridge' if l<16 else ('bridge+neck' if l<34 else 'neck')
            if settings and settings[-1][2]==label:settings[-1]=(settings[-1][0],r,label)
            else:settings.append((l,r,label))
    return d,{'phrase':phrases,'event':events,'pickup_setting':settings,'coil_mode':[(0.,d,'unknown')]},threshold

def stats():
    rows=[]
    for p in sorted((ROOT/'annotations/audio').glob('GTR*.TextGrid')):
        t=read_grid(p)
        rows.append(dict(id=p.stem,duration=t['event'][-1][1],phrases=sum(bool(v) for a,b,v in t['phrase']),pauses=sum(v=='pause' for a,b,v in t['event'])))
    return rows

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stats',action='store_true');args=ap.parse_args()
    if not args.stats:
        for wav in sorted((ROOT/'data/audio').glob('GTR*.wav')):
            out=ROOT/'annotations/audio'/f'{wav.stem}.TextGrid'
            if out.exists():print(f'Skip existing {out.name}');continue
            d,t,threshold=preannotate(wav);write_grid(out,d,t)
            print(wav.stem,'threshold dBFS',round(threshold,2))
    print(json.dumps(stats(),ensure_ascii=False,indent=2))
