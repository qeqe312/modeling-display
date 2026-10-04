// Independent geometry: Rodrigues rotation, cross products, determinants and sphere solve.
import assert from 'node:assert/strict';
import {writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const add=(a,b)=>a.map((v,i)=>v+b[i]), sub=(a,b)=>a.map((v,i)=>v-b[i]);
const mul=(a,s)=>a.map(v=>v*s),dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.sqrt(dot(a,a));let maxError=0,checks=0;
function near(a,b){const e=Math.abs(a-b);maxError=Math.max(maxError,e);assert(e<1e-9,`${a} != ${b}`);checks++;}
const M=[0,0,0],A=[Math.sqrt(3),0,0],B=[0,-1,0],C=[0,1,0],D=[Math.sqrt(3),2,0];
for(const [a,b] of [[A,B],[B,C],[C,D],[D,A]])near(norm(sub(a,b)),2);
near(Math.acos(dot(sub(A,B),sub(C,B))/(norm(sub(A,B))*norm(sub(C,B)))),Math.PI/3);
near(norm(sub(add(B,C),mul(M,2))),0);
const axis=mul(sub(M,A),1/norm(sub(M,A)));
function rotate(theta){return add(add(mul(B,Math.cos(theta)),mul(cross(axis,B),Math.sin(theta))),mul(axis,dot(axis,B)*(1-Math.cos(theta))));}
const baseArea=norm(cross(sub(M,A),sub(D,A)))/2;near(baseArea,Math.sqrt(3));
let maxV=-1,maxIndex=-1;
for(let i=0;i<=1000;i++){
  const t=i*Math.PI/1000,p=rotate(t),N=mul(add(p,D),.5),cn=sub(N,C);
  near(norm(sub(p,A)),2);near(norm(sub(p,M)),1);near(norm(cn),1);
  near(Math.acos(Math.abs(dot(sub(M,A),cn))/(norm(sub(M,A))*norm(cn))),Math.PI/6);
  const n1=cross(sub(p,A),sub(M,A)),n2=cross(sub(M,p),sub(C,p));
  if(i>0&&i<1000)near(dot(n1,n2)/(norm(n1)*norm(n2)),0);
  const V=Math.abs(dot(sub(p,A),cross(sub(M,A),sub(D,A))))/6;
  near(V,Math.sqrt(3)*Math.sin(t)/3);if(V>maxV){maxV=V;maxIndex=i;}
  near(N[0],Math.sqrt(3)/2);near(N[1],1-Math.cos(t)/2);near(N[2],Math.sin(t)/2);
}
assert.equal(maxIndex,500);near(maxV,Math.sqrt(3)/3);
// Solve O·Q=|Q|²/2 for the circumcenter, M is the origin.
function solve(matrix,values){const a=matrix.map((row,i)=>[...row,values[i]]);for(let j=0;j<3;j++){let pivot=j;for(let i=j+1;i<3;i++)if(Math.abs(a[i][j])>Math.abs(a[pivot][j]))pivot=i;[a[j],a[pivot]]=[a[pivot],a[j]];const k=a[j][j];a[j]=a[j].map(x=>x/k);for(let i=0;i<3;i++)if(i!==j){const f=a[i][j];a[i]=a[i].map((x,z)=>x-f*a[j][z]);}}return a.map(r=>r[3]);}
const p=rotate(Math.PI/2),O=solve([A,D,p],[A,D,p].map(q=>dot(q,q)/2));
near(O[0],Math.sqrt(3)/2);near(O[1],1);near(O[2],.5);
for(const q of [M,A,D,p])near(norm(sub(q,O)),Math.sqrt(2));near(norm(sub(C,O)),1);
assert(norm(sub(C,O))<Math.sqrt(2));
const report={answer:'AC',checks,maximumAbsoluteError:maxError,samples:1001,CN:1,lineAngleDegrees:30,maxVolume:Math.sqrt(3)/3,maxVolumeFoldDegrees:90,sphereCenter:O,sphereRadius:Math.sqrt(2),distanceOC:1,endpointNote:'B₁、M、C 共线，平面 B₁MC 未定义；A 对非退化翻折成立。'};
const out=new URL('./验证记录/math-report.json',import.meta.url);mkdirSync(fileURLToPath(new URL('./验证记录/',import.meta.url)),{recursive:true});writeFileSync(out,JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
