// Independent analytic verification. This file never imports the page/model code.
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const MAX=Math.sqrt(8),E=[-10/3,0],Q=[-5/3,0];
const radii=[...Array.from({length:1000},(_,i)=>MAX*(i+.5)/1000),.00001,1.4,1.99999,2.00001,MAX-.00001];
let maxResidual=0,maxRayResidual=0;
for(const r of radii){
  // The smaller root is rationalized to avoid cancellation near r=2.
  const d=4-r*r,z=r*Math.sqrt(8-r*r),small=d/(4+z),large=1/small;
  assert.ok(Math.abs(small*large-1)<1e-12);
  const hits=[small,large].map(k=>[2*(1-4*k*k)/(1+4*k*k),4*k/(1+4*k*k)]);
  for(let i=0;i<2;i++){
    const k=[small,large][i],[x,y]=hits[i];
    assert.ok(Math.abs(x*x/4+y*y-1)<1e-12);
    assert.ok(Math.abs(Math.abs(2*k-2)/Math.hypot(k,1)-r)<1e-9);
  }
  // Derive MN's normal from the two independently obtained ellipse intersections.
  const [M,N]=hits,normal=[N[1]-M[1],M[0]-N[0]];
  const c=normal[0]*M[0]+normal[1]*M[1],nn=normal[0]**2+normal[1]**2;
  const P=normal.map(a=>a*c/nn),v=[M[0]-N[0],M[1]-N[1]];
  const residual=Math.max(Math.abs(normal[0]*E[0]-c)/Math.hypot(...normal),
    Math.abs(P[0]*v[0]+P[1]*v[1])/Math.hypot(...v),
    Math.abs(Math.hypot(P[0]-Q[0],P[1])-5/3));
  assert.ok(residual<1e-9,`r=${r}, residual=${residual}`);
  maxResidual=Math.max(maxResidual,residual);
  // Independently evaluate solid/dashed split at the actual ellipse boundary.
  const delta=Math.asin(r/MAX);
  for(const angle of [Math.PI/4+delta,Math.PI/4-delta]){
    const u=[Math.cos(angle),Math.sin(angle)],t=u[0]/(u[0]**2/4+u[1]**2);
    const implicit=s=>(-2+s*u[0])**2/4+(s*u[1])**2-1;
    if(t>0){
      const boundaryError=Math.abs(implicit(t));maxRayResidual=Math.max(maxRayResidual,boundaryError);
      assert.ok(boundaryError<1e-12&&implicit(t/2)<0&&implicit(t+.1)>0);
    }else assert.ok(implicit(.1)>0,'a ray directed away from the ellipse is dashed from A');
  }
}
for(const r of [0,MAX]){
  const a=4-r*r,discriminant=64-4*a*a;
  assert.ok(Math.abs(discriminant)<1e-12,'two tangents coincide at the excluded endpoints');
}
// At r=2 the polynomial is linear (-8k=0); x=-2 is the other, vertical tangent.
const verticalDistance=Math.abs(-2-0),horizontalDistance=Math.abs(0-2);
assert.equal(verticalDistance,horizontalDistance);
const report={date:new Date().toLocaleString('sv-SE',{timeZone:'Asia/Shanghai'}),timeZone:'Asia/Shanghai',
  samples:radii.length,tolerance:1e-9,maxResidual,maxRayResidual,
  ellipse:'x²/4+y²=1',A:[-2,0],D:[0,2],E,Q,PQ:5/3,
  validRadius:'0<r<sqrt(8), r!=2',
  actualPLocus:'Two open arcs with endpoint limits (-30/73, +/-80/73); O excluded',
  independent:true};
const dir=new URL('./验证记录/',import.meta.url);mkdirSync(dir,{recursive:true});
writeFileSync(new URL('math-report.json',dir),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
