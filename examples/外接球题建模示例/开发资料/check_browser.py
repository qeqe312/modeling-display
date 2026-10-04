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
INLINE=PACKAGE/'外接球题建模示例.html'
OFFLINE=PACKAGE/'离线双文件版'/'外接球题建模示例.html'
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
    for path in [INLINE,OFFLINE]:
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
    check(page.evaluate('__S.state.step===3 && __S.state.sphere && __S.state.diameter && __S.state.guide'),'sphere diameter and guides enabled at startup')
    check(page.locator('#rValue3').inner_text()=='50π','surface area readout exact')
    check(page.locator('#options').evaluate("el=>el.classList.contains('reveal')"),'correct choice revealed immediately')
    check(page.locator('#previous,#next,[data-step]').count()==0,'no progressive lesson controls remain')
    expected={'A':[3,0,0],'B':[0,0,0],'C':[0,4,0],'P':[3,0,5],'O':[1.5,2,2.5],'M':[1.5,2,0]}
    data=page.evaluate('Object.fromEntries(Object.entries(__GEO).map(([k,v])=>[k,[v.x+1.5,2-v.z,v.y+2.5]]))')
    check(data==expected,'rendering basis preserves all teaching coordinates')
    # Label/sphere selection, multiselect, stable tap, blank retention.
    page.wait_for_timeout(80)
    before=page.evaluate('JSON.stringify(__S.cam)')
    page.mouse.click(**coords(page,'P',True));check(selection(page)==['P'],'click vertex label selects P')
    check(page.evaluate('JSON.stringify(__S.cam)')==before,'a tap does not rotate camera')
    page.mouse.click(**coords(page,'P',True));check(selection(page)==[],'click selected label deselects')
    for key in ['A','B','P']:page.mouse.click(**coords(page,key))
    check(selection(page)==['A','B','P'],'mouse vertex multiselect accumulates')
    blank={'x':page.locator('#cv').bounding_box()['x']+70,'y':370}
    page.mouse.click(**blank);check(selection(page)==['A','B','P'],'blank tap preserves multiselect')
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
    # Reading any proof preserves manual settings and keeps geometry cached.
    start=page.evaluate('__S.renderer.info.memory.geometries')
    before_state=page.evaluate('JSON.stringify(__S.state)')
    for i in range(24):page.locator(f'[data-proof="{i%4}"]').click()
    check(page.evaluate('JSON.stringify(__S.state)')==before_state,'reading proofs preserves all display settings')
    check(page.locator('[data-lesson]').evaluate_all('els=>els.every(el=>!el.hidden)'),'reading proofs never hides another solution card')
    finish=page.evaluate('__S.renderer.info.memory.geometries');check(finish==start,'geometry count stable after 24 proof jumps')
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
    for key in ['A','P']:
        pos=coords(page,key,True);touch_send(session,'touchStart',[{**pos,'id':1}]);touch_send(session,'touchEnd',[]);page.wait_for_timeout(50)
    check(selection(page)==['A','P'],'touch labels accumulate multiselect')
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
    page.locator('#menu').tap();page.wait_for_timeout(260);page.set_viewport_size({'width':1180,'height':820});page.wait_for_timeout(350)
    check('open' not in (page.locator('#panel').get_attribute('class') or ''),'orientation change closes drawer')
    page.locator('#menu').tap();page.wait_for_timeout(280);rect=page.locator('#panel').bounding_box()
    check(rect['x']==0 and rect['width']<450 and rect['y']==72,'landscape drawer enters from left')
    page.locator('#close').tap();page.wait_for_timeout(280);page.locator('[data-proof="3"]').tap();page.wait_for_timeout(350);check(page.locator('#rValue3').inner_text()=='50π','tablet result displayed while reading proof');check(page.locator('[data-lesson]').evaluate_all('els=>els.every(el=>!el.hidden)'),'tablet drawer contains the complete proof');check(page.locator('#proof-3').is_visible(),'tablet answer proof reachable')
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
        for key in ['A','B','C','P']:
            pos=coords(page,key);check(rect['x']<pos['x']<rect['x']+rect['width'] and rect['y']<pos['y']<rect['y']+rect['height'],f'{key} is on screen at {size}')
        check(not errors,f'no browser errors at {size}');context.close()
    # Normal production URL hides debug controls; missing library is readable.
    context,page,errors,requests=launch_page(browser,debug=False)
    check(page.evaluate('typeof window.__S')=='undefined','production URL does not expose debug state');context.close()
    context=browser.new_context(offline=True);page=context.new_page();page.route('**/three.min.js',lambda route:route.abort());page.goto(OFFLINE.as_uri())
    check(page.locator('#error').is_visible(),'readable message if library is missing');context.close()
    # The approved settings must operate on actual cached model groups.
    context,page,errors,requests=launch_page(browser)
    page.locator('#tab-settings').click()
    for control,group in {'cSolid':'faces','cSphere':'sphere','cDiameter':'diameter','cGuide':'guide','cAngles':'angles','cAxes':'axes'}.items():
        page.locator('#'+control).uncheck();page.wait_for_timeout(30)
        check(not page.evaluate(f'__S.groups.{group}.visible'),f'{control} hides actual model group')
        page.locator('#'+control).check();page.wait_for_timeout(30)
        check(page.evaluate(f'__S.groups.{group}.visible'),f'{control} shows actual model group')
    page.locator('#cLengths').uncheck()
    check(page.evaluate("__S.labels.filter(x=>x.kind==='edge').every(x=>!x.visible)"),'length labels hide independently')
    page.locator('#cLengths').check()
    page.locator('#sOpacity').focus();page.keyboard.press('End');page.wait_for_timeout(50)
    check(page.locator('#sOpacityval').inner_text()=='20%','opacity output updates')
    check(abs(page.evaluate('__S.groups.sphere.children[0].material.opacity')-.2)<1e-12,'opacity slider modifies real sphere material')
    page.locator('[data-quality="save"]').click()
    check(page.evaluate('__S.renderer.getPixelRatio()')==1,'save mode uses pixel ratio 1')
    check(not errors,'full display settings without browser errors');context.close()
    for size in [(390,844),(820,1180),(1180,820)]:
        context,page,errors,requests=launch_page(browser,size=size,touch=True)
        boundary=page.locator('.step-caption').bounding_box()['y']
        for key in ['A','B','C','P']:
            bottom=page.evaluate("key=>__S.labels.find(x=>x.key===key).el.getBoundingClientRect().bottom",key)
            check(bottom<boundary,f'{key} label clears formula panel at {size}')
        context.close()
    browser.close()
report={'passed':len(checks),'checks':checks,'metrics':metrics,'browserVersion':browser.version,'pageSha256':hashlib.sha256(INLINE.read_bytes()).hexdigest(),'scope':'Chromium desktop and emulated touch; real iPad/Safari hardware not tested'}
(ROOT/'验证记录'/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'metrics':metrics},indent=2))
