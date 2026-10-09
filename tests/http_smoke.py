import subprocess,time,json
from urllib.request import urlopen
a=subprocess.Popen(['python','src/main.py','--node','hall','--peer','http://127.0.0.1:18089','--port','18088','--iterations','8'],stdout=subprocess.PIPE,text=True)
b=subprocess.Popen(['python','src/main.py','--node','bedroom','--peer','http://127.0.0.1:18088','--port','18089','--iterations','8'],stdout=subprocess.PIPE,text=True)
try:
 for _ in range(50):
  try:
   with urlopen('http://127.0.0.1:18088/status',timeout=.5) as r:x=json.load(r)
   with urlopen('http://127.0.0.1:18089/status',timeout=.5) as r:y=json.load(r)
   if x.get('node')=='hall' and y.get('node')=='bedroom':break
  except OSError:pass
  time.sleep(.1)
 else:raise AssertionError('HTTP nodes unavailable')
 ao=a.communicate(timeout=15)[0];bo=b.communicate(timeout=15)[0]
 assert a.returncode==b.returncode==0
 assert any(json.loads(line)['rgb']!=[1,0,0] for line in ao.splitlines())
 assert any(json.loads(line)['rgb']!=[1,0,0] for line in bo.splitlines())
 print('two-node HTTP communication and coordinated color passed')
finally:
 for p in (a,b):
  if p.poll() is None:p.terminate();p.wait(timeout=3)
