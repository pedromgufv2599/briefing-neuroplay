const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+path.resolve(__dirname,'video.html'));
const ch=await p.evaluate(()=>CHUNKS.map(c=>({s:c.start,e:c.end,t:c.words.map(w=>w.w).join(' ')})));
const f=x=>{const ms=Math.round(x*1000);const h=String(Math.floor(ms/3600000)).padStart(2,'0'),m=String(Math.floor(ms/60000)%60).padStart(2,'0'),s=String(Math.floor(ms/1000)%60).padStart(2,'0'),r=String(ms%1000).padStart(3,'0');return `${h}:${m}:${s},${r}`};
fs.writeFileSync(path.resolve(__dirname,'../video/legendas-jeca.srt'),ch.map((c,i)=>`${i+1}\n${f(c.s)} --> ${f(c.e)}\n${c.t}\n`).join('\n'));
await b.close();})();
