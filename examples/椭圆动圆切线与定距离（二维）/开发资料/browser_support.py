"""Shared offline browser fixture for checks and screenshot inspection."""
from pathlib import Path
import os

DEV=Path(__file__).resolve().parent
HTML=DEV.parent/'成品/椭圆动圆切线与定距离.html'
VIEWPORTS=[('电脑',1600,1000,False),('平板竖屏',820,1180,True),('平板横屏',1180,820,True),('手机',390,844,True)]

# Observe real Canvas draw calls and Path2D allocation, independently of debug counters.
CAPTURE=r'''(()=>{
  const Base=window.Path2D;window.__pathAllocations=0;
  window.Path2D=new Proxy(Base,{construct(target,args){window.__pathAllocations++;return Reflect.construct(target,args);}});
  const p=CanvasRenderingContext2D.prototype;
  const clear=p.clearRect,begin=p.beginPath,move=p.moveTo,line=p.lineTo,stroke=p.stroke;
  window.__drawnLines=[];let commands=[];
  p.clearRect=function(...a){window.__drawnLines=[];return clear.apply(this,a)};
  p.beginPath=function(...a){commands=[];return begin.apply(this,a)};
  p.moveTo=function(x,y){commands.push([x,y]);return move.call(this,x,y)};
  p.lineTo=function(x,y){commands.push([x,y]);return line.call(this,x,y)};
  p.stroke=function(...a){if(!a.length&&commands.length)window.__drawnLines.push({points:commands.map(p=>[...p]),width:this.lineWidth,color:this.strokeStyle,dash:this.getLineDash()});return stroke.apply(this,a)};
})();'''

def launch_browser(playwright):
    return playwright.chromium.launch(executable_path=os.environ.get('GEO3D_BROWSER') or os.environ.get('BROWSER_EXECUTABLE_PATH') or None,headless=True,chromium_sandbox=True)

def open_page(browser,size=(1600,1000),touch=False,debug=True,observe=False):
    context=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=touch,is_mobile=touch,offline=True,device_scale_factor=2)
    page=context.new_page();errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    if observe:page.add_init_script(CAPTURE)
    page.goto(HTML.as_uri()+('#geo-debug' if debug else ''))
    if debug:page.wait_for_function('window.__S && __S.renderCount>0')
    page.wait_for_timeout(280)
    return context,page,errors,requests

def position(page,key=None,label=False,world=None):
    return page.evaluate('''o=>{const r=cv.getBoundingClientRect();let a;if(o.label){const l=__S.labels.find(l=>l.key===o.key);a=[l.hit.x+l.hit.w/2,l.hit.y+l.hit.h/2];}else a=__S.screen(o.world||__S.points[o.key]);return {x:r.left+a[0],y:r.top+a[1]}}''',{'key':key,'label':label,'world':world})

def drag(page,a,b,button='left'):
    page.mouse.move(**a);page.mouse.down(button=button);page.mouse.move(**b,steps=14);page.mouse.up(button=button);page.wait_for_timeout(60)

def touch(cdp,kind,points):
    cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})

def touch_drag(cdp,a,b):
    touch(cdp,'touchStart',[{**a,'id':1}])
    for i in range(1,15):touch(cdp,'touchMove',[{'x':a['x']+(b['x']-a['x'])*i/14,'y':a['y']+(b['y']-a['y'])*i/14,'id':1}])
    touch(cdp,'touchEnd',[])

def label_overlaps(page):
    return page.evaluate('''()=>{const a=__S.labels.filter(l=>l.visible&&l.hit),bad=[];for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){const p=a[i].hit,q=a[j].hit;if(p.x<q.x+q.w&&p.x+p.w>q.x&&p.y<q.y+q.h&&p.y+p.h>q.y)bad.push([a[i].key,a[j].key]);}return bad}''')
