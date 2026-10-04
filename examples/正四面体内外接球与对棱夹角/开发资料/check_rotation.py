"""Compare trusted rotation input against both retained reference examples."""
from pathlib import Path
import hashlib
import json
import os
from playwright.sync_api import sync_playwright

DEV=Path(__file__).resolve().parent
EXAMPLES=DEV.parents[1]
TITLE='正四面体内外接球与对棱夹角'
TITLES=['外接球题建模示例','正四棱台2023真题演示',TITLE]
checks=[]
results=[]

def check(condition,message):
    if not condition:raise AssertionError(message)
    checks.append(message)

def mouse_drag(page,x,y,dx,dy):
    page.mouse.move(x,y);page.mouse.down()
    page.mouse.move(x+dx,y+dy,steps=12);page.mouse.up()

def touch_drag(cdp,x,y,dx,dy):
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
    for i in range(1,13):
        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+dx*i/12,'y':y+dy*i/12,'id':1}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    for touch in [False,True]:
        for title in TITLES:
            path=EXAMPLES/title/'成品'/(title+'.html')
            context=browser.new_context(viewport={'width':820 if touch else 1600,'height':1180 if touch else 1000},has_touch=touch,is_mobile=touch,offline=True)
            page=context.new_page();errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(path.as_uri()+'#geo-debug');page.wait_for_function('window.__S && __S.renderCount>0');page.wait_for_timeout(100)
            page.evaluate("window.rotationInputs=[];document.getElementById('cv').addEventListener('pointerdown',e=>rotationInputs.push({trusted:e.isTrusted,type:e.pointerType}))")
            canvas=page.locator('#cv').bounding_box();cdp=context.new_cdp_session(page) if touch else None
            deltas=[]
            # Identical deltas at two screen positions must give identical sensitivity.
            for x,y in [(canvas['x']+70,320),(canvas['x']+110,590)]:
                before=page.evaluate('({...__S.cam})')
                (touch_drag(cdp,x,y,80,40) if touch else mouse_drag(page,x,y,80,40))
                after=page.evaluate('({...__S.cam})')
                delta=[after['azim']-before['azim'],after['elev']-before['elev']]
                check(abs(delta[0]+.48)<1e-10 and abs(delta[1]-.24)<1e-10,f'{title}: {"touch" if touch else "mouse"} sensitivity is 0.006 rad/pixel at ({x},{y})')
                deltas.append(delta)
            check(page.evaluate('__S.camera.up.equals(new THREE.Vector3(0,1,0))'),f'{title}: world vertical stays upright')
            check(page.evaluate('rotationInputs.every(e=>e.trusted) && rotationInputs.length===2'),f'{title}: rotation uses trusted browser input')
            check(not errors,f'{title}: no page errors')
            results.append({'example':title,'input':'trusted touch' if touch else 'mouse','deltas':deltas,'pageSha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            context.close()
    version=browser.version;browser.close()
report={'passed':len(checks),'checks':checks,'results':results,'browserVersion':version,'scope':'Chromium mouse and trusted CDP touch; compares the three final example files'}
(DEV/'验证记录/rotation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'browserVersion':version},indent=2))
