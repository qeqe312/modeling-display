from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import os
import hashlib

DEV=Path(__file__).resolve().parent
PAGE=DEV.parent/'成品'/'菱形沿AM翻折与动点.html'
OUT=DEV/'验证记录'/'截图'
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    results=[]
    for name,size,touch in [('电脑',(1600,1000),False),('平板竖屏',(820,1180),True),('平板横屏',(1180,820),True),('手机',(390,844),True)]:
        context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=touch,is_mobile=touch,offline=True,device_scale_factor=1)
        page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e).replace(PAGE.as_uri(),PAGE.name).replace(str(PAGE),PAGE.name)))
        page.goto(PAGE.as_uri()+'#geo-debug');page.wait_for_function('window.__S && __S.renderCount>0');page.wait_for_timeout(250)
        frames=page.evaluate('__S.renderCount');page.wait_for_timeout(500);idle_frames=page.evaluate('__S.renderCount')-frames
        screenshots={'model':name+'-模型.png','lesson':name+'-题目讲解.png','settings':name+'-显示设置.png','answer':name+'-完整答案.png','sphere':name+'-最大体积外接球.png'}
        page.screenshot(path=str(OUT/screenshots['model']))
        layout=page.evaluate('''()=>{const r=cv.getBoundingClientRect(),vertices=__S.labels.filter(l=>l.kind==='vertex'&&l.visible);let overlaps=0;for(let i=0;i<vertices.length;i++)for(let j=i+1;j<vertices.length;j++){const a=vertices[i].hit,b=vertices[j].hit;if(a&&b&&Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0)>1&&Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0)>1)overlaps++;}return {vertexLabelOverlaps:overlaps,viewportOverflow:document.documentElement.scrollWidth>innerWidth,baseHeight:__GEO.M.y,azimuth:__S.cam.azim,elevation:__S.cam.elev}}''')
        if touch:
            page.locator('#menu').tap();page.wait_for_timeout(280)
            page.wait_for_function("document.getElementById('panel').classList.contains('open') && !document.getElementById('panel').inert")
            page.locator('#tab-lesson').tap()
        else:
            page.locator('#tab-lesson').click()
        page.wait_for_function("document.getElementById('tab-lesson').getAttribute('aria-selected') === 'true' && !document.getElementById('lesson-panel').hidden")
        page.screenshot(path=str(OUT/screenshots['lesson']))
        page.evaluate('__S.focusProof(3)');page.wait_for_timeout(420);page.screenshot(path=str(OUT/screenshots['answer']))
        if touch:page.locator('#tab-settings').tap()
        else:page.locator('#tab-settings').click()
        page.wait_for_function("document.getElementById('tab-settings').getAttribute('aria-selected') === 'true' && !document.getElementById('settings-panel').hidden")
        page.wait_for_timeout(70)
        page.locator('.panel-scroll').evaluate('el=>el.scrollTop=0')
        page.screenshot(path=str(OUT/screenshots['settings']))
        page.evaluate("__S.state.sphere=true;document.getElementById('cSphere').checked=true;__S.setT(.5);__S.updateVisibility()")
        if touch:
            page.locator('#close').tap();page.wait_for_timeout(280)
        page.wait_for_timeout(90);page.screenshot(path=str(OUT/screenshots['sphere']))
        page.evaluate("__S.state.sphere=false;document.getElementById('cSphere').checked=false;__S.setT(1/3);__S.updateVisibility()")
        if not touch:
            # Extra states demonstrate the live readout and the endpoint degeneracy.
            for key,t in [('internal',.25),('endpoint',0)]:
                page.evaluate('t => __S.setT(t)',t)
                page.wait_for_timeout(90)
                screenshots[key]='翻折-内部位置.png' if key=='internal' else '翻折-展开端点.png'
                page.screenshot(path=str(OUT/screenshots[key]))
            page.evaluate('__S.setT(1/3)');page.wait_for_timeout(90)
        results.append({'name':name,'viewport':{'width':size[0],'height':size[1]},'hasTouch':touch,'isMobile':touch,'coarsePointer':page.evaluate("matchMedia('(pointer:coarse)').matches"),'screenshots':screenshots,'errors':list(errors),'frames':frames,'idleFrames':idle_frames,'angle':page.evaluate('__S.values.theta'),'geometries':page.evaluate('__S.renderer.info.memory.geometries'),'layout':layout,'htmlSHA256':hashlib.sha256(PAGE.read_bytes()).hexdigest()})
        context.close()
    browser.close()
    (OUT/'inspection.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
