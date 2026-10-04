import assert from 'node:assert/strict';
// Independent verification: standard Cartesian basis, not page coordinates.
const A=[3,0,0],B=[0,0,0],C=[0,4,0],P=[3,0,5];
const minus=(a,b)=>a.map((x,i)=>x-b[i]);
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const length=v=>Math.sqrt(dot(v,v));
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
near(length(minus(P,A)),5);near(length(minus(A,B)),3);near(length(minus(C,B)),4);
near(Math.acos(dot(minus(A,B),minus(C,B))/12),Math.PI/2);
near(dot(minus(P,A),minus(B,A)),0);near(dot(minus(P,A),minus(C,A)),0);
near(dot(minus(P,A),minus(C,A)),0);near(dot(minus(P,B),minus(C,B)),0);
// Solve the three equal-distance linear equations using Gaussian elimination.
const vertices=[A,C,P];
const augmented=vertices.map(v=>[...v.map(x=>2*x),dot(v,v)]);
for(let i=0;i<3;i++){
  const pivot=augmented[i][i];assert.ok(Math.abs(pivot)>1e-12);
  for(let j=i;j<4;j++)augmented[i][j]/=pivot;
  for(let k=0;k<3;k++){if(k===i)continue;const factor=augmented[k][i];for(let j=i;j<4;j++)augmented[k][j]-=factor*augmented[i][j];}
}
const O=augmented.map(row=>row[3]),midpoint=P.map((x,i)=>(x+C[i])/2);
O.forEach((x,i)=>near(x,midpoint[i]));
const radius=length(minus(O,B));
for(const v of [A,B,C,P])near(length(minus(O,v)),radius);
near(radius,5*Math.sqrt(2)/2);near(length(minus(P,C)),5*Math.sqrt(2));near(4*Math.PI*radius*radius,50*Math.PI);
near(length(minus(A,C)),5);near(3*4*5/6,10);
const palette={bg:'#0D1117',surface:'#161B22',surface2:'#1C232C',surface3:'#232B36',ink:'#E6EDF3',secondary:'#A9B6C4',muted:'#8B99A8',blue:'#6BA8E8',orange:'#FF7A45',violet:'#A692E8',bluebg:'#17293E',orangebg:'#2E1A11',violetbg:'#1E1B2E',selected:'#20130D'};
function luminance(hex){const v=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return dot(v,[.2126,.7152,.0722]);}
const contrast=(a,b)=>{const x=luminance(palette[a]),y=luminance(palette[b]);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
const contrasts=[];
for(const a of ['ink','secondary','muted'])for(const b of ['bg','surface','surface2','surface3'])contrasts.push({a,b,ratio:contrast(a,b)});
for(const [a,b] of [['blue','bluebg'],['orange','orangebg'],['violet','violetbg'],['selected','orange']])contrasts.push({a,b,ratio:contrast(a,b)});
for(const item of contrasts)assert.ok(item.ratio>=4.5,JSON.stringify(item));
console.log(JSON.stringify({verified:true,center:O,radius,diameter:length(minus(P,C)),surfaceArea:4*Math.PI*radius**2,minContrast:Math.min(...contrasts.map(c=>c.ratio)),contrastPairs:contrasts.length},null,2));
