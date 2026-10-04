(function () {
  'use strict';
  // Adapted from assets/template.html: spherical camera, Pointer Events,
  // screen-space vertex picking, DOM labels. Geometry is static and cached.
  const $ = id => document.getElementById(id);
  const compactQuery = matchMedia('(max-width:1100px), (pointer:coarse)');
  const coarseQuery = matchMedia('(pointer:coarse)');
  const reducedQuery = matchMedia('(prefers-reduced-motion:reduce)');
  function fail(message) { $('error').hidden = false; $('error').textContent = message; }
  if (!window.THREE) { fail('三维库未能加载。请打开单文件版，或把 three.min.js 与本页面放在同一文件夹。'); return; }

  // 【A】Problem and independently derived values.
  const R = Math.sqrt(50) / 2;
  const STANDARD = { B:[0,0,0], A:[3,0,0], C:[0,4,0], P:[3,0,5], O:[1.5,2,2.5], M:[1.5,2,0] };
  const LESSONS = [
    { title:'先看结构，再找直径', body:'蓝色是底面，橙色是垂直于底面的 PA。', label:'题目条件', rows:[['PA','5'],['AB','3'],['BC','4']] },
    { title:'两个直角，共用斜边 PC', body:'∠PAC＝∠PBC＝90°；PC＝√(5²＋5²)＝5√2。', label:'找到直径', rows:[['AC','5'],['PA','5'],['PC','5√2']] },
    { title:'PC 的中点，就是球心 O', body:'OA＝OB＝OC＝OP＝R。四个顶点均在同一球面上。', label:'验证外接球', rows:[['直径 PC','5√2'],['半径 R','5√2 / 2'],['R 近似值','3.536']] },
    { title:'球的表面积 S＝50π', body:'S＝4πR²＝π·PC²＝50π，选择 B。', label:'面积答案 · B', rows:[['R²','25 / 2'],['S＝4πR²','50π'],['面积近似值','157.080']] }
  ];
  const state = { step:3, solid:true, sphere:true, diameter:true, guide:true, angles:true, axes:false, labels:true, lengths:true, font:22, opacity:.08, quality:'auto' };
  const COLORS = { blue:0x6BA8E8, orange:0xFF7A45, violet:0xA692E8, edge:0xB9C9DD, mute:0x73849A };
  const canvas = $('cv'), stage = $('stage');
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true, powerPreference:'low-power' }); }
  catch (error) { fail('浏览器无法启动 WebGL。请在支持硬件加速的浏览器中打开本页面。'); return; }
  renderer.setClearColor(0x131A22, 0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, .1, 200);
  const cam = { azim:-.66, elev:.32, dist:16 };
  const target = new THREE.Vector3();
  let dimensions = { width:1, height:1, left:0, top:0, bottom:195 };
  let fitDistance = 16, frame = 0, tween = null, contextLost = false;
  let metricsDirty = true, renderCount = 0;
  const statistics = { intervals:[], durations:[], geometries:0 };

  // 【B】Use conventional teaching coordinates; only the rendering basis is rotated.
  const V = {};
  for (const [key,p] of Object.entries(STANDARD)) V[key] = new THREE.Vector3(p[0]-1.5, p[2]-2.5, 2-p[1]);
  const groups = {};
  for (const key of ['faces','edges','sphere','diameter','guide','angles','axes','vertices']) { groups[key] = new THREE.Group(); scene.add(groups[key]); }
  function material(color, opacity=1) { return new THREE.MeshBasicMaterial({ color, transparent:opacity<1, opacity, side:THREE.DoubleSide, depthWrite:opacity===1 }); }
  const lineMaterials = {};
  function tube(a,b,color,r=.016,opacity=1) {
    const key = color+':'+opacity;
    if (!lineMaterials[key]) lineMaterials[key] = material(color,opacity);
    return new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(a,b),1,r,6,false),lineMaterials[key]);
  }
  function triangle(keys,color,opacity) {
    const geometry = new THREE.BufferGeometry().setFromPoints(keys.map(k=>V[k])); geometry.setIndex([0,1,2]);
    return new THREE.Mesh(geometry,material(color,opacity));
  }
  function dashed(a,b,color,opacity=.7) {
    const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([a,b]),new THREE.LineDashedMaterial({color,transparent:true,opacity,dashSize:.13,gapSize:.11,depthWrite:false}));
    line.computeLineDistances(); return line;
  }
  function rightAngle(center,a,b,color,size=.38) {
    const u = new THREE.Vector3().subVectors(a,center).normalize().multiplyScalar(size);
    const v = new THREE.Vector3().subVectors(b,center).normalize().multiplyScalar(size);
    const p=center.clone().add(u), q=p.clone().add(v), r=center.clone().add(v);
    const g=new THREE.Group(); g.add(tube(p,q,color,.021),tube(q,r,color,.021)); return g;
  }
  const baseFace = triangle(['A','B','C'],COLORS.blue,.19);
  const pacFace = triangle(['P','A','C'],COLORS.violet,.12);
  const pbcFace = triangle(['P','B','C'],COLORS.blue,.07);
  groups.faces.add(baseFace,pacFace,pbcFace);
  for(const [a,b] of [['A','B'],['B','C'],['A','C']]) groups.edges.add(tube(V[a],V[b],COLORS.blue,.020));
  groups.edges.add(tube(V.P,V.A,COLORS.orange,.028));
  const pcEdge=tube(V.P,V.C,COLORS.edge,.014,.6), pbEdge=tube(V.P,V.B,COLORS.edge,.014,.55);
  groups.edges.add(pcEdge,pbEdge);
  groups.diameter.add(tube(V.P,V.C,COLORS.orange,.034));
  const sphereMaterial=new THREE.MeshBasicMaterial({color:COLORS.blue,transparent:true,opacity:state.opacity,side:THREE.FrontSide,depthWrite:false});
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(R,48,32),sphereMaterial);
  sphere.renderOrder=-2; groups.sphere.add(sphere);
  function sphereCircle(axis,color,opacity) {
    const points=[];
    for(let i=0;i<128;i++){ const a=i/128*Math.PI*2,c=R*Math.cos(a),s=R*Math.sin(a); points.push(axis==='xy'?new THREE.Vector3(c,s,0):axis==='yz'?new THREE.Vector3(0,c,s):new THREE.Vector3(c,0,s)); }
    return new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false}));
  }
  groups.sphere.add(sphereCircle('xy',COLORS.blue,.21),sphereCircle('yz',COLORS.blue,.21),sphereCircle('xz',COLORS.blue,.28));
  const silhouette=sphereCircle('xy',COLORS.edge,.48); groups.sphere.add(silhouette);
  const radiusLines=[];
  for(const key of ['A','B','P','C']) { const line=key==='A'?tube(V.O,V[key],COLORS.violet,.025):dashed(V.O,V[key],COLORS.violet,.55); radiusLines.push(line); groups.guide.add(line); }
  groups.guide.add(dashed(V.O,V.M,COLORS.violet,.62));
  groups.guide.add(rightAngle(V.M,V.O,V.A,COLORS.violet,.25));
  const angleB=rightAngle(V.B,V.A,V.C,COLORS.blue);
  const angleAInitial=rightAngle(V.A,V.P,V.B,COLORS.orange);
  const angleAProof=rightAngle(V.A,V.P,V.C,COLORS.orange);
  const angleBProof=rightAngle(V.B,V.P,V.C,COLORS.violet);
  groups.angles.add(angleB,angleAInitial,angleAProof,angleBProof);
  const axesLabels=[];
  for(const [label,dir] of [['x',new THREE.Vector3(1,0,0)],['y',new THREE.Vector3(0,0,-1)],['z',new THREE.Vector3(0,1,0)]]) {
    const end=V.B.clone().addScaledVector(dir,6.7);
    const arrow=new THREE.ArrowHelper(dir,V.B,6.5,COLORS.blue,.23,.11); groups.axes.add(arrow); axesLabels.push({label,position:end});
  }
  const pointGeometry=new THREE.SphereGeometry(.079,16,10), vertexMeshes={};
  for(const key of Object.keys(V)) {
    const mesh=new THREE.Mesh(pointGeometry,material(key==='P'?COLORS.orange:(key==='O'||key==='M')?COLORS.violet:COLORS.edge));
    mesh.position.copy(V[key]); vertexMeshes[key]=mesh; groups.vertices.add(mesh);
    if(key==='O') mesh.scale.setScalar(1.28);
  }
  const selected=new Set();
  const haloGeometry=new THREE.SphereGeometry(.079,12,8), haloMaterial=material(COLORS.orange,.18), halos={};
  for(const key of Object.keys(V)) { const mesh=new THREE.Mesh(haloGeometry,haloMaterial);mesh.position.copy(V[key]);mesh.scale.setScalar(2.8);mesh.visible=false;halos[key]=mesh;groups.vertices.add(mesh); }

  // Labels use cached measurements; no offsetWidth / layout reads during a drag frame.
  const labels=[], projection=new THREE.Vector3(), unitZ=new THREE.Vector3(0,0,1);
  function addLabel(key,text,position,color,kind,offset,when) {
    const el=document.createElement('div'); el.className='lab'+(color?' '+color:'')+(kind==='edge'?' edge-label':'');el.textContent=text;$('labels').appendChild(el);
    const item={key,el,position,kind,offset:offset||[0,0],when:when||(()=>true),width:0,height:0,x:0,y:0,hit:null,visible:false}; labels.push(item);return item;
  }
  for(const key of ['A','B','C','P','O','M']) addLabel(key,key,V[key],key==='P'?'orange':(key==='O'||key==='M')?'violet':'','vertex',null,()=>key==='O'||key==='M'?state.guide:true);
  const midpoint=(a,b)=>new THREE.Vector3().addVectors(V[a],V[b]).multiplyScalar(.5);
  addLabel(null,'AB = 3',midpoint('A','B'),'','edge',[0,22]);
  addLabel(null,'BC = 4',midpoint('B','C'),'','edge',[-12,16]);
  addLabel(null,'PA = 5',midpoint('P','A'),'orange','edge',[37,0]);
  addLabel(null,'AC = 5',midpoint('A','C'),'','edge',[0,22],()=>state.step>=1);
  addLabel(null,'PC = 5√2',midpoint('P','C').lerp(V.C,.3),'orange','edge',[-39,-8],()=>state.diameter);
  addLabel(null,'R',midpoint('O','A'),'violet','edge',[19,0],()=>state.guide);
  for(const entry of axesLabels) addLabel(null,entry.label,entry.position,'','axis',[8,0],()=>state.axes);
  function keyVisible(key){return (key!=='O'&&key!=='M')||state.guide;}
  function measureLabels(){ for(const item of labels){if(item.visible){item.width=item.el.offsetWidth;item.height=item.el.offsetHeight;}}metricsDirty=false; }
  function updateVisibility(){
    groups.faces.visible=state.solid; pacFace.visible=state.step>=1;pbcFace.visible=state.step>=1;
    groups.sphere.visible=state.sphere;groups.diameter.visible=state.diameter;pcEdge.visible=!state.diameter;
    groups.guide.visible=state.guide;groups.angles.visible=state.angles;groups.axes.visible=state.axes;
    angleAInitial.visible=state.step===0;angleAProof.visible=state.step>=1;angleBProof.visible=state.step>=1;
    for(const key of Object.keys(V)){vertexMeshes[key].visible=keyVisible(key);halos[key].visible=selected.has(key)&&keyVisible(key);}
    for(const item of labels){item.visible=item.when()&&(item.kind==='vertex'||item.kind==='axis'?state.labels:state.lengths);item.el.hidden=!item.visible;item.hit=null;}
    metricsDirty=true;invalidate();
  }
  function syncLabels(){
    if(metricsDirty) measureLabels();
    const w=dimensions.width,h=dimensions.height, placed=[];
    for(const item of labels){
      item.hit=null;if(!item.visible)continue;
      projection.copy(item.position).project(camera);
      if(projection.z<-1||projection.z>1){item.el.hidden=true;continue;}item.el.hidden=false;
      const px=(projection.x*.5+.5)*w,py=(-projection.y*.5+.5)*h;
      let x=px+item.offset[0],y=py+item.offset[1];
      if(item.kind==='vertex'){
        let dx=px-w/2,dy=py-(h/2-camera.view.offsetY),length=Math.hypot(dx,dy);
        if(length<18){dx=-1;dy=-.75;length=1.25;}
        x+=dx/length*(state.font*.9+12);y+=dy/length*(state.font*.9+12);
      }
      x=Math.max(item.width/2+8,Math.min(w-item.width/2-8,x));y=Math.max(item.height/2+8,Math.min(h-dimensions.bottom-item.height/2-10,y));
      placed.push({item,x,y,px,py});
    }
    // Rectangle avoidance also handles identical projected points in front/top views.
    for(let iteration=0;iteration<7;iteration++)for(let i=0;i<placed.length;i++)for(let j=i+1;j<placed.length;j++){
      const a=placed[i],b=placed[j],dx=b.x-a.x,dy=b.y-a.y;
      const overlapX=(a.item.width+b.item.width)/2+6-Math.abs(dx),overlapY=(a.item.height+b.item.height)/2+6-Math.abs(dy);
      if(overlapX>0&&overlapY>0){
        if(overlapX<overlapY){const shift=(overlapX+.2)*.5*(dx<0?-1:1);a.x-=shift;b.x+=shift;}
        else{const shift=(overlapY+.2)*.5*(dy<0?-1:1);a.y-=shift;b.y+=shift;}
      }
    }
    for(const o of placed){
      const item=o.item;xClamp(o);
      item.x=o.px;item.y=o.py;item.el.style.transform='translate3d('+o.x.toFixed(2)+'px,'+o.y.toFixed(2)+'px,0) translate(-50%,-50%)';
      item.hit={x0:o.x-item.width/2-3,x1:o.x+item.width/2+3,y0:o.y-item.height/2-3,y1:o.y+item.height/2+3};
    }
    function xClamp(o){o.x=Math.max(o.item.width/2+6,Math.min(w-o.item.width/2-6,o.x));o.y=Math.max(o.item.height/2+6,Math.min(h-dimensions.bottom-o.item.height/2-10,o.y));}
  }
  function pickVertex(px,py,type){
    const visible=labels.filter(item=>item.kind==='vertex'&&keyVisible(item.key));
    // Prioritize the label itself, as its visual position is deliberately offset.
    for(const item of visible){const r=item.hit;if(r&&px>=r.x0&&px<=r.x1&&py>=r.y0&&py<=r.y1)return item.key;}
    let best=null,distance=type==='touch'||type==='pen'?40:22;
    for(const key of Object.keys(V)){if(!keyVisible(key))continue;projection.copy(V[key]).project(camera);if(projection.z>1||projection.z<-1)continue;
      const d=Math.hypot(px-(projection.x*.5+.5)*dimensions.width,py-(-projection.y*.5+.5)*dimensions.height);
      if(d<distance){distance=d;best=key;}}
    return best;
  }
  function refreshSelection(){
    const list=$('selList'),box=$('pickBox');list.textContent=selected.size?'':'点模型中的顶点或字母';box.textContent='';
    for(const key of Object.keys(V)){
      const chosen=selected.has(key);vertexMeshes[key].scale.setScalar(chosen?1.85:key==='O'?1.28:1);vertexMeshes[key].material.color.setHex(chosen?COLORS.orange:key==='P'?COLORS.orange:(key==='O'||key==='M')?COLORS.violet:COLORS.edge);halos[key].visible=chosen&&keyVisible(key);
    }
    for(const item of labels)item.el.classList.toggle('sel',item.kind==='vertex'&&selected.has(item.key));
    for(const key of selected){const chip=document.createElement('span');chip.className='chip';chip.textContent=key;list.appendChild(chip);const row=document.createElement('div');row.className='pr';const name=document.createElement('span'),coord=document.createElement('span');name.textContent=key;coord.textContent='('+STANDARD[key].join(', ')+')';row.append(name,coord);box.append(row);}
    metricsDirty=true;invalidate();
  }
  function toggleSelection(key){if(!key)return;if(selected.has(key))selected.delete(key);else selected.add(key);refreshSelection();}

  // 【C】The problem has fixed vertices. A lesson changes visibility, never geometry.
  function showFullSolution(){
    state.step=3;state.sphere=true;state.diameter=true;state.guide=true;
    $('readout-title').textContent='外接球 · 完整结果';$('readout').classList.add('answer-readout');
    const rows=[['直径 PC','5√2'],['半径 R','5√2 / 2'],['球面积 S','50π']];
    for(let i=0;i<3;i++){$('rKey'+(i+1)).textContent=rows[i][0];$('rValue'+(i+1)).textContent=rows[i][1];}
    for(const el of document.querySelectorAll('[data-lesson]'))el.hidden=false;
    $('options').classList.add('reveal');synchronizeChecks();updateVisibility();
  }
  let focusedProof=0;
  function focusProof(index){
    focusedProof=Math.max(0,Math.min(3,index));tabSelect('lesson');
    if(compact())setDrawer(true);
    const card=document.getElementById('proof-'+focusedProof);
    for(const el of document.querySelectorAll('[data-lesson]'))el.classList.toggle('proof-focus',el===card);
    // Read the proof without changing manually configured model layers.
    card.scrollIntoView({behavior:reducedQuery.matches?'auto':'smooth',block:'start'});
  }
  const checks={cSolid:'solid',cSphere:'sphere',cDiameter:'diameter',cGuide:'guide',cAngles:'angles',cAxes:'axes',cLabels:'labels',cLengths:'lengths'};
  function synchronizeChecks(){for(const [id,key] of Object.entries(checks))$(id).checked=state[key];}

  // 【D】Demand rendering. Input events are coalesced into one animation frame.
  function invalidate(){if(!frame&&!contextLost&&!document.hidden)frame=requestAnimationFrame(render);}
  function applyCamera(){cam.elev=Math.max(-1.49,Math.min(1.49,cam.elev));const ce=Math.cos(cam.elev);camera.position.set(target.x+cam.dist*ce*Math.sin(cam.azim),target.y+cam.dist*Math.sin(cam.elev),target.z+cam.dist*ce*Math.cos(cam.azim));camera.lookAt(target);camera.updateMatrixWorld();invalidate();}
  function render(now){
    frame=0;if(contextLost||document.hidden)return;const start=performance.now();
    if(tween){const t=Math.min(1,(now-tween.start)/tween.duration),ease=1-Math.pow(1-t,3);cam.azim=tween.from.azim+(tween.to.azim-tween.from.azim)*ease;cam.elev=tween.from.elev+(tween.to.elev-tween.from.elev)*ease;cam.dist=tween.from.dist+(tween.to.dist-tween.from.dist)*ease;target.lerpVectors(tween.origin,tween.destination,ease);applyCamera();if(t===1)tween=null;}
    const sphereDistance=camera.position.length();
    silhouette.position.copy(camera.position).multiplyScalar(R*R/(sphereDistance*sphereDistance));
    silhouette.scale.setScalar(Math.sqrt(Math.max(0,1-R*R/(sphereDistance*sphereDistance))));
    projection.copy(camera.position).normalize();silhouette.quaternion.setFromUnitVectors(unitZ,projection);
    renderer.render(scene,camera);syncLabels();renderCount++;
    if(window.location.hash==='#geo-debug'){statistics.durations.push(performance.now()-start);if(statistics.durations.length>300)statistics.durations.shift();statistics.geometries=renderer.info.memory.geometries;}
    if(tween)invalidate();
  }
  function pixelRatio(){const device=window.devicePixelRatio||1,budget=state.quality==='sharp'?3500000:2000000;const maximum=state.quality==='save'?1:state.quality==='sharp'?2:coarseQuery.matches?1.35:1.65;return Math.min(device,maximum,Math.sqrt(budget/Math.max(1,dimensions.width*dimensions.height)));}
  function resize(){
    const rect=stage.getBoundingClientRect();if(rect.width<2||rect.height<2)return;
    const oldFit=fitDistance;dimensions={width:rect.width,height:rect.height,left:rect.left,top:rect.top,bottom:document.querySelector('.stage-bottom').getBoundingClientRect().height};
    renderer.setPixelRatio(pixelRatio());renderer.setSize(rect.width,rect.height,false);camera.aspect=rect.width/rect.height;
    const top=dimensions.width<600?150:68,bottom=dimensions.bottom+44,usableHeight=Math.max(130,rect.height-top-bottom),usableWidth=Math.max(200,rect.width-84);
    camera.setViewOffset(rect.width,rect.height,0,(bottom-top)/2,rect.width,rect.height);
    const vhalf=THREE.MathUtils.degToRad(camera.fov/2),hhalf=Math.atan(Math.tan(vhalf)*camera.aspect);
    fitDistance=Math.max(R/Math.sin(vhalf)*rect.height/usableHeight,R/Math.sin(hhalf)*rect.width/usableWidth)*1.05;
    if(!Number.isFinite(fitDistance))fitDistance=16;
    cam.dist=Math.max(7,Math.min(70,cam.dist*fitDistance/oldFit));tween=null;camera.updateProjectionMatrix();applyCamera();metricsDirty=true;
  }
  function setView(view,fitOnly=false){
    cancelGesture();const views={spatial:{azim:-.66,elev:.32},front:{azim:0,elev:.06},top:{azim:.03,elev:1.48}};
    const destination=fitOnly?{azim:cam.azim,elev:cam.elev}:views[view];
    if(reducedQuery.matches){Object.assign(cam,destination,{dist:fitDistance});target.set(0,0,0);applyCamera();}
    else{tween={start:performance.now(),duration:300,from:{...cam},to:{...destination,dist:fitDistance},origin:target.clone(),destination:new THREE.Vector3()};invalidate();}
    for(const button of document.querySelectorAll('[data-view]')){const active=!fitOnly&&button.dataset.view===view;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}
  }
  function manualCamera(){tween=null;for(const button of document.querySelectorAll('[data-view]')){button.classList.remove('active');button.setAttribute('aria-pressed','false');}}

  // Trusted browser Pointer Events. The down hit is reused at release.
  const pointers=new Map();let gesture=null,tap=null,pinchStart=null,camStartDist=0;
  const targetStart=new THREE.Vector3(),right=new THREE.Vector3(),up=new THREE.Vector3();
  function pinchGeometry(){const p=[...pointers.values()];return p.length>=2?{distance:Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y),x:(p[0].x+p[1].x)/2,y:(p[0].y+p[1].y)/2}:null;}
  function pan(dx,dy,origin){right.setFromMatrixColumn(camera.matrixWorld,0);up.setFromMatrixColumn(camera.matrixWorld,1);const k=2*cam.dist*Math.tan(THREE.MathUtils.degToRad(camera.fov/2))/dimensions.height;if(origin)target.copy(origin);target.addScaledVector(right,-dx*k);target.addScaledVector(up,dy*k);}
  function cancelGesture(){for(const id of pointers.keys()){try{canvas.releasePointerCapture(id);}catch(error){}}pointers.clear();gesture=null;tap=null;pinchStart=null;canvas.style.cursor='grab';}
  canvas.addEventListener('contextmenu',e=>e.preventDefault());
  canvas.addEventListener('pointerdown',e=>{
    if(e.button!==0&&e.button!==2)return;manualCamera();const rect=canvas.getBoundingClientRect();dimensions.left=rect.left;dimensions.top=rect.top;
    try{canvas.setPointerCapture(e.pointerId);}catch(error){}pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(pointers.size===1){gesture=e.button===2||e.shiftKey?'pan':'rotate';tap={x:e.clientX,y:e.clientY,time:performance.now(),moved:false,key:pickVertex(e.clientX-rect.left,e.clientY-rect.top,e.pointerType)};}
    else if(pointers.size===2){gesture='pinch';tap=null;pinchStart=pinchGeometry();camStartDist=cam.dist;targetStart.copy(target);}
  });
  canvas.addEventListener('pointermove',e=>{
    if(!pointers.has(e.pointerId))return;const before=pointers.get(e.pointerId),dx=e.clientX-before.x,dy=e.clientY-before.y;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(gesture==='pinch'&&pointers.size>=2){const p=pinchGeometry();if(p&&pinchStart){cam.dist=Math.max(7,Math.min(70,camStartDist*pinchStart.distance/Math.max(p.distance,2)));pan(p.x-pinchStart.x,p.y-pinchStart.y,targetStart);applyCamera();}return;}
    if(tap&&!tap.moved){if(Math.hypot(e.clientX-tap.x,e.clientY-tap.y)<=9)return;tap.moved=true;if(gesture==='rotate'){cam.azim-=(e.clientX-tap.x)*.006;cam.elev+=(e.clientY-tap.y)*.006;}else pan(e.clientX-tap.x,e.clientY-tap.y);}
    else if(gesture==='rotate'){cam.azim-=dx*.006;cam.elev+=dy*.006;}else if(gesture==='pan')pan(dx,dy);
    canvas.style.cursor='grabbing';applyCamera();
  });
  function endPointer(e){
    if(!pointers.has(e.pointerId))return;const single=pointers.size===1;
    if(e.type==='pointerup'&&single&&gesture==='rotate'&&tap&&!tap.moved&&performance.now()-tap.time<700)toggleSelection(tap.key);
    pointers.delete(e.pointerId);try{canvas.releasePointerCapture(e.pointerId);}catch(error){}
    if(!pointers.size){gesture=null;tap=null;pinchStart=null;canvas.style.cursor='grab';}
    else if(pointers.size===1){const rest=pointers.values().next().value;gesture='rotate';tap={x:rest.x,y:rest.y,time:performance.now(),moved:true,key:null};}
  }
  canvas.addEventListener('pointerup',endPointer);canvas.addEventListener('pointercancel',endPointer);
  canvas.addEventListener('lostpointercapture',e=>{if(pointers.has(e.pointerId)){pointers.delete(e.pointerId);if(!pointers.size){gesture=null;tap=null;pinchStart=null;canvas.style.cursor='grab';}}});
  canvas.addEventListener('wheel',e=>{e.preventDefault();manualCamera();cam.dist=Math.max(7,Math.min(70,cam.dist*Math.exp(Math.max(-180,Math.min(180,e.deltaY))*.0013)));applyCamera();},{passive:false});
  canvas.addEventListener('touchmove',e=>{if(e.cancelable)e.preventDefault();},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();contextLost=true;cancelGesture();if(frame)cancelAnimationFrame(frame);frame=0;fail('图形显示已暂停，等待浏览器恢复。若未自动恢复，请重新打开页面。');});
  canvas.addEventListener('webglcontextrestored',()=>{contextLost=false;$('error').hidden=true;invalidate();});

  // Drawer focus, scroll, and orientation are independent of WebGL input.
  let panelReturnFocus=null;
  function compact(){return compactQuery.matches||document.body.classList.contains('focused');}
  function setDrawer(open){
    const active=open&&compact();if(active){panelReturnFocus=document.activeElement;cancelGesture();}
    $('panel').classList.toggle('open',active);document.body.classList.toggle('drawer-open',active);$('menu').setAttribute('aria-expanded',String(active));
    if(compact()){$('panel').inert=!active;if(active){$('panel').setAttribute('role','dialog');$('panel').setAttribute('aria-modal','true');$('close').focus();}else{$('panel').removeAttribute('role');$('panel').removeAttribute('aria-modal');if(panelReturnFocus&&panelReturnFocus.isConnected)panelReturnFocus.focus();}}
    else $('panel').inert=false;
  }
  function tabSelect(name){for(const id of ['lesson','settings']){const active=id===name;$('tab-'+id).setAttribute('aria-selected',String(active));$('tab-'+id).tabIndex=active?0:-1;$(id+'-panel').hidden=!active;}}
  $('menu').addEventListener('click',()=>setDrawer(!$('panel').classList.contains('open')));$('close').addEventListener('click',()=>setDrawer(false));$('scrim').addEventListener('click',()=>setDrawer(false));
  $('focus').addEventListener('click',()=>{setDrawer(false);const active=document.body.classList.toggle('focused');$('focus').setAttribute('aria-pressed',String(active));$('focus').textContent=active?'退出专注':'专注模式';$('panel').inert=compact();});
  for(const name of ['lesson','settings'])$('tab-'+name).addEventListener('click',()=>tabSelect(name));
  document.querySelector('.panel-tabs').addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const current=$('tab-lesson').getAttribute('aria-selected')==='true'?'lesson':'settings';const next=e.key==='Home'?'lesson':e.key==='End'?'settings':current==='lesson'?'settings':'lesson';tabSelect(next);$('tab-'+next).focus();}});
  for(const [id,key] of Object.entries(checks))$(id).addEventListener('change',()=>{state[key]=$(id).checked;updateVisibility();});
  $('sFont').addEventListener('input',()=>{state.font=Number($('sFont').value);document.documentElement.style.setProperty('--lab-size',state.font+'px');$('sFontval').textContent=state.font+' px';metricsDirty=true;invalidate();});
  $('sOpacity').addEventListener('input',()=>{state.opacity=Number($('sOpacity').value)/100;sphereMaterial.opacity=state.opacity;$('sOpacityval').textContent=Math.round(state.opacity*100)+'%';invalidate();});
  for(const el of document.querySelectorAll('[data-quality]'))el.addEventListener('click',()=>{state.quality=el.dataset.quality;for(const button of document.querySelectorAll('[data-quality]')){const active=button===el;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}renderer.setPixelRatio(pixelRatio());renderer.setSize(dimensions.width,dimensions.height,false);invalidate();});
  $('clear').addEventListener('click',()=>{selected.clear();refreshSelection();});
  $('stage-next').addEventListener('click',()=>focusProof(0));for(const button of document.querySelectorAll('[data-proof]'))button.addEventListener('click',()=>focusProof(Number(button.dataset.proof)));
  for(const button of document.querySelectorAll('[data-view]'))button.addEventListener('click',()=>setView(button.dataset.view));$('reset').addEventListener('click',()=>setView('spatial'));$('fit').addEventListener('click',()=>setView('spatial',true));
  window.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if($('panel').classList.contains('open'))setDrawer(false);else{selected.clear();refreshSelection();}return;}
    if(e.key==='Tab'&&document.body.classList.contains('drawer-open')){const items=[...$('panel').querySelectorAll('button,input,summary')].filter(el=>!el.disabled&&el.getClientRects().length);const first=items[0],last=items[items.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}return;}
    if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;
    if(e.defaultPrevented)return;if(e.key==='ArrowRight'){e.preventDefault();focusProof(focusedProof+1);}if(e.key==='ArrowLeft'){e.preventDefault();focusProof(focusedProof-1);}if(e.key==='0')setView('spatial');
  });
  function updateInputHint(){$('hint').textContent=coarseQuery.matches?'单指旋转 · 双指缩放 / 平移 · 轻点顶点多选':'拖动旋转 · 滚轮缩放 · 右键平移 · 点顶点多选';}
  const mediaListen=(query,fn)=>query.addEventListener?query.addEventListener('change',fn):query.addListener(fn);
  mediaListen(compactQuery,()=>{setDrawer(false);$('panel').inert=compact();resize();});mediaListen(coarseQuery,()=>{updateInputHint();resize();});
  mediaListen(matchMedia('(orientation:portrait)'),()=>{setDrawer(false);cancelGesture();resize();});
  window.addEventListener('orientationchange',()=>{setDrawer(false);cancelGesture();});window.addEventListener('blur',cancelGesture);
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelGesture();tween=null;if(frame)cancelAnimationFrame(frame);frame=0;}else invalidate();});
  const observer=new ResizeObserver(resize);observer.observe(stage);observer.observe(document.querySelector('.stage-bottom'));window.addEventListener('resize',resize);if(window.visualViewport)window.visualViewport.addEventListener('resize',resize);
  setDrawer(false);$('panel').inert=compact();showFullSolution();updateInputHint();resize();cam.dist=fitDistance;applyCamera();
  if(location.hash==='#geo-debug'){
    window.__GEO=V;
    window.__S={state,cam,camera,renderer,groups,target,selected,labels,statistics,showFullSolution,focusProof,setView,resize,applyCamera,refreshSelection,pickVertex,setDrawer,updateVisibility,get renderCount(){return renderCount;},get dimensions(){return dimensions;},get pointers(){return pointers.size;},get gesture(){return gesture;},get fitDistance(){return fitDistance;}};
  }
})();
