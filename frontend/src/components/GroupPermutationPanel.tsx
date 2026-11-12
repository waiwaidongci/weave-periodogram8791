import {fmt} from '../utils/format';
export function GroupPermutationPanel({result}:{result:any}){
 const t=result.global_test,perMember=result.members,W=950,H=220,L=38,R=25,x=(v:number)=>L+(W-L-R)*v,barW=(W-L-R)/20-5;
 return <section className="section permutation-panel">
  <div className="section-head"><h2>整组所有频点，共用一个联合零分布。</h2><span>B={t.permutations} / {result.n_members}条测线 / QR缓存{result.qr_cache_builds}次</span></div>
  <p>每条测线只在自身内部打乱厚度标签，各自重算完整预设网格；每次抽取取全部测线、全部频点的最大功率，得到{result.n_members}维逐次最大值的联合零分布。不把任一单线p或事后挑出的最强峰当作组证据。</p>
  <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="整组联合置换最大功率分布">
   {t.histogram.counts.map((n,i)=><g key={i}><rect x={x(t.histogram.edges[i])+3} y={170-n/Math.max(...t.histogram.counts,1)*120} width={barW} height={n/Math.max(...t.histogram.counts,1)*120} className="null-bar"/>{n>0&&<text x={x(t.histogram.edges[i])+(W-L-R)/40} y={162-n/Math.max(...t.histogram.counts,1)*120} textAnchor="middle">{n}</text>}</g>)}
   <line x1={x(result.observed_max_power)} y1="25" x2={x(result.observed_max_power)} y2="175" className="peak-line"/><text x={L} y="205">0</text><text x={W-R} y="205" textAnchor="end">最大功率 1</text>
  </svg>
  <div className="p-equation"><strong>p = ({t.exceedances_with_ties} + 1) / ({t.permutations} + 1) = {fmt(t.global_p,6)}</strong><p>整组观测最大值取所有登记测线全部纳入频点的最大功率；数值并列按tol={t.power_tie_tolerance}保守计入上尾；最小Monte Carlo p={fmt(t.minimum_monte_carlo_p,6)}。</p></div>
  <div className="table-scroll"><table><thead><tr><th>序号 / 测线</th><th>自身全网格最大功率</th><th>自身最佳周期</th><th>组内胜出</th></tr></thead><tbody>{perMember.map((m:any)=><tr key={m.ordinal}><td>{m.ordinal} / {m.label}<small>{m.plan_name} · N{m.n} · {m.grid_size}频点</small></td><td>{fmt(m.observed_max_power,6)}</td><td>{fmt(m.best.period,5)} mm</td><td>{result.winning_member.ordinal===m.ordinal?'最强峰所在':''}</td></tr>)}</tbody></table></div>
  <details><summary>全部{t.null_maxima.length}个联合null最大值与各测线分列</summary><p className="null-values">{t.null_maxima.map((v,i)=>`#${i} ${fmt(v,6)}`).join('　/　')}</p><p className="null-values">逐线null最大值均值：{perMember.map((m:any,i:number)=>`${m.label} ${fmt(t.per_member_null_maxima[i].reduce((a:number,b:number)=>a+b,0)/t.permutations,4)}`).join('　/　')}</p></details>
 </section>
}
