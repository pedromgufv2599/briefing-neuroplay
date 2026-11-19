# Trilha original: violão dedilhado + terças caipiras + cordas + rio. 72 BPM, 18 compassos = 60 s.
import sys, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
FS=44100; DUR=60.0; N=int(FS*DUR)
BEAT=60/72; BAR=4*BEAT
rng=np.random.default_rng(5)
L=np.zeros(N); R=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def add(sig,t0,pan,gain):
    i=int(t0*FS); j=min(N,i+len(sig)); s=sig[:j-i]*gain
    L[i:j]+=s*np.cos(pan*np.pi/2); R[i:j]+=s*np.sin(pan*np.pi/2)
def pluck(m,dur=3.2,bright=1.0):
    t=np.arange(int(dur*FS))/FS; f=hz(m); out=np.zeros_like(t); pp=0.18
    for k in range(1,16):
        if f*k>9000: break
        a=abs(np.sin(np.pi*k*pp))/k**(1.25-0.2*bright)
        dec=1.1+0.55*k*(f/260)**0.35
        out+=a*np.sin(2*np.pi*f*k*t+rng.random()*6.28)*np.exp(-dec*t)
    att=np.minimum(1,t/0.004)
    nz=rng.standard_normal(len(t))*np.exp(-t/0.012)*0.08
    out=(out*att+nz); return out/np.max(np.abs(out))
def pad(ms,dur):
    t=np.arange(int((dur+1.8)*FS))/FS; out=np.zeros_like(t)
    for m in ms:
        for det in (-0.06,0,0.07):
            f=hz(m)*2**(det/12)
            for k in range(1,7): out+=np.sin(2*np.pi*f*k*t+rng.random()*6.28)/k**2.2
    env=np.minimum(1,t/1.4)*np.clip((dur+1.8-t)/1.8,0,1)
    return out*env/np.max(np.abs(out)+1e-9)
D=[50,57,62,66,69]; Acs=[49,57,61,64,69]; Bm=[47,54,59,62,66]; G=[43,50,55,59,62]
Em=[40,52,59,64,67]; A=[45,52,57,61,64]
PROG=[D,Acs,Bm,G, D,Acs,Bm,G, D,Acs,Bm,G, Em,Bm,G,A, D,D]
PAT=[0,2,4,3,1,3,4,2]
for b,ch in enumerate(PROG):
    t0=b*BAR; bar=b+1
    if bar<=2:       # gancho: notas soltas, respirando
        add(pluck(ch[0],4),t0,0.45,0.55); add(pluck(ch[4]+12,4,1.3),t0+BEAT*1.5,0.6,0.22)
        add(pluck(ch[3],4),t0+BEAT*2.5,0.55,0.25)
    elif bar<=5:     # dedilhado em semínimas, suave
        for k,idx in enumerate([0,2,3,4]):
            add(pluck(ch[idx]),t0+k*BEAT+rng.normal(0,0.008),0.35+0.08*idx,0.42 if k==0 else 0.3)
    elif bar<=16:    # rio: colcheias contínuas
        g=0.30 if bar<15 else 0.36
        for k,idx in enumerate(PAT):
            hum=rng.normal(0,0.009); acc=1.25 if k in (0,4) else 1.0
            add(pluck(ch[idx]),t0+k*BEAT/2+hum,0.3+0.1*idx,g*acc*(1.2 if idx==0 else 1))
        if bar>=15: add(pluck(ch[0]-12,3.5),t0,0.5,0.35)   # baixo em oitava na subida
    else:            # acorde final rasgueado lento
        if bar==17:
            for k,m in enumerate(D+[74,78]): add(pluck(m,6),t0+k*0.045,0.3+0.06*k,0.33)
            add(pluck(38,6),t0,0.5,0.35)
        else:
            add(pluck(81,5,1.3),t0+BEAT,0.6,0.16); add(pluck(78,5,1.3),t0+BEAT*1.5,0.4,0.14)
    if bar>=8 and bar<=17:   # cordas
        gp=0.10 if bar<12 else (0.14 if bar<15 else 0.2)
        if bar==17: gp=0.18
        add(pad(ch[1:4],BAR*(2 if bar==17 else 1)),t0,0.5,gp)
# melodia em terças paralelas (compassos 12-17)
DM=[62,64,66,67,69,71,73]
def terca_abaixo(m):
    pc=[x%12 for x in DM]; i=pc.index(m%12); j=(i-2)%7
    low=m-((DM[i]-DM[j])%12); return low
MEL=[(12,[(74,2),(71,1),(74,1)]),(13,[(76,2),(79,1),(76,1)]),(14,[(78,3),(74,1)]),
     (15,[(79,2),(78,1),(76,1)]),(16,[(76,2),(73,1),(76,1)]),(17,[(78,4)])]
for bar,notes in MEL:
    t=(bar-1)*BAR
    for m,d in notes:
        lift=1.25 if bar>=15 else 1.0
        add(pluck(m,2.6+d*0.5,1.2),t,0.52,0.26*lift); add(pluck(terca_abaixo(m),2.6+d*0.5,1.1),t+0.012,0.46,0.19*lift)
        t+=d*BEAT
# reverb estéreo
def ir(seed):
    r=np.random.default_rng(seed); t=np.arange(int(2.6*FS))/FS
    return r.standard_normal(len(t))*np.exp(-t/0.55)*np.minimum(1,t/0.01)
sos=butter(2,[90,7000],btype="band",fs=FS,output="sos")
L=sosfilt(sos,L); R=sosfilt(sos,R)
wl=fftconvolve(L,ir(1))[:N]; wr=fftconvolve(R,ir(2))[:N]
wl*=np.max(np.abs(L))/np.max(np.abs(wl)); wr*=np.max(np.abs(R))/np.max(np.abs(wr))
L=L+0.35*wl; R=R+0.35*wr
# rio: ruído filtrado com ondulação lenta
t=np.arange(N)/FS
def agua(seed):
    r=np.random.default_rng(seed); n=r.standard_normal(N)
    n=sosfilt(butter(2,[250,2200],btype="band",fs=FS,output="sos"),n)
    mod=0.6+0.25*np.sin(2*np.pi*0.13*t+seed)+0.15*np.sin(2*np.pi*0.41*t+2*seed)
    return n*mod
wa=np.max(np.abs(L))*0.035
L+=agua(3)*wa/np.std(agua(3)); R+=agua(4)*wa/np.std(agua(4))
# envelope geral e normalização
env=np.minimum(1,t/1.5)*np.clip((DUR-t)/3.0,0,1)
L*=env; R*=env
pk=max(np.max(np.abs(L)),np.max(np.abs(R))); L/=pk; R/=pk
st=(np.stack([L,R],1)*0.89*32767).astype(np.int16)
wavfile.write(sys.argv[1],FS,st); print("ok", sys.argv[1])
