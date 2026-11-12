import {useState} from 'react';import {PageTitle} from '../components/common/PageTitle';import {Empty} from '../components/common/Empty';import {Notice} from '../components/common/Notice';import {Status} from '../components/common/Status';import {Table} from '../components/common/Table';import {GroupPermutationPanel} from '../components/GroupPermutationPanel';import {SpectrumPlot} from '../components/SpectrumPlot';import {researchApi} from '../api/research';import {useTask} from '../hooks/useTask';import {fmt} from '../utils/format';
type Draft={key:number;study_id:number|'';plan_id:number|'';label:string};
export function GroupsPage({studies,plans,groups,groupRuns,user,reloadResearch}:any){
 const task=useTask(),[draft,D]=useState<Draft[]>([{key:0,study_id:'',plan_id:'',label:''}]),[name,N]=useState('联合置换组 '+new Date().toLocaleTimeString()),[protocol,P]=useState('预先登记组内测线与各自冻结频率计划；按整组所有频点最大功率做联合置换，每条测线只在自身内部打乱厚度。'),[Bb,PB]=useState(199),[seed,E]=useState(234),[runName,RN]=useState('联合置换研究 '+new Date().toLocaleTimeString()),[groupId,G]=useState(0),[runId,RI]=useState(0);
 const group=groups.find((g:any)=>g.id===(groupId||groups[0]?.id)),run=groupRuns.find((r:any)=>r.id===(runId||groupRuns[0]?.id)),result=run?.result;
 function pool(index:number){return plans.filter((p:any)=>p.study_id===draft[index].study_id)}
 function setMember(index:number,patch:Partial<Draft>){D(d=>d.map((m,i)=>i===index?{...m,...patch}:m))}
 function recalc(stale:any){D(stale.members.map((m:any,i:number)=>({key:i,study_id:m.study_id,plan_id:m.plan_id,label:m.label})));N(stale.name+' 重算 '+new Date().toLocaleTimeString());G(0)}
 const valid=draft.every(m=>m.study_id&&m.plan_id)&&new Set(draft.map(m=>m.study_id)).size===draft.length;
 return <><PageTitle index="05" title="跨测线挑峰，要用整组的零分布。" description="逐线全局p不能校正“从多条测线里挑最强峰”。先登记测线组及各自频率计划，再按整组所有频点最大功率做联合置换，保留完整null。"/>
 <div className="config-layout"><div>
 <form className="input-sheet" onSubmit={e=>{e.preventDefault();task.act(async()=>{await researchApi.createGroup({name,protocol,permutations:Bb,seed,members:draft.map((m,i)=>({ordinal:i+1,study_id:m.study_id,plan_id:m.plan_id,label:m.label}))});await reloadResearch();D([{key:0,study_id:'',plan_id:'',label:''}])},'测线组已登记；组登记时冻结各测线与计划快照')}}>
  <small>01 / REGISTER BEFORE SEARCH</small><h2>预先登记测线组</h2>
  <label>组名称<input value={name} onChange={e=>N(e.target.value)} required/></label>
  <label>组方案说明<textarea value={protocol} onChange={e=>P(e.target.value)} rows={3} required/></label>
  <div className="field-pair"><label>组级置换次数 B<input type="number" min="199" max="499" value={Bb} onChange={e=>PB(+e.target.value)} required/></label><label>组级随机种子 seed<input type="number" min="0" max="1000000000" value={seed} onChange={e=>E(+e.target.value)} required/></label></div>
  {draft.map((m,index)=><fieldset className="group-member" key={m.key}><legend>测线 {index+1}</legend>
   <label>测线研究<select value={m.study_id} onChange={e=>setMember(index,{study_id:+e.target.value,plan_id:''})} required><option value="">选择测线</option>{studies.map((s:any)=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
   <label>该测线的冻结频率计划<select value={m.plan_id} onChange={e=>setMember(index,{plan_id:+e.target.value})} required><option value="">选择计划</option>{pool(index).map((p:any)=><option key={p.id} value={p.id}>{p.name} · {p.grid_size}点 · B{p.permutations}</option>)}</select></label>
   <label>组内显示标签<input value={m.label} onChange={e=>setMember(index,{label:e.target.value})} placeholder="可留空，默认用测线名"/></label>
   {draft.length>1&&<button type="button" onClick={()=>D(d=>d.filter((_,i)=>i!==index))}>移除该测线</button>}
  </fieldset>)}
  {draft.length<8&&<button type="button" onClick={()=>D(d=>[...d,{key:Math.max(...d.map(x=>x.key))+1,study_id:'',plan_id:'',label:''}])}>＋ 增加一条测线</button>}
  <p>异长测线可以组合：每条只用自己的位置和厚度，各自重算自身网格。缺失或退化的测线不会被静默剔除，整组会明确失败并指出该成员。</p>
  {user.role!=='viewer'&&<button className="primary" disabled={task.busy||!valid}>登记测线组 →</button>}
 </form>
 <form className="run-sheet" onSubmit={e=>{e.preventDefault();if(group)task.act(async()=>{const r=await researchApi.createGroupRun({group_id:group.id,name:runName});await reloadResearch();G(group.id);RI(r.id)},'联合置换已排队；组与逐线快照已冻结')}}>
  <small>02 / JOINT FULL-GRID SEARCH</small><h2>从已登记组运行联合置换</h2>
  <label>测线组<select value={group?.id||''} onChange={e=>G(+e.target.value)}>{groups.map((g:any)=><option key={g.id} value={g.id}>{g.name}{g.stale?'（登记失效）':''}</option>)}</select></label>
  <label>组运行名称<input value={runName} onChange={e=>RN(e.target.value)} required/></label>
  {group?<><p>{group.protocol}</p><p>{group.members.length}条测线 / B{group.permutations} / seed{group.seed}<br/>{group.members.map((m:any)=>`${m.ordinal}. ${m.label}`).join('　')}</p>{group.stale&&<p className="error-text">该组登记已失效：{group.invalid_reasons.join('；')}。源数据或计划更新后须重算并另存新组；旧组结果不改写。</p>}{group.stale&&user.role!=='viewer'&&<button type="button" onClick={()=>recalc(group)}>以失效组为模板另存新组（重算）→</button>}</>:<p>尚无测线组，请先登记。</p>}
  {user.role!=='viewer'&&<button className="primary" disabled={task.busy||!group||group.stale}>送入联合置换队列 →</button>}
 </form>
 <Notice {...task}/>
 </div><aside className="method-note"><h3>整组最大功率 + 逐线内部置换</h3><p>每次抽取：每条测线在被冻结的自身位置x上打乱厚度y，重算该线所有纳入频点的功率并取该线最大值；再对全部测线取最大。p=(1+#整组null最大值≥整组观测最大值−tol)/(B+1)。</p><p>组级B与seed独立于各线计划；各线用同一组seed派生的不同子种子，保证可复现且可逐线审计。联合检验只取各线计划中的冻结频率网格，逐线置换强度由组级参数统一决定。组结果另存，不并入单线运行。</p><p>组证据仍不是制造原因、在线诊断或周期置信区间；登记后若更新源数据或计划，旧组标记失效。</p></aside></div>
 <section className="section"><h2>已登记测线组</h2>{groups.length?<Table headers={['组','方案','成员','状态']}>{groups.map((g:any)=><tr key={g.id}><td><strong>{g.name}</strong><small>#{g.id} · B{g.permutations} / seed{g.seed}</small></td><td>{g.protocol}</td><td>{g.members.map((m:any)=><div key={m.ordinal}>{m.ordinal}. {m.label}<small>{m.study_name} / {m.plan_name}</small></div>)}</td><td>{g.stale?<><span className="error-text">登记失效</span><small className="error-text">{g.invalid_reasons.join('；')}</small></>:'有效'}</td></tr>)}</Table>:<Empty title="还没有预先登记的测线组" help="先为每条测线冻结频率计划，再登记组；不可看完谱峰后挑选成员。"/>}</section>
 <section className="section"><h2>联合置换结果</h2>{groupRuns.length?<label>组运行<select value={run?.id||''} onChange={e=>RI(+e.target.value)}>{groupRuns.map((r:any)=><option key={r.id} value={r.id}>#{r.id} {r.name}</option>)}</select></label>:null}
 {run&&<p><Status value={run.status}/>{run.error&&<>　<span className="error-text">{run.error}</span></>}</p>}
 {!result?<Empty title={run?.status==='failed'?'整组未计算：存在缺失或退化成员':'等待真实worker计算'} help={run?.error||(groupRuns.length?'每2.5秒刷新；组结果另存于组运行表。':'先登记并运行一个测线组。')}/>:<>
  <dl className="peak-summary"><div><dt>联合胜出周期 / mm</dt><dd>{fmt(result.winning_member.period,5)}</dd></div><div><dt>整组最大功率</dt><dd>{fmt(result.observed_max_power,6)}</dd></div><div><dt>整组联合置换 p</dt><dd>{fmt(result.global_test.global_p,6)}</dd></div><div><dt>整组观测点 / 测线数</dt><dd>{result.total_points}<em> / {result.n_members}</em></dd></div></dl>
  <div className="group-winner"><small>JOINT WINNER / 第{result.winning_member.ordinal}位</small><h2>{result.winning_member.label}</h2><p>{result.winning_member.study_name} · {fmt(result.winning_member.frequency,9)} cycles/mm · 周期{fmt(result.winning_member.period,6)} mm · 功率{fmt(result.winning_member.power,9)}</p></div>
  <GroupPermutationPanel result={result}/>
  <section className="section"><h2>参与联合搜索的各测线完整谱</h2>{result.members.map((m:any)=><div className="group-member-result" key={m.ordinal}><h3>{m.ordinal}. {m.label}</h3><p>N{m.n} / {m.grid_size}频点 / 自身最大功率{fmt(m.observed_max_power,6)} / 自身最佳周期{fmt(m.best.period,5)} mm / 纳入{m.included_frequencies}，退化排除{m.excluded_frequencies}</p><SpectrumPlot result={m}/></div>)}
   <p>各线谱仅为组内审计展示；任一条线的单线p都未用于组级判断。</p></section>
  <details className="provenance"><summary>整组指纹、成员快照与联合检验定义</summary><p className="fingerprint">{run.group_fingerprint}</p><p>{result.tie_rule}</p><p>{result.global_test.definition}</p><p>{result.interpretation}</p><Table headers={['序号','测线','计划','N','源指纹']}>{result.members.map((m:any)=><tr key={m.ordinal}><td>{m.ordinal}</td><td>{m.label}<small>{m.study_name}</small></td><td>{m.plan_name}</td><td>{m.n}</td><td className="fingerprint">{m.source_fingerprint.slice(0,16)}…</td></tr>)}</Table></details>
 </>}
 </section></>}
