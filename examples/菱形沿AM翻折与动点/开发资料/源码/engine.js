  // 【D】Demand rendering. Input events are coalesced into one animation frame.
  function invalidate(){if(!frame&&!contextLost&&!document.hidden)frame=requestAnimationFrame(render);}
  function applyCamera(){cam.elev=Math.max(-1.49,Math.min(1.49,cam.elev));const ce=Math.cos(cam.elev);camera.position.set(target.x+cam.dist*ce*Math.sin(cam.azim),target.y+cam.dist*Math.sin(cam.elev),target.z+cam.dist*ce*Math.cos(cam.azim));camera.lookAt(target);camera.updateMatrixWorld();invalidate();}
  function render(now){
    frame=0;if(contextLost||document.hidden)return;const start=performance.now();advancePlayback(now);
    if(tween){const t=Math.min(1,(now-tween.start)/tween.duration),ease=1-Math.pow(1-t,3);cam.azim=tween.from.azim+(tween.to.azim-tween.from.azim)*ease;cam.elev=tween.from.elev+(tween.to.elev-tween.from.elev)*ease;cam.dist=tween.from.dist+(tween.to.dist-tween.from.dist)*ease;target.lerpVectors(tween.origin,tween.destination,ease);applyCamera();if(t===1)tween=null;}
    renderer.render(scene,camera);syncLabels();renderCount++;
    if(window.location.hash==='#geo-debug'){statistics.durations.push(performance.now()-start);if(statistics.durations.length>300)statistics.durations.shift();statistics.geometries=renderer.info.memory.geometries;}
    if(tween||state.playing)invalidate();
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
    if(!Number.isFinite(fitDistance))fitDistance=8;
    cam.dist=Math.max(3,Math.min(45,cam.dist*fitDistance/oldFit));tween=null;camera.updateProjectionMatrix();applyCamera();metricsDirty=true;
  }
  function setView(view,fitOnly=false){
    cancelGesture();const views={spatial:DEFAULT_VIEW,front:{azim:Math.PI/2,elev:.02},top:{azim:DEFAULT_VIEW.azim,elev:1.48}};
    const destination=fitOnly?{azim:cam.azim,elev:cam.elev}:views[view];
    if(reducedQuery.matches){Object.assign(cam,destination,{dist:fitDistance});target.set(0,0,0);applyCamera();}
    else{tween={start:performance.now(),duration:300,from:{...cam},to:{...destination,dist:fitDistance},origin:target.clone(),destination:new THREE.Vector3()};invalidate();}
    for(const button of document.querySelectorAll('[data-view]')){const active=!fitOnly&&button.dataset.view===view;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}
  }
  function manualCamera(){tween=null;for(const button of document.querySelectorAll('[data-view]')){button.classList.remove('active');button.setAttribute('aria-pressed','false');}}

  // Pointer capture preserves the down hit. A point gesture owns the camera lock.
  const pointers=new Map();let gesture=null,tap=null,pinchStart=null,camStartDist=0,pointPointer=null,dragOffset=0;
  const targetStart=new THREE.Vector3(),right=new THREE.Vector3(),up=new THREE.Vector3();
  function pinchGeometry(){const p=[...pointers.values()];return p.length>=2?{distance:Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y),x:(p[0].x+p[1].x)/2,y:(p[0].y+p[1].y)/2}:null;}
  function pan(dx,dy,origin){right.setFromMatrixColumn(camera.matrixWorld,0);up.setFromMatrixColumn(camera.matrixWorld,1);const k=2*cam.dist*Math.tan(THREE.MathUtils.degToRad(camera.fov/2))/dimensions.height;if(origin)target.copy(origin);target.addScaledVector(right,-dx*k);target.addScaledVector(up,dy*k);}
  function cancelGesture(){for(const id of pointers.keys()){try{canvas.releasePointerCapture(id);}catch(error){}}pointers.clear();gesture=null;tap=null;pinchStart=null;pointPointer=null;canvas.style.cursor='grab';stage.classList.remove('moving-point');}
  canvas.addEventListener('contextmenu',e=>e.preventDefault());
  canvas.addEventListener('pointerdown',e=>{
    if(e.button!==0&&e.button!==2)return;manualCamera();const rect=canvas.getBoundingClientRect();dimensions.left=rect.left;dimensions.top=rect.top;
    try{canvas.setPointerCapture(e.pointerId);}catch(error){}pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(pointers.size===1){const key=pickVertex(e.clientX-rect.left,e.clientY-rect.top,e.pointerType);gesture=e.button===2||e.shiftKey?'pan':key==='B1'?'point':'rotate';tap={x:e.clientX,y:e.clientY,time:performance.now(),moved:false,key};
      if(gesture==='point'){pausePlayback();syncReadings();pointPointer=e.pointerId;const raw=screenToT(e.clientX-rect.left,e.clientY-rect.top);dragOffset=raw===null?0:state.t-raw;stage.classList.add('moving-point');canvas.style.cursor='grabbing';}}
    else if(pointers.size===2&&gesture!=='point'&&gesture!=='blocked'){gesture='pinch';tap=null;pinchStart=pinchGeometry();camStartDist=cam.dist;targetStart.copy(target);}
  });
  canvas.addEventListener('pointermove',e=>{
    if(!pointers.has(e.pointerId))return;const before=pointers.get(e.pointerId),dx=e.clientX-before.x,dy=e.clientY-before.y;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(gesture==='blocked')return;
    if(gesture==='point'){
      if(e.pointerId!==pointPointer)return;if(tap&&!tap.moved){if(Math.hypot(e.clientX-tap.x,e.clientY-tap.y)<=9)return;tap.moved=true;}
      const raw=screenToT(e.clientX-dimensions.left,e.clientY-dimensions.top);if(raw!==null)setT(raw+dragOffset);return;
    }
    if(gesture==='pinch'&&pointers.size>=2){const p=pinchGeometry();if(p&&pinchStart){cam.dist=Math.max(3,Math.min(45,camStartDist*pinchStart.distance/Math.max(p.distance,2)));pan(p.x-pinchStart.x,p.y-pinchStart.y,targetStart);applyCamera();}return;}
    if(tap&&!tap.moved){if(Math.hypot(e.clientX-tap.x,e.clientY-tap.y)<=9)return;tap.moved=true;if(gesture==='rotate'){cam.azim-=(e.clientX-tap.x)*.006;cam.elev+=(e.clientY-tap.y)*.006;}else pan(e.clientX-tap.x,e.clientY-tap.y);}
    else if(gesture==='rotate'){cam.azim-=dx*.006;cam.elev+=dy*.006;}else if(gesture==='pan')pan(dx,dy);
    canvas.style.cursor='grabbing';applyCamera();
  });
  function endPointer(e){
    if(!pointers.has(e.pointerId))return;const single=pointers.size===1,wasPoint=gesture==='point';
    if(e.type==='pointerup'&&single&&(gesture==='rotate'||wasPoint)&&tap&&!tap.moved&&performance.now()-tap.time<700)toggleSelection(tap.key);
    pointers.delete(e.pointerId);try{canvas.releasePointerCapture(e.pointerId);}catch(error){}
    if(!pointers.size){gesture=null;tap=null;pinchStart=null;pointPointer=null;canvas.style.cursor='grab';stage.classList.remove('moving-point');}
    else if(wasPoint&&e.pointerId===pointPointer){gesture='blocked';tap=null;pointPointer=null;stage.classList.remove('moving-point');}
    else if(!wasPoint&&gesture!=='blocked'&&pointers.size===1){const rest=pointers.values().next().value;gesture='rotate';tap={x:rest.x,y:rest.y,time:performance.now(),moved:true,key:null};}
  }
  canvas.addEventListener('pointerup',endPointer);canvas.addEventListener('pointercancel',endPointer);
  canvas.addEventListener('lostpointercapture',e=>{if(pointers.has(e.pointerId)){pointers.delete(e.pointerId);if(pointPointer===e.pointerId){gesture='blocked';pointPointer=null;tap=null;stage.classList.remove('moving-point');}if(!pointers.size){gesture=null;tap=null;pinchStart=null;canvas.style.cursor='grab';}}});
  canvas.addEventListener('wheel',e=>{e.preventDefault();if(gesture==='point'||gesture==='blocked')return;manualCamera();cam.dist=Math.max(3,Math.min(45,cam.dist*Math.exp(Math.max(-180,Math.min(180,e.deltaY))*.0013)));applyCamera();},{passive:false});
  canvas.addEventListener('touchmove',e=>{if(e.cancelable)e.preventDefault();},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();contextLost=true;pausePlayback();cancelGesture();if(frame)cancelAnimationFrame(frame);frame=0;fail('图形显示已暂停，等待浏览器恢复。若未自动恢复，请重新打开页面。');});
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
  $('sOpacity').addEventListener('input',()=>{state.opacity=Number($('sOpacity').value)/100;for(const material of faceMaterials)material.opacity=state.opacity;$('sOpacityval').textContent=Math.round(state.opacity*100)+'%';invalidate();});
  for(const el of document.querySelectorAll('[data-quality]'))el.addEventListener('click',()=>{state.quality=el.dataset.quality;for(const button of document.querySelectorAll('[data-quality]')){const active=button===el;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}renderer.setPixelRatio(pixelRatio());renderer.setSize(dimensions.width,dimensions.height,false);invalidate();});
  $('play').addEventListener('click',togglePlayback);$('speed').addEventListener('change',()=>{state.speed=Number($('speed').value);});
  $('sT').addEventListener('input',()=>setT(Number($('sT').value)));
  for(const button of document.querySelectorAll('[data-t]'))button.addEventListener('click',()=>setT(Number(button.dataset.t)));
  $('clear').addEventListener('click',()=>{selected.clear();refreshSelection();});
  $('stage-next').addEventListener('click',()=>focusProof(0));for(const button of document.querySelectorAll('[data-proof]'))button.addEventListener('click',()=>focusProof(Number(button.dataset.proof)));
  for(const button of document.querySelectorAll('[data-view]'))button.addEventListener('click',()=>setView(button.dataset.view));$('reset').addEventListener('click',()=>setView('spatial'));$('fit').addEventListener('click',()=>setView('spatial',true));
  window.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if($('panel').classList.contains('open'))setDrawer(false);else{selected.clear();refreshSelection();}return;}
    if(e.key==='Tab'&&document.body.classList.contains('drawer-open')){const items=[...$('panel').querySelectorAll('button,input,select,summary')].filter(el=>!el.disabled&&el.getClientRects().length);const first=items[0],last=items[items.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}return;}
    if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;
    if(e.defaultPrevented)return;if(e.key==='ArrowRight'){e.preventDefault();focusProof(focusedProof+1);}if(e.key==='ArrowLeft'){e.preventDefault();focusProof(focusedProof-1);}if(e.key==='0')setView('spatial');
  });
  function updateInputHint(){$('hint').textContent=coarseQuery.matches?'拖动 B₁ 翻折 · 空白旋转 · 双指缩放 / 平移':'拖动 B₁ 翻折 · 空白旋转 · 滚轮缩放 · 顶点多选';}
  const mediaListen=(query,fn)=>query.addEventListener?query.addEventListener('change',fn):query.addListener(fn);
  mediaListen(compactQuery,()=>{setDrawer(false);$('panel').inert=compact();resize();});mediaListen(coarseQuery,()=>{updateInputHint();resize();});
  mediaListen(matchMedia('(orientation:portrait)'),()=>{setDrawer(false);cancelGesture();resize();});
  window.addEventListener('orientationchange',()=>{setDrawer(false);cancelGesture();});window.addEventListener('blur',()=>{cancelGesture();pausePlayback();syncReadings();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){pausePlayback();syncReadings();cancelGesture();tween=null;if(frame)cancelAnimationFrame(frame);frame=0;}else invalidate();});
  const observer=new ResizeObserver(resize);observer.observe(stage);observer.observe(document.querySelector('.stage-bottom'));window.addEventListener('resize',resize);if(window.visualViewport)window.visualViewport.addEventListener('resize',resize);
  setDrawer(false);$('panel').inert=compact();synchronizeChecks();setT(DEFAULT_T);updateVisibility();updateInputHint();resize();cam.dist=fitDistance;applyCamera();

  if(location.hash==='#geo-debug'){
    window.__GEO=V;
    window.__S={state,cam,camera,renderer,groups,target,selected,labels,statistics,values,STANDARD,DEFAULT_VIEW,vertexMeshes,foldPoint,toRender,pausePlayback,togglePlayback,setT,screenToT,focusProof,setView,resize,applyCamera,refreshSelection,pickVertex,setDrawer,updateVisibility,get renderCount(){return renderCount;},get dimensions(){return dimensions;},get pointers(){return pointers.size;},get gesture(){return gesture;},get fitDistance(){return fitDistance;}};
  }
})();
