import numpy as np, wave, json, sys
S=sys.argv[1]; B=json.load(open(f'{S}/work/beats.json'))
SR=48000; N=int(SR*B['end'])+SR//2; rng=np.random.default_rng(11)
dry=np.zeros((N,2)); wet=np.zeros((N,2))
def t_(d): return np.arange(int(d*SR))/SR
def place(sig,t,g=1.0,pan=0.0,rev=0.25):
    i=int(t*SR); s=sig[:max(0,min(len(sig),N-i))]*g
    st=np.stack([s*(1-max(0,pan)),s*(1+min(0,pan))],1)
    dry[i:i+len(s)]+=st; wet[i:i+len(s)]+=st*rev
def filt(x,lo=0,hi=SR/2):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
def env(n,a,d): t=np.arange(n)/SR; return np.minimum(1,t/max(a,1e-4))*np.exp(-t/max(d,1e-4))
def tone(f0,f1,d,curve=1.0):
    t=t_(d); f=f0*(f1/f0)**((t/d)**curve); return np.sin(2*np.pi*np.cumsum(f)/SR)
n=lambda d: rng.standard_normal(int(d*SR))
# ambient pad: soft chord, slow swell, cut at light2
dur=B['light2']; t=t_(dur)
pad=sum(a*np.sin(2*np.pi*f*t+ph) for f,a,ph in [(55,0.5,0),(82.4,0.35,1),(110,0.3,2),(164.8,0.16,3),(220.2,0.08,4)])
lfo=0.75+0.25*np.sin(2*np.pi*0.18*t)
sw=np.minimum(1,t/1.6)*(0.55+0.45*np.clip((t-B['reveal']+0.5)/4,0,1))*lfo
air=filt(n(dur),2500,7000)*0.05*np.clip((t-6)/3,0,1)
place((pad*sw*0.10+air),0,rev=0.3)
# room tone (soft pink-ish noise) until lights out
place(filt(n(B['light2']),80,1200)*0.012,0,rev=0)
# footsteps & cloth
for k,ts in enumerate(B['step_in']+B['step_out']):
    st=filt(n(0.18),60,700)*env(int(0.18*SR),0.004,0.035); st/=np.abs(st).max(); place(st*0.22,ts,pan=0.35,rev=0.2)
for ts in (1.05,B['exit']-0.25):
    c=filt(n(0.45),900,5000); c*=np.sin(np.pi*np.linspace(0,1,len(c)))**2; c/=np.abs(c).max(); place(c*0.07,ts,pan=0.4)
# slow-mo entry: deep pitch-down air whoosh
w=filt(n(1.1),150,2500); w*=np.sin(np.pi*np.linspace(0,1,len(w))**0.5)**2; w/=np.abs(w).max()
place(w*0.16,B['slow_in']-0.2,rev=0.5); place(tone(220,60,1.0,0.6)*np.linspace(1,0,int(1.0*SR))**2*0.07,B['slow_in'],rev=0.5)
# glass-on-wood tap at the reveal (bottle sound), with reverb
tap=sum(a*np.sin(2*np.pi*f*t_(0.9))*env(int(0.9*SR),0.0005,d) for f,a,d in [(2310,0.5,0.25),(3720,0.35,0.16),(5150,0.25,0.1),(6900,0.15,0.06)])
knock=tone(190,120,0.12)*env(int(0.12*SR),0.0005,0.025)
place(tap*0.22,B['reveal'],rev=0.9); place(knock*0.4,B['reveal'],rev=0.6)
# riser into hero + soft shimmer on the glint
r=filt(n(2.2),400,6000)*np.linspace(0,1,int(2.2*SR))**2.2; r/=np.abs(r).max(); place(r*0.08,B['freeze']-2.6,rev=0.4)
gl=sum(np.sin(2*np.pi*f*t_(1.6))*env(int(1.6*SR),0.02,0.5)*a for f,a in [(1568,0.4),(2349,0.3),(3136,0.2)])
place(gl*0.05,B['freeze']-1.75,rev=1.0,pan=-0.2)
# breaker thunks for the two light steps; swell cut after second
for k,ts in enumerate((B['light1'],B['light2'])):
    th=tone(95,48,0.35)*env(int(0.35*SR),0.001,0.09); cl=filt(n(0.05),300,4000)*env(int(0.05*SR),0.0005,0.008); th[:len(cl)]+=cl*0.6
    place(th*(0.45 if k==0 else 0.6),ts,rev=0.7)
    place(filt(n(0.25),40,200)*env(int(0.25*SR),0.002,0.06)*0.25,ts,rev=0.2)
# TWO WEEK: reverse swell into low piano note
rs=filt(n(0.7),300,5000)*np.linspace(0,1,int(0.7*SR))**3; rs/=np.abs(rs).max(); place(rs*0.10,B['two']-0.7,rev=0.6)
pt=t_(3.0); pno=sum(np.sin(2*np.pi*110*h*pt*(1+0.0004*h*h))*np.exp(-pt*(0.9+0.6*h))/h for h in range(1,9))
pno*=np.minimum(1,pt/0.004); place(pno*0.20,B['two'],rev=0.8)
# BLACKOUT: reverse suck then trailer hit
rv=filt(n(0.55),100,3000)*np.linspace(0,1,int(0.55*SR))**4; rv/=np.abs(rv).max(); place(rv*0.22,B['blackout']-0.55,rev=0.3)
sub=tone(62,28,2.8,0.7)*env(int(2.8*SR),0.002,0.9)
trans=filt(n(0.4),30,3000)*env(int(0.4*SR),0.0003,0.05); trans/=np.abs(trans).max()
metal=sum(np.sin(2*np.pi*f*t_(2.5))*env(int(2.5*SR),0.001,d)*a for f,a,d in [(97,0.5,0.8),(151.3,0.35,0.6),(233.7,0.25,0.45),(419.1,0.12,0.3)])
hit=np.zeros(int(2.8*SR)); hit+=sub*1.0; hit[:len(trans)]+=trans*0.7; hit[:len(metal)]+=metal*0.45
hit=np.tanh(hit*1.6)/np.tanh(1.6); place(hit*0.85,B['blackout'],rev=0.55)
# low drone tail
dt=t_(B['end']-B['blackout']); dr=(np.sin(2*np.pi*41.2*dt)+0.5*np.sin(2*np.pi*61.7*dt+1))*np.minimum(1,dt/1.2)*np.minimum(1,(dt[-1]-dt)/0.6)
place(dr*0.07,B['blackout']+0.2,rev=0.3)
# Link in bio: subtle soft tick
tk=np.sin(2*np.pi*1800*t_(0.08))*env(int(0.08*SR),0.0005,0.012); place(tk*0.10,B['link'],rev=0.6)
# reverb: synthetic stereo IR via FFT convolution
L=int(2.4*SR); ti=np.arange(L)/SR
ir=np.stack([filt(rng.standard_normal(L),150,9000)*np.exp(-ti/0.55) for _ in range(2)],1); ir/=np.sqrt((ir**2).sum(0))
nf=1<<int(np.ceil(np.log2(N+L)))
rev=np.stack([np.fft.irfft(np.fft.rfft(wet[:,c],nf)*np.fft.rfft(ir[:,c],nf),nf)[:N] for c in range(2)],1)
out=dry+rev*0.9
out=np.tanh(out*1.1)/1.1; out*=0.95/np.abs(out).max()
with wave.open(f'{S}/work/sfx2.wav','wb') as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((out*32000).astype('<i2').tobytes())
print('ok')
