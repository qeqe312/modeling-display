"""Save the final model, lesson, settings and degenerate screenshots for visual QA."""
from playwright.sync_api import sync_playwright
from browser_support import DEV,HTML,VIEWPORTS,launch_browser,open_page,label_overlaps
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,math

def main():
    out=DEV/'验证记录/截图';out.mkdir(parents=True,exist_ok=True);records=[]
    with sync_playwright() as p:
        browser=launch_browser(p)
        for name,w,h,touch in VIEWPORTS:
            context,page,errors,requests=open_page(browser,(w,h),touch)
            def shot(suffix):
                path=out/(name+'-'+suffix+'.png');page.screenshot(path=str(path))
                records.append({'viewport':[w,h],'touch':touch,'state':suffix,'path':'截图/'+path.name,
                                'labelOverlaps':label_overlaps(page),'errors':list(errors)})
            shot('模型')
            if touch:page.locator('#menu').click();page.wait_for_timeout(280)
            shot('题目讲解')
            if touch:page.keyboard.press('Escape');page.wait_for_timeout(280)
            page.locator('[data-proof="3"]').click();page.wait_for_timeout(350);shot('完整答案')
            page.locator('#tab-settings').click();shot('显示设置')
            if touch:page.keyboard.press('Escape');page.wait_for_timeout(280)
            page.evaluate('__S.setR(2.45)');page.locator('#fit').click();page.wait_for_timeout(70);shot('另一段轨迹')
            for radius,label in [(0,'退化圆'),(2,'竖直切线'),(math.sqrt(8),'切线重合')]:
                page.evaluate('__S.setR',radius);page.locator('#fit').click();page.wait_for_timeout(70);shot(label)
            context.close()
        browser.close()
    report={'date':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'htmlSHA256':hashlib.sha256(HTML.read_bytes()).hexdigest(),'records':records}
    (DEV/'验证记录/inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'screenshots':len(records),'zeroDefaultLabelOverlaps':all(not r['labelOverlaps'] for r in records if r['state']=='模型')},ensure_ascii=True))

if __name__=='__main__':main()
