"""Problem-specific checks using Chromium mouse and trusted CDP touch input."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import hashlib
import os
import sys
import time

ROOT=Path(__file__).resolve().parent
PACKAGE=(Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else ROOT.parent/'成品').resolve()
INLINE=PACKAGE/'正四面体内外接球与对棱夹角.html'
(ROOT/'验证记录').mkdir(exist_ok=True)
checks=[]
metrics={}
def check(condition,message):
    if not condition: raise AssertionError(message)
    checks.append(message)
def launch_page(browser,path=INLINE,size=(1600,1000),touch=False,debug=True):
    context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=touch,is_mobile=touch,offline=True,device_scale_factor=2)
    page=context.new_page();errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.goto(path.as_uri()+('#geo-debug' if debug else ''))
    if debug: page.wait_for_function('window.__S && __S.renderCount>0')
    page.wait_for_timeout(100)
    return context,page,errors,requests
def coords(page,key,label=False):
    if label:
        return page.evaluate('''key=>{const l=__S.labels.find(l=>l.key===key),r=document.getElementById('cv').getBoundingClientRect();return {x:r.left+(l.hit.x0+l.hit.x1)/2,y:r.top+(l.hit.y0+l.hit.y1)/2}}''',key)
    return page.evaluate('''key=>{const v=__GEO[key].clone().project(__S.camera),r=document.getElementById('cv').getBoundingClientRect();return {x:r.left+(v.x*.5+.5)*r.width,y:r.top+(-v.y*.5+.5)*r.height}}''',key)
def drag(page,start,end,button='left',steps=12):
    page.mouse.move(**start);page.mouse.down(button=button);page.mouse.move(**end,steps=steps);page.mouse.up(button=button);page.wait_for_timeout(60)
def touch_send(session,kind,points):
    session.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
def touch_drag(session,start,end):
    touch_send(session,'touchStart',[{**start,'id':1}])
    for i in range(1,13):touch_send(session,'touchMove',[{'x':start['x']+(end['x']-start['x'])*i/12,'y':start['y']+(end['y']-start['y'])*i/12,'id':1}])
    touch_send(session,'touchEnd',[])
def selection(page): return page.evaluate('[...__S.selected].sort()')
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    for path in [INLINE]:
        context,page,errors,requests=launch_page(browser,path)
        check(not errors,'offline startup without exceptions: '+path.parent.name)
        check(all(not u.startswith(('http:','https:')) for u in requests),'no network resources: '+path.parent.name)
        context.close()
    context,page,errors,requests=launch_page(browser)
    page.evaluate("window.inputEvents=[];document.getElementById('cv').addEventListener('pointerdown',e=>inputEvents.push({trusted:e.isTrusted,type:e.pointerType}))")
    # Complete solution is visible immediately and the model is fully configured.
    check(page.locator('[data-lesson]').count()==4,'all four proof cards exist')
    check(page.locator('[data-lesson]').evaluate_all('els=>els.every(el=>!el.hidden)'),'all four proof cards unfolded on startup')
    check(page.locator('.solution-overview button').count()==4,'four key formulas shown together')
    check(page.evaluate('__S.state.step===3 && __S.state.sphere && __S.state.inner && __S.state.opposite && __S.state.guide'),'both spheres, opposite edges and guides enabled at startup')
    check(page.locator('#rValue3').inner_text()=='90°','opposite edge angle readout exact')
    check(page.locator('#options').evaluate("el=>el.classList.contains('reveal')"),'correct choice revealed immediately')
    check(page.locator('#previous,#next,[data-step]').count()==0,'no progressive lesson controls remain')
    import math
    r=math.sqrt(6)/12; h=4*r; b=math.sqrt(3)/6
    expected={'A':[0,0,h],'B':[-.5,-b,0],'C':[.5,-b,0],'D':[0,2*b,0],'O':[0,0,r],'F':[0,0,0]}
    data=page.evaluate('r=>Object.fromEntries(Object.entries(__GEO).map(([k,v])=>[k,[v.x/6,-v.z/6,v.y/6+r]]))',r)
    check(all(abs(data[k][i]-v[i])<1e-12 for k,v in expected.items() for i in range(3)),'rendering basis preserves all teaching coordinates')
    check(''.join(page.locator('#options [data-answer="C"]').inner_text().split())=='C.4','choice C: all four statements correct')
    check('πa' in page.locator('.statements li').first.inner_text() and page.locator('.statements sup').inner_text()=='2','statement 1 uses the user-confirmed a squared')
    check(page.evaluate("[['A','B'],['A','C'],['A','D'],['B','C'],['B','D'],['C','D']].every(([a,b])=>Math.abs(__GEO[a].distanceTo(__GEO[b])-6)<1e-12)"),'six rendered edges have normalized length 1 after scale 6')
    check(abs(page.evaluate('__S.groups.sphere.children[0].geometry.parameters.radius/6')-math.sqrt(6)/4)<1e-12,'rendered outer sphere has correct radius')
    check(abs(page.evaluate('__S.groups.inner.children[0].geometry.parameters.radius/6')-math.sqrt(6)/12)<1e-12,'rendered inner sphere has correct radius')
    check(page.evaluate('__S.groups.inner.children.length===9'),'inner sphere includes four contact markers')
    check(page.evaluate("Math.abs(__GEO.B.y-__GEO.C.y)<1e-12 && Math.abs(__GEO.C.y-__GEO.D.y)<1e-12 && __GEO.A.y>__GEO.B.y && Math.abs(__GEO.A.x)<1e-12 && Math.abs(__GEO.A.z)<1e-12"),'BCD is the horizontal base and A is directly above its centroid')
    # Label/sphere selection, multiselect, stable tap, blank retention.
    page.wait_for_timeout(80)
    before=page.evaluate('JSON.stringify(__S.cam)')
    page.mouse.click(**coords(page,'D',True));check(selection(page)==['D'],'click vertex label selects D')
    check(page.evaluate('JSON.stringify(__S.cam)')==before,'a tap does not rotate camera')
    page.mouse.click(**coords(page,'D',True));check(selection(page)==[],'click selected label deselects')
    for key in ['A','B','D']:page.mouse.click(**coords(page,key))
    check(selection(page)==['A','B','D'],'mouse vertex multiselect accumulates')
    blank={'x':page.locator('#cv').bounding_box()['x']+70,'y':370}
    page.mouse.click(**blank);check(selection(page)==['A','B','D'],'blank tap preserves multiselect')
    page.keyboard.press('Escape');check(selection(page)==[],'Escape clears highlights')
    # Rotate, zoom, pan and camera preset.
    before=page.evaluate('__S.cam.azim');drag(page,blank,{'x':blank['x']+95,'y':blank['y']-35});check(page.evaluate('__S.cam.azim')!=before,'mouse drag rotates')
    before=page.evaluate('__S.cam.dist');page.mouse.wheel(0,100);page.wait_for_timeout(80);check(page.evaluate('__S.cam.dist')>before,'wheel zooms out')
    before=page.evaluate('__S.target.toArray()');drag(page,blank,{'x':blank['x']+60,'y':blank['y']+18},button='right');check(page.evaluate('__S.target.toArray()')!=before,'right drag pans')
    page.locator('[data-view="spatial"]').click();page.wait_for_timeout(450);check(page.evaluate('__S.target.length()')<1e-9,'preset resets camera target')
    for view in ['front','top','spatial']:
        page.locator(f'[data-view="{view}"]').click();page.wait_for_timeout(380)
        overlaps=page.evaluate('''()=>{const a=__S.labels.filter(l=>l.kind==='vertex'&&l.visible).map(l=>l.hit);let n=0;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)if(Math.min(a[i].x1,a[j].x1)-Math.max(a[i].x0,a[j].x0)>1&&Math.min(a[i].y1,a[j].y1)-Math.max(a[i].y0,a[j].y0)>1)n++;return n}''')
        check(overlaps==0,'vertex labels do not overlap in '+view+' view')
    # Same elevation stop and reversal behavior as the original two examples.
    for _ in range(3):drag(page,blank,{'x':blank['x'],'y':blank['y']+220})
    check(abs(page.evaluate('__S.cam.elev')-1.49)<1e-12,'mouse reaches the reference upper elevation limit')
    before=page.evaluate('__S.cam.azim')
    drag(page,blank,{'x':blank['x']+80,'y':blank['y']})
    check(abs(page.evaluate('__S.cam.azim')-before+.48)<1e-12,'horizontal mouse rotation still works at elevation limit')
    drag(page,blank,{'x':blank['x'],'y':blank['y']-40})
    check(abs(page.evaluate('__S.cam.elev')-1.25)<1e-12,'reversing mouse drag leaves upper limit immediately')
    for _ in range(3):drag(page,{'x':blank['x'],'y':600},{'x':blank['x'],'y':350})
    check(abs(page.evaluate('__S.cam.elev')+1.49)<1e-12,'mouse reaches the reference lower elevation limit')
    drag(page,blank,{'x':blank['x'],'y':blank['y']+40})
    check(abs(page.evaluate('__S.cam.elev')+1.25)<1e-12,'reversing mouse drag leaves lower limit immediately')
    check(page.evaluate('__S.camera.up.equals(new THREE.Vector3(0,1,0))'),'world vertical stays fixed during mouse orbit')
    orientation=page.evaluate('({azim:__S.cam.azim,elev:__S.cam.elev})')
    page.locator('#fit').click();page.wait_for_timeout(380)
    check(page.evaluate('q=>Math.abs(__S.cam.azim-q.azim)<1e-12 && Math.abs(__S.cam.elev-q.elev)<1e-12',orientation),'centering preserves spherical orbit orientation')
    page.locator('#reset').click();page.wait_for_timeout(380)
    check(page.evaluate('Math.abs(__S.cam.azim+.45)<1e-12 && Math.abs(__S.cam.elev-.30)<1e-12'),'reset restores face-based default view')
    # Display controls and no phantom labels.
    page.locator('#tab-settings').click()
    page.locator('#cLabels').uncheck();page.wait_for_timeout(60);check(page.locator('#labels .lab:not(.edge-label)').evaluate_all('els=>els.filter(e=>!e.hidden).length')==0,'vertex labels can be hidden')
    page.locator('#cLabels').check();page.locator('#cSolid').uncheck();page.wait_for_timeout(50)
    page.mouse.click(**coords(page,'A'));check('A' in selection(page),'vertices selectable with faces hidden')
    page.locator('#cSolid').check();page.locator('#sFont').focus();page.keyboard.press('End');page.wait_for_timeout(70)
    check(page.locator('#labels .lab').first.evaluate('el=>getComputedStyle(el).fontSize')=='32px','font size control reaches 32px')
    page.locator('#sFont').focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight');page.keyboard.press('ArrowRight');page.wait_for_timeout(60)
    check(page.locator('#sFontval').inner_text()=='16 px','font output synchronizes')
    page.locator('#cSphere').uncheck();check(not page.evaluate('__S.state.sphere'),'sphere visibility toggle')
    page.locator('#cSphere').check();page.locator('#cAxes').check();check(page.evaluate('__S.state.axes'),'coordinate axes toggle')
    for quality in ['save','sharp','auto']:
        page.locator(f'[data-quality="{quality}"]').click();check(page.evaluate('__S.state.quality')==quality,'quality control '+quality)
    page.locator('#clear').click();check(selection(page)==[],'clear all button')
    # All groups are warmed up before the cache stability measurement.
    page.wait_for_timeout(100)
    # Reading any proof preserves manual settings and keeps geometry cached.
    start=page.evaluate('__S.renderer.info.memory.geometries')
    before_state=page.evaluate('JSON.stringify(__S.state)')
    for i in range(24):page.locator(f'[data-proof="{i%4}"]').click()
    check(page.evaluate('JSON.stringify(__S.state)')==before_state,'reading proofs preserves all display settings')
    check(page.locator('[data-lesson]').evaluate_all('els=>els.every(el=>!el.hidden)'),'reading proofs never hides another solution card')
    finish=page.evaluate('__S.renderer.info.memory.geometries');check(finish==start,'geometry count stable after 24 proof jumps')
    page.evaluate('''()=>{for(let i=0;i<100;i++){__S.cam.azim+=.001;__S.applyCamera();__S.state.inner=!__S.state.inner;__S.updateVisibility();}}''')
    page.wait_for_timeout(100)
    check(page.evaluate('__S.renderer.info.memory.geometries')==start,'geometry count stable after 100 camera and layer updates')
    page.wait_for_timeout(450);start_frames=page.evaluate('__S.renderCount');page.wait_for_timeout(600)
    check(page.evaluate('__S.renderCount')==start_frames,'idle page renders zero additional frames')
    check(page.evaluate('inputEvents.length>0 && inputEvents.every(e=>e.trusted)'),'trusted mouse Pointer Events')
    check(not errors,'desktop interactions without page errors')
    metrics['desktop']={'cachedGeometries':finish,'idleAdditionalFrames':0,'pixelRatio':page.evaluate('__S.renderer.getPixelRatio()')}
    # Desktop focus expands WebGL, drawer remains available.
    page.locator('#focus').click();page.wait_for_timeout(100);check(page.locator('#cv').bounding_box()['x']==0,'focus mode gives full width')
    page.locator('#menu').click();check(page.locator('#panel').get_attribute('aria-modal')=='true','focus mode panel opens as modal')
    page.keyboard.press('Escape');page.locator('#focus').click();context.close()
    # Tablet portrait: direct trusted touch, no synthetic PointerEvent dispatch.
    context,page,errors,requests=launch_page(browser,size=(820,1180),touch=True)
    page.evaluate("window.inputEvents=[];document.getElementById('cv').addEventListener('pointerdown',e=>inputEvents.push({trusted:e.isTrusted,type:e.pointerType}))")
    check(page.locator('#cv').bounding_box()['width']==820,'portrait canvas uses full tablet width')
    page.locator('#menu').tap();page.wait_for_timeout(280);rect=page.locator('#panel').bounding_box()
    check(rect['width']==820 and rect['y']>72 and abs(rect['y']+rect['height']-1180)<2,'portrait drawer anchored to bottom')
    page.locator('#tab-settings').tap();page.locator('#cSphere').check();page.locator('#cGuide').check();page.locator('#close').tap();page.wait_for_timeout(300)
    session=context.new_cdp_session(page)
    for key in ['A','D']:
        pos=coords(page,key,True);touch_send(session,'touchStart',[{**pos,'id':1}]);touch_send(session,'touchEnd',[]);page.wait_for_timeout(50)
    check(selection(page)==['A','D'],'touch labels accumulate multiselect')
    point=coords(page,'C',True);selected=selection(page);touch_send(session,'touchStart',[{**point,'id':1}]);touch_send(session,'touchCancel',[]);check(selection(page)==selected,'touch cancel does not select a vertex')
    blank={'x':80,'y':500};before=page.evaluate('__S.cam.azim');touch_drag(session,blank,{'x':blank['x']+90,'y':blank['y']-40});page.wait_for_timeout(80)
    check(page.evaluate('__S.cam.azim')!=before,'single finger rotates model')
    before=page.evaluate('__S.cam.dist');target=page.evaluate('__S.target.toArray()')
    touch_send(session,'touchStart',[{'x':200,'y':750,'id':1},{'x':450,'y':750,'id':2}])
    touch_send(session,'touchMove',[{'x':155,'y':780,'id':1},{'x':525,'y':780,'id':2}]);touch_send(session,'touchEnd',[]);page.wait_for_timeout(80)
    check(page.evaluate('__S.cam.dist')<before,'two finger pinch zooms in')
    check(page.evaluate('__S.target.toArray()')!=target,'two finger centroid pans')
    check(page.evaluate('__S.pointers')==0,'touch pointers released cleanly')
    check(selection(page)==selected,'two finger gesture does not add a selection')
    check(page.evaluate("inputEvents.some(e=>e.type==='touch'&&e.trusted)&&inputEvents.every(e=>e.trusted)"),'trusted touch Pointer Events')
    page.locator('[data-view="spatial"]').tap();page.wait_for_timeout(380)
    for _ in range(3):touch_drag(session,{'x':70,'y':350},{'x':70,'y':600})
    check(abs(page.evaluate('__S.cam.elev')-1.49)<1e-12,'trusted touch reaches reference upper elevation limit')
    touch_drag(session,{'x':70,'y':400},{'x':70,'y':360})
    check(abs(page.evaluate('__S.cam.elev')-1.25)<1e-12,'reversing touch drag leaves upper limit immediately')
    for _ in range(3):touch_drag(session,{'x':70,'y':600},{'x':70,'y':350})
    check(abs(page.evaluate('__S.cam.elev')+1.49)<1e-12,'trusted touch reaches reference lower elevation limit')
    touch_drag(session,{'x':70,'y':400},{'x':70,'y':440})
    check(abs(page.evaluate('__S.cam.elev')+1.25)<1e-12,'reversing touch drag leaves lower limit immediately')
    check(page.evaluate('__S.pointers')==0,'touch pointers release after elevation-limit checks')
    page.locator('[data-view="spatial"]').tap();page.wait_for_timeout(380)
    page.locator('#menu').tap();page.wait_for_timeout(260);page.set_viewport_size({'width':1180,'height':820});page.wait_for_timeout(350)
    check('open' not in (page.locator('#panel').get_attribute('class') or ''),'orientation change closes drawer')
    page.locator('#menu').tap();page.wait_for_timeout(280);rect=page.locator('#panel').bounding_box()
    check(rect['x']==0 and rect['width']<450 and rect['y']==72,'landscape drawer enters from left')
    page.locator('#close').tap();page.wait_for_timeout(280);page.locator('[data-proof="3"]').tap();page.wait_for_timeout(350);check(page.locator('#rValue3').inner_text()=='90°','tablet result displayed while reading proof');check(page.locator('[data-lesson]').evaluate_all('els=>els.every(el=>!el.hidden)'),'tablet drawer contains the complete proof');check(page.locator('#proof-3').is_visible(),'tablet answer proof reachable')
    check(not errors,'tablet interactions without page errors')
    context.close()
    # Narrow screen and larger touch tablet remain overlays; no horizontal scroll.
    for size in [(390,844),(780,1000),(1366,1024)]:
        context,page,errors,requests=launch_page(browser,size=size,touch=True)
        check(page.locator('#menu').is_visible(),f'touch menu visible at {size}')
        check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'no horizontal overflow at {size}')
        page.wait_for_timeout(70)
        check(page.locator('.solution-overview button').evaluate_all('els=>els.every(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth})'),f'four formulas fit viewport at {size}')
        rect=page.locator('#cv').bounding_box()
        for key in ['A','B','C','D']:
            pos=coords(page,key);check(rect['x']<pos['x']<rect['x']+rect['width'] and rect['y']<pos['y']<rect['y']+rect['height'],f'{key} is on screen at {size}')
        check(not errors,f'no browser errors at {size}');context.close()
    # Normal production URL hides debug controls; missing library is readable.
    context,page,errors,requests=launch_page(browser,debug=False)
    check(page.evaluate('typeof window.__S')=='undefined','production URL does not expose debug state');context.close()
    context=browser.new_context(offline=True);page=context.new_page()
    broken=INLINE.read_text(encoding='utf-8')
    import re
    broken=re.sub(r'<script>.*?</script>','<script>/* dependency intentionally absent */</script>',broken,count=1,flags=re.S)
    page.set_content(broken)
    check(page.locator('#error').is_visible(),'readable message if library is missing');context.close()
    # The approved settings must operate on actual cached model groups.
    context,page,errors,requests=launch_page(browser)
    page.locator('#tab-settings').click()
    for control,group in {'cSolid':'faces','cSphere':'sphere','cInner':'inner','cOpposite':'opposite','cGuide':'guide','cAngles':'angles','cAxes':'axes'}.items():
        page.locator('#'+control).uncheck();page.wait_for_timeout(30)
        check(not page.evaluate(f'__S.groups.{group}.visible'),f'{control} hides actual model group')
        page.locator('#'+control).check();page.wait_for_timeout(30)
        check(page.evaluate(f'__S.groups.{group}.visible'),f'{control} shows actual model group')
    check(page.evaluate("()=>{const directions=[[1,0,0],[0,0,-1],[0,1,0]];return __S.groups.axes.children.every((a,i)=>a.position.distanceTo(__GEO.F)<1e-12 && new THREE.Vector3(0,1,0).applyQuaternion(a.quaternion).distanceTo(new THREE.Vector3(...directions[i]))<1e-12)}"),'axes originate at F, with xy parallel to BCD and z along FA')
    page.locator('#cGuide').uncheck();page.wait_for_timeout(40)
    check(page.evaluate("__S.labels.find(l=>l.key==='F').visible && !__S.labels.find(l=>l.key==='O').visible"),'axis origin F remains visible when auxiliary guides are hidden')
    page.locator('#cGuide').check()
    page.locator('#cLengths').uncheck()
    check(page.evaluate("__S.labels.filter(x=>x.kind==='edge').every(x=>!x.visible)"),'length labels hide independently')
    page.locator('#cLengths').check()
    page.locator('#sOpacity').focus();page.keyboard.press('End');page.wait_for_timeout(50)
    check(page.locator('#sOpacityval').inner_text()=='20%','opacity output updates')
    check(all(abs(x-.2)<1e-12 for x in page.evaluate('[__S.groups.sphere.children[0].material.opacity,__S.groups.inner.children[0].material.opacity]')),'opacity slider modifies both real sphere materials')
    page.locator('[data-quality="save"]').click()
    check(page.evaluate('__S.renderer.getPixelRatio()')==1,'save mode uses pixel ratio 1')
    check(not errors,'full display settings without browser errors');context.close()
    for size in [(390,844),(820,1180),(1180,820)]:
        context,page,errors,requests=launch_page(browser,size=size,touch=True)
        if size[0]<600:
            check(page.evaluate("()=>{const bottom=document.getElementById('readout').getBoundingClientRect().bottom;return __S.labels.filter(l=>l.kind==='vertex'&&l.visible).every(l=>l.el.getBoundingClientRect().top>=bottom+6)}"),'phone vertex labels clear the top readout panel')
        boundary=page.locator('.step-caption').bounding_box()['y']
        for key in ['A','B','C','D']:
            bottom=page.evaluate("key=>__S.labels.find(x=>x.key===key).el.getBoundingClientRect().bottom",key)
            check(bottom<boundary,f'{key} label clears formula panel at {size}')
        context.close()
    browser.close()
report={'passed':len(checks),'checks':checks,'metrics':metrics,'browserVersion':browser.version,'pageSha256':hashlib.sha256(INLINE.read_bytes()).hexdigest(),'scope':'Chromium desktop and emulated touch; real iPad/Safari hardware not tested'}
(ROOT/'验证记录'/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'metrics':metrics},indent=2))
