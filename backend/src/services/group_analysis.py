import numpy as np
from src.constants.numerics import POWER_TIE_TOL,GROUP_ALGORITHM_VERSION
from .validation import validate_points,validate_plan
from .qr_cache import build_cache
from .spectrum import observed_spectrum
from .permutation import null_maxima

class GroupAnalysisError(ValueError):
 def __init__(self,failures):
  self.failures=failures
  super().__init__('测线组存在缺失或退化成员，整组未计算：'+'；'.join(f"第{f['ordinal']}位 {f['label']}：{f['reason']}" for f in failures))

def prepare_member(member):
 ordinal=member['ordinal'];label=member.get('label') or f"测线{member.get('study_id','?')}"
 try:
  points=validate_points(member['points']);validate_plan(member['plan'])
  cache=build_cache([p['position'] for p in points],member['plan']['frequencies'])
  result,centered=observed_spectrum(cache,[p['thickness'] for p in points])
 except ValueError as error:
  raise ValueError(str(error)) from error
 return {'ordinal':ordinal,'label':label,'study':member['study'],'plan':member['plan'],'points':points,'cache':cache,'centered':centered,'result':result,'source_fingerprint':member.get('source_fingerprint')}

def member_summary(prepared):
 result=prepared['result'];spectrum=[{'frequency':e['frequency'],'period':e['period'],'included':e['included'],'reason':e['reason'],'power':e['power'],'window_power':e['window_power']} for e in result['spectrum']]
 return {'ordinal':prepared['ordinal'],'label':prepared['label'],'study_id':prepared['study']['id'],'study_name':prepared['study']['name'],'plan_name':prepared['plan']['name'],'n':len(prepared['points']),'grid_size':len(prepared['plan']['frequencies']),'observed_max_power':result['observed_max_power'],'included_frequencies':result['included_frequencies'],'excluded_frequencies':result['excluded_frequencies'],'best':result['best'],'spectrum':spectrum,'source_fingerprint':prepared.get('source_fingerprint')}

def analyze_group(group,members,fingerprint=None):
 prepared=[];failures=[]
 for member in members:
  try:prepared.append(prepare_member(member))
  except ValueError as error:failures.append({'ordinal':member['ordinal'],'label':member.get('label') or f"测线{member.get('study_id','?')}",'study_id':member.get('study_id'),'reason':str(error)})
 if failures:raise GroupAnalysisError(failures)
 if not prepared:raise GroupAnalysisError([{'ordinal':0,'label':'整组','study_id':None,'reason':'没有可计算的测线成员'}])
 n=len(prepared);B=group['permutations'];seed=group['seed'];children=np.random.SeedSequence(seed).spawn(n);child_seeds=[int(child.generate_state(1,dtype=np.uint32)[0]) for child in children]
 per_member_null=[]
 for member,child_seed in zip(prepared,child_seeds):
  per_member_null.append(null_maxima(member['cache'],member['centered'],member['result']['rss0'],B,child_seed))
 null=np.max(np.asarray(per_member_null,dtype=float),axis=0)
 observed=float(max(member['result']['observed_max_power'] for member in prepared))
 winners=[member for member in prepared if member['result']['observed_max_power']>=observed-POWER_TIE_TOL]
 winner=min(winners,key=lambda member:member['ordinal']);best=winner['result']['best'];count=int(np.sum(null>=observed-POWER_TIE_TOL));p=(count+1)/(B+1);hist,edges=np.histogram(null,bins=np.linspace(0,1,21))
 summaries=[member_summary(member) for member in prepared];total_points=sum(s['n'] for s in summaries)
 return {'group':{'id':group.get('id'),'name':group.get('name'),'protocol':group.get('protocol'),'permutations':B,'seed':seed},'members':summaries,'n_members':n,'total_points':total_points,'observed_max_power':observed,'winning_member':{'ordinal':winner['ordinal'],'label':winner['label'],'study_id':winner['study']['id'],'study_name':winner['study']['name'],'frequency':best['frequency'],'period':best['period'],'power':best['power']},'global_test':{'permutations':B,'seed':seed,'member_seeds':child_seeds,'null_maxima':[float(v) for v in null],'per_member_null_maxima':[[float(v) for v in row] for row in per_member_null],'exceedances_with_ties':count,'global_p':p,'minimum_monte_carlo_p':1/(B+1),'power_tie_tolerance':POWER_TIE_TOL,'histogram':{'counts':hist.tolist(),'edges':edges.tolist()},'definition':'Each member is permuted only within itself (fixed x, own cached QR); every member’s own predeclared grid is rescanned on every draw; the group statistic is the maximum power over all members and all their frequencies. p=(1+#group-null>=observed-tol)/(B+1).','assumptions':'Within each traverse, thickness labels are exchangeable under the no-periodic-signal null; group members may have different lengths and grids. Not a between-traverse causal test, single-frequency p, period CI, or online diagnosis.'},'qr_cache_builds':n,'tie_rule':'Winning member: lowest registered ordinal within 1e-12 of the group maximum; winning frequency inside that member uses its own lowest-frequency tie rule. Upper-tail null ties use the same tolerance.','fingerprint':fingerprint,'interpretation':'A group p is the search-corrected probability that the strongest power anywhere in the registered group grids could arise under within-traverse label exchangeability. A stronger single-traverse peak cannot be promoted without this joint null. Sampling windows, aliasing, leakage and grid spacing still limit interpretation; member plans are fixed before the group is run.','algorithm_version':GROUP_ALGORITHM_VERSION}
