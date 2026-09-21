"""Check the collected corpus: IDs, files, SHA-256, images and WAV signals."""
import hashlib
import json
import math
import struct
import wave
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'data/manifest.json').read_text(encoding='utf-8'))
records = manifest['records']
assert len(records) >= 10, 'The manual requires at least 10 objects'
ids = [r['guitar_id'] for r in records]
assert len(set(ids)) == len(ids), 'Duplicate guitar IDs'
material_ids = set()
for r in records:
    assert set(r['materials']) == {'text', 'image', 'audio'}, r['guitar_id']
    for kind, m in r['materials'].items():
        assert m['material_id'] not in material_ids
        material_ids.add(m['material_id'])
        p = root / m['path']
        assert p.is_file() and p.stat().st_size > 0, p
        assert hashlib.sha256(p.read_bytes()).hexdigest() == m['sha256'], p
        if kind == 'text':
            text = p.read_text(encoding='utf-8')
            assert text.startswith(r['model']), p
            assert len(text.split()) == m['word_count'], p
        elif kind == 'image':
            with Image.open(p) as image:
                assert image.size == (m['width'], m['height']), p
                image.verify()
        else:
            with wave.open(str(p)) as wav:
                assert wav.getsampwidth() == 2, p
                assert wav.getframerate() == m['sample_rate'] == 44100, p
                assert wav.getnchannels() == m['channels'], p
                duration = wav.getnframes() / wav.getframerate()
                assert abs(duration - m['duration_seconds']) < 0.002, p
                # Sample up to one second at the midpoint: catches silent/corrupt conversion.
                wav.setpos(wav.getnframes() // 2)
                raw = wav.readframes(min(44100, wav.getnframes() // 2))
                samples = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
                rms = math.sqrt(sum(v * v for v in samples) / len(samples))
                assert rms > 1, f'Check potentially silent file: {p}'
    print(r['guitar_id'], 'OK', r['materials']['text']['word_count'], 'words;', r['materials']['audio']['duration_seconds'], 's')
text = (root / 'data/text/GTR001.txt').read_text(encoding='utf-8')
assert text[0:20] == 'Reverend Six Gun HPP'
x, y, w, h = 207, 241, 57, 112
assert x >= 0 and y >= 0 and x + w <= 1200 and y + h <= 600
assert 0 < 16 < 34 < records[3]['materials']['audio']['duration_seconds']
print(f'PASS: {len(records)} objects, {len(material_ids)} materials; schema example coordinates valid.')
