// Independent formulas: does not load the page or Three.js.
import assert from 'node:assert/strict';
const add=(a,b)=>a.map((v,i)=>v+b[i]), sub=(a,b)=>a.map((v,i)=>v-b[i]);
const scale=(a,k)=>a.map(v=>v*k), dot=(a,b)=>a.reduce((n,v,i)=>n+v*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.hypot(...a), unit=a=>scale(a,1/norm(a));
let checks=0;
function near(actual,expected,tolerance=1e-9){assert.ok(Number.isFinite(actual));assert.ok(Math.abs(actual-expected)<tolerance,`${actual} != ${expected}`);checks++;}
const h=Math.tan(Math.PI/3)*Math.hypot(.5,.5);
const A=[-1,0,-1],B=[1,0,-1],C=[1,0,1],D=[-1,0,1],Ap=[-.5,h,-.5],Cp=[.5,h,.5];
const point=t=>add(C,scale(sub(Cp,C),t));
const normal=(a,b,c)=>cross(sub(b,a),sub(c,a));
const angle=t=>{
  const cosine=Math.abs(dot(unit(normal(Ap,B,D)),unit(normal(point(t),B,D))));
  return Math.acos(Math.min(1,cosine))*180/Math.PI;
};
near(h,Math.sqrt(6)/2);
near(Math.asin(h/norm(sub(Cp,C)))*180/Math.PI,60);
const pyramid=2*(h/2)/3,frustum=h*(4+1+Math.sqrt(4))/3;
near(pyramid/(frustum-pyramid),1/6);
near(pyramid+(frustum-pyramid),frustum);
near(dot(normal(Ap,B,D),normal(point(.5),B,D)),0);
near(Math.abs(dot(sub(A,point(.5)),unit(normal(point(.5),B,C))))/norm(sub(A,point(.5))),4*Math.sqrt(273)/91);
for(const t of [0,.25,.5,.75,1]){
  near(norm(sub(point(t),C))/norm(sub(Cp,C)),t);
  near(norm(sub(point(t),Cp))/norm(sub(Cp,C)),1-t);
  near(angle(t),angle(1-t));
}
near(angle(0),60);near(angle(.5),90);near(angle(1),60);
// Projection and inverse use orthogonal decomposition, independent of page determinant formula.
const FOV=40*Math.PI/180;
function camera(azimuth,elevation){
  const pos=scale([Math.cos(elevation)*Math.sin(azimuth),Math.sin(elevation),Math.cos(elevation)*Math.cos(azimuth)],6.6);
  const forward=unit(sub([0,h/2,0],pos)),right=unit(cross(forward,[0,1,0])),up=cross(right,forward);
  return {pos,forward,right,up};
}
function inverse(o,d){
  const u=sub(Cp,C),w=sub(o,C),perpendicular=vector=>sub(vector,scale(d,dot(vector,d)));
  const up=perpendicular(u),denominator=dot(up,up);
  return denominator<1e-9?null:Math.max(0,Math.min(1,dot(up,perpendicular(w))/denominator));
}
for(const [w,height] of [[1400,900],[820,1180],[780,1000],[1600,1000]]){
  for(const [az,el] of [[.75,.34],[1.2,.7],[2.1,.4],[3.4,.9],[4.2,-.2],[5.1,.3]]){
    const cam=camera(az,el),fy=1/Math.tan(FOV/2),fx=fy/(w/height);
    for(const t of [0,.25,.5,.75,1,-.2,1.2]){
      const delta=sub(point(t),cam.pos),z=dot(delta,cam.forward);
      assert.ok(z>0);
      const px=dot(delta,cam.right)*fx/z,py=dot(delta,cam.up)*fy/z;
      const ray=unit(add(add(scale(cam.right,px/fx),scale(cam.up,py/fy)),cam.forward));
      near(inverse(cam.pos,ray),Math.max(0,Math.min(1,t)),1e-12);
    }
  }
}
assert.equal(inverse([0,0,0],unit(sub(Cp,C))),null);checks++;
console.log(`Independent mathematics: ${checks} assertions passed`);
