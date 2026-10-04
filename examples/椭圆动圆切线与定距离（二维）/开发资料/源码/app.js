/* Canvas 2D reference. Sections: problem data -> model -> planar rendering -> gestures -> UI.
 * Change the problem model deliberately; retain equal-unit transforms, pointer ownership,
 * cached label sizes, responsive drawers and demand rendering when adapting another problem.
 */
(()=>{'use strict';
const $=id=>document.getElementById(id),cv=$('cv'),stage=$('stage'),panel=$('panel'),ctx=cv.getContext('2d');
if(!ctx){$('error').hidden=false;$('error').textContent='浏览器未能创建二维画布，请用现代浏览器重新打开。';return;}
const MAX=Math.sqrt(8),RHO=5/3,AMAX=2*Math.atan(3/8),EPS=1e-10;
const color={blue:'#6BA8E8',orange:'#FF7A45',violet:'#A692E8',ink:'#B9C9DD',grid:'#2A3441'};
const state={r:1.4,ellipse:true,circle:true,tangents:true,chord:true,projection:true,trace:true,aux:true,contact:false,grid:true,labels:true,lengths:false,font:22,opacity:.08,quality:'auto'};
const view={cx:0,cy:0,scale:70},selected=new Set(),pointers=new Map(),labels=[];
const metrics={renders:0,labelMeasurements:0,paths:4,trustedMouse:0,trustedTouch:0};
let W=1,H=1,dpr=1,frame=0,gesture=null,values=null,metricsDirty=true,needsFit=true,drawer=false,tab='lesson',returnFocus=null;
const ellipsePath=new Path2D(),unitCircle=new Path2D(),upperTrace=new Path2D(),lowerTrace=new Path2D();
ellipsePath.ellipse(0,0,2,1,0,0,2*Math.PI);unitCircle.arc(0,0,1,0,2*Math.PI);
for(let i=0;i<=200;i++){let a=AMAX*i/200,x=-RHO+RHO*Math.cos(a),y=RHO*Math.sin(a);if(i===0){upperTrace.moveTo(x,y);lowerTrace.moveTo(x,-y);}else{upperTrace.lineTo(x,y);lowerTrace.lineTo(x,-y);}}
const points={A:[-2,0],D:[0,2],O:[0,0],E:[-10/3,0],Q:[-5/3,0],M:[0,0],N:[0,0],P:[0,0],R:[1.4,2],T1:[0,0],T2:[0,0]};
const labelDefs=[['A','blue',[-44,-40]],['D','orange',[-36,-43]],['O','blue',[9,12]],['E','violet',[-42,12]],['Q','violet',[-18,20]],['M','orange',[-42,-44]],['N','orange',[10,-42]],['P','orange',[12,-43]],['R','orange',[15,-14]],['T1','orange',[10,12]],['T2','orange',[10,12]]];
for(const [key,kind,offset] of labelDefs){const el=document.createElement('div');el.className='lab '+kind+(key==='R'||key==='P'?' draggable':'')+(key.startsWith('T')?' small':'');el.textContent=key==='T1'?'T₁':key==='T2'?'T₂':key;$('labels').append(el);labels.push({key,el,offset,kind,hit:null,w:0,h:0,visible:false});}
for(const [key,text,kind] of [['radius','r','orange'],['length','|PQ|','violet']]){const el=document.createElement('div');el.className='lab edge-label '+kind;el.textContent=text;$('labels').append(el);labels.push({key,el,offset:[4,4],kind,hit:null,w:0,h:0,visible:false,length:true});}
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const fmt=(n,d=4)=>Number.isFinite(n)?(Math.abs(n)<.5*10**(-d)?0:n).toFixed(d):'—';
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
// Problem-specific analytic model. The contact-directed rays need not contain M for r > 2.
function compute(r){
  const alpha=Math.asin(clamp(r/MAX,0,1)),angles=[Math.PI/4+alpha,Math.PI/4-alpha];
  const dirs=angles.map(a=>[Math.cos(a),Math.sin(a)]);
  const cross=dirs.map(u=>{let t=u[0]/(u[0]*u[0]/4+u[1]*u[1]);return [-2+t*u[0],t*u[1]];});
  const contacts=dirs.map(u=>{let t=2*(u[0]+u[1]);return [-2+t*u[0],t*u[1]];});
  const m=3*(4-r*r)/32,valid=r>EPS&&r<MAX-EPS&&Math.abs(r-2)>EPS;
  const P=[-(10/3)*m*m/(1+m*m),(10/3)*m/(1+m*m)];
  let reason='有效位置 · 两条切线与两个不同交点';
  if(r<=EPS)reason='r＝0：圆退化，两条切线重合';
  else if(r>=MAX-EPS)reason='r＝2√2：A 在圆上，两条切线重合';
  else if(Math.abs(r-2)<=EPS)reason='r＝2：一条切线竖直，M 与 A 重合';
  return {valid,reason,m,dirs,cross,contacts,P,k:dirs.map(u=>Math.abs(u[0])<EPS?null:u[1]/u[0]),length:valid?dist(P,points.Q):null};
}
function setR(raw){
  if(!Number.isFinite(raw))return;
  const oldValid=values?.valid;state.r=clamp(raw,0,MAX);values=compute(state.r);
  points.M=values.cross[0];points.N=values.cross[1];points.P=values.P;points.R=[state.r,2];points.T1=values.contacts[0];points.T2=values.contacts[1];
  $('sR').value=state.r;$('sRval').textContent=fmt(state.r,3);$('rRadius').textContent=fmt(state.r,3);
  $('mK1').textContent=values.k[0]===null?'未定义（竖直）':fmt(values.k[0]);$('mK2').textContent=values.k[1]===null?'未定义（竖直）':fmt(values.k[1]);
  $('mProduct').textContent=$('rProduct').textContent=values.valid?'1.0000':'未定义';
  $('mSlope').textContent=values.valid?fmt(values.m):'未定义';$('mP').textContent=values.valid?'('+fmt(points.P[0],3)+', '+fmt(points.P[1],3)+')':'未定义';
  $('rLength').textContent=$('mLength').textContent=values.valid?fmt(values.length):'未定义';
  $('validFlag').textContent=values.valid?(state.r>2?'有效位置 · M 在射线反向':'有效位置 · |PQ| 恒定'):values.reason;$('validFlag').className='mid-flag '+(values.valid?'valid':'invalid');$('motionStatus').textContent=values.reason+(values.valid?(state.r>2?'。M 位于对应射线的反向；题目中的 AM 仍按整条直线计算。':'。半径改变时，P 仍沿两段弧运动。'):'。此时 MN、P 与 |PQ| 不按题意定义。');
  document.querySelectorAll('[data-r]').forEach(b=>b.classList.toggle('active',Math.abs(state.r-(b.dataset.r==='max'?MAX:+b.dataset.r))<1e-7));
  const rl=labels.find(l=>l.key==='radius'),ll=labels.find(l=>l.key==='length');rl.el.textContent='r＝'+fmt(state.r,2);ll.el.textContent='|PQ|＝5/3';
  if(oldValid!==values.valid)metricsDirty=true;rl.dirty=true;updateSelection();invalidate();
}
// Planar view. Both axes share one CSS-pixel scale; device pixel ratio affects only raster size.
function screen(p){return [W/2+(p[0]-view.cx)*view.scale,H/2-(p[1]-view.cy)*view.scale];}
function world(x,y){return [view.cx+(x-W/2)/view.scale,view.cy-(y-H/2)/view.scale];}
function local(e){const r=cv.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top];}
function uiRects(){const s=stage.getBoundingClientRect();return ['.stage-toolbar','#readout','.stage-bottom'].map(q=>{const r=stage.querySelector(q).getBoundingClientRect();return {x:r.left-s.left-5,y:r.top-s.top-5,w:r.width+10,h:r.height+10};});}
function fit(){
  const ui=uiRects(),top=Math.max(82,ui[0].y+ui[0].h+18,W<1000?ui[1].y+ui[1].h+20:0),bottom=ui[2].y-20;
  const xmin=-3.85,xmax=Math.max(2.45,state.circle?state.r+.5:2.45),ymin=state.aux?-2.08:-1.35,ymax=Math.max(1.6,state.circle?2+state.r+.5:2.5);
  view.scale=clamp(Math.min((W-64)/(xmax-xmin),Math.max(120,bottom-top)/(ymax-ymin)),12,1000);
  view.cx=(xmin+xmax)/2;view.cy=(ymin+ymax)/2+((top+bottom)/2-H/2)/view.scale;invalidate();
}
function resize(){
  const r=stage.getBoundingClientRect(),changed=W!==r.width||H!==r.height;W=r.width;H=r.height;
  const budget=state.quality==='sharp'?3500000:2000000,cap=state.quality==='save'?1:state.quality==='sharp'?2:matchMedia('(pointer:coarse)').matches?1.35:1.65;
  dpr=Math.max(.5,Math.min(devicePixelRatio||1,cap,Math.sqrt(budget/(W*H))));cv.width=Math.max(1,Math.round(W*dpr));cv.height=Math.max(1,Math.round(H*dpr));
  if(changed||needsFit){needsFit=false;fit();}invalidate();
}
function invalidate(){if(!frame&&!document.hidden)frame=requestAnimationFrame(render);}
function line(a,b,c,width=2,dash=[]){const p=screen(a),q=screen(b);ctx.beginPath();ctx.strokeStyle=c;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.moveTo(...p);ctx.lineTo(...q);ctx.stroke();ctx.setLineDash([]);}
function ray(a,u,c,width=2.1){
  // Clip the forward ray to the canvas, including when A is outside after panning.
  const p=screen(a),d=[u[0]*view.scale,-u[1]*view.scale];let enter=0,exit=Infinity;
  for(let i=0;i<2;i++){
    const size=i===0?W:H;if(Math.abs(d[i])<1e-12){if(p[i]<0||p[i]>size)return;continue;}
    let lo=-p[i]/d[i],hi=(size-p[i])/d[i];if(lo>hi)[lo,hi]=[hi,lo];enter=Math.max(enter,lo);exit=Math.min(exit,hi);
  }
  if(exit<enter||!Number.isFinite(exit))return;
  // A=(-2,0) is on x²/4+y²=1. The second intersection parameter is
  // t = ux/(ux²/4+uy²). A forward exit exists only when ux > 0.
  const ellipseExit=Math.max(0,u[0]/(u[0]*u[0]/4+u[1]*u[1]));
  const at=t=>[a[0]+t*u[0],a[1]+t*u[1]];
  const solidEnd=Math.min(exit,ellipseExit);
  if(solidEnd>enter+1e-12)line(at(enter),at(solidEnd),c,width);
  const dashStart=Math.max(enter,ellipseExit);
  if(exit>dashStart+1e-12)line(at(dashStart),at(exit),c,width,[8,6]);
}
function shape(path,x,y,sx,sy,c,width,dash=[],fill=0){ctx.save();const p=screen([x,y]);ctx.translate(...p);ctx.scale(view.scale*sx,-view.scale*sy);ctx.lineWidth=width/(view.scale*Math.abs(sx));ctx.setLineDash(dash.map(x=>x/(view.scale*Math.abs(sx))));ctx.strokeStyle=c;if(fill){ctx.globalAlpha=fill;ctx.fillStyle=c;ctx.fill(path);ctx.globalAlpha=1;}ctx.stroke(path);ctx.restore();}
function dot(p,c,size=4.5,open=false){const q=screen(p);ctx.beginPath();ctx.arc(...q,size,0,2*Math.PI);ctx.strokeStyle=c;ctx.lineWidth=2;if(open){ctx.fillStyle='#131A22';ctx.fill();ctx.stroke();}else{ctx.fillStyle=c;ctx.fill();}}
function isVisible(key){if(key==='R'||key==='radius')return state.circle;if(key==='P'||key==='length')return values.valid&&(state.projection||state.trace);if(key==='T1'||key==='T2')return state.contact&&state.tangents&&state.circle;return true;}
function grid(){
  const lo=world(0,H),hi=world(W,0),target=55/view.scale,pow=10**Math.floor(Math.log10(target)),unit=[1,2,5,10].find(v=>v*pow>=target)*pow;
  ctx.lineWidth=1;ctx.strokeStyle='#2A34416E';ctx.beginPath();
  for(let x=Math.ceil(lo[0]/unit)*unit;x<=hi[0];x+=unit){const p=screen([x,0]);ctx.moveTo(p[0],0);ctx.lineTo(p[0],H);}
  for(let y=Math.ceil(lo[1]/unit)*unit;y<=hi[1];y+=unit){const p=screen([0,y]);ctx.moveTo(0,p[1]);ctx.lineTo(W,p[1]);}ctx.stroke();
  line([lo[0],0],[hi[0],0],'#748699',1.4);line([0,lo[1]],[0,hi[1]],'#748699',1.4);
  ctx.fillStyle='#A9B6C4';ctx.font='12px Segoe UI';ctx.textAlign='center';
  const zero=screen([0,0]);for(let x=Math.ceil(lo[0]/unit)*unit;x<hi[0];x+=unit){if(Math.abs(x)<1e-9)continue;let p=screen([x,0]);ctx.fillText(String(+x.toFixed(3)),p[0],clamp(zero[1]+17,17,H-8));}
  ctx.textAlign='right';for(let y=Math.ceil(lo[1]/unit)*unit;y<hi[1];y+=unit){if(Math.abs(y)<1e-9)continue;let p=screen([0,y]);ctx.fillText(String(+y.toFixed(3)),clamp(zero[0]-9,24,W-7),p[1]+4);}
  ctx.font='italic 18px Georgia';ctx.fillText('x',W-14,clamp(zero[1]-10,20,H-10));ctx.fillText('y',clamp(zero[0]+22,24,W-7),24);
}
function rightAngle(at,a,b){const p=screen(at),x=screen(a),y=screen(b),ux=[x[0]-p[0],x[1]-p[1]],uy=[y[0]-p[0],y[1]-p[1]],dx=Math.hypot(...ux),dy=Math.hypot(...uy);if(dx<16||dy<16)return;let size=10;for(let i=0;i<2;i++){ux[i]*=size/dx;uy[i]*=size/dy;}ctx.beginPath();ctx.strokeStyle=color.ink;ctx.lineWidth=1.4;ctx.moveTo(p[0]+ux[0],p[1]+ux[1]);ctx.lineTo(p[0]+ux[0]+uy[0],p[1]+ux[1]+uy[1]);ctx.lineTo(p[0]+uy[0],p[1]+uy[1]);ctx.stroke();}
function render(){
  frame=0;metrics.renders++;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
  if(state.grid)grid();
  if(state.aux){shape(unitCircle,-RHO,0,RHO,RHO,'#A692E880',1.5,[7,7]);line(points.E,points.O,'#A692E866',2);}
  if(state.trace){shape(upperTrace,0,0,1,1,color.orange,3.5);shape(lowerTrace,0,0,1,1,color.orange,3.5);dot([-30/73,80/73],color.orange,4,true);dot([-30/73,-80/73],color.orange,4,true);dot(points.O,color.orange,4,true);}
  if(state.ellipse)shape(ellipsePath,0,0,1,1,color.blue,2.8,[],state.opacity);
  if(state.circle&&state.r>EPS)shape(unitCircle,0,2,state.r,state.r,color.orange,2.5,[],state.opacity);
  if(state.tangents){values.dirs.forEach(u=>ray(points.A,u,color.orange,2.1));}
  if(state.chord&&values.valid){line(points.M,points.N,color.violet,3.3);}
  if(state.projection&&values.valid){line(points.O,points.P,color.blue,2.5);line(points.Q,points.P,color.violet,2.5);rightAngle(points.P,points.O,points.E);}
  if(state.contact&&state.tangents&&state.circle){line(points.D,points.T1,'#FF7A4599',1.5,[4,5]);line(points.D,points.T2,'#FF7A4599',1.5,[4,5]);rightAngle(points.T1,points.D,points.A);rightAngle(points.T2,points.D,points.A);}
  if(state.circle){line(points.D,points.R,'#FF7A4570',1.2,[3,5]);dot(points.R,color.orange,6);const q=screen(points.R);ctx.beginPath();ctx.arc(...q,11,0,2*Math.PI);ctx.strokeStyle='#FF7A4570';ctx.lineWidth=1.8;ctx.stroke();}
  for(const l of labels){if(l.length||l.key==='R'||!isVisible(l.key))continue;const p=points[l.key];if(selected.has(l.key)){const q=screen(p);ctx.beginPath();ctx.arc(...q,10,0,2*Math.PI);ctx.fillStyle='#FF7A4540';ctx.fill();}dot(p,selected.has(l.key)?color.orange:color[l.kind],l.key==='P'?6:l.key.startsWith('T')?3.5:4.8);}
  syncLabels();
}
const overlap=(a,b,gap=3)=>a.x<b.x+b.w+gap&&a.x+a.w+gap>b.x&&a.y<b.y+b.h+gap&&a.y+a.h+gap>b.y;
function syncLabels(){
  for(const l of labels){l.visible=isVisible(l.key)&&(l.length?state.lengths:state.labels);l.el.hidden=!l.visible;l.hit=null;l.el.classList.toggle('sel',selected.has(l.key));l.el.classList.toggle('dragging',gesture?.key===l.key&&gesture?.moved);}
  for(const l of labels){if(l.visible&&(metricsDirty||l.dirty)){l.w=l.el.offsetWidth;l.h=l.el.offsetHeight;metrics.labelMeasurements++;l.dirty=false;}}metricsDirty=false;
  const obstacles=uiRects(),placed=[],anchors=labels.filter(l=>!l.length&&l.visible).map(l=>screen(points[l.key]));
  for(const l of labels){if(!l.visible)continue;let p=l.length?(l.key==='radius'?[(points.D[0]+points.R[0])/2,2]:[(points.Q[0]+points.P[0])/2,points.P[1]/2]):points[l.key];let s=screen(p);if(s[0]<-25||s[0]>W+25||s[1]<-25||s[1]>H+25){l.el.hidden=true;l.visible=false;continue;}
    const candidates=[l.offset,[12,-l.h-12],[-l.w-12,-l.h-12],[12,12],[-l.w-12,12],[-l.w/2,-l.h-22],[-l.w/2,23],[22,-l.h/2],[-l.w-22,-l.h/2],[12,-l.h-58],[-l.w-12,-l.h-58],[12,52],[-l.w-12,52]];
    let best=null,score=Infinity;for(let i=0;i<candidates.length;i++){const o=candidates[i],box={x:clamp(s[0]+o[0],8,Math.max(8,W-l.w-8)),y:clamp(s[1]+o[1],8,Math.max(8,H-l.h-8)),w:l.w,h:l.h};let cost=i*.7+Math.hypot(box.x+l.w/2-s[0],box.y+l.h/2-s[1])*.01;for(const r of obstacles)if(overlap(box,r))cost+=10000;for(const r of placed)if(overlap(box,r,5))cost+=1000;for(const a of anchors)if(a[0]>box.x-4&&a[0]<box.x+box.w+4&&a[1]>box.y-4&&a[1]<box.y+box.h+4)cost+=150;if(cost<score){score=cost;best=box;}}
    l.el.style.transform='translate3d('+best.x+'px,'+best.y+'px,0)';l.hit=best;placed.push(best);
  }
}
function updateSelection(){const list=$('selList'),box=$('pickBox');list.replaceChildren();box.replaceChildren();if(!selected.size)list.textContent='点图中的点或字母';for(const key of selected){let chip=document.createElement('span');chip.className='chip';chip.textContent=key;list.append(chip);let row=document.createElement('div');row.className='pr';let name=document.createElement('span'),value=document.createElement('code');name.textContent=key;value.textContent=key==='P'&&!values.valid?'未定义':'('+points[key].map(n=>fmt(n,3)).join(', ')+')';row.append(name,value);box.append(row);}}
function toggle(key){if(!key||!points[key])return;selected.has(key)?selected.delete(key):selected.add(key);metricsDirty=true;updateSelection();invalidate();}
// Hit once at pointerdown; use that decision until release or cancellation.
function pick(p,type){
  const near=(key,t)=>isVisible(key)&&dist(p,screen(points[key]))<t;
  if(near('R',type==='mouse'?11:16))return 'R';if(near('P',type==='mouse'?10:14))return 'P';
  for(const l of labels){if(!l.length&&l.visible&&l.hit&&p[0]>=l.hit.x&&p[0]<=l.hit.x+l.hit.w&&p[1]>=l.hit.y&&p[1]<=l.hit.y+l.hit.h)return l.key;}
  let key=null,best=type==='mouse'?22:40;for(const l of labels){if(l.length||!isVisible(l.key))continue;let d=dist(p,screen(points[l.key]));if(d<best){best=d;key=l.key;}}return key;
}
function angleToR(a){const m=Math.tan(clamp(a,-AMAX,AMAX)/2);return Math.sqrt(clamp(4-32*m/3,0,8));}
function pointAngle(p){const w=world(...p);return Math.atan2(w[1],w[0]+RHO);}
function stop(){for(const id of pointers.keys()){try{if(cv.hasPointerCapture(id))cv.releasePointerCapture(id);}catch{}}pointers.clear();gesture=null;cv.style.cursor='grab';invalidate();}
function pinchStart(){const a=[...pointers.values()];gesture={mode:'pinch',distance:dist(a[0],a[1]),center:[(a[0][0]+a[1][0])/2,(a[0][1]+a[1][1])/2]};}
cv.addEventListener('pointerdown',e=>{
  e.preventDefault();if(e.isTrusted){if(e.pointerType==='mouse')metrics.trustedMouse++;else if(e.pointerType==='touch')metrics.trustedTouch++;}
  const p=local(e);pointers.set(e.pointerId,p);cv.setPointerCapture(e.pointerId);
  if(gesture?.mode==='radius'||gesture?.mode==='point'||gesture?.mode==='blocked')return;
  if(pointers.size===2){pinchStart();return;}if(pointers.size>2)return;
  const key=pick(p,e.pointerType),circleHit=state.circle&&Math.abs(dist(world(...p),points.D)-state.r)*view.scale<(e.pointerType==='mouse'?10:18);
  const mode=e.button===2||e.shiftKey?'pan':key==='R'||(!key&&circleHit)?'radius':key==='P'?'point':'pan';
  gesture={mode,id:e.pointerId,key,start:p,last:p,moved:false,time:performance.now(),rOffset:state.r-dist(world(...p),points.D),angleOffset:2*Math.atan(values.m)-pointAngle(p)};cv.style.cursor=mode==='pan'?'grabbing':'ew-resize';
});
cv.addEventListener('pointermove',e=>{
  const p=local(e);if(!pointers.has(e.pointerId)){const k=pick(p,e.pointerType),ch=state.circle&&Math.abs(dist(world(...p),points.D)-state.r)*view.scale<10;cv.style.cursor=k==='P'||k==='R'||ch?'ew-resize':k?'pointer':'grab';return;}
  pointers.set(e.pointerId,p);if(!gesture)return;let g=gesture;
  if(g.mode==='blocked')return;
  if(g.mode==='pinch'){if(pointers.size!==2)return;const a=[...pointers.values()],c=[(a[0][0]+a[1][0])/2,(a[0][1]+a[1][1])/2],d=dist(a[0],a[1]);zoom(d/Math.max(g.distance,1),...g.center);view.cx-=(c[0]-g.center[0])/view.scale;view.cy+=(c[1]-g.center[1])/view.scale;g.center=c;g.distance=d;invalidate();return;}
  if(g.id!==e.pointerId)return;if(!g.moved&&dist(p,g.start)<=9)return;
  if(!g.moved){g.moved=true;g.last=g.start;}if(g.mode==='radius')setR(dist(world(...p),points.D)+g.rOffset);
  else if(g.mode==='point')setR(angleToR(pointAngle(p)+g.angleOffset));
  else {view.cx-=(p[0]-g.last[0])/view.scale;view.cy+=(p[1]-g.last[1])/view.scale;invalidate();}g.last=p;
});
function release(e,cancel=false){if(!pointers.has(e.pointerId))return;let g=gesture;pointers.delete(e.pointerId);try{if(cv.hasPointerCapture(e.pointerId))cv.releasePointerCapture(e.pointerId);}catch{}
  if(g&&(g.mode==='radius'||g.mode==='point')&&g.id!==e.pointerId)return;
  if(g&&g.id===e.pointerId&&!g.moved&&!cancel&&performance.now()-g.time<700&&e.button!==2)toggle(g.key);
  gesture=pointers.size?{mode:'blocked'}:null;cv.style.cursor='grab';invalidate();
}
cv.addEventListener('pointerup',e=>release(e));cv.addEventListener('pointercancel',e=>release(e,true));cv.addEventListener('lostpointercapture',e=>{if(pointers.has(e.pointerId))release(e,true);});cv.addEventListener('contextmenu',e=>e.preventDefault());cv.addEventListener('touchmove',e=>{if(e.cancelable)e.preventDefault();},{passive:false});
function zoom(factor,x=W/2,y=H/2){const p=world(x,y);view.scale=clamp(view.scale*factor,12,1000);view.cx=p[0]-(x-W/2)/view.scale;view.cy=p[1]+(y-H/2)/view.scale;invalidate();}
cv.addEventListener('wheel',e=>{e.preventDefault();if(gesture)return;zoom(Math.exp(clamp(-e.deltaY*.0015,-.5,.5)),...local(e));},{passive:false});
// Common page controls. Proof navigation preserves model, view, layers and selection.
function isDrawer(){return matchMedia('(max-width:1100px), (pointer:coarse)').matches||document.body.classList.contains('focused');}
function syncPanel(){const overlay=isDrawer();panel.inert=overlay&&!drawer;$('menu').setAttribute('aria-expanded',String(drawer));if(overlay&&drawer){panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');}else {panel.removeAttribute('role');panel.removeAttribute('aria-modal');}}
function setDrawer(open){if(!isDrawer())return;stop();drawer=open;panel.classList.toggle('open',open);document.body.classList.toggle('drawer-open',open);syncPanel();if(open){returnFocus=document.activeElement;$('close').focus();}else if(returnFocus&&!returnFocus.closest('#panel'))returnFocus.focus();}
function selectTab(which){tab=which;for(const t of ['lesson','settings']){$('tab-'+t).setAttribute('aria-selected',String(t===which));$('tab-'+t).tabIndex=t===which?0:-1;$(t+'-panel').hidden=t!==which;}$('panel').querySelector('.panel-scroll').scrollTop=0;}
function proof(i){selectTab('lesson');if(isDrawer())setDrawer(true);document.querySelectorAll('[data-lesson]').forEach(el=>el.classList.remove('proof-focus'));const el=$('proof-'+i);el.classList.add('proof-focus');el.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}
$('menu').onclick=()=>setDrawer(!drawer);$('close').onclick=()=>setDrawer(false);$('scrim').onclick=()=>setDrawer(false);
$('focus').onclick=()=>{stop();drawer=false;panel.classList.remove('open');document.body.classList.remove('drawer-open');document.body.classList.toggle('focused');const on=document.body.classList.contains('focused');$('focus').setAttribute('aria-pressed',String(on));$('focus').textContent=on?'退出专注':'专注模式';syncPanel();};
for(const t of ['lesson','settings']){$('tab-'+t).onclick=()=>selectTab(t);$('tab-'+t).onkeydown=e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const next=e.key==='Home'?'lesson':e.key==='End'?'settings':t==='lesson'?'settings':'lesson';selectTab(next);$('tab-'+next).focus();}};}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(drawer)setDrawer(false);else {stop();selected.clear();metricsDirty=true;updateSelection();invalidate();}}if(e.key==='Tab'&&drawer){const a=[...panel.querySelectorAll('button,input,summary')].filter(el=>!el.closest('[hidden]')&&el.offsetParent!==null&&el.tabIndex>=0);if(e.shiftKey&&document.activeElement===a[0]){e.preventDefault();a.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===a.at(-1)){e.preventDefault();a[0].focus();}}});
$('sR').addEventListener('input',e=>setR(+e.target.value));document.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>setR(b.dataset.r==='max'?MAX:+b.dataset.r));
document.querySelectorAll('[data-layer]').forEach(c=>c.onchange=()=>{state[c.dataset.layer]=c.checked;metricsDirty=true;invalidate();});
for(const [id,key] of [['cLabels','labels'],['cLengths','lengths']])$(id).onchange=e=>{state[key]=e.target.checked;metricsDirty=true;invalidate();};
$('sFont').oninput=e=>{state.font=+e.target.value;document.documentElement.style.setProperty('--lab-size',state.font+'px');$('sFontval').textContent=state.font+' px';metricsDirty=true;invalidate();};
$('sOpacity').oninput=e=>{state.opacity=+e.target.value/100;$('sOpacityval').textContent=e.target.value+'%';invalidate();};
$('clear').onclick=()=>{selected.clear();metricsDirty=true;updateSelection();invalidate();};
document.querySelectorAll('[data-quality]').forEach(b=>b.onclick=()=>{state.quality=b.dataset.quality;document.querySelectorAll('[data-quality]').forEach(c=>{c.classList.toggle('active',c===b);c.setAttribute('aria-pressed',String(c===b));});resize();});
document.querySelectorAll('[data-proof]').forEach(b=>b.onclick=()=>proof(+b.dataset.proof));$('stage-next').onclick=()=>proof(0);
$('fit').onclick=()=>{stop();fit();};$('reset').onclick=()=>{stop();fit();};$('zoomIn').onclick=()=>{stop();zoom(1.25);};$('zoomOut').onclick=()=>{stop();zoom(.8);};
function layoutChange(){if(drawer)setDrawer(false);stop();syncPanel();metricsDirty=true;resize();}
new ResizeObserver(resize).observe(stage);window.addEventListener('orientationchange',()=>{needsFit=true;layoutChange();});matchMedia('(orientation:portrait)').addEventListener('change',()=>{needsFit=true;layoutChange();});matchMedia('(max-width:1100px), (pointer:coarse)').addEventListener('change',layoutChange);
window.addEventListener('blur',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();if(frame)cancelAnimationFrame(frame);frame=0;}else invalidate();});
$('hint').textContent=matchMedia('(pointer:coarse)').matches?'拖圆周或 P · 空白平移 · 双指缩放 · 点字母多选':'拖圆周或 P · 空白平移 · 滚轮缩放 · 点字母多选';
if(location.hash==='#geo-debug')window.__S={state,view,points,labels,metrics,selected,setR,compute,screen,world,fit,angleToR,stop,get values(){return values;},get gesture(){return gesture;},get dpr(){return dpr;},get dimensions(){return {width:W,height:H};},get renderCount(){return metrics.renders;}};
syncPanel();setR(1.4);resize();
})();
