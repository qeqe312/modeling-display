"""Real Chromium input regression; never launches with --no-sandbox."""
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_demo import build

COUNT = 0


def check(condition, message):
    global COUNT
    if not condition:
        raise AssertionError(message)
    COUNT += 1


def fill_template(text):
    values = {key: "回归测试" for key in set(re.findall(r"__[A-Z0-9_]+__", text))}
    values["__ELEMENT_SWITCHES__"] = ''.join(
        f'<label class="check"><input type="checkbox" id="{key}">测试</label>'
        for key in ("cSolid", "cAxes", "cPlane1", "cPlane2", "cQ1", "cQ3"))
    for key, value in values.items():
        text = text.replace(key, value)
    return text


def coordinates(page, key="P", t=None):
    return page.evaluate("""({key,t}) => {
      var S=window.__S, r=S.renderer.domElement.getBoundingClientRect();
      var v=key==='P' ? (t===null ? S.computeP().clone() : __GEO.C.clone().lerp(__GEO.Cp,t)) : __GEO[key].clone();
      v.project(S.camera);
      return {x:r.left+(v.x*.5+.5)*r.width,y:r.top+(-v.y*.5+.5)*r.height};
    }""", {"key": key, "t": t})


def open_debug(context, path):
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(path.as_uri() + "#geo-debug")
    page.wait_for_function("window.__S && window.__S.pLabelRect")
    page.evaluate("""() => { window.inputEvents=[]; document.getElementById('cv').addEventListener('pointerdown', e => inputEvents.push({trusted:e.isTrusted,type:e.pointerType})); }""")
    return page, errors


def exercise(page):
    # Compare displayed ratios to Euclidean distances, including endpoints.
    for t in (0, .25, .5, .75, 1):
        result = page.evaluate("""t => { __S.setT(t); var p=__S.computeP();
          return {display:document.getElementById('rRatio').textContent,
                  a:p.distanceTo(__GEO.C),b:p.distanceTo(__GEO.Cp),angle:document.getElementById('rAng').textContent}; }""", t)
        a, b = [float(x.strip()) for x in result["display"].split(":")]
        if t == 0:
            check(a == 0 and b == 1, "C endpoint ratio")
        elif t == 1:
            check(a == 1 and b == 0, "Cprime endpoint ratio")
        else:
            check(abs(b / a - result["b"] / result["a"]) < .01, "ratio matches actual distances")
        if t in (0, .5, 1):
            check(abs(float(result["angle"].rstrip("°")) - (90 if t == .5 else 60)) < .1, "angle readout")
    page.evaluate("__S.setT(.5)")
    page.wait_for_timeout(50)
    point = coordinates(page)
    page.mouse.click(**point)
    check(page.evaluate("__S.selKeys.includes('P')"), "select moving point")
    for selector in ('#labels .lab.p.sel', '#selList .chip'):
        contrast = page.locator(selector).evaluate("""el => {
          var s=getComputedStyle(el), rgb=x=>x.match(/[\\d.]+/g).slice(0,3).map(Number);
          var lum=x=>rgb(x).map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
          var a=lum(s.color),b=lum(s.backgroundColor);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
        }""")
        check(contrast >= 4.5, 'selected text meets AA contrast')
    page.mouse.click(**point)
    check(not page.evaluate("__S.selKeys.includes('P')"), "deselect moving point")
    label = page.evaluate("""() => { var l=__S.pLabelRect,r=__S.renderer.domElement.getBoundingClientRect(); return {x:r.left+(l.x0+l.x1)/2,y:r.top+(l.y0+l.y1)/2}; }""")
    page.mouse.click(**label)
    check(page.evaluate("__S.selKeys.includes('P')"), "select label")
    camera = page.evaluate("JSON.stringify(__S.cam)")
    destination = coordinates(page, t=.8)
    page.mouse.move(**label)
    page.mouse.down()
    page.mouse.move(**destination, steps=12)
    page.mouse.up()
    check(abs(page.evaluate("__S.state.t") - .8) < .01, "drag from label")
    check(page.evaluate("JSON.stringify(__S.cam)") == camera, "camera stays locked")
    check(abs(page.evaluate("parseFloat(document.getElementById('sT').value)-__S.state.t")) < .001, "slider synchronized")
    check(page.evaluate("__S.selKeys.every(k=>k==='P')"), "drag does not select other points")
    page.keyboard.press("Escape")
    for key in ("A", "B"):
        page.mouse.click(**coordinates(page, key))
    check(page.evaluate("__S.selKeys.includes('A') && __S.selKeys.includes('B')"), "vertex multiselect")
    rect = page.locator("#cv").bounding_box()
    blank = {"x": rect["x"] + 40, "y": rect["y"] + rect["height"] - 50}
    selected = page.evaluate("JSON.stringify(__S.selKeys)")
    page.mouse.click(**blank)
    check(page.evaluate("JSON.stringify(__S.selKeys)") == selected, "blank preserves selection")
    azimuth = page.evaluate("__S.cam.azim")
    page.mouse.move(**blank)
    page.mouse.down()
    page.mouse.move(blank["x"] + 90, blank["y"] - 40, steps=8)
    page.mouse.up()
    check(page.evaluate("__S.cam.azim") != azimuth, "blank rotates")
    distance = page.evaluate("__S.cam.dist")
    page.mouse.wheel(0, 100)
    page.wait_for_function(f"__S.cam.dist !== {distance}")
    check(page.evaluate("__S.cam.dist") != distance, "wheel zooms")
    old_position = page.evaluate("__S.camera.position.toArray()")
    page.mouse.move(**blank)
    page.mouse.down(button="right")
    page.mouse.move(blank["x"] + 60, blank["y"], steps=5)
    page.mouse.up(button="right")
    check(page.evaluate("__S.camera.position.toArray()") != old_position, "right button pans")
    check(page.evaluate("inputEvents.length>0 && inputEvents.every(e=>e.trusted)"), "browser generates trusted mouse events")
    page.locator('#cLabels').uncheck()
    check(not page.evaluate('__S.state.labels'), 'labels toggle')
    page.locator('#cLabels').check()
    page.locator('#cSolid').uncheck()
    check(not page.evaluate('__S.state.solid'), 'solid toggle')
    page.locator('#cSolid').check()
    page.locator('#sFont').focus()
    page.keyboard.press('Home')
    for _ in range(14):
        page.keyboard.press('ArrowRight')
    check(page.locator('#labels .lab').first.evaluate("el=>getComputedStyle(el).fontSize") == '28px', 'font size control')
    # Test current camera projection against page inverse, not another copied projection.
    for t in (0, .25, .5, .75, 1):
        actual = page.evaluate("""t => {var r=__S.renderer.domElement.getBoundingClientRect(),p=__GEO.C.clone().lerp(__GEO.Cp,t).project(__S.camera); return __S.screenToT((p.x*.5+.5)*r.width,(-p.y*.5+.5)*r.height,r);}""", t)
        check(abs(actual - t) < 1e-12, "screen inverse roundtrip")


