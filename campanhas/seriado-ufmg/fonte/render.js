const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:2000},deviceScaleFactor:1});
await p.goto('file://'+path.resolve(__dirname,'estaticos.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
const map={s1:'carrossel-1-polemico',s2:'carrossel-2-o-que-e',s3:'carrossel-3-semana',s4:'carrossel-4-preco',feed:'criativo-A-feed',story:'criativo-B-story'};
for(const [id,n] of Object.entries(map)){await p.locator('#'+id).screenshot({path:path.resolve(__dirname,'../png/'+n+'.png')});}
await b.close();})();
