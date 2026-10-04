"""Folding-specific offline, mathematical, mouse and trusted touch acceptance."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import hashlib
import json
import math
import os

DEV=Path(__file__).resolve().parent
PAGE=DEV.parent/'成品'/'菱形沿AM翻折与动点.html'
OUT=DEV/'验证记录'
OUT.mkdir(exist_ok=True)
checks=[];metrics={}
def check(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
def launch(browser,size=(1600,1000),touch=False,debug=True):
    context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=touch,is_mobile=touch,offline=True,device_scale_factor=1)
    page=context.new_page();errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
    page.goto(PAGE.as_uri()+('#geo-debug' if debug else ''))
    if debug:page.wait_for_function('window.__S && __S.renderCount>0')
    page.wait_for_timeout(130)
    return context,page,errors,requests
def pos(page,key='B1',label=False,t=None):
    return page.evaluate('''o=>{const r=cv.getBoundingClientRect();if(o.label){const l=__S.labels.find(l=>l.key===o.key);return {x:r.left+(l.hit.x0+l.hit.x1)/2,y:r.top+(l.hit.y0+l.hit.y1)/2};}const p=o.t===null?__GEO[o.key].clone():__S.foldPoint(o.t,__GEO.B1.clone());p.project(__S.camera);return {x:r.left+(p.x*.5+.5)*r.width,y:r.top+(-p.y*.5+.5)*r.height}}''',{'key':key,'label':label,'t':t})
def cam(page):return page.evaluate('JSON.stringify([__S.cam,__S.target.toArray(),__S.camera.position.toArray()])')
def selected(page):return page.evaluate('[...__S.selected].sort()')
def mouse_drag(page,start,end):
    page.mouse.move(**start);page.mouse.down();page.mouse.move(**end,steps=18);page.mouse.up();page.wait_for_timeout(65)
def touch(session,kind,points):session.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
def touch_drag(session,start,end):
    touch(session,'touchStart',[{**start,'id':1}])
    for i in range(1,19):touch(session,'touchMove',[{'x':start['x']+(end['x']-start['x'])*i/18,'y':start['y']+(end['y']-start['y'])*i/18,'id':1}])
    touch(session,'touchEnd',[])
def constraint(page):
    return page.evaluate('''()=>{const t=__S.state.t,b=__S.STANDARD.B1,n=__S.STANDARD.N,d=__S.STANDARD.D;return t>=0&&t<=1&&Math.abs(b[0])<1e-12&&Math.abs(b[1]*b[1]+b[2]*b[2]-1)<1e-12&&b[2]>-1e-12&&n.every((v,i)=>Math.abs(v-(b[i]+d[i])/2)<1e-12)}''')
def blank(page):
    return page.evaluate('''()=>{const r=cv.getBoundingClientRect();for(const y of [220,265,310,355])for(const x of [50,r.width-70,r.width*.25,r.width*.75]){if(y>r.height-__S.dimensions.bottom-30)continue;const px=r.left+x,py=r.top+y;if(document.elementFromPoint(px,py)===cv&&!__S.pickVertex(x,y,'touch'))return {x:px,y:py};}throw Error('no safe blank input location')}''')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    metrics['browser']=browser.version
    context,page,errors,requests=launch(browser)
    page.evaluate("window.inputs=[];cv.addEventListener('pointerdown',e=>inputs.push({trusted:e.isTrusted,type:e.pointerType}))")
    check(not errors and not any(u.startswith(('http:','https:')) for u in requests),'file:// offline startup, zero remote resources')
    check(page.locator('[data-lesson]').count()==4 and page.locator('[data-lesson]').evaluate_all('a=>a.every(e=>!e.hidden)'),'all four proofs initially unfolded')
    check(page.locator('#sT,#play,#speed').evaluate_all("a=>a.every(e=>e.closest('#settings-panel'))"),'angle, play/pause and speed are inside display settings')
    check(abs(page.evaluate('__S.state.t')-1/3)<1e-12,'default folding angle 60 degrees')
    check(page.evaluate("['A','M','C','D'].every(k=>Math.abs(__GEO[k].y+.45)<1e-12)"),'horizontal fixed base is the lowest face')
    for t in [0,.001,.1,.25,.5,.75,.999,1]:
        page.evaluate('__S.setT',t);v=page.evaluate('({v:__S.values,b:__S.STANDARD.B1,n:__S.STANDARD.N})')
        check(constraint(page),f'B₁ circle and N midpoint constraint at {t}')
        check(abs(v['v']['CN']-1)<1e-9 and abs(v['v']['theta']-30)<1e-9,f'constant length and angle at {t}')
        check(abs(v['v']['volume']-math.sqrt(3)*math.sin(math.pi*t)/3)<1e-9,f'volume formula at {t}')
        if t in (0,1):check(v['v']['planeAngle'] is None and page.locator('#mAngle').inner_text()=='未定义' and not page.evaluate('__S.groups.plane2.visible'),f'degenerate plane endpoint {t}')
        else:check(v['v']['planeAngle']==90,f'perpendicular planes at {t}')
    maximum=page.evaluate('''()=>{let max=0,samples=0;const saved={...__S.cam},origin=__S.target.clone();for(const azim of [.2,.42,1.1,2.4,4.5])for(const elev of [-.7,.25,.9])for(const zoom of [.8,1.2]){__S.cam.azim=azim;__S.cam.elev=elev;__S.cam.dist=__S.fitDistance*zoom;__S.target.set(.2,-.1,.15);__S.applyCamera();for(let i=0;i<=100;i++){const t=i/100,p=__S.foldPoint(t,__GEO.B1.clone()).project(__S.camera),u=__S.screenToT((p.x*.5+.5)*__S.dimensions.width,(-p.y*.5+.5)*__S.dimensions.height);if(u===null)throw Error('unexpected null inverse');max=Math.max(max,Math.abs(t-u));samples++;}}Object.assign(__S.cam,saved);__S.target.copy(origin);__S.applyCamera();return {max,samples}}''')
    check(maximum['max']<1e-9,'world ray/circle plane inverse across 3030 view/zoom/pan samples');metrics['circleInverse']=maximum
    edge_error=page.evaluate('''()=>{const saved={...__S.cam},origin=__S.target.clone();__S.cam.azim=0;__S.cam.elev=.5;__S.target.x=__GEO.M.x;__S.applyCamera();let error=0;for(const t of [.12,.25,.42,.61,.83]){__S.setT(t);const p=__S.foldPoint(t,__GEO.B1.clone()).project(__S.camera),u=__S.screenToT((p.x*.5+.5)*__S.dimensions.width,(-p.y*.5+.5)*__S.dimensions.height);error=Math.max(error,Math.abs(t-u));}Object.assign(__S.cam,saved);__S.target.copy(origin);__S.applyCamera();return error}''')
    check(edge_error<1e-6,'edge-on ambiguous ray chooses nearest continuous circle branch');metrics['edgeOnParameterError']=edge_error
    page.evaluate('__S.setT(1/3)');page.wait_for_timeout(70)
    drag_errors=[]
    for target in [.2,.65,1.1,-.1,.5]:
        camera=cam(page);selection=selected(page);mouse_drag(page,pos(page),pos(page,t=target));t=page.evaluate('__S.state.t');expected=max(0,min(1,target));drag_errors.append(abs(t-expected))
        check(abs(t-expected)<.003,f'mouse circle drag and boundary clamp {target}')
        check(cam(page)==camera and selected(page)==selection,f'point drag locks complete camera and avoids selection {target}')
        check(constraint(page) and abs(float(page.locator('#sT').input_value())-t)<.0006,f'drag synchronizes slider and midpoint {target}')
    for endpoint,target in [(0,.25),(1,.75)]:
        page.evaluate('__S.setT',endpoint);page.wait_for_timeout(65);camera=cam(page);mouse_drag(page,pos(page),pos(page,t=target))
        check(abs(page.evaluate('__S.state.t')-target)<.003 and cam(page)==camera,f'coincident endpoint B₁ can be grabbed {endpoint}')
    page.evaluate('__S.setT(1/3)');page.wait_for_timeout(60)
    start=pos(page,label=True);camera=cam(page);t0=page.evaluate('__S.state.t');page.mouse.move(**start);page.mouse.down();check(page.evaluate('__S.state.t')==t0,'label pointerdown does not jump')
    page.mouse.move(start['x']+25,start['y']-55,steps=12);page.mouse.up();page.wait_for_timeout(50)
    check(abs(page.evaluate('__S.state.t')-t0)>.01 and cam(page)==camera and constraint(page),'displaced B₁ label drives folding with camera lock')
    camera=cam(page);page.mouse.move(**pos(page));page.mouse.down();page.mouse.wheel(0,120);check(cam(page)==camera,'wheel cannot zoom while B₁ owns gesture');page.mouse.up();page.keyboard.press('Escape')
    for key in ['A','D','N']:page.mouse.click(**pos(page,key,True))
    check(selected(page)==['A','D','N'],'vertex label multiselect accumulates')
    page.mouse.click(**blank(page));check(selected(page)==['A','D','N'],'blank click preserves selection')
    page.evaluate('__S.setT(.45)');check(page.locator('#pickBox .pr').last.locator('span').last.text_content()=='(0.866, 0.922, 0.494)','selected moving midpoint coordinate updates at t=0.45')
    page.keyboard.press('Escape');check(selected(page)==[],'Escape clears highlights')
    page.locator('#tab-settings').click()
    for value in ['0','0.5','1']:
        page.locator(f'[data-t="{value}"]').click();check(abs(page.evaluate('__S.state.t')-float(value))<1e-12,'native quick position '+value)
    page.locator('#sT').focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight');check(page.evaluate('__S.state.t>0 && __S.state.t<.01'),'keyboard angle slider moves model')
    layer_map={'cSolid':'faces','cOriginal':'original','cPlane1':'plane1','cPlane2':'plane2','cLineAngle':'lineAngle','cAngles':'angles','cNTrack':'nTrack','cVolume':'volume','cAxes':'axes'}
    page.evaluate('__S.setT(.5)')
    for control,group in layer_map.items():
        page.locator('#'+control).uncheck();check(not page.evaluate(f'__S.groups.{group}.visible'),control+' hides actual geometry')
        page.locator('#'+control).check();check(page.evaluate(f'__S.groups.{group}.visible'),control+' shows actual geometry')
    page.locator('#cSphere').check();check(page.evaluate('__S.groups.sphere.visible && __S.vertexMeshes.O.visible'),'maximum volume circum-sphere and center shown at 90 degrees')
    check(page.evaluate('Math.abs(__GEO.O.distanceTo(__GEO.C)-1)<1e-9 && Math.abs(__GEO.O.distanceTo(__GEO.A)-Math.sqrt(2))<1e-9'),'rendered sphere contains C and passes through vertices')
    page.evaluate('__S.setT(.4)');check(not page.evaluate('__S.groups.sphere.visible || __S.vertexMeshes.O.visible'),'sphere hidden away from claimed maximum-volume position')
    page.locator('#cLabels').uncheck();page.wait_for_timeout(50);check(page.evaluate("__S.labels.filter(l=>l.kind==='vertex').every(l=>!l.visible&&l.hit===null)"),'hidden vertex labels clear hit rectangles')
    page.locator('#cLabels').check();page.locator('#cLengths').check();check(page.evaluate("__S.labels.filter(l=>l.kind==='edge').every(l=>l.visible)"),'length labels have independent switch')
    page.locator('#sFont').focus();page.keyboard.press('End');check(page.evaluate('__S.state.font===32'),'label font up to 32px')
    page.locator('#sOpacity').focus();page.keyboard.press('End');check(page.evaluate('__S.groups.faces.children.every(x=>x.material.opacity===.5) && __S.groups.plane1.children[0].material.opacity===.5'),'opacity modifies base and fold face materials')
    for quality in ['save','sharp','auto']:
        page.locator(f'[data-quality="{quality}"]').click();check(page.evaluate('__S.state.quality')==quality,'quality '+quality)
    before=page.evaluate('JSON.stringify([__S.state,__S.cam,__S.target.toArray(),[...__S.selected]])')
    page.locator('[data-proof="2"]').click();check(page.evaluate('JSON.stringify([__S.state,__S.cam,__S.target.toArray(),[...__S.selected]])')==before,'formula navigation preserves display, angle, camera and selection')
    page.locator('#tab-settings').click();page.evaluate('__S.setT(.9)');page.locator('#speed').select_option('60');page.locator('#play').click();page.wait_for_timeout(650)
    check(page.evaluate('__S.state.playing && __S.state.t<1 && __S.state.t>.8') and constraint(page),'playback reverses at 180 degrees and respects constraint')
    page.locator('#play').click();check(not page.evaluate('__S.state.playing'),'native pause stops playback');page.wait_for_timeout(100);paused=page.evaluate('__S.state.t');page.wait_for_timeout(300);check(page.evaluate('__S.state.t')==paused,'paused angle remains fixed')
    page.locator('#play').click();page.wait_for_timeout(80);page.mouse.click(**pos(page));check(not page.evaluate('__S.state.playing'),'grabbing B₁ pauses playback')
    page.locator('#cSphere').uncheck();page.evaluate('__S.setT(.5)');page.wait_for_timeout(60)
    count=page.evaluate('__S.renderer.info.memory.geometries');page.evaluate('''async()=>{for(let i=0;i<100;i++){__S.setT((i%41)/40);await new Promise(requestAnimationFrame);}__S.setT(.5)}''');page.wait_for_timeout(80)
    check(page.evaluate('__S.renderer.info.memory.geometries')==count,'100 rendered folding updates keep geometry count stable')
    page.wait_for_timeout(400);frames=page.evaluate('__S.renderCount');page.wait_for_timeout(600);check(page.evaluate('__S.renderCount')==frames,'paused idle adds zero render frames')
    metrics['desktop']={'geometries':count,'idleAdditionalFrames':0,'maxMouseParameterError':max(drag_errors)}
    # The approved camera direction and sensitivity are retained.
    page.locator('#reset').click();page.wait_for_timeout(370);initial=page.evaluate('({...__S.cam})');start=blank(page);mouse_drag(page,start,{'x':start['x']+50,'y':start['y']+25});end=page.evaluate('({...__S.cam})')
    check(abs(end['azim']-(initial['azim']-.3))<1e-9 and abs(end['elev']-(initial['elev']+.15))<1e-9,'mouse rotation sensitivity 0.006 rad per CSS pixel')
    observed=page.evaluate('[__S.cam.azim,__S.cam.elev]');page.locator('#fit').click();page.wait_for_timeout(370);check(page.evaluate('[__S.cam.azim,__S.cam.elev]')==observed,'centering preserves orientation')
    page.locator('#reset').click();page.wait_for_timeout(370);check(page.evaluate('__S.cam.azim===__S.DEFAULT_VIEW.azim && __S.cam.elev===__S.DEFAULT_VIEW.elev'),'reset and spatial use the same default camera')
    start=blank(page);old=cam(page);page.mouse.move(**start);page.mouse.down(button='right');page.mouse.move(start['x']+30,start['y']+15,steps=8);page.mouse.up(button='right');page.wait_for_timeout(50);check(cam(page)!=old,'right mouse pans the scene')
    old=page.evaluate('__S.cam.dist');page.mouse.wheel(0,100);page.wait_for_timeout(50);check(page.evaluate('__S.cam.dist')!=old,'mouse wheel changes zoom')
    page.locator('#reset').click();page.wait_for_timeout(370)
    check(page.evaluate('inputs.length>0 && inputs.every(e=>e.trusted && e.type==="mouse")'),'trusted mouse Pointer Events')
    check(not errors,'desktop checks without page exceptions');context.close()
    for size in [(820,1180),(1180,820),(390,844)]:
        context,page,errors,requests=launch(browser,size,touch=True);session=context.new_cdp_session(page)
        page.evaluate("window.inputs=[];cv.addEventListener('pointerdown',e=>inputs.push({trusted:e.isTrusted,type:e.pointerType}))")
        err=[]
        for target in [.2,.65,1.08,-.08,.5]:
            camera=cam(page);touch_drag(session,pos(page),pos(page,t=target));page.wait_for_timeout(60);delta=abs(page.evaluate('__S.state.t')-max(0,min(1,target)));err.append(delta)
            check(delta<.003 and constraint(page),f'trusted touch constrained B₁ drag {target} at {size}')
            check(cam(page)==camera,f'touch camera lock {target} at {size}')
        for key in ['B1']:
            start=pos(page,key,True);camera=cam(page);touch_drag(session,start,{'x':start['x']+20,'y':start['y']-45});page.wait_for_timeout(50)
            check(cam(page)==camera and constraint(page),f'trusted touch label dragging at {size}')
        page.evaluate('__S.setT(.4)');page.wait_for_timeout(50);start=pos(page);camera=cam(page)
        touch(session,'touchStart',[{**start,'id':1}]);touch(session,'touchStart',[{**start,'id':1},{'x':65,'y':480,'id':2}]);touch(session,'touchMove',[{**pos(page,t=.6),'id':1},{'x':120,'y':480,'id':2}]);touch(session,'touchEnd',[])
        check(cam(page)==camera,'second finger cannot take point camera lock '+str(size))
        touch(session,'touchStart',[{**pos(page),'id':1}]);touch(session,'touchCancel',[]);check(page.evaluate('__S.pointers===0 && __S.gesture===null'),'touch cancellation clears gesture '+str(size))
        angles=page.evaluate('[__S.cam.azim,__S.cam.elev]');start=blank(page);touch_drag(session,start,{'x':start['x']+40,'y':start['y']+20});page.wait_for_timeout(50);after=page.evaluate('[__S.cam.azim,__S.cam.elev]');check(abs(after[0]-(angles[0]-.24))<1e-6 and abs(after[1]-(angles[1]+.12))<1e-6,'single-finger camera recovers with 0.006 sensitivity '+str(size))
        start=blank(page);dist=page.evaluate('__S.cam.dist');touch(session,'touchStart',[{**start,'id':1},{'x':start['x']+100,'y':start['y'],'id':2}]);touch(session,'touchMove',[{'x':start['x']-10,'y':start['y']+10,'id':1},{'x':start['x']+140,'y':start['y']+10,'id':2}]);touch(session,'touchEnd',[]);page.wait_for_timeout(50)
        check(page.evaluate('__S.cam.dist')<dist,'trusted two-finger zoom and pan '+str(size))
        check(page.evaluate('inputs.length>0 && inputs.every(e=>e.trusted && e.type==="touch")'),'trusted touch Pointer Events '+str(size))
        page.locator('#menu').tap();page.wait_for_timeout(280);box=page.locator('#panel').bounding_box()
        check(page.evaluate("!document.getElementById('panel').inert && document.getElementById('panel').getAttribute('aria-modal')==='true'"),'drawer focus state '+str(size))
        if size[0]<size[1]:check(abs(box['width']-size[0])<1 and box['y']>0,'portrait bottom drawer '+str(size))
        else:check(abs(box['width']-390)<1 and abs(box['x'])<1,'landscape left drawer '+str(size))
        page.locator('#tab-settings').tap();check(page.locator('#play').is_visible() and page.locator('#sT').is_visible(),'play/pause and angle visible in tablet settings '+str(size))
        page.keyboard.press('Escape');page.wait_for_timeout(270);check(page.evaluate("document.getElementById('panel').inert && !document.getElementById('panel').classList.contains('open')"),'Escape closes drawer and disables hidden focus '+str(size))
        check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'no horizontal viewport overflow '+str(size))
        check(not errors and not any(u.startswith(('http:','https:')) for u in requests),'tablet/phone offline no errors '+str(size))
        metrics[str(size)]={'maximumTouchParameterError':max(err),'coarse':page.evaluate("matchMedia('(pointer:coarse)').matches")};context.close()
    context,page,errors,requests=launch(browser,debug=False);check(page.evaluate('!window.__S && !window.__GEO'),'release URL has no debug handles');context.close();browser.close()
report={'passed':len(checks),'checks':checks,'metrics':metrics,'htmlSHA256':hashlib.sha256(PAGE.read_bytes()).hexdigest(),'unverified':['实体 iPad/Safari；其他浏览器与硬件'], 'inputTolerance':'参数误差 <0.003（0.54°），浏览器像素量化；解析反解单独要求 1e-9。'}
(OUT/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'metrics':metrics},ensure_ascii=False,indent=2))