def touch_checks(browser, path):
    context = browser.new_context(viewport={"width": 820, "height": 1180}, has_touch=True, is_mobile=True, offline=True)
    page, errors = open_debug(context, path)
    check(page.locator("#toggle").is_visible(), "tablet drawer toggle visible")
    page.locator("#toggle").tap()
    check("open" in page.locator("#panel").get_attribute("class"), "drawer opens")
    page.locator("#toggle").tap()
    page.wait_for_timeout(400)
    session = context.new_cdp_session(page)
    point, destination = coordinates(page), coordinates(page, t=.75)
    before = page.evaluate("JSON.stringify(__S.cam)")
    def send(kind, points):
        session.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": points})
    send("touchStart", [{**point, "id": 1}])
    for i in range(1, 9):
        send("touchMove", [{"x": point["x"] + (destination["x"]-point["x"])*i/8,
                            "y": point["y"] + (destination["y"]-point["y"])*i/8, "id": 1}])
    send("touchEnd", [])
    check(abs(page.evaluate("__S.state.t") - .75) < .01, "touch drags moving point")
    check(page.evaluate("JSON.stringify(__S.cam)") == before, "touch drag locks camera")
    page.keyboard.press("Escape")
    point = coordinates(page)
    send("touchStart", [{**point, "id": 1}])
    send("touchCancel", [])
    check(not page.evaluate("__S.selKeys.includes('P')"), "cancel does not select")
    dist = page.evaluate("__S.cam.dist")
    send("touchStart", [{"x": 100, "y": 900, "id": 1}, {"x": 300, "y": 900, "id": 2}])
    send("touchMove", [{"x": 70, "y": 900, "id": 1}, {"x": 330, "y": 900, "id": 2}])
    send("touchEnd", [])
    check(page.evaluate("__S.cam.dist") < dist, "two-finger pinch zoom")
    check(page.evaluate("inputEvents.some(e=>e.type==='touch' && e.trusted)"), "trusted touch events")
    check(not errors, f"touch page errors: {errors}")
    context.close()


