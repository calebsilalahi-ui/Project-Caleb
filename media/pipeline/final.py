import sys, numpy as np, subprocess, math, cv2, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=sys.argv[1]; W,H=480,854; OW,OH=1080,1920; FPS=30
raw=subprocess.run(['ffmpeg','-v','error','-i',f'{S}/work/traced60.mp4','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
V=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3); NV=len(V)
IF='/usr/share/fonts/opentype/inter/'
def ease(x): x=min(max(x,0.0),1.0); return x*x*(3-2*x)
def lerp(a,b,x): return a+(b-a)*x
# ---------- time remap: speed profile integrated -> source time
FREEZE=8.15
def speed(T):
    v=1.0
    if T>=2.9: v=lerp(1,0.42,ease((T-2.9)/0.45))
    if T>=4.8: v=lerp(0.42,1,ease((T-4.8)/0.4))
    if T>=6.55: v=lerp(1,1.7,ease((T-6.55)/0.2))
    if T>=7.05: v=lerp(1.7,1,ease((T-7.05)/0.25))
    return v
src=[0.0]; T=0; dt=1/FPS/8
while src[-1]<FREEZE:
    src.append(src[-1]+speed(T)*dt); T+=dt
T_FREEZE=T
END=T_FREEZE+5.6
NF=int(END*FPS)
def s_of(T):
    k=int(T/dt); return min(src[min(k,len(src)-1)],FREEZE)
# beats (output time)
L1=T_FREEZE+0.25; L2=L1+0.45; T_TWO=L2+0.65; T_BLK=T_TWO+0.8; T_LINK=T_BLK+0.95
def T_of_s(s):
    return next(k*dt for k,v in enumerate(src) if v>=s)
beats=dict(freeze=T_FREEZE,light1=L1,light2=L2,two=T_TWO,blackout=T_BLK,link=T_LINK,end=END,reveal=T_of_s(3.7),slow_in=2.9,exit=T_of_s(5.5),step_in=[T_of_s(x) for x in (1.25,1.65,2.05)],step_out=[T_of_s(x) for x in (5.35,5.7,6.0)])
json.dump(beats,open(f'{S}/work/beats.json','w'),indent=1); print(beats)
BOT=(256,541)  # between the two Lira bottles (source px)
BOTTLES=[(222,498,255,586),(257,500,290,585)]
# ---------- camera
def camera(T):
    s=s_of(T)
    if T<1.2: x=ease(T/1.2); return lerp(1.0,1.05,x),lerp(240,250,x),lerp(427,440,x)
    if T<2.6: return 1.05,250,440
    if T<5.0:  x=ease((T-2.6)/2.3); return lerp(1.05,1.38,x),lerp(250,262,x),lerp(440,512,x)
    if T<T_of_s(5.3): x=ease((T-5.0)/0.7); return lerp(1.38,1.14,x),lerp(262,320,x),lerp(512,400,x)
    if T<T_FREEZE: x=ease((T-T_of_s(5.3))/(T_FREEZE-T_of_s(5.3))); x=1-(1-x)**2; return lerp(1.14,2.0,x),lerp(320,BOT[0],x),lerp(400,BOT[1]-10,x)
    x=(T-T_FREEZE)/(END-T_FREEZE); z=2.0+0.28*x
    if T>=T_BLK: z+=0.035*math.exp(-(T-T_BLK)*8)
    return z,BOT[0],BOT[1]-10-18*x
def jolt(T):
    if T<T_BLK: return 0,0
    a=9*math.exp(-(T-T_BLK)*14); return a*math.sin(T*90),a*math.cos(T*70)
def dof(T):  # 0..1 background defocus
    if T<T_of_s(5.6): return 0
    return ease((T-T_of_s(5.6))/1.2)
def light(T):
    if T<L1: return 1.0
    if T<L2: return lerp(0.5,0.42,min(1,(T-L1)/0.4)) if T>L1+0.05 else lerp(1,0.5,(T-L1)/0.05)
    return lerp(0.42,0.0,min(1,(T-L2)/0.08))
yy,xx=np.mgrid[0:OH,0:OW].astype(np.float32)
VIG=(1-0.42*(((xx-OW/2)/(OW/2))**2+((yy-OH/2)/(OH/2))**2)/2)[...,None]
rng=np.random.default_rng(5)
GRAIN=[cv2.GaussianBlur(rng.normal(0,1,(OH//2,OW//2)).astype(np.float32),(0,0),0.6) for _ in range(8)]
def grade(x):
    x=x/255.0; x=x*0.93+0.025; x=np.power(np.clip(x,0,1),1.06)
    x=0.5+(x-0.5)*1.12
    l=x.mean(2,keepdims=True); x=l+(x-l)*0.84
    x[...,0]*=1.035; x[...,2]*=0.965
    sh=np.clip(1-l*2.2,0,1); x[...,2]+=0.035*sh[...,0]; x[...,1]+=0.012*sh[...,0]
    return x
# ---------- type
def text_img(txt,font,size,fill,track=0.0,glow=None):
    f=ImageFont.truetype(IF+font,size); ws=[f.getlength(c) for c in txt]; tw=int(sum(ws)+track*size*(len(txt)-1)); asc,desc=f.getmetrics()
    pad=int(size*0.8); im=Image.new('RGBA',(tw+2*pad,asc+desc+2*pad),(0,0,0,0)); d=ImageDraw.Draw(im); x=pad
    for c,w in zip(txt,ws): d.text((x,pad),c,font=f,fill=fill); x+=w+track*size
    if glow:
        g=im.filter(ImageFilter.GaussianBlur(glow[1])); gl=Image.new('RGBA',im.size,glow[0]+(0,)); gl.putalpha(g.getchannel('A').point(lambda v:int(min(255,v*glow[2]))))
        gl.alpha_composite(im); im=gl
    return im
def paste(canvas,img,cx,cy,scale=1.0,alpha=1.0):
    if alpha<=0.003: return
    im=img if abs(scale-1)<1e-3 else img.resize((int(img.width*scale),int(img.height*scale)),Image.LANCZOS)
    if alpha<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*alpha)))
    canvas.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
IVORY=(240,234,222,255); LIRA=(212,232,140,255)
BLK=text_img('BLACKOUT','Inter-Black.otf',158,LIRA,track=0.01,glow=((196,226,110),34,0.75))
LINK=text_img('LINK IN BIO','Inter-Medium.otf',36,(236,230,218,235),track=0.32)
def two_img(track): return text_img('TWO WEEK','Inter-Light.otf',82,IVORY,track=track)
TWO_CACHE={}
BAR=int(OH*0.05)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','-',
   '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p',f'{S}/work/final_video.mp4'],stdin=subprocess.PIPE)
