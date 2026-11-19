import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1920; C=24; GW,GH=W//C,H//C   # 45 x 80 pinos
F="/tmp/claude-0/-home-user-briefing-neuroplay/9d23b749-3a0b-5941-a4cd-7d4912098701/scratchpad/fonts/"
def font(name,size,wght):
    f=ImageFont.truetype(F+name,size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
HZ=40  # linha do horizonte (em pinos)
# ---------- camada de pinos (independe da cor) ----------
def overlay():
    lt=Image.new("RGBA",(W,H),(0,0,0,0)); dk=Image.new("RGBA",(W,H),(0,0,0,0))
    cl=Image.new("RGBA",(C,C),(0,0,0,0)); cd=Image.new("RGBA",(C,C),(0,0,0,0))
    a=ImageDraw.Draw(cl); b=ImageDraw.Draw(cd)
    # bordas do bloco
    a.line([(0,0),(C-1,0)],fill=(255,255,255,70)); a.line([(0,0),(0,C-1)],fill=(255,255,255,50))
    b.line([(0,C-1),(C-1,C-1)],fill=(0,0,0,110)); b.line([(C-1,0),(C-1,C-1)],fill=(0,0,0,90))
    r=8; cx=cy=C/2-0.5
    b.ellipse([cx-r+2,cy-r+3,cx+r+2,cy+r+3],fill=(0,0,0,70))          # sombra projetada
    b.ellipse([cx-r,cy-r,cx+r,cy+r],outline=(0,0,0,60),width=1)
    a.arc([cx-r+1,cy-r+1,cx+r-1,cy+r-1],200,320,fill=(255,255,255,150),width=2)  # brilho
    a.ellipse([cx-r+3,cy-r+3,cx-r+7,cy-r+6],fill=(255,255,255,120))
    for gy in range(GH):
        for gx in range(GW):
            lt.paste(cl,(gx*C,gy*C)); dk.paste(cd,(gx*C,gy*C))
    return lt,dk
# ---------- cenário em grade ----------
RND=random.Random(3)
FLORES={(RND.randrange(GW),RND.randrange(HZ+3,GH)):RND.choice([(242,205,55),(201,26,9),(255,255,255),(160,110,190)]) for _ in range(70)}
NUV=[(6,9,5),(29,6,6),(38,14,4),(15,16,3)]
ARV=[(4,HZ+1),(41,HZ+2),(9,HZ-1)]
def rio_x(gy):
    p=(gy-HZ)/(GH-HZ)
    return 24+5*math.sin(gy*0.13+0.6)+p*8, 0.6+p*7.5   # centro, meia-largura
def cor(gx,gy,tt,fase):
    # tt: 0 entardecer -> 1 amanhecer
    if gy<HZ:
        u=gy/HZ; band=math.floor(u*9)/9
        top=mix((22,30,74),(88,160,220),tt); mid=mix((124,58,110),(160,205,240),tt); low=mix((246,130,62),(255,214,140),tt)
        c=mix(top,mid,band/0.6) if band<0.6 else mix(mid,low,(band-0.6)/0.4)
        sx,sy=22,HZ-1-4*tt; d=math.hypot(gx-sx,(gy-sy)*1.0)
        if d<5.2: return mix((255,226,120),(255,246,200),tt)
        if d<6.6: return mix(c,(255,200,110),0.55)
        for nx,ny,nl in NUV:
            nx2=(nx+tt*4)%GW
            if (abs(gy-ny)<1 and nx2<=gx<nx2+nl) or (gy==ny-1 and nx2+1<=gx<nx2+nl-1):
                return mix(mix((255,190,170),(255,255,255),tt),c,0.15)
        if not tt and gy<12 and (gx*7+gy*13)%23==0: return (240,230,200)
        # serras
        m=HZ-2-3*abs(math.sin(gx*0.21))-2*abs(math.sin(gx*0.47+1))
        if gy>=m: return mix((92,56,104),(84,130,96),tt)
        return c
    cx,hw=rio_x(gy)
    if abs(gx-cx)<=hw:
        base=mix((14,64,140),(30,110,190),tt)
        mid=mix((40,110,190),(80,160,225),tt)
        k=(gy*1.0 - fase + (gx*3)%5) % 9
        if k<1: return (210,236,255)
        if k<2.2: return mid
        return base if abs(gx-cx)<hw*0.55 else mid
    if abs(gx-cx)<=hw+1.1: return mix((176,146,96),(222,198,140),tt)
    for ax,ay in ARV:
        if gx==ax and ay<=gy<=ay+1: return (110,70,40)
        if abs(gx-ax)+abs(gy-(ay-2))<=2: return mix((30,80,40),(40,130,60),tt)
    if (gx,gy) in FLORES: return FLORES[(gx,gy)]
    p=(gy-HZ)/(GH-HZ)
    g=mix(mix((60,110,50),(110,180,70),tt),mix((24,60,34),(50,120,50),tt),p)
    return g if (gx+gy)%11 else mix(g,(0,0,0),0.12)
def mosaico(tt,fase,LT,DK):
    sm=Image.new("RGB",(GW,GH)); px=sm.load()
    for gy in range(GH):
        for gx in range(GW): px[gx,gy]=cor(gx,gy,tt,fase)
    img=sm.resize((W,H),Image.NEAREST).convert("RGBA")
    img=Image.alpha_composite(img,DK); img=Image.alpha_composite(img,LT)
    return img.convert("RGB")
# ---------- minifigura ----------
YEL=(245,205,48)
def sombra_lado(d,poly,alpha=55):
    d.polygon(poly,fill=(0,0,0,alpha))
def minifig(img,x,y,u,quem,boca=0,prop=None,olhar=0):
    d=ImageDraw.Draw(img,"RGBA")
    if quem=="jeca":
        shirt=(196,40,28); shirt2=(240,232,214); pants=(178,140,92); legs_dark=(140,106,66)
    else:
        shirt=(58,110,190); shirt2=(250,250,250); pants=(40,52,80); legs_dark=(28,36,58)
    # sombra no chão
    d.ellipse([x-1.5*u,y-0.18*u,x+1.5*u,y+0.22*u],fill=(0,0,0,70))
    # pernas
    lw=0.98*u
    for s in (-1,1):
        x0=x+(0.02*u if s>0 else -0.02*u-lw)
        d.rounded_rectangle([x0,y-1.3*u,x0+lw,y],radius=int(0.08*u),fill=pants)
        d.rectangle([x0,y-0.22*u,x0+lw,y],fill=legs_dark)
    d.line([(x,y-1.3*u),(x,y-0.05*u)],fill=(0,0,0,90),width=max(2,int(u*0.04)))
    # quadril
    d.rounded_rectangle([x-1.0*u,y-1.62*u,x+1.0*u,y-1.28*u],radius=int(0.06*u),fill=legs_dark if quem=="jeca" else pants)
    # tronco (trapézio)
    tb,tt_=y-1.62*u,y-3.1*u
    torso=[(x-1.0*u,tb),(x+1.0*u,tb),(x+0.76*u,tt_),(x-0.76*u,tt_)]
    d.polygon(torso,fill=shirt)
    if quem=="jeca":  # xadrez
        for k in range(-4,5):
            xx=x+k*0.24*u; d.line([(xx,tt_),(xx*1+k*0.05*u,tb)],fill=shirt2+(110,),width=max(2,int(0.07*u)))
        for k in range(1,6):
            yy=tt_+k*(tb-tt_)/6; w=0.76*u+(1.0-0.76)*u*k/6
            d.line([(x-w,yy),(x+w,yy)],fill=(90,20,14,120),width=max(2,int(0.06*u)))
        d.polygon([(x-0.25*u,tt_),(x+0.25*u,tt_),(x,tt_+0.45*u)],fill=(240,232,214))  # gola
    else:
        d.polygon([(x-0.3*u,tt_),(x+0.3*u,tt_),(x,tt_+0.55*u)],fill=shirt2)
        for s in (-1,1):  # alças da mochila
            d.line([(x+s*0.55*u,tt_+0.02*u),(x+s*0.75*u,tb-0.05*u)],fill=(40,40,40),width=int(0.16*u))
        d.rounded_rectangle([x-0.38*u,tt_+0.9*u,x+0.38*u,tt_+1.25*u],radius=int(0.08*u),fill=(242,205,55))  # emblema
    sombra_lado(d,[(x+0.35*u,tb),(x+1.0*u,tb),(x+0.76*u,tt_),(x+0.3*u,tt_)],40)
    # braços + mãos
    for s in (-1,1):
        sh=(x+s*0.78*u,tt_+0.15*u); el=(x+s*1.22*u,tt_+1.05*u)
        d.line([sh,el],fill=shirt,width=int(0.46*u)); d.ellipse([sh[0]-0.23*u,sh[1]-0.23*u,sh[0]+0.23*u,sh[1]+0.23*u],fill=shirt)
        d.ellipse([el[0]-0.23*u,el[1]-0.23*u,el[0]+0.23*u,el[1]+0.23*u],fill=shirt)
        hx,hy=el[0]+s*0.05*u,el[1]+0.3*u
        d.ellipse([hx-0.24*u,hy-0.2*u,hx+0.24*u,hy+0.28*u],fill=YEL)
        d.ellipse([hx-0.1*u,hy-0.08*u,hx+0.1*u,hy+0.12*u],fill=mix(YEL,(0,0,0),0.35))
    # objeto na mão (Diadorim)
    if prop and quem=="diadorim":
        hx,hy=x+1.27*u,tt_+1.35*u
        if prop=="gabarito":
            d.polygon([(hx-0.1*u,hy-0.9*u),(hx+0.7*u,hy-1.0*u),(hx+0.8*u,hy+0.1*u),(hx,hy+0.2*u)],fill=(250,250,245))
            for k in range(5):
                yy=hy-0.75*u+k*0.18*u; d.line([(hx+0.05*u,yy),(hx+0.62*u,yy-0.07*u)],fill=(120,120,140),width=2)
            d.ellipse([hx+0.45*u,hy-0.2*u,hx+0.65*u,hy],outline=(201,26,9),width=3)
        else:
            d.rounded_rectangle([hx-0.15*u,hy-0.75*u,hx+0.95*u,hy+0.15*u],radius=6,fill=(201,26,9))
            d.rectangle([hx+0.35*u,hy-0.75*u,hx+0.45*u,hy+0.15*u],fill=(140,14,6))
            d.rectangle([hx-0.05*u,hy-0.65*u,hx+0.3*u,hy+0.05*u],fill=(250,248,240))
    # cabeça
    nk=tt_-0.12*u
    d.rectangle([x-0.35*u,nk,x+0.35*u,tt_+0.02*u],fill=YEL)
    hb,ht=nk,nk-1.0*u
    d.rounded_rectangle([x-0.58*u,ht,x+0.58*u,hb],radius=int(0.24*u),fill=YEL)
    d.rounded_rectangle([x-0.3*u,ht-0.2*u,x+0.3*u,ht+0.05*u],radius=int(0.06*u),fill=YEL)
    d.rounded_rectangle([x+0.22*u,ht+0.05*u,x+0.58*u,hb],radius=int(0.2*u),fill=(0,0,0,30))
    d.line([(x-0.42*u,ht+0.2*u),(x-0.42*u,hb-0.25*u)],fill=(255,255,255,90),width=max(2,int(0.07*u)))
    # rosto
    ex=0.2*u; ey=ht+0.42*u; ox=olhar*0.06*u
    for s in (-1,1): d.ellipse([x+s*ex-0.07*u+ox,ey-0.09*u,x+s*ex+0.07*u+ox,ey+0.09*u],fill=(20,20,20))
    for s in (-1,1): d.ellipse([x+s*ex-0.03*u+ox,ey-0.06*u,x+s*ex+0.0*u+ox,ey-0.02*u],fill=(255,255,255))
    if quem=="jeca":
        for s in (-1,1): d.line([(x+s*0.12*u,ey-0.2*u),(x+s*0.32*u,ey-0.24*u)],fill=(150,150,150),width=max(3,int(0.06*u)))
    my=ht+0.7*u
    if boca: d.ellipse([x-0.13*u,my-0.04*u,x+0.13*u,my+0.16*u],fill=(60,20,20))
    else: d.arc([x-0.2*u,my-0.12*u,x+0.2*u,my+0.1*u],20,160,fill=(20,20,20),width=max(3,int(0.05*u)))
    if quem=="jeca":  # bigode e chapéu de palha
        d.chord([x-0.3*u,my-0.2*u,x+0.3*u,my+0.08*u],180,360,fill=(170,170,170))
        hy=ht+0.08*u; straw=(222,184,104); dark=(176,140,70)
        d.ellipse([x-1.05*u,hy-0.2*u,x+1.05*u,hy+0.2*u],fill=straw)
        d.ellipse([x-1.05*u,hy-0.05*u,x+1.05*u,hy+0.2*u],fill=dark)
        d.ellipse([x-1.0*u,hy-0.22*u,x+1.0*u,hy+0.12*u],fill=straw)
        d.rounded_rectangle([x-0.58*u,hy-0.75*u,x+0.58*u,hy],radius=int(0.2*u),fill=straw)
        d.rectangle([x-0.58*u,hy-0.22*u,x+0.58*u,hy-0.06*u],fill=(160,30,20))
        for k in range(-3,4): d.line([(x+k*0.15*u,hy-0.7*u),(x+k*0.15*u,hy-0.25*u)],fill=dark+(120,),width=2)
        d.rounded_rectangle([x+0.2*u,hy-0.75*u,x+0.58*u,hy],radius=int(0.2*u),fill=(0,0,0,30))
    else:  # cabelo
        hc=(80,50,30)
        d.rounded_rectangle([x-0.64*u,ht-0.22*u,x+0.64*u,ht+0.3*u],radius=int(0.26*u),fill=hc)
        d.polygon([(x-0.64*u,ht+0.1*u),(x-0.1*u,ht+0.1*u),(x-0.64*u,ht+0.55*u)],fill=hc)
        d.rounded_rectangle([x+0.25*u,ht-0.2*u,x+0.64*u,ht+0.3*u],radius=int(0.2*u),fill=(0,0,0,40))
# ---------- texto com destaque ----------
def linha(d,cx,y,txt,f,cor,dest,A,stroke=0):
    partes=[]; neg=False
    for i,p in enumerate(txt.split("*")):
        if p: partes.append((p,i%2==1))
    w=sum(d.textlength(p,font=f) for p,_ in partes); x=cx-w/2
    for p,hl in partes:
        d.text((x+3,y+4),p,font=f,fill=(0,0,0,int(A*0.45)))
        d.text((x,y),p,font=f,fill=(dest if hl else cor)+(A,))
        x+=d.textlength(p,font=f)
