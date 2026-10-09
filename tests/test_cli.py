import json,subprocess,sys,unittest
class CLICompatibility(unittest.TestCase):
 def test_established_simulation_command(self):
  result=subprocess.run([sys.executable,'-m','src.main','--iterations','2','--interval','0'],capture_output=True,text=True,timeout=10,check=True)
  rows=[json.loads(line) for line in result.stdout.splitlines()]
  self.assertEqual(len(rows),2)
  self.assertEqual([r['local']['node'] for r in rows],['room-a','room-a'])
  self.assertEqual([r['local']['seq'] for r in rows],[1,2])
