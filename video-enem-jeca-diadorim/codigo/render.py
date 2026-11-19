import sys, subprocess, math; sys.path.insert(0,sys.argv[1]); from bloco import *
OUT=sys.argv[2]; MODO=sys.argv[3]
LT,DK=overlay()
NU="Nunito%5Bwght%5D.ttf"
WH=(255,250,240); YL=(255,206,64); RED=(250,47,34); BLUE=(70,130,220)
CX=510; MAXW=790; TOP=290   # zona segura Reels: texto entre x 90-930 e y 250-1480
def fit(d,lines,size,w=MAXW,wg=850):
    while True:
        f=font(NU,size,wg)
        if max(d.textlength(l.replace("*",""),font=f) for l in lines)<=w or size<30: return f,size
        size-=2
def painel(d,x0,y0,x1,y1,A):
    d.rounded_rectangle([x0,y0,x1,y1],radius=28,fill=(18,16,34,int(165*A)))
    for k in range(4):  # pinos no topo da placa
        cx=x0+60+k*44; d.rounded_rectangle([cx-14,y0-10,cx+14,y0+4],radius=5,fill=(18,16,34,int(165*A)))
def legenda(layer,who,lines,A,nota=None):
    d=ImageDraw.Draw(layer)
    f,sz=fit(d,lines,60); lh=int(sz*1.3)
    h=len(lines)*lh+60+(46 if nota else 0)
    painel(d,CX-430,TOP+40,CX+430,TOP+40+h,A)
    if who:
        col=RED if who=="JECA" else BLUE; fl=font(NU,30,900)
        tw=d.textlength(who,font=fl)
        d.rounded_rectangle([CX-tw/2-26,TOP+12,CX+tw/2+26,TOP+64],radius=26,fill=col+(int(255*A),))
        d.text((CX-tw/2,TOP+17),who,font=fl,fill=(255,255,255,int(255*A)))
    y=TOP+40+34
    for l in lines: linha(d,CX,y,l,f,WH,YL,int(255*A)); y+=lh
    if nota: linha(d,CX,y+4,nota,font(NU,28,600),(255,220,170),YL,int(220*A))
def titulo(layer,linhas,A,y=TOP+20,size=104,sub=None):
    d=ImageDraw.Draw(layer); f,sz=fit(d,linhas,size,wg=950); lh=int(sz*1.12)
    painel(d,CX-440,y,CX+440,y+len(linhas)*lh+70+(70 if sub else 0),A)
    yy=y+30
    for l in linhas: linha(d,CX,yy,l,f,WH,YL,int(255*A)); yy+=lh
    if sub: linha(d,CX,yy+8,sub,font(NU,42,800),(255,225,190),YL,int(255*A)); yy+=70
    return yy+40
def pill(d,y,A):
    fm=font("Montserrat%5Bwght%5D.ttf",44,800); t="NEU BARREIRO"; tw=d.textlength(t,font=fm)
    d.rounded_rectangle([CX-tw/2-40,y,CX+tw/2+40,y+76],radius=38,fill=RED+(int(255*A),))
    d.text((CX-tw/2,y+12),t,font=fm,fill=(255,255,255,int(255*A)))
JX,DX,JY,DY,JU,DU=320,600,1470,1480,104,94
if MODO=="capa":
    img=mosaico(0.72,0,LT,DK)
    minifig(img,JX,JY,JU,"jeca",olhar=1); minifig(img,DX,DY,DU,"diadorim",prop="caderno",olhar=-1)
    layer=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    fk=font(NU,34,900); k="CONSELHOS DO JECA"; d.text((CX-d.textlength(k,font=fk)/2+2,282),k,font=fk,fill=(0,0,0,110)); d.text((CX-d.textlength(k,font=fk)/2,280),k,font=fk,fill=(255,255,255,255))
    yy=titulo(layer,["O gabarito mede","*um domingo*.","*Não mede você.*"],1,y=350,size=104,sub="Pra quem conferiu e doeu.")
    pill(d,1545,1)
    Image.alpha_composite(img.convert("RGBA"),layer).convert("RGB").save(OUT); print("ok"); sys.exit()
FPS=30; DUR=60
CAPS=[
 (0.0, 4.0,"HOOK",["O gabarito mede","*um domingo*.","*Não mede você.*"]),
 (4.2, 9.0,"DIADORIM",["Mas, Jeca… eu estudei tanto.","E *não deu*."]),
 (9.2,16.5,"JECA",["Deu, sim.","Deu *um ano inteiro* de você","ficando mais forte.","Isso nenhuma prova corrige."]),
 (16.7,26.5,"JECA",["Olha o rio, Diadorim.","Ele não chega no mar","em linha reta.","Desvia, espera, cava pedra.","Mas *nunca para de correr*."]),
 (26.7,36.5,"JECA",["Tudo que você aprendeu","*ficou em você*.","E quem escolhe aprender,","*escolhe o bem*. Todo dia.","Mesmo cansado."]),
 (36.7,46.5,"JECA",["Se precisar, chora hoje.","Amanhã, lava o rosto","e *abre o caderno*.","Não pra provar nada a ninguém.","*Pra se reencontrar.*"]),
 (46.7,53.8,"JECA",["O real tá no meio","*da travessia*, Diadorim.","E a sua tá só começando."]),
 (54.0,60.0,"FIM",["A prova foi um dia.","*A jornada é sua.*"]),
]
def al(t,a,b,fd=0.4):
    return 0 if (t<a or t>b) else max(0,min(1,(t-a)/fd,(b-t)/fd))
def ss(x): x=max(0,min(1,x)); return x*x*(3-2*x)
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-c:v","libx264","-pix_fmt","yuv420p","-crf","19","-preset","medium",OUT],stdin=subprocess.PIPE)
for i in range(FPS*DUR):
    t=i/FPS
    tt=0.12+0.83*ss((t-28)/22)              # entardecer -> amanhecer
    img=mosaico(tt,t*6,LT,DK)               # rio corre para baixo
    fala=None
    for a,b,who,_ in CAPS:
        if a+0.3<t<b-0.5: fala=who
    flap=int(t*7)%2
    jb=1 if fala in ("JECA","HOOK") and flap else 0
    db=1 if fala=="DIADORIM" and flap else 0
    bob=lambda on: int(4*math.sin(t*14)) if on else 0
    prop="gabarito" if t<41 else "caderno"
    minifig(img,JX,JY+bob(jb),JU,"jeca",boca=jb,olhar=1)
    minifig(img,DX,DY+bob(db),DU,"diadorim",boca=db,prop=prop,olhar=-1 if fala!="DIADORIM" else 0)
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    for a,b,who,lines in CAPS:
        A=al(t,a,b)
        if A<=0: continue
        if who=="HOOK": titulo(layer,lines,A,y=330,size=110)
        elif who=="FIM":
            yy=titulo(layer,lines,A,y=330,size=100,sub="Manda pra quem precisa ouvir isso."); d=ImageDraw.Draw(layer)
            pill(d,yy+10,A)
        else: legenda(layer,who,lines,A,nota="inspirado em Guimarães Rosa" if a==46.7 else None)
    fr=Image.alpha_composite(img.convert("RGBA"),layer).convert("RGB")
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print("ok")
