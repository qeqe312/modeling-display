import assert from 'node:assert/strict';
const h=Math.sqrt(6)/2;
const A=[-1,-1,0],B=[1,-1,0],C=[1,1,0],D=[-1,1,0],Ap=[-.5,-.5,h],Cp=[.5,.5,h];
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.sqrt(dot(a,a));
const normal=(a,b,c)=>cross(sub(b,a),sub(c,a));
const point=t=>C.map((v,i)=>v+t*(Cp[i]-v));
let passed=0;
function near(a,b,label){assert.ok(Math.abs(a-b)<1e-10,`${label}: ${a} != ${b}`);passed++;}
near(norm(sub(Cp,C)),Math.SQRT2,'lateral edge length');
near(Math.atan2(h,Math.SQRT1_2),Math.PI/3,'lateral edge angle 60 degrees');
// The first question works for any a and h; it does not require question 2's angle.
for(const a of [.3,1,2.7])for(const height of [.5,1.7,4]){
  const whole=height*(a*a+4*a*a+Math.sqrt(a*a*4*a*a))/3;
  const pyramid=2*a*a*(height/2)/3;
  near(pyramid/(whole-pyramid),1/6,'volume ratio by subtraction');
}
for(let i=0;i<=100;i++){
  const t=i/100,P=point(t),n1=normal(Ap,B,D),n2=normal(P,B,D);
  const angle=Math.acos(Math.abs(dot(n1,n2))/(norm(n1)*norm(n2)));
  near(angle,Math.acos(Math.abs(t-.5)/Math.sqrt(t*t-t+1)),'independent plane-angle formula');
  const pyramid=Math.abs(dot(sub(P,B),cross(sub(C,B),sub(D,B))))/6;
  near(pyramid,2*t*h/3,'tetrahedron volume from determinant');
  if(t>0){const n=normal(P,B,C),pa=sub(A,P),sin=Math.abs(dot(pa,n))/(norm(pa)*norm(n));near(sin,Math.sqrt(24/(56-28*t+14*t*t)),'line angle by cross product');}
}
const mid=point(.5),n=normal(mid,B,C);
near(Math.abs(dot(sub(A,mid),n))/(norm(sub(A,mid))*norm(n)),4*Math.sqrt(273)/91,'exact final answer');
const F=[5/7,-1,4*h/7];
near(dot(sub(F,B),n),0,'foot F lies in plane PBC');
near(norm(cross(sub(A,F),n)),0,'AF is normal to plane');
near(dot(sub(A,F),sub(mid,F)),0,'AF perpendicular to PF');
console.log(JSON.stringify({passed,volumeRatio:'1:6',sinTheta:4*Math.sqrt(273)/91,thetaDegrees:Math.asin(4*Math.sqrt(273)/91)*180/Math.PI}));
