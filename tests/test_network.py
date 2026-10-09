import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from main import Network,validate
class Tests(unittest.TestCase):
 def record(self,node,seq=1,door=False,lux=100):return {'node':node,'seq':seq,'door_open':door,'lux':lux}
 def test_coordination(self):
  n=Network();n.ingest(self.record('a'),0);self.assertEqual(n.color(0,2),(1,0,0))
  n.ingest(self.record('b',door=True,lux=20),0);self.assertEqual(n.color(0,2),(0,0,1));self.assertEqual(n.color(6,2),(1,0,0))
 def test_replay_and_invalid(self):
  n=Network();n.ingest(self.record('a'),0);self.assertFalse(n.ingest(self.record('a'),1));self.assertTrue(n.ingest(self.record('a'),6))
  for r in [{},self.record('a',lux=float('nan')),self.record('a',door=1)]:
   with self.assertRaises(ValueError):validate(r)
