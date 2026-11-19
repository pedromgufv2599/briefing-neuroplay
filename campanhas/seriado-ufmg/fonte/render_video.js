const {chromium}=require('playwright');const path=require('path');const {spawn}=require('child_process');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(__dirname,'video.html'));await p.evaluate(()=>document.fonts.ready);
const out=path.resolve(__dirname,'../video/jeca-seriado-ufmg-40s.mp4');
const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-i',path.resolve(__dirname,'../video/trilha-seriado-ufmg-40s.wav'),'-shortest','-c:v','libx264','-pix_fmt','yuv420p','-preset','medium','-crf','20','-af','loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000','-c:a','aac','-b:a','192k','-movflags','+faststart',out],{stdio:['pipe','ignore','inherit']});
const N=40*30;
for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/30);const buf=await p.screenshot({type:'jpeg',quality:92});
 if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150===0)console.error('frame',i);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();})();
