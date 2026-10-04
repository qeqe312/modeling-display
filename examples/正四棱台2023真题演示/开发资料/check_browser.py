"""Problem-specific geometry and interaction checks in real Chromium input paths."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import hashlib
import math
import os

DEV=Path(__file__).resolve().parent
(DEV/'验证记录').mkdir(parents=True,exist_ok=True)
INLINE=DEV.parent/'成品'/'正四棱台2023真题演示.html'
OFFLINE=INLINE.parent/'离线双文件版'/INLINE.name
checks=[];metrics={}
def check(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
def launch(browser,path=INLINE,size=(1600,1000),touch=False,debug=True):
    context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=touch,is_mobile=touch,offline=True,device_scale_factor=2)
    page=context.new_page();errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
    page.goto(path.as_uri()+('#geo-debug' if debug else ''))
    if debug:page.wait_for_function('window.__S && __S.renderCount>0')
    page.wait_for_timeout(120)
    return context,page,errors,requests
def pos(page,key='P',label=False,t=None):
    return page.evaluate('''o=>{const r=cv.getBoundingClientRect();if(o.label){const l=__S.labels.find(l=>l.key===o.key);return {x:r.left+(l.hit.x0+l.hit.x1)/2,y:r.top+(l.hit.y0+l.hit.y1)/2};}const p=o.t===null?__GEO[o.key].clone():__GEO.C.clone().lerp(__GEO.Cp,o.t);p.project(__S.camera);return {x:r.left+(p.x*.5+.5)*r.width,y:r.top+(-p.y*.5+.5)*r.height}}''',{'key':key,'label':label,'t':t})
def camera_state(page):return page.evaluate('JSON.stringify([__S.cam,__S.target.toArray(),__S.camera.position.toArray()])')
def selected(page):return page.evaluate('[...__S.selected].sort()')
def mouse_drag(page,start,end,button='left',steps=14):
    page.mouse.move(**start);page.mouse.down(button=button);page.mouse.move(**end,steps=steps);page.mouse.up(button=button);page.wait_for_timeout(60)
def touch(session,kind,points):session.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
def touch_drag(session,start,end):
    touch(session,'touchStart',[{**start,'id':1}])
    for i in range(1,15):touch(session,'touchMove',[{'x':start['x']+(end['x']-start['x'])*i/14,'y':start['y']+(end['y']-start['y'])*i/14,'id':1}])
    touch(session,'touchEnd',[])
def sample_constraint(page):
    return page.evaluate('''()=>{const t=__S.state.t,p=__GEO.P,e=__GEO.C.clone().lerp(__GEO.Cp,t);return t>=0&&t<=1&&p.distanceTo(e)<1e-12}''')
def overlap_count(page):
    return page.evaluate('''()=>{const a=__S.labels.filter(l=>l.kind==='vertex'&&l.visible).map(l=>l.hit);let n=0;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)if(Math.min(a[i].x1,a[j].x1)-Math.max(a[i].x0,a[j].x0)>1&&Math.min(a[i].y1,a[j].y1)-Math.max(a[i].y0,a[j].y0)>1)n++;return n}''')

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    for path in [INLINE,OFFLINE]:
        context,page,errors,requests=launch(browser,path)
        check(not errors,'offline startup: '+path.parent.name)
        check(not any(u.startswith(('http:','https:')) for u in requests),'zero network resources: '+path.parent.name)
        context.close()
    context,page,errors,requests=launch(browser)
    page.evaluate("window.inputs=[];cv.addEventListener('pointerdown',e=>inputs.push({trusted:e.isTrusted,type:e.pointerType}))")
    check(page.locator('[data-lesson]').count()==4 and page.locator('[data-lesson]').evaluate_all('els=>els.every(e=>!e.hidden)'),'four complete proof cards unfolded')
    check(page.locator('.solution-overview button').count()==4,'all four key formulas shown together')
    check(page.evaluate('__S.state.t===.5 && __S.state.plane1 && __S.state.plane2 && __S.state.lineAngle'),'midpoint and auxiliary planes enabled')
    check(page.locator('#sT').evaluate("el=>el.closest('#settings-panel')!==null"),'motion slider in display settings')
    check(page.locator('#rSin').inner_text()=='0.7263','exact answer rounded correctly')
    check(page.locator('#mVolume').inner_text()=='1 : 6','remaining-volume ratio correctly displayed')
    # Independent formulas are compared against actual rendered coordinates at many positions.
    for t in [0,.001,.1,.25,.5,.75,.999,1]:
        page.evaluate('__S.setT',t)
        values=page.evaluate('({v:__S.values,p:__S.STANDARD.P})')
        angle=math.degrees(math.acos(abs(t-.5)/math.sqrt(t*t-t+1)))
        check(abs(values['v']['planeAngle']-angle)<1e-9,f'plane angle matches independent formula t={t}')
        check(sample_constraint(page),f'point stays on CC′ at t={t}')
        if t>0:check(abs(values['v']['sinTheta']-math.sqrt(24/(56-28*t+14*t*t)))<1e-9,f'line angle matches independent formula t={t}')
        else:check(values['v']['sinTheta'] is None and page.locator('#rSin').inner_text()=='未定义','P=C handles undefined plane without NaN')
    page.evaluate('__S.setT(.5)');page.wait_for_timeout(60)
    # Perspective inverse uses the complete camera projection, including its view offset.
    max_error=page.evaluate('''()=>{let error=0;const saved={...__S.cam},oldTarget=__S.target.clone();for(const angle of [0,.8,2.08,3.6]){__S.cam.azim=angle;__S.cam.elev=.4;__S.target.set(.2,-.1,.15);__S.applyCamera();for(let i=0;i<=100;i++){const t=i/100,p=__GEO.C.clone().lerp(__GEO.Cp,t).project(__S.camera),u=__S.screenToT((p.x*.5+.5)*__S.dimensions.width,(-p.y*.5+.5)*__S.dimensions.height);error=Math.max(error,Math.abs(t-u));}}Object.assign(__S.cam,saved);__S.target.copy(oldTarget);__S.applyCamera();return error}''')
    check(max_error<1e-9,'404 perspective inverse samples including camera pan')
    metrics['maximumProjectionError']=max_error
    # Trusted mouse drags are constrained and lock azimuth, elevation, distance and target.
    for end_t in [.25,.75,1.2,-.15,.5]:
        before=camera_state(page);selection=selected(page)
        mouse_drag(page,pos(page),pos(page,t=end_t))
        expected=max(0,min(1,end_t))
        check(abs(page.evaluate('__S.state.t')-expected)<2e-5,f'mouse dragging to t={end_t} clamps correctly')
        check(camera_state(page)==before,f'camera locked while dragging to t={end_t}')
        check(selected(page)==selection,f'point movement causes no vertex selection t={end_t}')
        check(sample_constraint(page),f'mouse constraint t={end_t}')
        check(abs(float(page.locator('#sT').input_value())-expected)<.00051,f'model drag synchronizes slider t={end_t}')
    # Dragging the displaced label does not jump at pointerdown and still drives P.
    start=pos(page,label=True);before=camera_state(page);t0=page.evaluate('__S.state.t')
    page.mouse.move(**start);page.mouse.down();check(page.evaluate('__S.state.t')==t0,'label grab preserves point position')
    page.mouse.move(start['x']+35,start['y']-65,steps=12);page.mouse.up();page.wait_for_timeout(80)
    check(abs(page.evaluate('__S.state.t')-t0)>.01 and sample_constraint(page),'label dragging moves P on its constrained edge')
    check(camera_state(page)==before,'label dragging locks camera')
    # Endpoint priority: grabbing the coincident ball must still drag P.
    for endpoint,destination in [(0,.3),(1,.7)]:
        page.evaluate('__S.setT',endpoint);page.wait_for_timeout(50);before=camera_state(page)
        mouse_drag(page,pos(page),pos(page,t=destination));check(abs(page.evaluate('__S.state.t')-destination)<2e-5,f'P can be grabbed at endpoint {endpoint}');check(camera_state(page)==before,f'endpoint drag {endpoint} locks camera')
    page.evaluate('__S.setT(.5)');page.wait_for_timeout(50)
    for key in ['A','B','P']:page.mouse.click(**pos(page,key,True))
    check(selected(page)==['A','B','P'],'mouse label multiselect')
    page.mouse.click(**pos(page,'P',True));check(selected(page)==['A','B'],'point tap toggles highlight without moving')
    page.keyboard.press('Escape');check(selected(page)==[],'Escape clears selection')
    page.locator('#tab-settings').click()
    page.locator('#sT').focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight');page.keyboard.press('ArrowRight');page.wait_for_timeout(60)
    check(abs(page.evaluate('__S.state.t')-.002)<1e-12 and sample_constraint(page),'native slider moves model through shared parameter')
    for value in ['0','0.5','1']:
        page.locator(f'[data-t="{value}"]').click();check(abs(page.evaluate('__S.state.t')-float(value))<1e-12,'quick point position '+value)
    page.locator('[data-t="0.5"]').click()
    for control,group in {'cSolid':'faces','cPlane1':'plane1','cPlane2':'plane2','cLineAngle':'lineAngle','cVolume':'volume','cAngles':'angles','cAxes':'axes'}.items():
        page.locator('#'+control).uncheck();page.wait_for_timeout(30);check(not page.evaluate(f'__S.groups.{group}.visible'),f'{control} hides actual geometry')
        page.locator('#'+control).check();page.wait_for_timeout(30);check(page.evaluate(f'__S.groups.{group}.visible'),f'{control} shows actual geometry')
    page.locator('#cLabels').uncheck();check(page.evaluate("__S.labels.filter(l=>l.kind==='vertex').every(l=>!l.visible)"),'vertex letters hide independently')
    page.locator('#cLabels').check();page.locator('#cLengths').check();check(page.evaluate("__S.labels.filter(l=>l.kind==='edge').every(l=>l.visible)"),'edge values show independently')
    page.locator('#sFont').focus();page.keyboard.press('End');page.wait_for_timeout(60);check(page.locator('#sFontval').inner_text()=='32 px','font size reaches 32px')
    page.locator('#sOpacity').focus();page.keyboard.press('End');page.wait_for_timeout(40)
    check(page.evaluate('__S.groups.faces.children.every(m=>Math.abs(m.material.opacity-.3)<1e-12)'),'opacity updates real frustum faces')
    for quality in ['save','sharp','auto']:
        page.locator(f'[data-quality="{quality}"]').click();check(page.evaluate('__S.state.quality')==quality,'quality '+quality)
    page.locator('#clear').click();check(selected(page)==[],'clear highlights button')
    previous=page.evaluate('JSON.stringify(__S.state)')
    for i in range(8):page.locator(f'[data-proof="{i%4}"]').click()
    check(page.evaluate('JSON.stringify(__S.state)')==previous,'proof navigation preserves every layer and P position')
    check(page.locator('[data-lesson]').evaluate_all('els=>els.every(e=>!e.hidden)'),'navigation keeps all proofs unfolded')
    # Cache stability includes moving faces/arcs, extremes and display changes.
    page.wait_for_timeout(120);geometry_count=page.evaluate('__S.renderer.info.memory.geometries')
    page.evaluate('''async()=>{for(let i=0;i<90;i++){__S.setT((i%31)/30);await new Promise(requestAnimationFrame);}__S.setT(.5)}''');page.wait_for_timeout(80)
    check(page.evaluate('__S.renderer.info.memory.geometries')==geometry_count,'90 rendered point updates allocate no geometries')
    page.wait_for_timeout(450);frames=page.evaluate('__S.renderCount');page.wait_for_timeout(600)
    check(page.evaluate('__S.renderCount')==frames,'idle renders zero additional frames')
    durations=page.evaluate('__S.statistics.durations.slice(-80).sort((a,b)=>a-b)')
    metrics['desktop']={'geometries':geometry_count,'idleAdditionalFrames':0,'renderCpuP95Milliseconds':durations[int(len(durations)*.95)] if durations else None,'pixelRatio':page.evaluate('__S.renderer.getPixelRatio()')}
    check(page.evaluate('inputs.length>0 && inputs.every(e=>e.trusted)'),'trusted mouse Pointer Events')
    check(not errors,'desktop tests have no JavaScript exceptions');context.close()
    # Tablet touch uses CDP's real input dispatch, including cancellation and second finger.
    for size in [(820,1180),(1180,820)]:
        context,page,errors,requests=launch(browser,size=size,touch=True);session=context.new_cdp_session(page)
        page.evaluate("window.inputs=[];cv.addEventListener('pointerdown',e=>inputs.push({trusted:e.isTrusted,type:e.pointerType}))")
        for destination in [.2,.8,1.15,-.12,.5]:
            before=camera_state(page);touch_drag(session,pos(page),pos(page,t=destination));page.wait_for_timeout(70)
            check(abs(page.evaluate('__S.state.t')-max(0,min(1,destination)))<2e-5,f'trusted touch P drag {destination} at {size}')
            check(camera_state(page)==before and sample_constraint(page),f'touch camera lock and constraint {destination} at {size}')
        check(selected(page)==[],'touch point drags do not select vertices '+str(size))
        start=pos(page);before=camera_state(page)
        touch(session,'touchStart',[{**start,'id':1}]);touch(session,'touchStart',[{**start,'id':1},{'x':80,'y':480,'id':2}])
        touch(session,'touchMove',[{**pos(page,t=.65),'id':1},{'x':150,'y':480,'id':2}]);touch(session,'touchEnd',[]);page.wait_for_timeout(80)
        check(camera_state(page)==before,'second finger cannot rotate during P drag '+str(size))
        touch(session,'touchStart',[{**pos(page),'id':1}]);touch(session,'touchCancel',[])
        check(page.evaluate('__S.pointers===0 && __S.gesture===null'),'touch cancellation releases camera lock '+str(size))
        before=camera_state(page);touch_drag(session,{'x':60,'y':390},{'x':130,'y':360});page.wait_for_timeout(60)
        check(camera_state(page)!=before,'camera rotates after releasing point '+str(size))
        before=page.evaluate('__S.cam.dist');origin=page.evaluate('__S.target.toArray()')
        touch(session,'touchStart',[{'x':90,'y':300,'id':1},{'x':260,'y':300,'id':2}]);touch(session,'touchMove',[{'x':70,'y':340,'id':1},{'x':300,'y':340,'id':2}]);touch(session,'touchEnd',[]);page.wait_for_timeout(50)
        check(page.evaluate('__S.cam.dist')<before and page.evaluate('__S.target.toArray()')!=origin,'two-finger zoom and pan '+str(size))
        page.locator('#reset').tap();page.wait_for_timeout(380);page.evaluate('__S.setT(.5)');page.wait_for_timeout(60)
        for key in ['A','P']:
            touch(session,'touchStart',[{**pos(page,key,True),'id':1}]);touch(session,'touchEnd',[]);page.wait_for_timeout(40)
        check(selected(page)==['A','P'],'touch label multiselect '+str(size))
        check(page.evaluate("inputs.some(e=>e.type==='touch'&&e.trusted)&&inputs.every(e=>e.trusted)"),'trusted touch event evidence '+str(size))
        page.locator('#menu').tap();page.wait_for_timeout(280);rect=page.locator('#panel').bounding_box()
        if size[0]<size[1]:check(rect['width']==size[0] and abs(rect['y']+rect['height']-size[1])<2,'portrait bottom drawer')
        else:check(rect['x']==0 and rect['width']==390 and rect['y']==72,'landscape left drawer')
        page.locator('#tab-settings').tap();page.locator('[data-t="0.5"]').tap();check(page.locator('#sTval').inner_text()=='0.500','touch settings sync midpoint '+str(size))
        page.locator('#sT').focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight');check(abs(page.evaluate('__S.state.t')-.001)<1e-12,'tablet slider sync '+str(size))
        page.locator('#tab-lesson').tap();check(page.locator('[data-lesson]').evaluate_all('els=>els.every(e=>!e.hidden)'),'tablet continuous complete solution '+str(size))
        page.locator('#close').tap();page.wait_for_timeout(280)
        page.locator('[data-proof="3"]').tap();page.wait_for_timeout(350);check(page.locator('#proof-3').is_visible(),'tablet formula opens final derivation '+str(size))
        page.set_viewport_size({'width':size[1],'height':size[0]});page.wait_for_timeout(300)
        check(not page.locator('#panel').evaluate("e=>e.classList.contains('open')"),'orientation change closes drawer '+str(size))
        check(not errors,'tablet no browser exceptions '+str(size));context.close()
    # Fit, label avoidance and responsive clearance across small and large touch screens.
    for size in [(390,844),(780,1000),(820,1180),(1180,820),(1366,1024)]:
        context,page,errors,requests=launch(browser,size=size,touch=True)
        check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'no horizontal overflow '+str(size))
        check(page.locator('.solution-overview button').evaluate_all('els=>els.every(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight})'),'all formulas fit '+str(size))
        boundary=page.locator('.step-caption').bounding_box()['y']
        check(page.locator('#labels .lab').evaluate_all('els=>els.filter(e=>!e.hidden).every(e=>e.getBoundingClientRect().bottom<'+str(boundary)+')'),'labels clear formula panel '+str(size))
        for view in ['front','top','spatial']:
            page.locator(f'[data-view="{view}"]').tap();page.wait_for_timeout(370)
            check(overlap_count(page)==0,'vertex labels avoid overlap '+view+' '+str(size))
        check(not errors,'viewport no errors '+str(size));context.close()
    context,page,errors,requests=launch(browser,debug=False);check(page.evaluate('typeof __S')=='undefined','production page has no debug global');context.close()
    context=browser.new_context(offline=True);page=context.new_page();page.route('**/three.min.js',lambda r:r.abort());page.goto(OFFLINE.as_uri());check(page.locator('#error').is_visible(),'missing local library has a readable error');context.close()
    browser.close()
report={'passed':len(checks),'checks':checks,'metrics':metrics,'browserVersion':browser.version,'pageSha256':hashlib.sha256(INLINE.read_bytes()).hexdigest(),'scope':'Chrome desktop mouse and trusted CDP touch; tablet viewport simulation, no physical iPad/Safari'}
(DEV/'验证记录'/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'metrics':metrics},indent=2))
