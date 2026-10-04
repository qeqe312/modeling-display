(function () {
  'use strict';
  // Fixed model; shared input, camera, labels and drawer engine follows in engine.js.
  const $ = id => document.getElementById(id);
  const compactQuery = matchMedia('(max-width:1100px), (pointer:coarse)');
  const coarseQuery = matchMedia('(pointer:coarse)');
  const reducedQuery = matchMedia('(prefers-reduced-motion:reduce)');
  function fail(message) { $('error').hidden = false; $('error').textContent = message; }
  if (!window.THREE) { fail('三维库未能加载。请使用已内嵌依赖的离线单文件成品。'); return; }

  // 【A】Normalized teaching coordinates. a=1; rendering changes basis and scale only.
  const A_EDGE=1, SCALE=6, h=A_EDGE*Math.sqrt(6)/3, r=h/4, b=A_EDGE*Math.sqrt(3)/6;
  const STANDARD={A:[0,0,h],B:[-A_EDGE/2,-b,0],C:[A_EDGE/2,-b,0],D:[0,2*b,0],O:[0,0,r],F:[0,0,0]};
  const R=SCALE*Math.sqrt(6)/4, innerRadius=R/3;
  const MIN_DISTANCE=R*1.35, MAX_DISTANCE=R*20;
  const state={step:3,solid:true,sphere:true,inner:true,opposite:true,guide:true,angles:true,axes:false,labels:true,lengths:true,font:22,opacity:.08,quality:'auto'};
  const COLORS={blue:0x6BA8E8,orange:0xFF7A45,violet:0xA692E8,edge:0xB9C9DD,mute:0x73849A};
  const canvas=$('cv'),stage=$('stage');
  let renderer;
  try {renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'low-power'});}
  catch(error){fail('浏览器无法启动 WebGL。请在支持硬件加速的浏览器中打开本页面。');return;}
  renderer.setClearColor(0x131A22,0);
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,1,.1,200);
  const cam={azim:-.45,elev:.30,dist:16},target=new THREE.Vector3();
  let dimensions={width:1,height:1,left:0,top:0,bottom:195};
  let fitDistance=16,frame=0,tween=null,contextLost=false,metricsDirty=true,renderCount=0;
  const statistics={intervals:[],durations:[],geometries:0};

  // 【B】All geometry/materials are constructed once and reused.
  // Teaching origin is F, z follows FA; rendering remains centered on sphere center O.
  function renderVector(p){return new THREE.Vector3(SCALE*p[0],SCALE*(p[2]-r),-SCALE*p[1]);}
  const V={};
  for(const [key,p] of Object.entries(STANDARD))V[key]=renderVector(p);
  const groups={};
  for(const key of ['faces','edges','sphere','inner','opposite','guide','angles','axes','vertices']){groups[key]=new THREE.Group();scene.add(groups[key]);}
  function material(color,opacity=1){return new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,side:THREE.DoubleSide,depthWrite:opacity===1});}
  const lineMaterials={};
  function tube(a,b,color,r=.016,opacity=1){const key=color+':'+opacity;if(!lineMaterials[key])lineMaterials[key]=material(color,opacity);return new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(a,b),1,r,6,false),lineMaterials[key]);}
  function triangle(keys,color,opacity){const geometry=new THREE.BufferGeometry().setFromPoints(keys.map(k=>V[k]));geometry.setIndex([0,1,2]);return new THREE.Mesh(geometry,material(color,opacity));}
  function dashed(a,b,color,opacity=.7){const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([a,b]),new THREE.LineDashedMaterial({color,transparent:true,opacity,dashSize:.13,gapSize:.10,depthWrite:false}));line.computeLineDistances();return line;}
  function rightAngle(center,a,b,color,size=.28){const u=new THREE.Vector3().subVectors(a,center).normalize().multiplyScalar(size),v=new THREE.Vector3().subVectors(b,center).normalize().multiplyScalar(size);const p=center.clone().add(u),Q=p.clone().add(v),r=center.clone().add(v),g=new THREE.Group();g.add(tube(p,Q,color,.022),tube(Q,r,color,.022));return g;}
  for(const face of [['B','C','D'],['A','C','D'],['A','B','D'],['A','B','C']])groups.faces.add(triangle(face,COLORS.blue,.075));
  const EDGES=[['A','B'],['A','C'],['A','D'],['B','C'],['B','D'],['C','D']];
  for(const [a,b] of EDGES)groups.edges.add(tube(V[a],V[b],COLORS.edge,.018,.85));
  groups.opposite.add(tube(V.A,V.B,COLORS.orange,.038),tube(V.C,V.D,COLORS.violet,.038));

  function sphereCircle(radius,axis,color,opacity){const points=[];for(let i=0;i<128;i++){const a=i/128*Math.PI*2,c=radius*Math.cos(a),s=radius*Math.sin(a);points.push(axis==='xy'?new THREE.Vector3(c,s,0):axis==='yz'?new THREE.Vector3(0,c,s):new THREE.Vector3(c,0,s));}return new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false}));}
  const sphereMaterial=new THREE.MeshBasicMaterial({color:COLORS.blue,transparent:true,opacity:state.opacity,side:THREE.FrontSide,depthWrite:false});
  const innerMaterial=new THREE.MeshBasicMaterial({color:COLORS.violet,transparent:true,opacity:state.opacity,side:THREE.FrontSide,depthWrite:false});
  const silhouettes=[];
  for(const [name,radius,mat,color] of [['sphere',R,sphereMaterial,COLORS.blue],['inner',innerRadius,innerMaterial,COLORS.violet]]){
    const mesh=new THREE.Mesh(new THREE.SphereGeometry(radius,48,32),mat);mesh.renderOrder=name==='sphere'?-2:-1;groups[name].add(mesh);
    for(const axis of ['xy','yz','xz'])groups[name].add(sphereCircle(radius,axis,color,.25));
    const outline=sphereCircle(radius,'xy',color,.7);groups[name].add(outline);silhouettes.push({outline,radius});
  }
  const contactGeometry=new THREE.SphereGeometry(.046,12,8),contactMaterial=material(COLORS.violet);
  for(const key of ['A','B','C','D']){const mesh=new THREE.Mesh(contactGeometry,contactMaterial);mesh.position.copy(V[key]).multiplyScalar(-1/3);groups.inner.add(mesh);}
  groups.guide.add(tube(V.O,V.A,COLORS.blue,.026),tube(V.O,V.F,COLORS.violet,.028));
  groups.guide.add(rightAngle(V.F,V.O,V.B,COLORS.violet,.23));
  // AB and CD are skew: only the translated directions through O intersect.
  const u=new THREE.Vector3().subVectors(V.B,V.A).normalize(),v=new THREE.Vector3().subVectors(V.D,V.C).normalize();
  for(const [dir,color] of [[u,COLORS.orange],[v,COLORS.violet]])groups.angles.add(dashed(dir.clone().multiplyScalar(-1.95),dir.clone().multiplyScalar(1.95),color,.88));
  groups.angles.add(rightAngle(V.O,u,v,COLORS.orange,.34));
  const axesLabels=[];
  for(const [label,dir] of [['x',new THREE.Vector3(1,0,0)],['y',new THREE.Vector3(0,0,-1)],['z',new THREE.Vector3(0,1,0)]]){groups.axes.add(new THREE.ArrowHelper(dir,V.F,R*.84,COLORS.blue,.20,.10));axesLabels.push({label,position:V.F.clone().addScaledVector(dir,R*.9)});}
  const pointGeometry=new THREE.SphereGeometry(.077,16,10),vertexMeshes={},selected=new Set();
  for(const key of Object.keys(V)){const mesh=new THREE.Mesh(pointGeometry,material(key==='O'||key==='F'?COLORS.violet:COLORS.edge));mesh.position.copy(V[key]);vertexMeshes[key]=mesh;groups.vertices.add(mesh);if(key==='O')mesh.scale.setScalar(1.28);}
  const haloGeometry=new THREE.SphereGeometry(.077,12,8),haloMaterial=material(COLORS.orange,.18),halos={};
  for(const key of Object.keys(V)){const mesh=new THREE.Mesh(haloGeometry,haloMaterial);mesh.position.copy(V[key]);mesh.scale.setScalar(2.8);mesh.visible=false;halos[key]=mesh;groups.vertices.add(mesh);}

  const labels=[],projection=new THREE.Vector3(),unitZ=new THREE.Vector3(0,0,1);
  function addLabel(key,text,position,color,kind,offset,when){const el=document.createElement('div');el.className='lab'+(color?' '+color:'')+(kind==='edge'?' edge-label':'');el.textContent=text;$('labels').appendChild(el);const item={key,el,position,kind,offset:offset||[0,0],when:when||(()=>true),width:0,height:0,x:0,y:0,hit:null,visible:false};labels.push(item);return item;}
  for(const key of ['A','B','C','D','O','F'])addLabel(key,key,V[key],key==='O'||key==='F'?'violet':'','vertex',null,()=>keyVisible(key));
  const midpoint=(a,b)=>new THREE.Vector3().addVectors(V[a],V[b]).multiplyScalar(.5);
  addLabel(null,'AB = a',midpoint('A','B'),'orange','edge',[0,-24]);
  addLabel(null,'CD = a',midpoint('C','D'),'violet','edge',[0,24]);
  addLabel(null,'AC = a',midpoint('A','C'),'','edge',[0,-24]);
  addLabel(null,'R',midpoint('O','A'),'','edge',[22,-14],()=>state.guide);
  addLabel(null,'r',midpoint('O','F'),'violet','edge',[-25,14],()=>state.guide);
  for(const entry of axesLabels)addLabel(null,entry.label,entry.position,'','axis',[8,0],()=>state.axes);
  function keyVisible(key){return key==='O'?state.guide:key==='F'?(state.guide||state.axes):true;}
  function measureLabels(){for(const item of labels)if(item.visible){item.width=item.el.offsetWidth;item.height=item.el.offsetHeight;}metricsDirty=false;}
  function updateVisibility(){for(const key of ['sphere','inner','opposite','guide','angles','axes'])groups[key].visible=state[key];groups.faces.visible=state.solid;for(const key of Object.keys(V)){vertexMeshes[key].visible=keyVisible(key);halos[key].visible=selected.has(key)&&keyVisible(key);}for(const item of labels){item.visible=item.when()&&(item.kind==='vertex'||item.kind==='axis'?state.labels:state.lengths);item.el.hidden=!item.visible;item.hit=null;}metricsDirty=true;invalidate();}
