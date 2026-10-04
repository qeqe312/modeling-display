from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import os
import sys
import hashlib

ROOT=Path(__file__).resolve().parent
PACKAGE=(Path(sys.argv[1]).expanduser() if len(sys.argv)>1 else ROOT.parent/'成品').resolve()
PAGE=PACKAGE/'正四面体内外接球与对棱夹角.html'
OUT=ROOT/'验证记录'/'截图'
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    results=[]
    for name,size,touch in [('desktop',(1600,1000),False),('portrait',(820,1180),True),('landscape',(1180,820),True),('phone',(390,844),True)]:
        context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=touch,is_mobile=touch,offline=True,device_scale_factor=1)
        page=context.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e).replace(PAGE.as_uri(),PAGE.name).replace(str(PAGE),PAGE.name)))
        page.goto(PAGE.as_uri()+'#geo-debug');page.wait_for_function('window.__S && __S.renderCount>0');page.wait_for_timeout(180)
        screenshots={'model':name+'.png'}
        page.screenshot(path=str(OUT/screenshots['model']))
        info=page.evaluate('''() => ({frames:__S.renderCount,geometries:__S.renderer.info.memory.geometries,drawCalls:__S.renderer.info.render.calls,pixelRatio:__S.renderer.getPixelRatio(),stage:__S.dimensions,allCardsUnfolded:[...document.querySelectorAll('[data-lesson]')].every(x=>!x.hidden)})''')
        before=info['frames'];page.wait_for_timeout(500);info['idleFrames']=page.evaluate('__S.renderCount')-before
        if touch:
            page.locator('#menu').tap();page.wait_for_timeout(280)
            page.wait_for_function("document.getElementById('panel').classList.contains('open') && !document.getElementById('panel').inert")
            page.locator('#tab-lesson').tap()
            page.wait_for_function("document.getElementById('tab-lesson').getAttribute('aria-selected') === 'true' && !document.getElementById('lesson-panel').hidden")
            screenshots['lesson']=name+'-proof.png'
            page.screenshot(path=str(OUT/screenshots['lesson']))
            page.locator('#tab-settings').tap()
        else:
            page.locator('#tab-settings').click()
        page.wait_for_function("document.getElementById('tab-settings').getAttribute('aria-selected') === 'true' && !document.getElementById('settings-panel').hidden")
        page.wait_for_timeout(70)
        screenshots['settings']=name+'-settings.png'
        page.screenshot(path=str(OUT/screenshots['settings']))
        page.locator('#tab-lesson').click()
        page.locator('#proof-3').scroll_into_view_if_needed()
        page.wait_for_timeout(80)
        screenshots['answer']=name+'-answer.png'
        page.screenshot(path=str(OUT/screenshots['answer']))
        page.locator('#tab-settings').click()
        for control in ['cSphere','cInner','cOpposite','cGuide','cAngles']:
            page.locator('#'+control).uncheck()
        page.locator('#cAxes').check()
        if touch:
            page.locator('#close').tap();page.wait_for_timeout(280)
        page.wait_for_timeout(80)
        screenshots['axes']=name+'-axes.png'
        page.screenshot(path=str(OUT/screenshots['axes']))
        info.update({'device':name,'viewport':{'width':size[0],'height':size[1]},'hasTouch':touch,'isMobile':touch,'coarsePointer':page.evaluate("matchMedia('(pointer:coarse)').matches"),'screenshots':screenshots,'errors':list(errors),'pageSha256':hashlib.sha256(PAGE.read_bytes()).hexdigest(),'browserVersion':browser.version})
        results.append(info);context.close()
    browser.close()
    (OUT/'inspection.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=True,indent=2))
