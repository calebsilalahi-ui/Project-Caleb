import sys, numpy as np, mediapipe as mp, cv2, subprocess
from mediapipe.tasks.python import vision, BaseOptions
S=sys.argv[1]; F=np.load(f'{S}/work/frames.npy'); M=np.load(f'{S}/work/mask.npy'); CAT=np.load(f'{S}/work/cat.npy')
NF,H,W=len(F),854,480
M[150:,0:215,190:345]=0
pl=vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=f'{S}/models/pose.task')))
HAIR=np.array([26,22,24]); SKIN=np.array([196,128,84]); TOP=np.array([96,108,40]); PANTS=np.array([56,58,66]); LINE=np.array([28,20,16])
hip_prev=int(H*0.74)
out=F.copy()
for i in range(30,196):
    f=F[i]; m=M[i]>0
    if m.mean()<0.005: continue
    cm=CAT[i].copy()
    r=pl.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(f)))
    lms=r.pose_landmarks[0] if r.pose_landmarks else None
    if lms and min(lms[23].visibility,lms[24].visibility)>0.3: hip_prev=int(0.5*hip_prev+0.5*(lms[23].y+lms[24].y)/2*H+0.5*H*0.03)
    ff=f.astype(np.float32)/255.; lum=cv2.bilateralFilter(ff.mean(2),9,0.15,7)
    med=np.median(lum[m]) if m.any() else 0.4
    sh=np.clip(0.78+1.1*(lum-med),0.55,1.25); sh=np.round(sh*3)/3*0.6+cv2.GaussianBlur(sh,(0,0),3)*0.4  # cel bands softened
    col=np.zeros((H,W,3),np.float32)
    rows=np.arange(H)[:,None]
    cloth=m&((cm==4)|(cm==5)|(cm==0))
    bl=np.clip((rows-hip_prev)/10.0+0.5,0,1)[...,None]*np.ones((1,W,1)); tp=TOP*(1-bl)+PANTS*bl; col[cloth]=tp[cloth]
    col[m&(cm==1)]=HAIR; col[m&((cm==2)|(cm==3))]=SKIN
    # skin detector fallback for arms the model labels as clothes
    r_,g_,b_=ff[...,0],ff[...,1],ff[...,2]; gr=g_/np.maximum(r_,1e-3); skin=(r_>g_)&(g_>b_)&((r_-b_)>0.10)&(lum>0.3)&(gr>0.55)&(gr<0.88)&(cm>0)
    col[m&skin&(cm!=1)]=SKIN
    shc=np.clip(0.85+0.6*(cv2.GaussianBlur(lum,(0,0),7)-med),0.65,1.12)
    shade=np.where(cloth[...,None],shc[...,None],sh[...,None]); col*=shade
    # light pixel texture: 2px mosaic of the painted layer
    sm=cv2.resize(cv2.resize(col,(W//2,H//2),interpolation=cv2.INTER_AREA),(W,H),interpolation=cv2.INTER_NEAREST)
    col=sm*0.8+col*0.2
    # crisp outlines (smooth), between regions and around silhouette
    lab=np.where(m,np.where(np.all(col==0,2),0,1),0).astype(np.uint8)
    regions=np.zeros((H,W),np.uint8); regions[m]=1; regions[m&(cm==1)]=2; regions[m&((cm==2)|(cm==3)|skin)]=3; regions[cloth&(rows>hip_prev)]=4
    e=np.zeros((H,W),np.uint8)
    for k in range(1,5): e|=cv2.morphologyEx((regions==k).astype(np.uint8),cv2.MORPH_GRADIENT,np.ones((2,2),np.uint8))
    e=cv2.GaussianBlur(e.astype(np.float32),(0,0),0.6)
    col=col*(1-e[...,None]*0.85)+LINE*e[...,None]*0.85
    # glasses from eye landmarks
    if lms:
        L,R,N,EL,ER=lms[2],lms[5],lms[0],lms[7],lms[8]
        ed=np.hypot((L.x-R.x)*W,(L.y-R.y)*H); hd=max(np.hypot((N.x-EL.x)*W,(N.y-EL.y)*H),np.hypot((N.x-ER.x)*W,(N.y-ER.y)*H))
        rad=int(np.clip(0.42*ed if ed>12 else 0.28*hd,6,13))
        pts=[(int(e_.x*W),int(e_.y*H)) for e_ in (L,R) if e_.visibility>0.5 and m[min(H-1,max(0,int(e_.y*H))),min(W-1,max(0,int(e_.x*W)))]]
        tmp=col.copy()
        for p in pts: cv2.circle(tmp,p,rad,(40,26,18),2,cv2.LINE_AA)
        if len(pts)==2 and ed>2*rad*0.8: cv2.line(tmp,(pts[0][0]-rad if pts[0][0]>pts[1][0] else pts[0][0]+rad,pts[0][1]),(pts[1][0]+rad if pts[0][0]>pts[1][0] else pts[1][0]-rad,pts[1][1]),(40,26,18),2,cv2.LINE_AA)
        col=tmp
    a=cv2.GaussianBlur(m.astype(np.float32),(0,0),0.8)[...,None]
    out[i]=np.clip(col*a+f*(1-a),0,255).astype(np.uint8)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','480x854','-r','30','-i','-','-c:v','libx264','-crf','12','-pix_fmt','yuv444p',f'{S}/work/traced30.mp4'],stdin=subprocess.PIPE)
p.stdin.write(out.tobytes()); p.stdin.close(); p.wait()
np.save(f'{S}/work/traced.npy',out); print('ok')
