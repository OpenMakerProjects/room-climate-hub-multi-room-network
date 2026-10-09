"""Local multi-room coordinator with real Pi GPIO/I2C adapters and deterministic simulation."""
import argparse,json,math,time,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.request import urlopen
from urllib.parse import urlparse

def validate(r):
 if not isinstance(r,dict) or set(r)!={'node','seq','door_open','lux'}:raise ValueError('record keys')
 if not isinstance(r['node'],str) or not 1<=len(r['node'])<=32:raise ValueError('node')
 if type(r['seq']) is not int or r['seq']<0 or type(r['door_open']) is not bool:raise ValueError('types')
 if type(r['lux']) not in (int,float) or not math.isfinite(r['lux']) or not 0<=r['lux']<=65535:raise ValueError('lux')
 return r
class Network:
 def __init__(self):self.nodes={}
 def ingest(self,r,now):
  r=validate(r);old=self.nodes.get(r['node'])
  if old and r['seq']<=old[0]['seq'] and now-old[1]<5:return False
  self.nodes[r['node']]=(dict(r),now);return True
 def color(self,now,expected):
  fresh=[r for r,t in self.nodes.values() if now-t<=5]
  if len(fresh)<expected:return (1,0,0)
  if any(r['door_open'] and r['lux']<50 for r in fresh):return (0,0,1)
  return (0,1,0)

# Legacy simulation API retained for downstream consumers and original regression tests.
from dataclasses import dataclass
@dataclass(frozen=True)
class Snapshot:
 timestamp:float
 values:list
 score:float
 valid:bool
class Controller:
 def __init__(self,threshold=0.53,confirmations=2):
  if not 0.0<=threshold<=1.0:raise ValueError('threshold must be between 0 and 1')
  self.threshold=threshold;self.confirmations_required=max(1,confirmations)
  self.confirmations=0;self.output_active=False
 def evaluate(self,values,timestamp=None):
  valid=bool(values) and all(math.isfinite(v) and 0<=v<=1 for v in values)
  score=sum(values)/len(values) if valid else 0.0
  self.confirmations=min(self.confirmations+1,self.confirmations_required) if valid and score>=self.threshold else 0
  self.output_active=valid and self.confirmations>=self.confirmations_required
  return Snapshot(time.time() if timestamp is None else timestamp,values,score,valid)

class Hardware:
 def __init__(self):
  from gpiozero import RGBLED,Button
  from smbus2 import SMBus,i2c_msg
  self.led=RGBLED(17,27,22,pwm=True,active_high=True)
  self.door=Button(23,pull_up=True,bounce_time=0.05);self.bus=SMBus(1);self.msg=i2c_msg
  self.bus.write_byte(0x23,0x10);time.sleep(0.18)
 def read(self):
  m=self.msg.read(0x23,2);self.bus.i2c_rdwr(m);b=list(m)
  return not self.door.is_pressed,(b[0]*256+b[1])/1.2
 def output(self,c):self.led.color=c
 def close(self):self.led.off();self.led.close();self.door.close();self.bus.close()
def main():
 p=argparse.ArgumentParser();p.add_argument('--node',default='room-a');p.add_argument('--peer',action='append',default=[]);p.add_argument('--port',type=int,default=8088);p.add_argument('--hardware',action='store_true');p.add_argument('--iterations',type=int,default=0);p.add_argument('--interval',type=float,default=1.0)
 a=p.parse_args()
 if a.interval<0 or not math.isfinite(a.interval):p.error('--interval must be finite and nonnegative')
 for peer in a.peer:
  u=urlparse(peer)
  if u.scheme!='http' or not u.hostname or u.username or u.password or u.path not in ('','/'):raise ValueError('peer must be plain LAN http://host:port')
 latest={};lock=threading.Lock();net=Network();hardware=Hardware() if a.hardware else None
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   if self.path!='/status':self.send_error(404);return
   with lock:body=json.dumps(latest).encode()
   self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('0.0.0.0',a.port),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  seq=0
  while not a.iterations or seq<a.iterations:
   seq+=1;now=time.monotonic()
   try:door,lux=hardware.read() if hardware else (seq%4==0,20 if seq%4==0 else 100)
   except OSError:
    if hardware:hardware.output((1,0,0))
    time.sleep(1);continue
   record={'node':a.node,'seq':seq,'door_open':door,'lux':round(lux,2)}
   with lock:latest.clear();latest.update(record)
   net.ingest(record,now)
   for peer in a.peer:
    try:
     with urlopen(peer.rstrip('/')+'/status',timeout=0.5) as resp:
      data=resp.read(2049)
      if len(data)>2048:raise ValueError('oversized peer record')
      net.ingest(json.loads(data),now)
    except (OSError,ValueError):pass
   color=net.color(now,1+len(a.peer))
   if hardware:hardware.output(color)
   print(json.dumps({'project_id':8,'local':record,'rgb':color}),flush=True);time.sleep(a.interval)
 finally:
  server.shutdown();server.server_close()
  if hardware:hardware.close()
if __name__=='__main__':main()
