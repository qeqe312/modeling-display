// Independent vector/determinant verification. Does not import page model code.
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
const checks=[];
let maxError=0;
function close(actual,expected,description){const error=Math.abs(actual-expected);maxError=Math.max(error,maxError);assert.ok(error<1e-9,`${description}: ${actual} vs ${expected}`);checks.push(description);}
const sub=(a,b)=>a.map((x,i)=>x-b[i]);
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const norm=a=>Math.hypot(...a);
for(const a of [.2,1,2,3.7]){
  // An independent base-horizontal construction, not the page's cube construction.
  const h=Math.sqrt(2/3)*a;
  const A=[0,0,h],B=[a/Math.sqrt(3),0,0],C=[-a/(2*Math.sqrt(3)),a/2,0],D=[-a/(2*Math.sqrt(3)),-a/2,0];
  const points=[A,B,C,D],O=[0,0,h/4],F=[0,0,0];
  for(let i=0;i<4;i++)for(let j=i+1;j<4;j++)close(norm(sub(points[i],points[j])),a,`a=${a}: edge ${i}${j}`);
  const R=norm(sub(A,O)),r=norm(sub(O,F));
  for(const [i,p] of points.entries())close(norm(sub(p,O)),Math.sqrt(6)*a/4,`a=${a}: outer contact ${i}`);
  for(let i=0;i<4;i++){
    const face=points.filter((_,j)=>i!==j),n=cross(sub(face[1],face[0]),sub(face[2],face[0]));
    const distance=Math.abs(dot(sub(O,face[0]),n))/norm(n);
    close(distance,r,`a=${a}: inner tangency distance ${i}`);
    const centroid=face[0].map((x,j)=>(x+face[1][j]+face[2][j])/3);
    close(norm(sub(centroid,O)),r,`a=${a}: face centroid on inner sphere ${i}`);
    close(norm(cross(sub(centroid,O),n)),0,`a=${a}: contact radius normal to face ${i}`);
  }
  close(R,3*r,`a=${a}: R=3r`);
  close(4*Math.PI*R*R,1.5*Math.PI*a*a,`a=${a}: outer area`);
  close(4/3*Math.PI*r**3,Math.sqrt(6)/216*Math.PI*a**3,`a=${a}: inner volume`);
  const volume=Math.abs(dot(sub(B,A),cross(sub(C,A),sub(D,A))))/6;
  close(volume,Math.sqrt(2)/12*a**3,`a=${a}: determinant tetrahedron volume`);
  close(volume,4*(Math.sqrt(3)/4*a*a)*r/3,`a=${a}: four O pyramids sum to whole`);
  for(const [i,j,k,l] of [[0,1,2,3],[0,2,1,3],[0,3,1,2]]){
    const u=sub(points[j],points[i]),v=sub(points[l],points[k]);
    close(dot(u,v),0,`a=${a}: opposite edge dot ${i}${j}/${k}${l}`);
    close(Math.acos(Math.min(1,Math.abs(dot(u,v))/(norm(u)*norm(v))))*180/Math.PI,90,`a=${a}: opposite angle ${i}${j}/${k}${l}`);
  }
  // Independently rotate the base-horizontal construction into the F-based teaching frame.
  const angle=7*Math.PI/6,c=Math.cos(angle),s=Math.sin(angle);
  const teaching=points.map(([x,y,z])=>[c*x-s*y,s*x+c*y,z]);
  const expected=[[0,0,h],[-a/2,-Math.sqrt(3)*a/6,0],[a/2,-Math.sqrt(3)*a/6,0],[0,Math.sqrt(3)*a/3,0]];
  const rendered=teaching.map(([x,y,z])=>[6*x,6*(z-r),-6*y]);
  for(const [i,p] of teaching.entries()){
    p.forEach((x,j)=>close(x,expected[i][j],`a=${a}: F-based teaching vertex ${i}/${j}`));
    const [X,Y,Z]=rendered[i],inverse=[X/6,-Z/6,Y/6+r];
    inverse.forEach((x,j)=>close(x,p[j],`a=${a}: render inverse ${i}/${j}`));
    close(norm(rendered[i])/6,norm(sub(p,[0,0,r])),`a=${a}: centered outer radius ${i}`);
  }
  for(let i=0;i<4;i++)for(let j=i+1;j<4;j++)close(norm(sub(teaching[i],teaching[j])),a,`a=${a}: F-based teaching edge ${i}${j}`);
  for(let i=1;i<4;i++)close(teaching[i][2],0,`a=${a}: BCD at z=0 ${i}`);
  close(teaching[0][0],0,`a=${a}: A above F in x`);
  close(teaching[0][1],0,`a=${a}: A above F in y`);
  close(teaching[0][2],h,`a=${a}: A height h`);
  const AB=sub(teaching[1],teaching[0]),CD=sub(teaching[3],teaching[2]);
  close(dot(AB,CD),0,`a=${a}: updated teaching AB dot CD`);

}
checks.push('statement 1 agrees with outer surface area proportional to a squared');
const report={passed:checks.length,maxAbsoluteError:maxError,tolerance:1e-9,edgeSamples:[.2,1,2,3.7],conclusions:[true,true,true,true],answer:'C',normalized:{R:Math.sqrt(6)/4,r:Math.sqrt(6)/12,h:Math.sqrt(6)/3,outerArea:1.5*Math.PI,innerVolume:Math.sqrt(6)*Math.PI/216,tetrahedronVolume:Math.sqrt(2)/12},method:'Independent base-horizontal coordinates, determinants, face normal distances; F-based teaching coordinates and centered rendering checked separately',checks};
writeFileSync(new URL('./验证记录/math-report.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify({passed:report.passed,maxAbsoluteError:maxError,answer:report.answer,normalized:report.normalized},null,2));
