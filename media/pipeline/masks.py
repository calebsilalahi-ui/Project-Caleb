import sys, numpy as np, mediapipe as mp, cv2
from mediapipe.tasks.python import vision, BaseOptions
S=sys.argv[1]; F=np.load(f'{S}/work/frames.npy'); NF=len(F); H,W=854,480
mk=lambda p: vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=p),output_category_mask=True,output_confidence_masks=True))
mc=mk(f'{S}/models/seg.tflite'); dl=mk(f'{S}/models/deeplab.tflite')
def pad(f): sq=np.zeros((854,854,3),np.uint8); sq[:,187:667]=f; return mp.Image(image_format=mp.ImageFormat.SRGB,data=sq)
plateA=F[24].astype(np.float32); plateB=F[200].astype(np.float32)  # empty room before / after
CAT=np.zeros((NF,H,W),np.uint8); CONF=np.zeros((NF,H,W),np.float32)
a,b=30,196
for i in range(a,b):
    f=F[i]; im=pad(f)
    r1=mc.segment(im); cm=r1.category_mask.numpy_view().squeeze()[:,187:667]
    bgc=r1.confidence_masks[0].numpy_view().squeeze()[:,187:667]
    r2=dl.segment(im); pc=r2.confidence_masks[15].numpy_view().squeeze()[:,187:667]
    p=np.maximum(1-bgc,pc)
    # background subtraction vs nearest clean plate with robust exposure gain
    pl=plateA if i<120 else plateB; ff=f.astype(np.float32)
    g=np.median(pl.reshape(-1,3),0)/np.maximum(np.median(ff.reshape(-1,3),0),1)
    d=np.abs(ff*g-pl).max(2)/255.
    lum=ff.mean(2)/255.; r_,g_,b_=ff[...,0]/255.,ff[...,1]/255.,ff[...,2]/255.
    skin=(r_>g_)&(g_>b_)&((r_-b_)>0.12)&(lum>0.22)&(lum<0.8)
    pers=((lum<0.28)|skin).astype(np.float32)
    dm=cv2.GaussianBlur(np.clip((d-0.24)/0.15,0,1)*pers,(0,0),2)
    # trust subtraction only near the person (right part of frame / near model mask)
    near=cv2.dilate((p>0.3).astype(np.uint8),np.ones((31,31),np.uint8)).astype(np.float32)
    if (p>0.5).mean()<0.08: near=np.ones_like(near)*(np.arange(W)[None,:]>W*0.55)  # edge pass: right side
    if i<50 or i>150: near=np.maximum(near,(np.arange(W)[None,:]>W*0.55).astype(np.float32)*np.ones((H,1)))
    dm[0:215,190:345]=0  # wall clock: static, never subtract
    p=np.maximum(p,dm*near*0.95)
    CONF[i]=p; CAT[i]=cm
# temporal smoothing of confidence
sm=CONF.copy()
for i in range(a+1,b-1): sm[i]=0.25*CONF[i-1]+0.5*CONF[i]+0.25*CONF[i+1]
M=np.zeros((NF,H,W),np.uint8)
for i in range(a,b):
    m=(sm[i]>0.5).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,21)))
    inv=(1-m).astype(np.uint8); n2,lab2,st2,_=cv2.connectedComponentsWithStats(inv)
    for k in range(1,n2):
        x,y,w,h,ar=st2[k]
        if ar<6000 and x>0 and y>0 and x+w<W and y+h<H and F[i][lab2==k].mean()<80: m[lab2==k]=1
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    keep=np.zeros_like(m)
    for k in range(1,n):
        if st[k,4]>1500: keep[lab==k]=1
    M[i]=keep
np.save(f'{S}/work/mask.npy',M); np.save(f'{S}/work/cat.npy',CAT)
for t in [1.1,1.3,1.5,2.0,3.0,4.5,5.2,5.6,5.9,6.2,6.4]: print(t,'%.2f'%M[int(t*30)].mean())
