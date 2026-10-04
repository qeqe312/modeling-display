(function () {
  'use strict';
  const $=id=>document.getElementById(id);
  const compactQuery=matchMedia('(max-width:1100px), (pointer:coarse)'),coarseQuery=matchMedia('(pointer:coarse)'),reducedQuery=matchMedia('(prefers-reduced-motion:reduce)');
  function fail(message){$('error').hidden=false;$('error').textContent=message;}
  if(!window.THREE){fail('三维库未能加载，请打开完整的离线单文件。');return;}
  const SQ3=Math.sqrt(3),R=1.85,DEFAULT_VIEW={azim:.42,elev:.46},DEFAULT_T=1/3;
  // Teaching (x,y,z) -> render (x-√3/2,z-.45,.5-y). Base z=0 stays horizontal.
  const STANDARD={A:[SQ3,0,0],B:[0,-1,0],M:[0,0,0],C:[0,1,0],D:[SQ3,2,0],B1:[0,-.5,SQ3/2],N:[SQ3/2,.75,SQ3/4],O:[SQ3/2,1,.5]};
  const names={B1:'B₁'},state={t:DEFAULT_T,playing:false,speed:30,solid:true,original:true,plane1:true,plane2:true,lineAngle:true,volume:false,angles:true,nTrack:false,sphere:false,axes:false,labels:true,lengths:false,font:22,opacity:.14,quality:'auto'};
  const COLORS={blue:0x6BA8E8,orange:0xFF7A45,violet:0xA692E8,edge:0xB9C9DD,mute:0x73849A};
  const canvas=$('cv'),stage=$('stage');let renderer;
  try{renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'low-power'});}catch(error){fail('浏览器无法启动 WebGL，请在支持硬件加速的浏览器中打开。');return;}
  renderer.setClearColor(0x131A22,0);
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,1,.1,200),cam={...DEFAULT_VIEW,dist:8},target=new THREE.Vector3();
  let dimensions={width:1,height:1,left:0,top:0,bottom:195},fitDistance=8,frame=0,tween=null,contextLost=false,metricsDirty=true,renderCount=0;
  const statistics={durations:[],geometries:0},V={};
  const toRender=(p,out)=>out.set(p[0]-SQ3/2,p[2]-.45,.5-p[1]);
  for(const [key,p]of Object.entries(STANDARD))V[key]=toRender(p,new THREE.Vector3());
  const groups={};for(const key of ['faces','edges','original','plane1','plane2','lineAngle','volume','angles','nTrack','sphere','axes','vertices']){groups[key]=new THREE.Group();scene.add(groups[key]);}
  function material(color,opacity=1){return new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,side:THREE.DoubleSide,depthWrite:opacity===1});}
  const lineMaterials={},axisY=new THREE.Vector3(0,1,0),lineDirection=new THREE.Vector3(),unitTube=new THREE.TubeGeometry(new THREE.LineCurve3(new THREE.Vector3(),axisY),1,1,6,false);
  function positionTube(mesh,a,b,r){lineDirection.subVectors(b,a);const length=lineDirection.length();mesh.visible=length>1e-10;if(length>1e-10){mesh.position.copy(a);mesh.quaternion.setFromUnitVectors(axisY,lineDirection.multiplyScalar(1/length));mesh.scale.set(r,length,r);}return mesh;}
  function tube(a,b,color,r=.011,opacity=1){const key=color+':'+opacity;if(!lineMaterials[key])lineMaterials[key]=material(color,opacity);return positionTube(new THREE.Mesh(unitTube,lineMaterials[key]),a,b,r);}
  function triangle(keys,color,opacity){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(9),3));const mesh=new THREE.Mesh(geometry,material(color,opacity));mesh.frustumCulled=false;writeTriangle(mesh,keys);return mesh;}
  function writeTriangle(mesh,keys){const a=mesh.geometry.attributes.position.array;for(let i=0;i<3;i++){const p=V[keys[i]];a[i*3]=p.x;a[i*3+1]=p.y;a[i*3+2]=p.z;}mesh.geometry.attributes.position.needsUpdate=true;}
  function dashed(a,b,color){const mesh=new THREE.Line(new THREE.BufferGeometry().setFromPoints([a,b]),new THREE.LineDashedMaterial({color,transparent:true,opacity:.5,dashSize:.07,gapSize:.06,depthWrite:false}));mesh.computeLineDistances();return mesh;}
  const faceMaterials=[],dynamicFaces=[],dynamicLines=[];
  function movingFace(group,keys,color,opacity){const mesh=triangle(keys,color,opacity);groups[group].add(mesh);dynamicFaces.push({mesh,keys});return mesh;}
  function movingLine(group,a,b,color,r=.011,opacity=1){const mesh=tube(V[a],V[b],color,r,opacity);groups[group].add(mesh);dynamicLines.push({mesh,a,b,r});return mesh;}
  for(const keys of [['A','M','C'],['A','C','D']]){const mesh=triangle(keys,COLORS.blue,state.opacity);groups.faces.add(mesh);faceMaterials.push(mesh.material);}
  for(const [a,b]of [['A','M'],['M','C'],['C','D'],['D','A']])groups.edges.add(tube(V[a],V[b],COLORS.blue,a==='A'&&b==='M'?.022:.012));
  groups.original.add(triangle(['A','B','M'],COLORS.mute,.045),dashed(V.A,V.B,COLORS.mute),dashed(V.B,V.M,COLORS.mute));
  const foldedFace=movingFace('plane1',['A','B1','M'],COLORS.orange,state.opacity);faceMaterials.push(foldedFace.material);
  // Structural edges and all selectable points survive hidden face layers.
  movingLine('edges','A','B1',COLORS.orange,.015);movingLine('edges','M','B1',COLORS.orange,.015);
  movingLine('edges','B1','C',COLORS.blue,.010,.75);movingLine('edges','B1','D',COLORS.edge,.010,.75);
  movingFace('plane2',['B1','M','C'],COLORS.blue,.11);
  movingLine('lineAngle','C','N',COLORS.violet,.019);
  const cDirection=V.C.clone().add(new THREE.Vector3(1.12,0,0));groups.lineAngle.add(dashed(V.C,cDirection,COLORS.violet));
  const thetaPieces=[];for(let i=0;i<16;i++){const mesh=tube(V.C,V.C,COLORS.violet,.006);thetaPieces.push(mesh);groups.lineAngle.add(mesh);}
  for(const keys of [['B1','A','M'],['B1','M','D'],['B1','D','A'],['A','D','M']])movingFace('volume',keys,COLORS.violet,.10);
  groups.volume.add(tube(V.M,V.D,COLORS.violet,.008,.6));
  const arcA=new THREE.Vector3(),arcB=new THREE.Vector3(),foldPoint=(t,out)=>out.set(-SQ3/2,Math.sin(Math.PI*t)-.45,.5+Math.cos(Math.PI*t));
  // Constant unit tubes are transformed, never rebuilt during folding.
  for(let i=0;i<64;i++){foldPoint(i/64,arcA);foldPoint((i+.72)/64,arcB);groups.angles.add(tube(arcA,arcB,COLORS.orange,.005,.38));
    const a=toRender([SQ3/2,1-Math.cos(Math.PI*i/64)/2,Math.sin(Math.PI*i/64)/2],new THREE.Vector3()),b=toRender([SQ3/2,1-Math.cos(Math.PI*(i+.65)/64)/2,Math.sin(Math.PI*(i+.65)/64)/2],new THREE.Vector3());groups.nTrack.add(tube(a,b,COLORS.violet,.004,.6));}
  const phiPieces=[];for(let i=0;i<24;i++){const mesh=tube(V.M,V.M,COLORS.orange,.006);phiPieces.push(mesh);groups.angles.add(mesh);}
  const sphereMesh=new THREE.Mesh(new THREE.SphereGeometry(Math.sqrt(2),48,32),material(COLORS.violet,.06));sphereMesh.position.copy(V.O);groups.sphere.add(sphereMesh);
  // Three great circles make the transparent sphere readable without a dense wireframe.
  const sphereLineMaterial=new THREE.LineBasicMaterial({color:COLORS.violet,transparent:true,opacity:.40,depthWrite:false});
  for(let plane=0;plane<3;plane++){const pts=[];for(let i=0;i<=96;i++){const a=2*Math.PI*i/96,u=Math.sqrt(2)*Math.cos(a),v=Math.sqrt(2)*Math.sin(a);pts.push(V.O.clone().add(new THREE.Vector3(plane===0?0:u,plane===1?0:plane===0?u:v,plane===2?0:v)));}groups.sphere.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),sphereLineMaterial));}
  groups.sphere.add(dashed(V.O,V.C,COLORS.violet));
  const axesLabels=[];for(const [label,dir]of [['x',new THREE.Vector3(1,0,0)],['y',new THREE.Vector3(0,0,-1)],['z',axisY]]){groups.axes.add(new THREE.ArrowHelper(dir,V.M,1.25,COLORS.blue,.10,.045));axesLabels.push({label,position:V.M.clone().addScaledVector(dir,1.34)});}
  const pointGeometry=new THREE.SphereGeometry(.034,16,10),haloGeometry=new THREE.SphereGeometry(.034,12,8),haloMaterial=material(COLORS.orange,.15),vertexMeshes={},halos={},selected=new Set();
  function pointColor(key){return key==='B1'?COLORS.orange:key==='N'||key==='O'?COLORS.violet:key==='B'?COLORS.mute:COLORS.edge;}
  for(const key of Object.keys(V)){const mesh=new THREE.Mesh(pointGeometry,material(pointColor(key)));mesh.position.copy(V[key]);mesh.scale.setScalar(key==='B1'?1.65:1);vertexMeshes[key]=mesh;groups.vertices.add(mesh);const halo=new THREE.Mesh(haloGeometry,haloMaterial);halo.position.copy(V[key]);halo.scale.setScalar(key==='B1'?3.1:2.5);halos[key]=halo;groups.vertices.add(halo);}
  const labels=[],projection=new THREE.Vector3();
  function addLabel(key,text,position,color,kind,offset,when){const el=document.createElement('div');el.className='lab'+(color?' '+color:'')+(kind==='edge'?' edge-label':kind==='annotation'?' annotation-label':'');el.textContent=text;$('labels').appendChild(el);const item={key,el,position,kind,offset:offset||[0,0],when:when||(()=>true),width:0,height:0,x:0,y:0,hit:null,visible:false};labels.push(item);return item;}
  const atMaximum=()=>Math.abs(state.t-.5)<1e-7,nondegenerate=()=>state.t>1e-9&&state.t<1-1e-9;
  function keyVisible(key){return key==='B'?state.original:key==='O'?state.sphere&&atMaximum():true;}
  for(const key of Object.keys(V))addLabel(key,names[key]||key,V[key],key==='B1'?'orange':key==='N'||key==='O'?'violet':'','vertex',null,()=>keyVisible(key));
  const midpoint=(a,b)=>new THREE.Vector3().addVectors(V[a],V[b]).multiplyScalar(.5),lengthAB=midpoint('A','B1'),lengthBM=midpoint('B1','M'),lengthCN=midpoint('C','N');
  addLabel(null,'AM = √3',midpoint('A','M'),'','edge',[0,18]);addLabel(null,'MC = 1',midpoint('M','C'),'','edge',[0,18]);addLabel(null,'AB₁ = 2',lengthAB,'orange','edge',[0,-15]);addLabel(null,'MB₁ = 1',lengthBM,'orange','edge',[-35,0]);addLabel(null,'CN = 1',lengthCN,'violet','edge',[0,19],()=>state.lineAngle);
  const thetaPosition=new THREE.Vector3(),phiPosition=new THREE.Vector3();addLabel(null,'θ = 30°',thetaPosition,'violet','annotation',[0,0],()=>state.lineAngle);const phiLabel=addLabel(null,'φ',phiPosition,'orange','annotation',[0,0],()=>state.angles&&state.t>.015);
  for(const entry of axesLabels)addLabel(null,entry.label,entry.position,'','axis',[8,0],()=>state.axes);
  function measureLabels(){for(const item of labels)if(item.visible){item.width=item.el.offsetWidth;item.height=item.el.offsetHeight;}metricsDirty=false;}
  function updateVisibility(){for(const key of ['faces','original','plane1','plane2','lineAngle','volume','angles','nTrack','sphere','axes'])groups[key].visible=key==='faces'?state.solid:key==='plane2'?state.plane2&&nondegenerate():key==='sphere'?state.sphere&&atMaximum():state[key];for(const key of Object.keys(V)){vertexMeshes[key].visible=keyVisible(key);halos[key].visible=(key==='B1'||selected.has(key))&&keyVisible(key);}for(const item of labels){item.visible=item.when()&&(item.kind==='edge'?state.lengths:state.labels);item.el.hidden=!item.visible;item.hit=null;}syncSphereStatus();metricsDirty=true;invalidate();}
  function syncLabels(){
    if(metricsDirty)measureLabels();const w=dimensions.width,h=dimensions.height,placed=[];
    for(const item of labels){item.hit=null;if(!item.visible)continue;projection.copy(item.position).project(camera);if(projection.z<-1||projection.z>1){item.el.hidden=true;continue;}item.el.hidden=false;const px=(projection.x*.5+.5)*w,py=(-projection.y*.5+.5)*h;let x=px+item.offset[0],y=py+item.offset[1];if(item.kind==='vertex'){let dx=px-w/2,dy=py-(h/2-camera.view.offsetY),length=Math.hypot(dx,dy);if(length<18){dx=-1;dy=-.75;length=1.25;}x+=dx/length*(state.font*.72+12);y+=dy/length*(state.font*.72+12);}placed.push({item,x,y,px,py});}
    for(let iteration=0;iteration<18;iteration++)for(let i=0;i<placed.length;i++)for(let j=i+1;j<placed.length;j++){const a=placed[i],b=placed[j],dx=b.x-a.x,dy=b.y-a.y,ox=(a.item.width+b.item.width)/2+7-Math.abs(dx),oy=(a.item.height+b.item.height)/2+7-Math.abs(dy);if(ox>0&&oy>0){if(ox<oy){const shift=(ox+.3)*.5*(dx<0?-1:1);a.x-=shift;b.x+=shift;}else{const shift=(oy+.3)*.5*(dy<0?-1:1);a.y-=shift;b.y+=shift;}}}
    // Keep labels away from top controls as well as the formula dock.
    for(const o of placed){const item=o.item;o.x=Math.max(item.width/2+6,Math.min(w-item.width/2-6,o.x));o.y=Math.max(item.height/2+6,Math.min(h-dimensions.bottom-item.height/2-10,o.y));item.x=o.px;item.y=o.py;item.el.style.transform='translate3d('+o.x.toFixed(2)+'px,'+o.y.toFixed(2)+'px,0) translate(-50%,-50%)';item.hit={x0:o.x-item.width/2-3,x1:o.x+item.width/2+3,y0:o.y-item.height/2-3,y1:o.y+item.height/2+3};}
  }
  function pickVertex(px,py,type){const visible=labels.filter(item=>item.kind==='vertex'&&keyVisible(item.key)),touch=type==='touch'||type==='pen',tol=touch?40:22;projection.copy(V.B1).project(camera);const pOnScreen=projection.z>=-1&&projection.z<=1,pDistance=Math.hypot(px-(projection.x*.5+.5)*dimensions.width,py-(-projection.y*.5+.5)*dimensions.height);
    if(pOnScreen&&pDistance<(touch?18:12))return 'B1';for(const item of visible){const r=item.hit;if(r&&px>=r.x0&&px<=r.x1&&py>=r.y0&&py<=r.y1)return item.key;}if(pOnScreen&&pDistance<tol)return 'B1';let best=null,distance=tol;for(const key of Object.keys(V)){if(!keyVisible(key))continue;projection.copy(V[key]).project(camera);if(projection.z>1||projection.z<-1)continue;const d=Math.hypot(px-(projection.x*.5+.5)*dimensions.width,py-(-projection.y*.5+.5)*dimensions.height);if(d<distance){distance=d;best=key;}}return best;}
  function refreshSelection(){const list=$('selList'),box=$('pickBox');list.textContent=selected.size?'':'点模型中的顶点或字母';box.textContent='';for(const key of Object.keys(V)){const chosen=selected.has(key);vertexMeshes[key].scale.setScalar(chosen?1.9:key==='B1'?1.65:1);vertexMeshes[key].material.color.setHex(chosen?COLORS.orange:pointColor(key));halos[key].visible=(chosen||key==='B1')&&keyVisible(key);}for(const item of labels)item.el.classList.toggle('sel',item.kind==='vertex'&&selected.has(item.key));for(const key of selected){const chip=document.createElement('span');chip.className='chip';chip.textContent=names[key]||key;list.appendChild(chip);const row=document.createElement('div');row.className='pr';const name=document.createElement('span'),coord=document.createElement('span');name.textContent=names[key]||key;coord.textContent='('+STANDARD[key].map(v=>Number(v.toFixed(3))).join(', ')+')';row.append(name,coord);box.append(row);}metricsDirty=true;invalidate();}
  function updateSelectedP(){for(const key of ['B1','N']){if(!selected.has(key))continue;const index=[...selected].indexOf(key);$('pickBox').children[index].lastElementChild.textContent='('+STANDARD[key].map(v=>Number(v.toFixed(3))).join(', ')+')';}}
  function toggleSelection(key){if(!key)return;if(selected.has(key))selected.delete(key);else selected.add(key);refreshSelection();}
  const values={phi:60,planeAngle:90,CN:1,theta:30,volume:.5};
  function calculate(){values.phi=state.t*180;values.planeAngle=nondegenerate()?90:null;values.CN=V.C.distanceTo(V.N);values.theta=Math.acos(Math.min(1,Math.abs(V.N.x-V.C.x)/values.CN))*180/Math.PI;values.volume=SQ3*Math.sin(Math.PI*state.t)/3;}
  function syncSphereStatus(){$('sphereStatus').textContent=!state.sphere?'图层未开启':atMaximum()?'R＝√2，OC＝1（球内）':'仅 φ＝90° 时可见';}
  function syncReadings(){const angle=values.phi.toFixed(1)+'°';$('sT').value=String(state.t);$('sTval').textContent=angle;$('sT').setAttribute('aria-valuetext',angle);$('mRatio').textContent=angle;$('mCN').textContent=values.CN.toFixed(4);$('mAngle').textContent=values.planeAngle===null?'未定义':values.planeAngle.toFixed(1)+'°';$('mSin').textContent=values.theta.toFixed(1)+'°';$('mVolume').textContent=values.volume.toFixed(4);$('rT').textContent=angle;$('rAngle').textContent=values.CN.toFixed(4);$('rSin').textContent=values.volume.toFixed(4);$('midFlag').textContent=atMaximum()?'90° · 体积最大 √3/3':!nondegenerate()?'共面端点 · 平面 B₁MC 未定义':state.playing?'播放翻折中 · N 为中点':'沿 AM 翻折 · N 为中点';$('midFlag').classList.toggle('at-mid',atMaximum());syncSphereStatus();for(const el of document.querySelectorAll('[data-t]')){const active=Math.abs(state.t-Number(el.dataset.t))<1e-7;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));}}
  const cnUnit=new THREE.Vector3(),thetaOrth=new THREE.Vector3();
  function updateDynamic(){for(const {mesh,keys}of dynamicFaces)writeTriangle(mesh,keys);for(const {mesh,a,b,r}of dynamicLines)positionTube(mesh,V[a],V[b],r);for(const key of ['B1','N']){vertexMeshes[key].position.copy(V[key]);halos[key].position.copy(V[key]);}
    lengthAB.addVectors(V.A,V.B1).multiplyScalar(.5);lengthBM.addVectors(V.M,V.B1).multiplyScalar(.5);lengthCN.addVectors(V.C,V.N).multiplyScalar(.5);
    cnUnit.subVectors(V.N,V.C).normalize();thetaOrth.set(0,cnUnit.y,cnUnit.z).normalize();for(let i=0;i<16;i++){const a=Math.PI/6*i/16,b=Math.PI/6*(i+1)/16;arcA.copy(V.C).addScaledVector(thetaOrth,.28*Math.sin(a));arcA.x+=.28*Math.cos(a);arcB.copy(V.C).addScaledVector(thetaOrth,.28*Math.sin(b));arcB.x+=.28*Math.cos(b);positionTube(thetaPieces[i],arcA,arcB,.006);}thetaPosition.copy(V.C).addScaledVector(thetaOrth,.48*Math.sin(Math.PI/12));thetaPosition.x+=.48*Math.cos(Math.PI/12);
    for(let i=0;i<24;i++){const a=Math.PI*state.t*i/24,b=Math.PI*state.t*(i+1)/24;arcA.set(V.M.x,V.M.y+.33*Math.sin(a),V.M.z+.33*Math.cos(a));arcB.set(V.M.x,V.M.y+.33*Math.sin(b),V.M.z+.33*Math.cos(b));positionTube(phiPieces[i],arcA,arcB,.006);}phiPosition.set(V.M.x,V.M.y+.52*Math.sin(Math.PI*state.t/2),V.M.z+.52*Math.cos(Math.PI*state.t/2));
  }
  // Sole update entry: drag, native slider, shortcuts and animation all call here.
  function setT(value,fromPlayback=false){if(!Number.isFinite(value))return;if(!fromPlayback)pausePlayback();const before=nondegenerate(),oldMaximum=atMaximum();state.t=Math.max(0,Math.min(1,value));const angle=Math.PI*state.t;STANDARD.B1[1]=-Math.cos(angle);STANDARD.B1[2]=Math.sin(angle);for(let i=0;i<3;i++)STANDARD.N[i]=(STANDARD.B1[i]+STANDARD.D[i])/2;toRender(STANDARD.B1,V.B1);toRender(STANDARD.N,V.N);calculate();updateDynamic();syncReadings();updateSelectedP();if(before!==nondegenerate()||oldMaximum!==atMaximum())updateVisibility();invalidate();}
  const rayO=new THREE.Vector3(),rayD=new THREE.Vector3(),rayW=new THREE.Vector3(),rayScores=new Float64Array(129);
  function screenToT(px,py){
    rayO.copy(camera.position);rayD.set(px/dimensions.width*2-1,1-py/dimensions.height*2,.5).unproject(camera).sub(rayO).normalize();
    // Ray intersects B₁'s circle plane x=-√3/2; recover φ using atan2(z,-y).
    if(Math.abs(rayD.x)>1e-6){const distance=(-SQ3/2-rayO.x)/rayD.x;if(distance<=0)return null;const z=rayO.y+distance*rayD.y+.45,minusY=rayO.z+distance*rayD.z-.5;if(Math.hypot(z,minusY)<1e-9)return null;let a=Math.atan2(z,minusY);if(a< -Math.PI/2)a+=2*Math.PI;return a/Math.PI;}
    // Edge-on circle: choose a locally continuous minimum of distance to the world ray.
    const score=t=>{foldPoint(t,rayW);rayW.sub(rayO);const along=Math.max(0,rayW.dot(rayD));return rayW.addScaledVector(rayD,-along).lengthSq();};
    for(let i=0;i<=128;i++)rayScores[i]=score(i/128);
    let best=state.t,min=Infinity;
    for(let j=0;j<=128;j++){if(j>0&&rayScores[j]>rayScores[j-1]||j<128&&rayScores[j]>rayScores[j+1])continue;let lo=Math.max(0,(j-1)/128),hi=Math.min(1,(j+1)/128);for(let i=0;i<55;i++){const a=lo+(hi-lo)/3,b=hi-(hi-lo)/3;if(score(a)<score(b))hi=b;else lo=a;}const t=(lo+hi)/2,s=score(t);if(s<min-1e-10||Math.abs(s-min)<=1e-10&&Math.abs(t-state.t)<Math.abs(best-state.t)){min=s;best=t;}}
    return best;
  }
  let playLast=null,playDirection=1;
  function pausePlayback(){state.playing=false;playLast=null;$('play').textContent='▶ 播放翻折';$('play').setAttribute('aria-pressed','false');}
  function togglePlayback(){if(state.playing){pausePlayback();syncReadings();return;}cancelGesture();state.playing=true;playLast=null;playDirection=state.t>=1?-1:1;$('play').textContent='Ⅱ 暂停翻折';$('play').setAttribute('aria-pressed','true');syncReadings();invalidate();}
  function advancePlayback(now){if(!state.playing)return;if(playLast===null){playLast=now;return;}const elapsed=Math.min(.1,(now-playLast)/1000);playLast=now;let next=state.t+playDirection*elapsed*state.speed/180;if(next>=1){next=2-next;playDirection=-1;}if(next<=0){next=-next;playDirection=1;}setT(next,true);}
  let focusedProof=0;
  function focusProof(index){focusedProof=Math.max(0,Math.min(3,index));tabSelect('lesson');if(compact())setDrawer(true);const card=$('proof-'+focusedProof);for(const el of document.querySelectorAll('[data-lesson]'))el.classList.toggle('proof-focus',el===card);card.scrollIntoView({behavior:reducedQuery.matches?'auto':'smooth',block:'start'});}
  const checks={cSolid:'solid',cOriginal:'original',cPlane1:'plane1',cPlane2:'plane2',cLineAngle:'lineAngle',cVolume:'volume',cAngles:'angles',cNTrack:'nTrack',cSphere:'sphere',cAxes:'axes',cLabels:'labels',cLengths:'lengths'};
  function synchronizeChecks(){for(const [id,key]of Object.entries(checks))$(id).checked=state[key];}
