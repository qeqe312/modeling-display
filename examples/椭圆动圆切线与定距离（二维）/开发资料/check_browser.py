"""Verify the final offline Canvas example through actual browser input and draw calls."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_support import DEV,HTML,VIEWPORTS,launch_browser,open_page,position,drag,touch,touch_drag,label_overlaps
import hashlib,json,math,platform
from datetime import datetime
from zoneinfo import ZoneInfo

MAX=math.sqrt(8)
checks=[];metrics={}
def check(ok,name):
    if not ok:raise AssertionError(name)
    checks.append(name)
def view(page):return page.evaluate('JSON.stringify(__S.view)')
def selection(page):return page.evaluate('[...__S.selected].sort()')
def p_at(r):
    m=3*(4-r*r)/32
    return [-10*m*m/(3*(1+m*m)),10*m/(3*(1+m*m))]

def verify_drawn_rays(page):
    data=page.evaluate('''()=>({lines:window.__drawnLines,A:__S.screen(__S.points.A),M:__S.screen(__S.points.M),N:__S.screen(__S.points.N),valid:__S.values.valid,d:__S.dimensions})''')
    rays=[l for l in data['lines'] if abs(l['width']-2.1)<1e-5 and l['color']=='#ff7a45']
    check(len(rays) in (2,3,4),'two rays split into visible solid/dashed segments')
    solid=[l for l in rays if not l['dash']];dashed=[l for l in rays if l['dash']]
    check(len(dashed)==2,'both forward rays have dashed external parts')
    for line in rays:
        a,b=line['points'];world=page.evaluate('a=>a.map(p=>__S.world(...p))',[a,b]);mid=[(world[0][i]+world[1][i])/2 for i in range(2)]
        implicit=mid[0]**2/4+mid[1]**2-1
        check(implicit>=-1e-9 if line['dash'] else implicit<=1e-9,'dash corresponds to outside ellipse; solid corresponds to inside')
        direction=[b[0]-a[0],b[1]-a[1]]
        check((a[0]-data['A'][0])*direction[0]+(a[1]-data['A'][1])*direction[1]>=-1e-7,'no backwards extension behind A')
    for line in solid:
        boundary=page.evaluate('p=>__S.world(...p)',line['points'][-1]);check(abs(boundary[0]**2/4+boundary[1]**2-1)<1e-9,'solid ends at actual ellipse intersection')
    for line in dashed:
        end=line['points'][-1];check(min(abs(end[0]),abs(end[1]),abs(end[0]-data['d']['width']),abs(end[1]-data['d']['height']))<1e-8,'dashed ray ends at canvas edge')
    chord=[l for l in data['lines'] if abs(l['width']-3.3)<1e-5 and l['color']=='#a692e8']
    check(len(chord)==(1 if data['valid'] else 0),'one chord segment exactly when defined')
    if chord:check(math.dist(chord[0]['points'][0],data['M'])<1e-8 and math.dist(chord[0]['points'][1],data['N'])<1e-8,'MN contains no extension')

def run():
    with sync_playwright() as p:
        browser=launch_browser(p);metrics['browser']=browser.version
        context,page,errors,requests=open_page(browser,observe=True)
        check(not errors,'offline startup without page errors');check(not any(u.startswith(('http:','https:')) for u in requests),'no network resources')
        check(page.locator('[data-lesson]').evaluate_all('a=>a.length===4&&a.every(e=>!e.hidden)'),'complete proofs unfolded')
        check(page.locator('#sR').evaluate("e=>!!e.closest('#settings-panel')"),'motion control in settings')
        worst=0
        for r in [MAX*(i+.5)/101 for i in range(101)]+[1.99999,2.00001]:
            page.evaluate('__S.setR',r);data=page.evaluate('({P:__S.points.P,M:__S.points.M,N:__S.points.N,k:__S.values.k})')
            error=max(abs(a-b) for a,b in zip(data['P'],p_at(r)));worst=max(worst,error)
            check(error<1e-9,'actual foot matches independent coordinate formula')
            check(all(abs(hit[0]**2/4+hit[1]**2-1)<1e-9 for hit in [data['M'],data['N']]),'actual ellipse intersections')
            check(abs(data['k'][0]*data['k'][1]-1)<1e-9,'finite slopes have product one')
        metrics['coordinateMaxResidual']=worst
        for r in [0,2,MAX]:
            page.evaluate('__S.setR',r);page.wait_for_timeout(30)
            check(not page.evaluate('__S.values.valid'),'degenerate radius correctly marked')
            check(page.locator('#rLength').inner_text()=='未定义' and page.locator('#rProduct').inner_text()=='未定义','undefined values never replaced by limits')
            check(page.evaluate("__S.labels.find(l=>l.key==='P').hit===null"),'undefined P has no ghost hitbox')
        projection=page.evaluate('''()=>{const old={...__S.view};let error=0;for(let scale of [12,40,150,1000])for(let cx of [-5,0,3]){Object.assign(__S.view,{scale,cx,cy:.7});for(let i=0;i<100;i++){let p=[i/13-3,i/27-2],q=__S.world(...__S.screen(p));error=Math.max(error,...p.map((n,j)=>Math.abs(n-q[j])));}}Object.assign(__S.view,old);return error}''')
        metrics['orthographicRoundtripMaxError']=projection;check(projection<1e-9,'1200 planar coordinate roundtrips at multiple scales and pans')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50)
        for r in [.8,2.45,1.4]:
            old=view(page);before=selection(page);drag(page,position(page,'R'),position(page,world=[r,2]))
            check(abs(page.evaluate('__S.state.r')-r)<.025,'trusted mouse handle drag precision')
            check(view(page)==old and selection(page)==before,'handle drag locks view and does not select')
            check(abs(float(page.locator('#sR').input_value())-page.evaluate('__S.state.r'))<.001,'drag synchronizes slider')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);a=position(page,'R',True);old=view(page)
        page.mouse.move(**a);page.mouse.down();check(page.evaluate('__S.state.r')==1.4,'R label grab has no jump');page.mouse.move(a['x']+40,a['y'],steps=12);page.mouse.up();page.wait_for_timeout(50)
        check(page.evaluate('__S.state.r')>1.7 and view(page)==old,'R label drags with position offset')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);old=view(page)
        drag(page,position(page,world=[-1.4,2]),position(page,world=[-.8,2]));check(abs(page.evaluate('__S.state.r')-.8)<.025 and view(page)==old,'circle circumference is directly draggable')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);old=view(page)
        drag(page,position(page,'P'),position(page,world=p_at(2.45)));check(abs(page.evaluate('__S.state.r')-2.45)<.05 and view(page)==old,'P crosses excluded r=2 continuously onto the other arc')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);a=position(page,'P',True);page.mouse.move(**a);page.mouse.down();check(page.evaluate('__S.state.r')==1.4,'P label grab has no jump');page.mouse.move(a['x']-10,a['y']-35,steps=12);page.mouse.up();page.wait_for_timeout(50)
        check(page.evaluate('__S.state.r')!=1.4 and abs(page.evaluate('Math.hypot(__S.points.P[0]+5/3,__S.points.P[1])-5/3'))<1e-12,'P label stays constrained')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);drag(page,position(page,'R'),position(page,world=[3.5,2]));check(page.evaluate('__S.state.r')==MAX,'radius overshoot clamps to legal display range')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50)
        for key in ['A','Q','D']:page.mouse.click(**position(page,key,True))
        check(selection(page)==['A','D','Q'],'label multiselect');page.mouse.click(**position(page,'Q',True));check(selection(page)==['A','D'],'tap toggles selection')
        page.mouse.click(**position(page,world=[-3,3]));check(selection(page)==['A','D'],'empty click preserves selection');page.keyboard.press('Escape');check(not selection(page),'Escape clears highlights')
        old=view(page);drag(page,position(page,world=[-3,3]),position(page,world=[-2.5,3.4]));check(view(page)!=old,'blank drag pans')
        oldscale=page.evaluate('__S.view.scale');page.mouse.move(**position(page,world=[0,2]));page.mouse.wheel(0,-160);page.wait_for_timeout(50);check(page.evaluate('__S.view.scale')>oldscale,'mouse wheel zooms');page.locator('#fit').click()
        page.locator('#tab-settings').click();page.locator('#sR').focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight');check(abs(page.evaluate('__S.state.r')-.001)<1e-12,'native keyboard slider drives model');page.locator('[data-r="1.4"]').click()
        for el in page.locator('[data-layer]').all():
            key=el.get_attribute('data-layer');before=page.locator('#cv').screenshot();on=el.is_checked();el.set_checked(not on);page.wait_for_timeout(30)
            check(before!=page.locator('#cv').screenshot(),'layer affects rendered pixels: '+key);el.set_checked(on)
        page.locator('#cLabels').uncheck();page.wait_for_timeout(30);check(page.evaluate('__S.labels.filter(l=>!l.length).every(l=>!l.visible&&l.hit===null)'),'hidden labels remove hitboxes');page.locator('#cLabels').check()
        page.locator('#cLengths').check();page.wait_for_timeout(40);check(page.evaluate('__S.labels.filter(l=>l.length).every(l=>l.visible)'),'length labels functional');page.locator('#cLengths').uncheck()
        for n in ['14','32','22']:
            page.locator('#sFont').fill(n);page.locator('#sFont').dispatch_event('input');page.wait_for_timeout(40);check(page.locator('#labels .lab').first.evaluate('e=>getComputedStyle(e).fontSize')==n+'px','label font control affects pixels')
        page.locator('#sOpacity').fill('30');page.locator('#sOpacity').dispatch_event('input');page.wait_for_timeout(30);before=page.locator('#cv').screenshot();page.locator('#sOpacity').fill('0');page.locator('#sOpacity').dispatch_event('input');page.wait_for_timeout(30);check(before!=page.locator('#cv').screenshot(),'fill opacity changes pixels');page.locator('#sOpacity').fill('8');page.locator('#sOpacity').dispatch_event('input')
        page.locator('[data-quality="save"]').click();save=page.evaluate('cv.width');page.locator('[data-quality="sharp"]').click();check(page.evaluate('cv.width')>save,'quality changes raster resolution');page.locator('[data-quality="auto"]').click()
        page.evaluate('__S.setR(1.25)');page.locator('#cAux').uncheck();page.mouse.click(**position(page,'Q',True));old=page.evaluate('JSON.stringify([__S.state,__S.view,[...__S.selected]])');page.locator('[data-proof="3"]').click();check(old==page.evaluate('JSON.stringify([__S.state,__S.view,[...__S.selected]])'),'proof navigation preserves user state')
        page.locator('#tab-settings').click();page.locator('#cAux').check();page.locator('#clear').click();page.evaluate('__S.setR(1.4)');page.locator('#fit').click();page.wait_for_timeout(100)
        count=page.evaluate('__S.renderCount');page.wait_for_timeout(650);check(page.evaluate('__S.renderCount')==count,'idle schedules zero frames')
        paths=page.evaluate('window.__pathAllocations');measure=page.evaluate('__S.metrics.labelMeasurements')
        for i in range(90):page.evaluate('__S.setR',.6+i/100);page.wait_for_timeout(18)
        check(page.evaluate('window.__pathAllocations')==paths,'90 updates allocate no new Path2D');check(page.evaluate('__S.metrics.labelMeasurements')==measure,'ordinary radius motion uses cached label sizes')
        metrics['pathsAfter90Updates']=page.evaluate('window.__pathAllocations');metrics['idleAddedFrames']=0;metrics['trustedMouseDowns']=page.evaluate('__S.metrics.trustedMouse');check(metrics['trustedMouseDowns']>0,'mouse events are browser trusted');check(not errors,'mouse run has no exceptions');context.close()
        context,page,errors,requests=open_page(browser,(820,1180),True);cdp=context.new_cdp_session(page)
        old=view(page);touch_drag(cdp,position(page,'R'),position(page,world=[.8,2]));page.wait_for_timeout(70);check(abs(page.evaluate('__S.state.r')-.8)<.025 and view(page)==old,'trusted touch radius drag and view lock')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);a=position(page,'R',True);old=view(page);touch(cdp,'touchStart',[{**a,'id':1}]);check(page.evaluate('__S.state.r')==1.4,'touch label grab has no jump');touch(cdp,'touchMove',[{'x':a['x']+40,'y':a['y'],'id':1}]);touch(cdp,'touchEnd',[]);check(page.evaluate('__S.state.r')>1.6 and view(page)==old,'trusted touch R label drag')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);a=position(page,'R');b=position(page,world=[-3,2]);old=view(page)
        touch(cdp,'touchStart',[{**a,'id':1}]);touch(cdp,'touchStart',[{**a,'id':1},{**b,'id':2}]);touch(cdp,'touchMove',[{'x':a['x']+30,'y':a['y'],'id':1},{'x':b['x']-30,'y':b['y']+20,'id':2}]);page.mouse.wheel(0,-120);check(view(page)==old,'second finger and wheel cannot steal model drag');touch(cdp,'touchEnd',[])
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);old=view(page);touch_drag(cdp,position(page,'P'),position(page,world=p_at(.8)));page.wait_for_timeout(70);check(abs(page.evaluate('__S.state.r')-.8)<.06 and view(page)==old,'trusted touch P drag and constraint')
        page.evaluate('__S.setR(1.4)');page.wait_for_timeout(50);old=view(page);touch_drag(cdp,position(page,world=[-2.8,2.8]),position(page,world=[-2.4,3.1]));page.wait_for_timeout(50);check(view(page)!=old,'single touch pans empty canvas');page.locator('#fit').click()
        a=position(page,world=[-2.5,2.8]);b=position(page,world=[-.5,2.8]);scale=page.evaluate('__S.view.scale');touch(cdp,'touchStart',[{**a,'id':1},{**b,'id':2}]);touch(cdp,'touchMove',[{'x':a['x']-30,'y':a['y'],'id':1},{'x':b['x']+30,'y':b['y'],'id':2}]);touch(cdp,'touchEnd',[]);page.wait_for_timeout(50);check(page.evaluate('__S.view.scale')>scale,'trusted pinch zoom')
        a=position(page,'R');touch(cdp,'touchStart',[{**a,'id':1}]);touch(cdp,'touchCancel',[]);check(page.evaluate('__S.gesture===null'),'touch cancellation clears gesture')
        metrics['trustedTouchDowns']=page.evaluate('__S.metrics.trustedTouch');check(metrics['trustedTouchDowns']>0 and not errors,'trusted touch without exceptions');context.close()
        for name,w,h,has_touch in VIEWPORTS:
            context,page,errors,requests=open_page(browser,(w,h),has_touch,observe=True)
            check(not errors and not page.evaluate('document.documentElement.scrollWidth>innerWidth'),name+' no overflow or errors');check(not label_overlaps(page),name+' default labels separated')
            expected=w if has_touch and h>w else 390;check(page.locator('#panel').evaluate('e=>Math.round(e.getBoundingClientRect().width)')==expected,name+' expected panel width')
            for r in [0,.8,1.4,2,2.45,MAX]:
                page.evaluate('__S.setR',r);page.locator('#fit').click();page.wait_for_timeout(40);verify_drawn_rays(page);check(not label_overlaps(page),name+' labels separated at sampled radius')
            if has_touch:
                page.locator('#menu').click();page.wait_for_timeout(280);rect=page.locator('#panel').bounding_box();check(abs(rect['x'])<1 and (rect['y']>72 if h>w else abs(rect['y']-72)<1),name+' drawer direction');check(not page.locator('#panel').evaluate('e=>e.inert'),name+' open drawer focusable');page.keyboard.press('Escape');page.wait_for_timeout(280);check(page.locator('#panel').evaluate('e=>e.inert'),name+' hidden drawer inert')
            context.close()
        context,page,errors,requests=open_page(browser,debug=False);check(page.evaluate('typeof window.__S')=='undefined','normal page has no debug handle');context.close();browser.close()
    metrics.update({'date':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'platform':platform.system(),
                    'htmlSHA256':hashlib.sha256(HTML.read_bytes()).hexdigest(),'passed':len(checks),
                    'mouseRadiusTolerance':.025,'touchRadiusTolerance':.025,'PDragRadiusTolerance':.06,
                    'unverified':['Physical iPad','Safari','Firefox']})
    (DEV/'验证记录').mkdir(exist_ok=True)
    (DEV/'验证记录/browser-report.json').write_text(json.dumps({'metrics':metrics,'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(metrics,ensure_ascii=True))

if __name__=='__main__':run()
