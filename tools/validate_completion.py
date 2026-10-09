from pathlib import Path
import re,json,hashlib,xml.etree.ElementTree as ET
from decode_project_image import validate_png
r=Path(__file__).resolve().parents[1]
for f in ['README.md','LICENSE','docs/circuit-diagram.svg','docs/images/project-overview.png']:assert (r/f).is_file(),f
assert ET.parse(r/'docs/circuit-diagram.svg').getroot().tag=='{http://www.w3.org/2000/svg}svg'
svg=(r/'docs/circuit-diagram.svg').read_text();assert '<script' not in svg and 'href=' not in svg
b=(r/'docs/images/project-overview.png').read_bytes();dims=validate_png(b)
m=json.loads((r/'docs/images/project-overview.manifest.json').read_text())
assert len(b)==m['bytes'] and list(dims)==m['dimensions'] and hashlib.sha256(b).hexdigest()==m['sha256']
assert not list((r/'docs/images').glob('*.b64.*'))
for target in re.findall(r'!?\[[^]]*\]\(([^)]+)\)',(r/'README.md').read_text()):
 if not target.startswith(('https://','http://','#')):assert (r/target.split('#')[0]).exists(),target
assert 'Permission is hereby granted' in (r/'LICENSE').read_text()
for p in r.rglob('*'):
 if p.is_file() and not any(x in p.parts for x in ['.git','.pio','__pycache__']) and p.suffix not in ['.png','.pyc']:
  assert not re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN [A-Z ]*PRIVATE KEY',p.read_text(errors='ignore')),str(p)
print('PNG SHA/CRC/dimensions, SVG, links, MIT and credential checks passed')
