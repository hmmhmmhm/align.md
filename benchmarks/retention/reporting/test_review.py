import hashlib,importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('review_verify',Path(__file__).with_name('verify_review.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
SOURCE=Path(__file__).parents[1]/'results/2026-10-15-astra-v1'
class ReviewReplay(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  for rel in ['trials','review','review-packets']:
   shutil.copytree(SOURCE/rel,self.root/rel)
  shutil.copy2(SOURCE/'review-key.json',self.root/'review-key.json');p=self.root/'source-snapshot/benchmarks/retention';p.mkdir(parents=True);shutil.copy2(SOURCE/'source-snapshot/benchmarks/retention/cases.json',p/'cases.json')
 def tearDown(self):self.temp.cleanup()
 def refresh_hash(self,path):
  f=self.root/'review/manifest.json';m=json.loads(f.read_text());m['sha256'][str(path.relative_to(self.root))]=hashlib.sha256(path.read_bytes()).hexdigest();f.write_text(json.dumps(m))
 def test_unmodified_evidence(self):self.assertTrue(v.verify(self.root)['verified'])
 def test_bad_quote_even_with_updated_hash(self):
  p=self.root/'review/judgments.json';d=json.loads(p.read_text());d[0]['first']['quotes']=['UNSUPPORTED EXCERPT'];p.write_text(json.dumps(d));self.refresh_hash(p)
  self.assertTrue(any('quote not in source' in e for e in v.verify(self.root)['errors']))
 def test_duplicate_judgment_even_with_updated_hash(self):
  p=self.root/'review/judgments.json';d=json.loads(p.read_text());d[-1]=d[0];p.write_text(json.dumps(d));self.refresh_hash(p)
  self.assertTrue(any('incomplete or duplicate' in e for e in v.verify(self.root)['errors']))
 def test_changed_packet_response_even_with_updated_hash(self):
  p=self.root/'review-packets/packets.json';d=json.loads(p.read_text());d[0]['first_submission']='changed response';p.write_text(json.dumps(d));self.refresh_hash(p)
  self.assertTrue(any('packets differ' in e for e in v.verify(self.root)['errors']))
 def test_omitted_packet_even_with_updated_hash(self):
  p=self.root/'review-packets/packets.json';d=json.loads(p.read_text());d.pop();p.write_text(json.dumps(d));self.refresh_hash(p)
  self.assertTrue(any('packets differ' in e for e in v.verify(self.root)['errors']))
if __name__=='__main__':unittest.main()
