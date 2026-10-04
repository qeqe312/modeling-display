from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import os
DEV=Path(__file__).resolve().parent
OUT=DEV/'验证记录'/'截图'
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)
    page=b.new_page(viewport={'width':1600,'height':1000})
    page.goto((DEV.parent/'成品'/'正四棱台2023真题演示.html').as_uri()+'#geo-debug');page.wait_for_function('window.__S && __S.renderCount>0');page.wait_for_timeout(150)
    page.evaluate("window.ev=[];for(const kind of ['pointerdown','pointermove','pointerup'])cv.addEventListener(kind,e=>ev.push({kind,x:e.clientX,y:e.clientY,t:__S.state.t,gesture:__S.gesture,key:__S.pickVertex(e.clientX-cv.getBoundingClientRect().left,e.clientY-cv.getBoundingClientRect().top,e.pointerType)}))")
    results=[]
    for end in [.25,.75,1.2,-.15,.5]:
        positions=page.evaluate('''end=>[__S.state.t,end].map(t=>{const v=__GEO.C.clone().lerp(__GEO.Cp,t).project(__S.camera),r=cv.getBoundingClientRect();return {x:r.left+(v.x*.5+.5)*r.width,y:r.top+(-v.y*.5+.5)*r.height}})''',end)
        page.mouse.move(**positions[0]);page.mouse.down();gesture=page.evaluate('__S.gesture');page.mouse.move(**positions[1],steps=14);page.mouse.up();page.wait_for_timeout(80)
        results.append({'end':end,'gesture':gesture,'t':page.evaluate('__S.state.t'),'down':page.evaluate("ev.filter(e=>e.kind==='pointerdown').slice(-1)")})
    print(json.dumps(results,indent=2))
    page.screenshot(path=str(OUT/'拖动诊断.png'));b.close()