for i in range(NF):
    T=i/FPS; s=s_of(T)
    fr=V[min(NV-1,int(round(s*60)))].astype(np.float32)
    z,cx,cy=camera(T); jx,jy=jolt(T)
    cw,ch=W/z,H/z; cx=min(max(cx,cw/2),W-cw/2); cy=min(max(cy,ch/2),H-ch/2)
    x0,y0=cx-cw/2,cy-ch/2; k=OW/cw
    img=cv2.resize(fr[int(max(0,y0-2)):int(min(H,y0+ch+3)),int(max(0,x0-2)):int(min(W,x0+cw+3))],None,fx=k,fy=k,interpolation=cv2.INTER_LANCZOS4)
    ox,oy=(x0-max(0,int(max(0,x0-2))))*k-jx,(y0-int(max(0,y0-2)))*k-jy
    Mx=np.float32([[1,0,-ox],[0,1,-oy]]); img=cv2.warpAffine(img,Mx,(OW,OH),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    bx,by=(BOT[0]-x0)*k-jx,(BOT[1]-y0)*k-jy
    d=dof(T)
    if d>0:
        bl=cv2.GaussianBlur(img,(0,0),4+10*d)
        foc=np.exp(-(((xx-bx)/(95*k/2.2))**2+((yy-by)/(150*k/2.2))**2))[...,None]
        a=np.clip((1-foc*1.5),0,1)*d; img=img*(1-a)+bl*a
    # glint sweep across the bottles
    gT=T-T_of_s(7.0)
    if 0<gT<0.9:
        bm=np.zeros((OH,OW),np.float32)
        for (a1,b1,a2,b2) in BOTTLES:
            p1=(int((a1-x0)*k-jx),int((b1+12-y0)*k-jy)); p2=(int((a2-x0)*k-jx),int((b2-y0)*k-jy)); cv2.rectangle(bm,p1,p2,1.0,-1)
        bm=cv2.GaussianBlur(bm,(0,0),6)
        pos=lerp(-0.3,1.3,ease(gT/0.9)); band=(xx-bx+(yy-by)*0.6)/(220*k/2.2)
        g=np.exp(-((band-(pos*2-1))/0.12)**2)*bm*0.55*math.sin(math.pi*gT/0.9)
        img=img+g[...,None]*255
    x=grade(img)
    Lv=light(T)
    if Lv<1:
        pool=np.exp(-(((xx-bx)/(170*k/2.2))**2+((yy-by)/(230*k/2.2))**2))[...,None]
        floor=0.045+0.30*pool*(1 if T>=L2 else 0)
        lv=np.maximum(Lv,floor); x=x*lv; x[...,2]*=1+0.10*(1-Lv)
    x*=VIG
    gn=cv2.resize(GRAIN[i%8],(OW,OH),interpolation=cv2.INTER_LINEAR)[...,None]
    x+=gn*(0.016 if Lv>0.5 else 0.022)
    x=np.clip(x*255,0,255).astype(np.uint8)
    if T_BLK<=T<T_BLK+2/FPS: x=np.clip(x.astype(np.int16)+60,0,255).astype(np.uint8)  # one-frame light flash
    x[:BAR]=0; x[OH-BAR:]=0
    can=Image.fromarray(x).convert('RGBA')
    if T>=T_TWO:
        p=min(1,(T-T_TWO)/0.9); tr=round(lerp(0.62,0.42,1-(1-p)**3),2)
        if tr not in TWO_CACHE: TWO_CACHE[tr]=two_img(tr)
        paste(can,TWO_CACHE[tr],OW/2,OH*0.215-12*(1-ease(p)),1.0,ease(min(1,(T-T_TWO)/0.6)))
    if T>=T_BLK:
        p=(T-T_BLK)/0.16; sc=lerp(1.18,1.0,1-(1-min(p,1))**3)
        br=1.0+0.06*math.sin((T-T_BLK)*2.4)  # glow breathing
        paste(can,BLK,OW/2+jx,OH*0.735+jy,sc*br if p>=1 else sc,min(1,p*2.5))
    if T>=T_LINK:
        p=min(1,(T-T_LINK)/0.7); paste(can,LINK,OW/2,OH*0.835+10*(1-ease(p)),1.0,ease(p)*0.9)
        lw=int(150*ease(min(1,(T-T_LINK-0.2)/0.6)))
        if lw>0: ImageDraw.Draw(can).line([(OW/2-lw/2,OH*0.835+34),(OW/2+lw/2,OH*0.835+34)],fill=(212,232,140,int(200*ease(p))),width=2)
    if T>END-0.45:
        can=Image.blend(can,Image.new('RGBA',can.size,(0,0,0,255)),ease((T-(END-0.45))/0.45))
    enc.stdin.write(np.asarray(can.convert('RGB')).tobytes())
enc.stdin.close(); enc.wait(); print('done',NF,END)
