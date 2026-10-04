(function () {
  'use strict';
  const $=id=>document.getElementById(id);
  const compactQuery=matchMedia('(max-width:1100px), (pointer:coarse)'),coarseQuery=matchMedia('(pointer:coarse)'),reducedQuery=matchMedia('(prefers-reduced-motion:reduce)');
  function fail(message){$('error').hidden=false;$('error').textContent=message;}
  if(!window.THREE){fail('三维库未能加载。请打开单文件版，或将 three.min.js 与双文件版页面放在一起。');return;}
  // Teaching coordinates: bottom center is the origin; z is vertical.
  const H=Math.sqrt(6)/2,R=1.56;
  const STANDARD={A:[-1,-1,0],B:[1,-1,0],C:[1,1,0],D:[-1,1,0],Ap:[-.5,-.5,H],Bp:[.5,-.5,H],Cp:[.5,.5,H],Dp:[-.5,.5,H],P:[.75,.75,H/2],F:[5/7,-1,4*H/7]};
  const names={Ap:'A′',Bp:'B′',Cp:'C′',Dp:'D′'};
  const state={t:.5,solid:true,plane1:true,plane2:true,lineAngle:true,volume:false,angles:false,axes:false,labels:true,lengths:false,font:22,opacity:.08,quality:'auto'};
  const COLORS={blue:0x6BA8E8,orange:0xFF7A45,violet:0xA692E8,green:0x8FBF5A,edge:0xB9C9DD,mute:0x73849A};
  const canvas=$('cv'),stage=$('stage');let renderer;
  try{renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'low-power'});}catch(error){fail('浏览器无法启动 WebGL。请在支持硬件加速的浏览器中打开本页面。');return;}
  renderer.setClearColor(0x131A22,0);
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,1,.1,200),cam={azim:2.08,elev:.38,dist:8},target=new THREE.Vector3();
  let dimensions={width:1,height:1,left:0,top:0,bottom:195},fitDistance=8,frame=0,tween=null,contextLost=false,metricsDirty=true,renderCount=0;
  const statistics={durations:[],geometries:0};
  const V={};for(const [key,p]of Object.entries(STANDARD))V[key]=new THREE.Vector3(p[0],p[2]-H/2,-p[1]);
  const groups={};for(const key of ['faces','edges','plane1','plane2','lineAngle','volume','angles','axes','vertices']){groups[key]=new THREE.Group();scene.add(groups[key]);}
  function material(color,opacity=1){return new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,side:THREE.DoubleSide,depthWrite:opacity===1});}
  const lineMaterials={},axisY=new THREE.Vector3(0,1,0),lineDirection=new THREE.Vector3();
  // One unit TubeGeometry serves every straight segment, including moving segments.
  const unitTube=new THREE.TubeGeometry(new THREE.LineCurve3(new THREE.Vector3(),axisY),1,1,6,false);
  function positionTube(mesh,a,b,r){lineDirection.subVectors(b,a);const length=lineDirection.length();mesh.visible=length>1e-10;if(length>1e-10){mesh.position.copy(a);mesh.quaternion.setFromUnitVectors(axisY,lineDirection.multiplyScalar(1/length));mesh.scale.set(r,length,r);}return mesh;}
  function tube(a,b,color,r=.011,opacity=1){const key=color+':'+opacity;if(!lineMaterials[key])lineMaterials[key]=material(color,opacity);return positionTube(new THREE.Mesh(unitTube,lineMaterials[key]),a,b,r);}
  function triangle(keys,color,opacity){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(9),3));const mesh=new THREE.Mesh(geometry,material(color,opacity));mesh.frustumCulled=false;writeTriangle(mesh,keys);return mesh;}
  function writeTriangle(mesh,keys){const a=mesh.geometry.attributes.position.array;for(let i=0;i<3;i++){const p=V[keys[i]];a[i*3]=p.x;a[i*3+1]=p.y;a[i*3+2]=p.z;}mesh.geometry.attributes.position.needsUpdate=true;}
  function dashed(a,b,color){const mesh=new THREE.Line(new THREE.BufferGeometry().setFromPoints([a,b]),new THREE.LineDashedMaterial({color,transparent:true,opacity:.8,dashSize:.055,gapSize:.045,depthWrite:false}));mesh.computeLineDistances();return mesh;}
  const faceMaterials=[];
  for(const keys of [['A','B','C'],['A','C','D'],['Ap','Cp','Bp'],['Ap','Dp','Cp'],['A','Ap','Bp'],['A','Bp','B'],['B','Bp','Cp'],['B','Cp','C'],['C','Cp','Dp'],['C','Dp','D'],['D','Dp','Ap'],['D','Ap','A']]){const mesh=triangle(keys,COLORS.blue,state.opacity);groups.faces.add(mesh);faceMaterials.push(mesh.material);}
  for(const [a,b]of [['A','B'],['B','C'],['C','D'],['D','A'],['Ap','Bp'],['Bp','Cp'],['Cp','Dp'],['Dp','Ap'],['A','Ap'],['B','Bp'],['D','Dp']])groups.edges.add(tube(V[a],V[b],a.length===1&&b.length===1?COLORS.blue:COLORS.edge,.012));
  groups.edges.add(tube(V.C,V.Cp,COLORS.orange,.016,.68));
  const motionTrack=tube(V.C,V.P,COLORS.orange,.019);groups.edges.add(motionTrack);
  groups.plane1.add(triangle(['Ap','B','D'],COLORS.blue,.19),tube(V.Ap,V.B,COLORS.blue,.009),tube(V.Ap,V.D,COLORS.blue,.009));
  groups.edges.add(tube(V.B,V.D,COLORS.edge,.011,.78));
  const pbdFace=triangle(['P','B','D'],COLORS.orange,.19),pb=tube(V.P,V.B,COLORS.orange,.010),pd=tube(V.P,V.D,COLORS.orange,.010);groups.plane2.add(pbdFace,pb,pd);
  const pbcFace=triangle(['P','B','C'],COLORS.violet,.16),pa=tube(V.P,V.A,COLORS.orange,.018),pf=tube(V.P,V.F,COLORS.violet,.011),ah=dashed(V.A,V.F,COLORS.violet);groups.lineAngle.add(pbcFace,pa,pf,ah);
  const corner1=tube(V.F,V.F,COLORS.violet,.008),corner2=tube(V.F,V.F,COLORS.violet,.008);groups.lineAngle.add(corner1,corner2);
  const arcPieces=[];for(let i=0;i<16;i++){const mesh=tube(V.P,V.P,COLORS.violet,.006);arcPieces.push(mesh);groups.lineAngle.add(mesh);}
  const volumeFaces=[];for(const keys of [['P','B','C'],['P','C','D'],['P','D','B'],['B','D','C']]){const mesh=triangle(keys,COLORS.green,.13);volumeFaces.push({mesh,keys});groups.volume.add(mesh);}
  const volumeLines=[];for(const k of ['B','C','D']){const mesh=tube(V.P,V[k],COLORS.green,.010);volumeLines.push({mesh,k});groups.volume.add(mesh);}
  // Static 60-degree marker at A, with the horizontal projection of AA′.
  const footAp=new THREE.Vector3(-.5,-H/2,.5),angleU=footAp.clone().sub(V.A).normalize();
  groups.angles.add(dashed(V.Ap,footAp,COLORS.green),tube(V.A,footAp,COLORS.green,.010));
  const anglePoints=[];for(let i=0;i<=20;i++){const theta=(Math.PI/3)*i/20;anglePoints.push(V.A.clone().addScaledVector(angleU,.34*Math.cos(theta)).addScaledVector(axisY,.34*Math.sin(theta)));}
  groups.angles.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(anglePoints),20,.006,6,false),material(COLORS.green)));
  const axesLabels=[];for(const [label,dir]of [['x',new THREE.Vector3(1,0,0)],['y',new THREE.Vector3(0,0,-1)],['z',axisY]]){const origin=new THREE.Vector3(0,-H/2,0),end=origin.clone().addScaledVector(dir,1.48);groups.axes.add(new THREE.ArrowHelper(dir,origin,1.4,COLORS.blue,.10,.045));axesLabels.push({label,position:end});}
  const pointGeometry=new THREE.SphereGeometry(.041,16,10),haloGeometry=new THREE.SphereGeometry(.041,12,8),haloMaterial=material(COLORS.orange,.16),vertexMeshes={},halos={},selected=new Set();
  for(const key of Object.keys(V)){const mesh=new THREE.Mesh(pointGeometry,material(key==='P'?COLORS.orange:key==='F'?COLORS.violet:COLORS.edge));mesh.position.copy(V[key]);mesh.scale.setScalar(key==='P'?1.45:1);vertexMeshes[key]=mesh;groups.vertices.add(mesh);const halo=new THREE.Mesh(haloGeometry,haloMaterial);halo.position.copy(V[key]);halo.scale.setScalar(key==='P'?2.8:2.5);halo.visible=key==='P';halos[key]=halo;groups.vertices.add(halo);}
  // All DOM label sizes are cached; movement never reads layout metrics.
  const labels=[],projection=new THREE.Vector3();
  function addLabel(key,text,position,color,kind,offset,when){const el=document.createElement('div');el.className='lab'+(color?' '+color:'')+(kind==='edge'?' edge-label':'');el.textContent=text;$('labels').appendChild(el);const item={key,el,position,kind,offset:offset||[0,0],when:when||(()=>true),width:0,height:0,x:0,y:0,hit:null,visible:false};labels.push(item);return item;}
  function keyVisible(key){return key!=='F'||state.lineAngle&&state.t>1e-9;}
  for(const key of Object.keys(V))addLabel(key,names[key]||key,V[key],key==='P'?'orange':key==='F'?'violet':'','vertex',null,()=>keyVisible(key));
  const midpoint=(a,b)=>new THREE.Vector3().addVectors(V[a],V[b]).multiplyScalar(.5);
  addLabel(null,'AB = 2',midpoint('A','B'),'','edge',[0,18]);addLabel(null,'A′B′ = 1',midpoint('Ap','Bp'),'','edge',[0,-15]);
  addLabel(null,'CC′ = √2',midpoint('C','Cp'),'orange','edge',[46,0]);
  addLabel(null,'60°',V.A.clone().addScaledVector(angleU,.45).addScaledVector(axisY,.17),'green','annotation',[0,0],()=>state.angles);
  const thetaPosition=new THREE.Vector3();const thetaLabel=addLabel(null,'θ',thetaPosition,'violet','annotation',[5,-4],()=>state.lineAngle&&state.t>1e-9);
  for(const entry of axesLabels)addLabel(null,entry.label,entry.position,'','axis',[8,0],()=>state.axes);
  function measureLabels(){for(const item of labels)if(item.visible){item.width=item.el.offsetWidth;item.height=item.el.offsetHeight;}metricsDirty=false;}
  function updateVisibility(){for(const key of ['faces','plane1','plane2','lineAngle','volume','angles','axes'])groups[key].visible=key==='faces'?state.solid:key==='lineAngle'?state.lineAngle&&state.t>1e-9:state[key];for(const key of Object.keys(V)){vertexMeshes[key].visible=keyVisible(key);halos[key].visible=(key==='P'||selected.has(key))&&keyVisible(key);}for(const item of labels){item.visible=item.when()&&(item.kind==='edge'?state.lengths:state.labels);item.el.hidden=!item.visible;item.hit=null;}metricsDirty=true;invalidate();}
  function syncLabels(){
    if(metricsDirty)measureLabels();const w=dimensions.width,h=dimensions.height,placed=[];
    for(const item of labels){item.hit=null;if(!item.visible)continue;projection.copy(item.position).project(camera);if(projection.z<-1||projection.z>1){item.el.hidden=true;continue;}item.el.hidden=false;const px=(projection.x*.5+.5)*w,py=(-projection.y*.5+.5)*h;let x=px+item.offset[0],y=py+item.offset[1];if(item.kind==='vertex'){let dx=px-w/2,dy=py-(h/2-camera.view.offsetY),length=Math.hypot(dx,dy);if(length<18){dx=-1;dy=-.75;length=1.25;}x+=dx/length*(state.font*.72+12);y+=dy/length*(state.font*.72+12);}placed.push({item,x,y,px,py});}
    for(let iteration=0;iteration<14;iteration++)for(let i=0;i<placed.length;i++)for(let j=i+1;j<placed.length;j++){const a=placed[i],b=placed[j],dx=b.x-a.x,dy=b.y-a.y,ox=(a.item.width+b.item.width)/2+7-Math.abs(dx),oy=(a.item.height+b.item.height)/2+7-Math.abs(dy);if(ox>0&&oy>0){if(ox<oy){const shift=(ox+.3)*.5*(dx<0?-1:1);a.x-=shift;b.x+=shift;}else{const shift=(oy+.3)*.5*(dy<0?-1:1);a.y-=shift;b.y+=shift;}}}
    for(const o of placed){const item=o.item;o.x=Math.max(item.width/2+6,Math.min(w-item.width/2-6,o.x));o.y=Math.max(item.height/2+6,Math.min(h-dimensions.bottom-item.height/2-10,o.y));item.x=o.px;item.y=o.py;item.el.style.transform='translate3d('+o.x.toFixed(2)+'px,'+o.y.toFixed(2)+'px,0) translate(-50%,-50%)';item.hit={x0:o.x-item.width/2-3,x1:o.x+item.width/2+3,y0:o.y-item.height/2-3,y1:o.y+item.height/2+3};}
  }
  function pickVertex(px,py,type){
    const visible=labels.filter(item=>item.kind==='vertex'&&keyVisible(item.key));
    // P's ball takes priority at coincident endpoints. Other displaced labels remain selectable.
    const touch=type==='touch'||type==='pen',tol=touch?40:22;projection.copy(V.P).project(camera);const pOnScreen=projection.z>=-1&&projection.z<=1,pDistance=Math.hypot(px-(projection.x*.5+.5)*dimensions.width,py-(-projection.y*.5+.5)*dimensions.height);
    if(pOnScreen&&pDistance<(touch?18:12))return 'P';
    for(const item of visible){const r=item.hit;if(r&&px>=r.x0&&px<=r.x1&&py>=r.y0&&py<=r.y1)return item.key;}
    if(pOnScreen&&pDistance<tol)return 'P';
    let best=null,distance=tol;for(const key of Object.keys(V)){if(!keyVisible(key))continue;projection.copy(V[key]).project(camera);if(projection.z>1||projection.z<-1)continue;const d=Math.hypot(px-(projection.x*.5+.5)*dimensions.width,py-(-projection.y*.5+.5)*dimensions.height);if(d<distance){distance=d;best=key;}}return best;
  }
  function refreshSelection(){const list=$('selList'),box=$('pickBox');list.textContent=selected.size?'':'点模型中的顶点或字母';box.textContent='';for(const key of Object.keys(V)){const chosen=selected.has(key);vertexMeshes[key].scale.setScalar(chosen?1.85:key==='P'?1.45:1);vertexMeshes[key].material.color.setHex(chosen?COLORS.orange:key==='P'?COLORS.orange:key==='F'?COLORS.violet:COLORS.edge);halos[key].visible=(chosen||key==='P')&&keyVisible(key);}for(const item of labels)item.el.classList.toggle('sel',item.kind==='vertex'&&selected.has(item.key));for(const key of selected){const chip=document.createElement('span');chip.className='chip';chip.textContent=names[key]||key;list.appendChild(chip);const row=document.createElement('div');row.className='pr';const name=document.createElement('span'),coord=document.createElement('span');name.textContent=names[key]||key;coord.textContent='('+STANDARD[key].map(v=>Number(v.toFixed(3))).join(', ')+')';row.append(name,coord);box.append(row);}metricsDirty=true;invalidate();}
  function updateSelectedP(){if(!selected.has('P'))return;const keys=[...selected],index=keys.indexOf('P');$('pickBox').children[index].lastElementChild.textContent='('+STANDARD.P.map(v=>Number(v.toFixed(3))).join(', ')+')';}
  function toggleSelection(key){if(!key)return;if(selected.has(key))selected.delete(key);else selected.add(key);refreshSelection();}
  const n1=new THREE.Vector3(),n2=new THREE.Vector3(),n3=new THREE.Vector3(),tmpA=new THREE.Vector3(),tmpB=new THREE.Vector3(),arcA=new THREE.Vector3(),arcB=new THREE.Vector3(),uPA=new THREE.Vector3(),uPF=new THREE.Vector3(),orth=new THREE.Vector3(),cornerA=new THREE.Vector3(),cornerB=new THREE.Vector3(),cornerC=new THREE.Vector3();
  function normal(a,b,c,out){tmpA.subVectors(b,a);tmpB.subVectors(c,a);return out.crossVectors(tmpA,tmpB);}
  const values={planeAngle:90,sinTheta:4*Math.sqrt(273)/91,theta:Math.asin(4*Math.sqrt(273)/91)*180/Math.PI,v1:H/3,v2:2*H};
  function calculate(){normal(V.Ap,V.B,V.D,n1);normal(V.P,V.B,V.D,n2);values.planeAngle=Math.acos(Math.min(1,Math.abs(n1.dot(n2))/(n1.length()*n2.length())))*180/Math.PI;values.v1=2*state.t*H/3;values.v2=7*H/3-values.v1;if(state.t<=1e-9){values.sinTheta=null;values.theta=null;return;}normal(V.P,V.B,V.C,n3);tmpA.subVectors(V.A,V.P);values.sinTheta=Math.abs(tmpA.dot(n3))/(tmpA.length()*n3.length());values.theta=Math.asin(Math.min(1,values.sinTheta))*180/Math.PI;}
  function syncReadings(){const t=state.t,mid=Math.abs(t-.5)<1e-7,ratio=mid?'1 : 1':t===0?'0 : 1':t===1?'1 : 0':t.toFixed(3)+' : '+(1-t).toFixed(3),volume=mid?'1 : 6':(2*t).toFixed(3)+' : '+(7-2*t).toFixed(3),angle=values.planeAngle.toFixed(1)+'°',sin=values.sinTheta===null?'未定义':values.sinTheta.toFixed(4);$('sT').value=String(t);$('sTval').textContent=t.toFixed(3);$('mRatio').textContent=ratio;$('mVolume').textContent=volume;$('mAngle').textContent=angle;$('mSin').textContent=sin;$('rT').textContent=t.toFixed(3);$('rAngle').textContent=angle;$('rSin').textContent=sin;$('midFlag').textContent=mid?'P 为中点 · 两面垂直':t<=1e-9?'P = C · 平面 PBC 未定义':'P 在 CC′ 上 · 可直接拖动';$('midFlag').classList.toggle('at-mid',mid);for(const el of document.querySelectorAll('[data-t]')){const active=Math.abs(t-Number(el.dataset.t))<1e-7;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));}}
  function updateDynamic(){
    writeTriangle(pbdFace,['P','B','D']);writeTriangle(pbcFace,['P','B','C']);positionTube(pb,V.P,V.B,.010);positionTube(pd,V.P,V.D,.010);positionTube(pa,V.P,V.A,.018);positionTube(pf,V.P,V.F,.011);positionTube(motionTrack,V.C,V.P,.019);
    for(const entry of volumeFaces)writeTriangle(entry.mesh,entry.keys);for(const entry of volumeLines)positionTube(entry.mesh,V.P,V[entry.k],.010);
    vertexMeshes.P.position.copy(V.P);halos.P.position.copy(V.P);
    if(state.t>1e-9){uPA.subVectors(V.A,V.P).normalize();uPF.subVectors(V.F,V.P).normalize();orth.copy(uPA).addScaledVector(uPF,-uPA.dot(uPF)).normalize();const theta=values.theta*Math.PI/180;for(let i=0;i<16;i++){arcA.copy(V.P).addScaledVector(uPF,.23*Math.cos(theta*i/16)).addScaledVector(orth,.23*Math.sin(theta*i/16));arcB.copy(V.P).addScaledVector(uPF,.23*Math.cos(theta*(i+1)/16)).addScaledVector(orth,.23*Math.sin(theta*(i+1)/16));positionTube(arcPieces[i],arcA,arcB,.006);}thetaPosition.copy(V.P).addScaledVector(uPF,.31*Math.cos(theta/2)).addScaledVector(orth,.31*Math.sin(theta/2));cornerA.copy(V.F).addScaledVector(uPF,-.105);cornerC.copy(V.F).addScaledVector(n3.normalize(),-.105);cornerB.copy(cornerA).addScaledVector(n3,-.105);positionTube(corner1,cornerA,cornerB,.008);positionTube(corner2,cornerB,cornerC,.008);}
  }
  // Sole parameter entry for model dragging, range input and quick positions.
  function setT(value){if(!Number.isFinite(value))return;const next=Math.max(0,Math.min(1,value)),wasValid=state.t>1e-9;state.t=next;V.P.lerpVectors(V.C,V.Cp,next);STANDARD.P[0]=STANDARD.P[1]=1-next/2;STANDARD.P[2]=H*next;calculate();updateDynamic();syncReadings();updateSelectedP();if(wasValid!==(next>1e-9))updateVisibility();invalidate();}
  const rayO=new THREE.Vector3(),rayD=new THREE.Vector3(),segmentU=new THREE.Vector3().subVectors(V.Cp,V.C),rayW=new THREE.Vector3();
  function screenToT(px,py){const aspect=dimensions.width/dimensions.height;if(aspect<.35||aspect>3)return null;rayO.copy(camera.position);rayD.set(px/dimensions.width*2-1,1-py/dimensions.height*2,.5).unproject(camera).sub(rayO).normalize();rayW.subVectors(rayO,V.C);const uu=segmentU.lengthSq(),ud=segmentU.dot(rayD),uw=segmentU.dot(rayW),dw=rayD.dot(rayW),den=uu-ud*ud;if(den<1e-9)return null;const t=(uw-ud*dw)/den;return Number.isFinite(t)?t:null;}
  let focusedProof=0;
  function focusProof(index){focusedProof=Math.max(0,Math.min(3,index));tabSelect('lesson');if(compact())setDrawer(true);const card=$('proof-'+focusedProof);for(const el of document.querySelectorAll('[data-lesson]'))el.classList.toggle('proof-focus',el===card);card.scrollIntoView({behavior:reducedQuery.matches?'auto':'smooth',block:'start'});}
  const checks={cSolid:'solid',cPlane1:'plane1',cPlane2:'plane2',cLineAngle:'lineAngle',cVolume:'volume',cAngles:'angles',cAxes:'axes',cLabels:'labels',cLengths:'lengths'};
  function synchronizeChecks(){for(const [id,key]of Object.entries(checks))$(id).checked=state[key];}