def main():
    with tempfile.TemporaryDirectory(prefix="geo3d-browser-") as tmp, sync_playwright() as playwright:
        base = Path(tmp)
        # Historical-engine regression is independent of the current examples,
        # whose layouts and debug interfaces are checked by their own scripts.
        template = fill_template((ROOT / "assets/template.html").read_text(encoding="utf-8"))
        source = base / "template.html"
        source.write_text(template, encoding="utf-8")
        page_path = build(source, base / "offline")
        inline_path = build(source, base / "inline", True)
        executable = os.environ.get("GEO3D_BROWSER")
        browser = playwright.chromium.launch(headless=True, executable_path=executable, chromium_sandbox=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900}, offline=True)
        for path in (page_path, inline_path):
            page, errors = open_debug(context, path)
            exercise(page)
            check(not errors, f"page errors: {errors}")
            page.close()
        touch_checks(browser, page_path)
        touch_checks(browser, inline_path)
        for path in (page_path, inline_path):
            page = context.new_page()
            page.goto(path.as_uri())
            check(page.evaluate("window.__S === undefined && window.__GEO === undefined"), "production has no debug handles")
            check(page.locator("canvas").count() == 1, "offline mode renders")
            page.close()
        # A malicious name must remain text, even in selected-vertex lists/readouts.
        attack = '<svg onload="document.body.dataset.injected=1"></svg>'
        malicious = template.replace("A:'A'", "A:" + json.dumps(attack))
        source.write_text(malicious, encoding="utf-8")
        path = build(source, base / "safe-label")
        page, errors = open_debug(context, path)
        page.evaluate("__S.selKeys.push('A'); __S.applyPickStyles()")
        check(page.locator("#selList").inner_text() == attack, "malicious label is literal text")
        check(page.locator("svg").count() == 0 and page.evaluate("!document.body.dataset.injected"), "label cannot execute")
        page.close()
        # Four-vertex static model; change only A/B/C configurations, not D engine.
        tetra = template.replace("enabled : true", "enabled : false", 1)
        tetra = re.sub(r'var READOUT = \{.*?\n\};', 'var READOUT = {angle:null,critical:null,coordinate:function(p){return [p.x,p.y,p.z];}};', tetra, count=1, flags=re.S)
        tetra = re.sub(r'var V = \{.*?\n\};', 'var V = {A:[0,0,0],B:[1,0,0],C:[0,1,0],D:[0,0,1]};', tetra, count=1, flags=re.S)
        tetra = re.sub(r'var SOLID_FACES = \[.*?\n\];', "var SOLID_FACES=[{pts:['A','B','C'],opacity:.3},{pts:['A','B','D'],opacity:.3},{pts:['A','C','D'],opacity:.3},{pts:['B','C','D'],opacity:.3}];", tetra, count=1, flags=re.S)
        tetra = re.sub(r'var EDGES = \[.*?\n\];', "var EDGES=[['A','B'],['A','C'],['A','D'],['B','C'],['B','D'],['C','D']];", tetra, count=1, flags=re.S)
        tetra = re.sub(r'function buildDynamicLegacy\(groups\) \{.*?\n\}', 'function buildDynamicLegacy(groups) {}', tetra, count=1, flags=re.S)
        check(tetra.split('【D】引擎')[1] == template.split('【D】引擎')[1], "tetra keeps engine unchanged")
        source.write_text(tetra, encoding="utf-8")
        path = build(source, base / "tetra")
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(path.as_uri()+"#geo-debug")
        page.wait_for_function("window.__S")
        check(page.evaluate("Object.keys(__GEO).length===4"), "tetra starts")
        check(page.locator("#rAng").inner_text() == "—", "no invented static angle")
        check(not errors, f"tetra errors: {errors}")
        page.close()
        # Original loader, missing local file, offline CDN: both real sources fail.
        source.write_text(template, encoding="utf-8")
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(source.as_uri())
        check("Three.js 未能加载" in page.locator('[role="alert"]').inner_text(), "readable missing-library error")
        check(not errors, "missing library handled without exception")
        context.close()
        browser.close()
    print(f"Browser regression: {COUNT} assertions passed (sandbox enabled, offline)")


if __name__ == "__main__":
    main()
