# LIGHTS-OUT TEMPLATE v3.2 (rembg replaced by bundled u2netp via onnxruntime) — 17.433 s, 1280x720, 30 fps, 523 frames
# usage: python3 render_template.py <clips_dir> <out.mp4> [preview_frame_ids_csv]
import numpy as np,subprocess,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H,FPS=1280,720,30;N=523
import json,os
import onnxruntime as ort
# rembg-equivalent u2netp mask (no PyPI): same preprocessing/postprocessing as rembg.remove(only_mask=True)
def new_session(name):
    return ort.InferenceSession(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models',name+'.onnx'),providers=['CPUExecutionProvider'])
def remove(img,session=None,only_mask=True):
    im=img.convert('RGB').resize((320,320),Image.LANCZOS);a=np.array(im).astype(np.float32);a=a/max(float(a.max()),1e-6)
    a=(a-np.array([0.485,0.456,0.406],np.float32))/np.array([0.229,0.224,0.225],np.float32)
    o=session.run(None,{session.get_inputs()[0].name:a.transpose(2,0,1)[None].astype(np.float32)})[0][:,0]
    o=(o-o.min())/max(float(o.max()-o.min()),1e-6)
    return Image.fromarray((o[0]*255).astype(np.uint8),'L').resize(img.size,Image.LANCZOS)
CFG={"words":{"lights":"LIGHTS","out":"OUT","fear":"FEARLESS","full":"FULL","thr":"THROTTLE","no":"NO","brakes":"BRAKES","limits":"LIMITS",
"racer":"RACER","win":"WIN","fast":"FAST","born":"BORN TO WIN","rise":"RISE","legend":"LEGEND","go":"GO","push":"PUSH","faster":"FASTER",
"now":"NOW","forever":"FOREVER","heart":"HEART","strong":"STRONG","legacy":"LEGACY","always":"ALWAYS","top":"TOP","first":"FIRST",
"we":"WE","believe":"BELIEVE","tag":"P1"},
"end_words":["BORN","TO","RACE","BORN","TO","WIN","THE","RACE","IS","MINE"],"accent_hue_shift":0,"audio":"audio.wav"}
if os.path.exists('config.json'):
    _c=json.load(open('config.json'));CFG['words'].update(_c.pop('words',{}));CFG.update(_c)
Wd={k:v.upper() for k,v in CFG['words'].items()}
SES=new_session('u2netp');PF='fonts/Playfair.ttf';AN='fonts/Anton.ttf'
CL,OUT=sys.argv[1],sys.argv[2]
YY,XX=np.mgrid[0:H,0:W].astype(np.float32)
VIG=np.clip(1.25-0.85*(((XX-W/2)/(W*0.62))**2+((YY-H/2)/(H*0.7))**2),0.15,1)[...,None]
def ss(x,a=0.0,b=1.0):
    x=np.clip((x-a)/(b-a),0,1);return x*x*(3-2*x)
def ease(p):return float(ss(p))
def over(a,b):
    ab=b[...,3:4];o=np.empty_like(a);o[...,:3]=b[...,:3]*ab+a[...,:3]*(1-ab);o[...,3:4]=ab+a[...,3:4]*(1-ab);return o
def toL(im):return np.asarray(im).astype(np.float32)/255
def toI(a,mode=None):return Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8),mode)
def txt(s,path,size,fill=(235,235,235),cond=1.0,wght=None,grad=True,shear=0.0,ext=0,plate=None,maxw=1200):
    f=ImageFont.truetype(path,size)
    if wght:
        try:f.set_variation_by_axes([wght])
        except Exception:pass
    b=f.getbbox(s);w,h=b[2]-b[0]+24,b[3]-b[1]+24
    m=Image.new('L',(w,h),0);ImageDraw.Draw(m).text((12-b[0],12-b[1]),s,font=f,fill=255)
    if shear:
        sw=int(abs(shear)*h);m=m.transform((w+sw,h),Image.AFFINE,(1,shear,-shear*h,0,1,0),Image.BICUBIC);w+=sw
    a=toL(m);col=np.ones((h,w,3),np.float32)*np.array(fill,np.float32)/255
    if grad:col*=np.linspace(1.0,0.5,h)[:,None,None]
    L=np.dstack([col,a])
    if plate is not None:
        P=np.zeros((h+30,w+50,4),np.float32);P[...,:3]=plate;P[...,3]=1;P[15:15+h,25:25+w]=over(P[15:15+h,25:25+w],L);L=P
    if ext:
        p=ext;Bk=np.zeros((L.shape[0]+p,L.shape[1]+p,4),np.float32)
        for k in range(p,0,-1):
            d=L.copy();d[...,:3]*=0.18+0.35*(1-k/p);T=np.zeros_like(Bk);T[k:k+L.shape[0],k:k+L.shape[1]]=d;Bk=over(Bk,T)
        T=np.zeros_like(Bk);T[:L.shape[0],:L.shape[1]]=L;L=over(Bk,T)
    if cond!=1.0:L=toL(toI(L,'RGBA').resize((max(1,int(L.shape[1]*cond)),L.shape[0]),Image.LANCZOS))
    if maxw and L.shape[1]>maxw:k=maxw/L.shape[1];L=toL(toI(L,'RGBA').resize((maxw,max(1,int(L.shape[0]*k))),Image.LANCZOS))
    return L
def place(fr,L,cx,cy,sc=1.0,rot=0,al=1.0,behind=None,colmask=None,sx=1.0,sy=1.0,amask=None):
    if al<=0.003:return fr
    im=toI(L,'RGBA')
    if sc*sx!=1 or sc*sy!=1:im=im.resize((max(1,int(im.width*sc*sx)),max(1,int(im.height*sc*sy))),Image.BILINEAR)
    if rot:im=im.rotate(rot,Image.BICUBIC,expand=True)
    A=toL(im);h,w=A.shape[:2];x0=int(cx-w/2);y0=int(cy-h/2)
    xa,ya,xb,yb=max(0,x0),max(0,y0),min(W,x0+w),min(H,y0+h)
    if xa>=xb or ya>=yb:return fr
    s=A[ya-y0:yb-y0,xa-x0:xb-x0];a=s[...,3:4]*al
    if behind is not None:a=a*(1-behind[ya:yb,xa:xb,None])
    if amask is not None:a=a*amask[ya:yb,xa:xb,None]
    if colmask is not None:a=a*colmask[None,xa:xb,None]
    fr[ya:yb,xa:xb]=fr[ya:yb,xa:xb]*(1-a)+s[...,:3]*a;return fr
def nf(seed,lo=(14,25)):
    r=np.random.default_rng(seed)
    a=toL(toI(r.random(lo)).resize((W,H),Image.BICUBIC));b=toL(toI(r.random((60,107))).resize((W,H),Image.BICUBIC))
    n=a*0.65+b*0.35;return (n-n.min())/(n.max()-n.min())
NF=[nf(s) for s in range(5)]
NFL=[toL(toI(nf(10+s,(6,10))).filter(ImageFilter.GaussianBlur(10))) for s in range(3)]
def nm(p,k,sh=10):return np.clip((p*1.2-0.1-NF[k])*sh+0.5,0,1)[...,None]
def noisetr(A,B,p,k):
    p=ease(p)**1.5;mA=nm(min(1,p*1.5),k);mB=nm(max(0,p*1.25-0.25),(k+1)%5);return (A*(1-mA))*(1-mB)+B*mB
def grade(fr,g=1.05):
    r,gg,b=fr[...,0],fr[...,1],fr[...,2];l=(0.299*r+0.587*gg+0.114*b)[...,None]
    red=np.clip((r-np.maximum(gg,b))[...,None]*3,0,1);o=l*(1-red)+fr*red
    return np.clip((o-0.03)/0.97,0,1)**g
def post(fr,i):
    fr=fr*VIG;s=toL(toI(fr).resize((320,180),Image.BILINEAR));s=np.clip(s-0.62,0,1)*2.2
    bl=toL(toI(s).filter(ImageFilter.GaussianBlur(6)).resize((W,H),Image.BILINEAR))
    fr=np.clip(fr+bl*0.4,0,1);soft=toL(toI(fr).filter(ImageFilter.GaussianBlur(1.3)))
    fr=fr*0.72+soft*0.28+np.random.default_rng(i).normal(0,0.014,(H,W,1)).astype(np.float32)
    if CFG['accent_hue_shift']:
        hsv=np.asarray(toI(fr).convert('HSV')).copy();hsv[...,0]=((hsv[...,0].astype(np.int32)+int(CFG['accent_hue_shift']*255/360))%256).astype(np.uint8)
        fr=toL(Image.fromarray(hsv,'HSV').convert('RGB'))
    return np.clip(fr,0,1)
CACHE={}
def load(name,ss_,dur,size=(W,H)):
    w,h=size;raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss_),'-i',f'{CL}/{name}.mp4','-t',str(dur),'-vf',f'fps=30,scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
def clip(name,ct,s0,dur):
    if name not in CACHE:CACHE.clear();CACHE[name]=(load(name,s0,dur),s0)
    a,s=CACHE[name];i=min(len(a)-1,max(0,int(round((ct-s)*30))));return a[i].astype(np.float32)/255
PS={}
def pvid(name,ct):
    if name not in PS:PS[name]=load(name,0.5,2.5,(400,225))
    a=PS[name];g=grade(a[min(len(a)-1,int(ct*30))].astype(np.float32)/255)*0.95;return np.dstack([g,np.ones((225,400,1),np.float32)])
MC={}
def matte(key,fr):
    if key in MC:return MC[key]
    m=toL(remove(toI(fr).resize((480,270)),session=SES,only_mask=True).resize((W,H),Image.BILINEAR));MC.clear();MC[key]=m;return m
def stl(k,size=(W,H)):return toL(Image.open(f'st/{k}.png').convert('RGB').resize(size))
def pst(k):return np.dstack([grade(stl(k,(400,225)))*0.95,np.ones((225,400,1),np.float32)])
def redbg(beam=True):
    d=np.sqrt(((XX-W/2)/W)**2+((YY-H*0.35)/H)**2);fr=np.zeros((H,W,3),np.float32);fr[...,0]=np.clip(0.32-d*0.45,0,1)
    if beam:b=np.exp(-((XX-W*0.5)/38)**2)*0.75;fr[...,0]+=b;fr[...,1]+=b*0.02
    return fr
def flood(c):fr=np.zeros((H,W,3),np.float32);fr[:]=c;return fr
def mix(a,b,x):return a*(1-x)+b*x
def warp(L,amp,ph):
    if amp<0.5:return L
    h,w=L.shape[:2];yy,xx=np.mgrid[0:h,0:w]
    xs=np.clip((xx+amp*np.sin(yy/17+ph)).astype(int),0,w-1);ys=np.clip((yy+amp*np.cos(xx/23+ph*1.3)).astype(int),0,h-1);return L[ys,xs]
def blurL(L,r):return toL(toI(L,'RGBA').filter(ImageFilter.GaussianBlur(r)))
def inktext(fr,L,cx,cy,pin,pout,k,rot=-12,shadow=False):
    if pin<=0 or pout>=1:return fr
    Lw=warp(L,16*(1-pin)+12*pout,pin*3+k)
    am=ss(pin*1.4-0.15-NFL[k],-0.07,0.07)
    if pout>0:am=am*(1-ss(pout*1.5-0.2-NFL[(k+1)%3]+(0.5-YY/H)*0.4,-0.07,0.07))
    if shadow:
        S=Lw.copy();S[...,:3]=0.05;fr=place(fr,blurL(S,7),cx+8,cy+10,1,rot,al=0.7,amask=am)
    fr=place(fr,blurL(Lw,10),cx,cy,1,rot,al=0.4,amask=am);return place(fr,Lw,cx,cy,1,rot,amask=am)
def halftone(g,cell=7):
    h,w=g.shape;yy,xx=np.mgrid[0:h,0:w];d=np.sqrt(((xx%cell)-cell/2)**2+((yy%cell)-cell/2)**2)/(cell*0.72)
    return ss(np.sqrt(np.clip(g,0,1))-d,-0.08,0.08)
def cutout(k,mode='rembg',crop=None,size=(720,405)):
    im=Image.open(f'st/{k}.png').convert('RGB')
    if crop:im=im.crop(crop)
    im=im.resize(size);g=toL(im.convert('L'))
    a=toL(remove(im,session=SES,only_mask=True)) if mode=='rembg' else ss(g,0.35,0.6)
    ht=halftone(np.clip(g*1.4,0,1));col=np.dstack([(0.3+0.6*ht)*c for c in (0.88,0.84,0.84)])
    return np.dstack([col,a*(0.25+0.75*ht)*0.88])
MS='/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf'
SIL=(232,232,236);RED=(205,8,28);MRED=(190,48,50);PAP=(242,238,230)
def redgrad(top,y1=0.75,smoke=0.08):
    g=np.clip(1-YY/(H*y1),0,1)**1.4;fr=g[...,None]*np.array(top,np.float32)
    fr[...,0]+=NF[1]*smoke*g;return fr
REDG=redgrad((0.42,0.03,0.05));REDC=redgrad((0.5,0.03,0.05),0.6);REDE=redgrad((0.8,0.07,0.09),0.85,0.12);REDF=redgrad((0.38,0.02,0.04),0.7)
REDP=redgrad((0.35,0.02,0.04),1.0)
BEAMV=(np.exp(-((XX-640)/90)**2)*0.35)[...,None]*np.array([1,0.05,0.06],np.float32)
BEAMD=(np.exp(-((XX-0.45*YY-420)/70)**2)*0.6)[...,None]*np.array([1,0.04,0.05],np.float32)
def zoomcrop(fr,z,cx=640,cy=360):
    if abs(z-1)<1e-3:return fr
    im=toI(fr) if fr.ndim==3 else toI(fr,'L');big=im.resize((int(W*z),int(H*z)),Image.BILINEAR)
    x0=int(cx*z-cx);y0=int(cy*z-cy);x0=max(0,min(big.width-W,x0));y0=max(0,min(big.height-H,y0))
    return toL(big.crop((x0,y0,x0+W,y0+H)))
def rotz(fr,a,z=1.1):
    im=toI(fr).resize((int(W*z),int(H*z)),Image.BILINEAR).rotate(a,Image.BICUBIC);x0=(im.width-W)//2;y0=(im.height-H)//2
    return toL(im.crop((x0,y0,x0+W,y0+H)))
def comp(canvas,raw,m,s,cx,cy):
    if s!=1:
        im=toI(raw).resize((int(W*s),int(H*s)),Image.BILINEAR);mm=toI(m,'L').resize((int(W*s),int(H*s)),Image.BILINEAR)
        A=toL(im);Mm=toL(mm);M=np.zeros((H,W),np.float32);S=np.zeros((H,W,3),np.float32)
        h,w=A.shape[:2];x0=int(cx-w/2);y0=int(cy-h/2);xa,ya,xb,yb=max(0,x0),max(0,y0),min(W,x0+w),min(H,y0+h)
        M[ya:yb,xa:xb]=Mm[ya-y0:yb-y0,xa-x0:xb-x0];S[ya:yb,xa:xb]=A[ya-y0:yb-y0,xa-x0:xb-x0]
    else:M,S=m,raw
    return canvas*(1-M[...,None])+S*M[...,None],M
def shiftx(a,dx):
    dx=int(dx);o=np.zeros_like(a)
    if dx>=0:o[:,dx:]=a[:,:W-dx] if dx<W else 0
    else:o[:,:W+dx]=a[:,-dx:] if -dx<W else 0
    return o
def letters(s,path,size,fill,cond=1.0,wght=None,grad=False,maxw=1100):
    f=ImageFont.truetype(path,size)
    if maxw and f.getlength(s)*cond>maxw:return letters(s,path,int(size*maxw/(f.getlength(s)*cond)),fill,cond,wght,grad,None)
    if wght:
        try:f.set_variation_by_axes([wght])
        except Exception:pass
    wb=f.getbbox(s);top,bot=wb[1],wb[3];hh=bot-top+24
    tot=f.getlength(s)*cond;x=-tot/2;out=[]
    for ch in s:
        cw=f.getlength(ch);m=Image.new('L',(int(cw)+24,hh),0);ImageDraw.Draw(m).text((12,12-top),ch,font=f,fill=255)
        a=toL(m);col=np.ones((hh,m.width,3),np.float32)*np.array(fill,np.float32)/255
        if grad:col*=np.linspace(1.0,0.5,hh)[:,None,None]
        L=np.dstack([col,a])
        if cond!=1.0:L=toL(toI(L,'RGBA').resize((max(1,int(L.shape[1]*cond)),hh),Image.LANCZOS))
        w=cw*cond;out.append((L,x+w/2));x+=w
    return out
def imgtext(s,path,size,k,shear):
    L=txt(s,path,size,(255,255,255),1,grad=False,shear=shear);h,w=L.shape[:2];im=Image.open(f'st/{k}.png').convert('L').resize((w,h))
    g=toL(im)*0.55+toL(im.resize((max(1,w//14),h)).resize((w,h),Image.BILINEAR))*0.45;g=np.clip(g*1.1,0,1)
    return np.dstack([np.repeat(g[...,None],3,2)*np.array([0.95,0.93,0.92]),L[...,3:4]])
def leak(fr,p,t):
    d=(XX+(H-YY))/(W+H);msk=ss(p*1.6-d-0.25*NFL[0],-0.15,0.15)*(0.9+0.1*np.sin((XX-YY)/70+t*12))
    return mix(fr,flood((1,0.93,0.94)),np.clip(msk,0,1)[...,None])
def bloom(fr,p,cx=640,cy=330):
    R=np.sqrt((XX-cx)**2+(YY-cy)**2)+220*(NF[2]-0.5)+120*(NFL[1]-0.5);r=40+p*900
    a=ss(r-R,-50,50)[...,None];c=np.array([1,0.86,0.88])*(1-a*0)+0;return mix(fr,flood((1,0.86,0.88)),a)
def mksheet():
    Ws,Hs=1250,2600;P=np.ones((Hs,Ws),np.float32)*0.87;g4=toL(Image.open('st/4.png').convert('L').resize((Ws,700)))
    P[0:700]=g4*0.7+0.08;P[1500:2200]=g4[:,::-1]*0.7+0.08
    im=toI(np.dstack([P*0.96,P*0.93,P*0.87]));d=ImageDraw.Draw(im)
    d.rectangle([Ws-80,0,Ws,Hs],fill=(160,42,42));d.polygon([(0,520),(0,700),(380,0),(260,0)],fill=(168,52,50));d.rectangle([0,1180,Ws,1240],fill=(40,38,36))
    a=toL(im);r=np.random.default_rng(3);tex=toL(toI(r.random((Hs//3,Ws//3))).resize((Ws,Hs),Image.BICUBIC));a=a*(0.88+0.12*tex[...,None])
    return np.dstack([a,np.ones((Hs,Ws,1),np.float32)])
SHEET=mksheet()
def poster(t):
    y=int(200+(t-5.56)*250);fr=place(REDP.copy(),SHEET[y:y+1150],600,360,1.0,-16);l=fr.mean(2,keepdims=True);return mix(fr,l,0.15)
T={}
T['lights']=txt(Wd['lights'],PF,360,SIL,0.6,wght=800);T['out']=txt(Wd['out'],PF,560,SIL,1.25,wght=800)
T['fear']=txt(Wd['fear'],PF,760,RED,0.36,wght=900)
T['full']=txt(Wd['full'],AN,400,MRED,1,grad=False,shear=0.25);T['thr']=txt(Wd['thr'],AN,230,PAP,1,grad=False,shear=0.25,plate=(0.17,0.16,0.16))
T['no']=txt(Wd['no'],AN,520,MRED,1,grad=False,shear=0.25);T['brakes']=imgtext(Wd['brakes'],AN,300,4,0.25);T['limits']=txt(Wd['limits'],AN,300,(32,30,28),1,grad=False,shear=0.25)
T['racer']=txt(Wd['racer'],AN,300,SIL);T['win']=txt(Wd['win'],AN,210,SIL);T['fast']=txt(Wd['fast'],AN,190,SIL)
T['born']=txt(Wd['born'],PF,30,(240,240,240),1,wght=600,grad=False);T['rise']=txt(Wd['rise'],AN,120,RED,1,grad=False,shear=0.25,plate=(0.94,0.94,0.94))
T['legend']=txt(Wd['legend'],PF,330,(200,200,205),0.8,wght=500,grad=False)
T['go']=txt(Wd['go'],AN,720,(240,240,240),1,shear=0.25,ext=40,maxw=None);T['push']=txt(Wd['push'],AN,300,(235,235,235),1,shear=0.25,ext=24,maxw=None);T['faster']=txt(Wd['faster'],AN,520,(240,240,240),1,shear=0.25,ext=34,maxw=None)
T['now']=txt(Wd['now'],PF,260,(250,250,250),0.55,wght=800,grad=False)
FOREV=letters(Wd['forever'],PF,230,SIL,0.85,wght=700,grad=True);FT=np.random.default_rng(4).permutation(len(FOREV))
T['heart']=txt(Wd['heart'],AN,30,(240,240,240),1,grad=False);T['strong']=txt(Wd['strong'],AN,30,(240,240,240),1,grad=False)
T['legacy']=txt(Wd['legacy'],AN,400,(255,255,255),1,grad=False);T['always']=txt(Wd['always'],AN,170,(190,188,188),1,grad=False);T['top']=txt(Wd['top'],AN,150,(200,198,198),1,grad=False)
T['first']=blurL(txt(Wd['first'],AN,300,(160,158,158),1,grad=False),4);T['we']=txt(Wd['we'],AN,200,(245,245,245),1,grad=False)
BEL=letters(Wd['believe'],AN,240,(250,250,250));BJ=[[-30,25,-18,30,-25,20,-15][k%7] for k in range(len(BEL))];BJ2=[0]*len(BEL)
T['w']=[txt(w,MS,46,(245,245,245),1,grad=False) for w in [x.upper() for x in CFG['end_words']]]
ASSETS=[cutout(3),cutout(1,size=(640,360)),cutout(6,'luma',(0,0,700,752),(560,600))]
PANELS=[(8.05,('v','c3'),210,150,12,-450,-200),(8.12,('s',4),1080,140,-12,450,-200),(8.20,('v','c1'),200,580,-9,-450,250),(8.27,('s',6),1090,590,10,450,250),(8.35,('v','c2'),640,20,4,0,-320),(8.45,('s',3),640,720,-4,0,320)]
PST={4:pst(4),6:pst(6),3:pst(3)}
r=np.random.default_rng(11);KS=r.random(40);STR=KS[((XX*0.7+YY)//110).astype(int)%40]
SHK=np.random.default_rng(5).normal(0,1,(N,2));CELL=(NF[3]*10).astype(int);DIRS=np.random.default_rng(9).normal(0,1,(11,2))
LEGM=np.zeros((H,W),np.float32);_L=T['legacy'];_h,_w=_L.shape[:2];_x0,_y0=(W-_w)//2,(H-_h)//2+20
LEGM[max(0,_y0):_y0+_h,max(0,_x0):_x0+_w]=_L[max(0,-_y0):,max(0,-_x0):max(0,-_x0)+min(W,_w),3][:min(H,_h),:min(W,_w)]
LASTA=[None];FSH=[None]
def shock(fr,t0,t,cy=400):
    d=t-t0
    if not(0<=d<0.3):return fr
    R=np.sqrt((XX-640)**2+(YY-cy)**2)+1e-3;rr=d*2600;amp=28*(1-d/0.3);disp=amp*np.exp(-((R-rr)/55)**2)
    xs=np.clip(XX-disp*(XX-640)/R,0,W-1).astype(np.int32);ys=np.clip(YY-disp*(YY-cy)/R,0,H-1).astype(np.int32)
    o=fr[ys,xs].copy();o[...,0]=fr[ys,np.clip(xs+4,0,W-1)][...,0];return o+(np.exp(-((R-rr)/30)**2)*0.18*(1-d/0.3))[...,None]
def shake(fr,i,t,hits,a0=16):
    amp=sum(a0*np.exp(-(t-h)/0.07) for h in hits if t>=h)
    if amp<0.7:return fr
    dx,dy=SHK[i]*amp;big=toL(toI(fr).resize((int(W*1.06),int(H*1.06)),Image.BILINEAR));x0=int(W*0.03+dx);y0=int(H*0.03+dy)
    x0=max(0,min(big.shape[1]-W,x0));y0=max(0,min(big.shape[0]-H,y0));return big[y0:y0+H,x0:x0+W]
def flare(fr,y,inten,col,cx=640):
    g=np.exp(-((YY-y)/2.5)**2)*np.exp(-((XX-cx)/520)**2)+np.exp(-((YY-y)/14)**2)*np.exp(-((XX-cx)/300)**2)*0.4+np.exp(-((XX-cx)**2+(YY-y)**2)/(2*45**2))*0.8
    return fr+g[...,None]*np.array(col,np.float32)*inten
def segB(t):
    dt=t-3.633;raw=grade(clip('c2',0.5+max(0,dt),0.5,1.2));m=matte(('B',int(t*15)),raw)
    fr=raw*m[...,None]+(raw*0.6+REDG*0.7)*(1-m[...,None])
    if dt<0.2:
        p=ease(dt/0.2);sm=ss(p*1.35-STR,-0.04,0.04)[...,None];fr=LASTA[0]*0.55*(1-sm)+fr*sm;m=m*sm[...,0]
    q=ease(dt/0.14);sy=1+1.5*(1-q);sx=1+0.22*(1-q)
    fr=place(fr,T['lights'],640+12*dt,390,1-0.04*dt,sx=sx,sy=sy,behind=m*(XX>560))
    for k,(x0,v) in enumerate([(200,260),(900,-180)]):
        bar=ss(1-np.abs((XX-(x0+v*dt))-(YY-360)*0.55)/26,0,0.4)*(np.abs(YY-360-k*80)<260);fr=fr*(1-bar[...,None]*0.85)
    return fr
def segC(t):
    raw=grade(clip('c3',1.0+(t-4.77)*1.2,1.0,0.9));m=matte(('C',int(t*15)),raw);dx=-220+(t-4.77)*520
    cv=place(REDC.copy(),T['out'],640,370,1.0+0.03*(t-4.77));car=shiftx(raw,dx);mc=shiftx(m,dx)
    return cv*(1-mc[...,None])+car*mc[...,None]
def segR(t):return place(redbg(False)+BEAMV,T['fear'],640,370,1.0+0.04*(t-5.2))
VEL=np.array([69.0,-240.0])
def PFr(t):
    fr=poster(t);o=VEL*(t-5.73)
    fr=inktext(fr,T['full'],440+o[0],240+o[1],ease((t-5.70)/0.25),ease((t-6.18)/0.3),0,rot=-16)
    fr=inktext(fr,T['thr'],720+o[0],500+o[1],ease((t-5.82)/0.25),ease((t-6.22)/0.3),1,rot=-16)
    fr=inktext(fr,T['no'],380+o[0],600+o[1],ease((t-6.22)/0.28),0,2,rot=-16)
    if t>=6.38:
        p=ease((t-6.38)/0.34);x=1600-p*880
        for k in (3,2,1):
            if p<1:fr=place(fr,T['brakes'],x+o[0]+k*60*(1-p),800+o[1],1,-16,al=0.2*(1-p))
        fr=inktext(fr,T['brakes'],x+o[0],800+o[1],ease((t-6.38)/0.25),0,0,rot=-16)
    fr=inktext(fr,T['limits'],640+o[0],1060+o[1],ease((t-6.6)/0.28),0,1,rot=-16)
    if t>=7.05:
        p=(t-7.05)/0.28;b=np.exp(-((XX-YY*0.8-(-800+p*2400))/400)**2)[...,None];fr=mix(fr,flood((0.8,0.06,0.09)),b*0.6+0.35*ease(p))
    return fr
def segD(t,i):
    dt=t-7.43;raw=grade(clip('c5',0.3+dt*0.5,0.3,1.3));m0=matte(('D',int(t*15)),raw);s=0.78
    cv=REDG.copy()+BEAMV*1.3;cv=cv+(0.5+0.5*NF[1])[...,None]*np.array([0.55,0.03,0.05])*max(0,1-dt/0.3)
    if t>=7.5:
        rg=np.random.default_rng(int(t*15))
        for k in range(8):
            w=int(rg.integers(120,460));h=int(rg.integers(10,42));x=int(rg.integers(250,1030-w//2));y=int(rg.integers(250,520));v=float(rg.uniform(0.3,0.6))
            cv[y:y+h,x:x+w]=mix(cv[y:y+h,x:x+w],(np.linspace(v*0.4,v,w)[None,:,None]*np.ones((h,1,3))),0.7)
    for t0,src,x,y,rt,fx,fy in PANELS:
        if t<t0:continue
        q=ease((t-t0)/0.2);L=pvid(src[1],t-t0) if src[0]=='v' else PST[src[1]];d=(t-t0);px,py=x+fx*(1-q)+d*8,y+fy*(1-q)
        if q<1:
            for k in (3,2,1):cv=place(cv,L,px+fx*0.08*k*(1-q),py+fy*0.08*k*(1-q),1.55,rt+12*(1-q),al=0.2*(1-q))
        cv=place(cv,L,px,py,1.55,rt+12*(1-q),al=0.95)
    p=ease(dt/0.17);x=-200+p*840;rr=-8*ease((t-8.4)/0.25)
    for k in (4,3,2,1):
        if p<1:cv=place(cv,T['racer'],x-k*60*(1-p),430,1,rr,al=0.25)
    cv=place(cv,T['racer'],x,430,1+0.08*ease((t-8.4)/0.25),rr)
    for t0,key,a,b_,rt in [(8.15,'win',(-300,760),(300,600),18),(8.3,'fast',(1600,-60),(1000,230),-16)]:
        if t>=t0:q=ease((t-t0)/0.2);cv=place(cv,T[key],a[0]+(b_[0]-a[0])*q,a[1]+(b_[1]-a[1])*q,1,rt)
    fr,M=comp(cv,raw,m0,s,640,H-s*H/2);fr=place(fr,T['born'],640,int(H-s*H*0.3))
    if 8.0<=t<8.12:fr=flare(fr,int(H-s*H*0.3),1.6*(1-(t-8.0)/0.12),(1,0.78,0.6))
    if 8.4<=t<8.62:fr=flare(fr,int(H-s*H*0.3),1.3*(1-(t-8.4)/0.22),(0.5,0.75,1.0))
    fr=shock(fr,7.43,t);fr=shock(fr,8.0,t,int(H-s*H*0.3));fr=shake(fr,i,t,[7.43,8.0,8.08,8.29,8.41,8.57,8.68])
    z=1.12-0.12*ease((t-8.4)/0.6);fr=zoomcrop(fr,z,640,400)
    if t>=8.9:
        k=ease((t-8.9)/0.3);fr=sum(zoomcrop(fr,1+0.035*j*k) for j in range(4))/4;fr=place(fr,T['legend'],640,330,1+0.1*k,al=0.55*k)
    if t>=9.32:fr=place(fr,T['rise'],420,200,1.6 if t<9.35 else 1.0,-10)
    return fr
def G(t):fr=redbg(False)+BEAMD;fr=place(fr,T['go'],620,400,1.0+0.06*(t-9.42),-15);return place(fr,T['rise'],420,640,0.8,-10)
def shatter(A,p):
    out=np.zeros_like(A)
    for c in range(11):
        dx,dy=(DIRS[c]*p*160).astype(int);sh=np.roll(np.roll(A,dy,0),dx,1);out+=sh*(CELL==c)[...,None]
    return out*(1-nm(p*1.3,0,8)*0.9)
def X(t):
    fr=redbg(False)+BEAMD;d=t-9.68
    for k,x,y,rt,s,vx,vy in [(0,260,250,-18,1.6,40,-10),(1,1020,180,12,1.5,-30,8),(2,760,560,10,1.4,-25,12)]:
        fr=place(fr,blurL(ASSETS[k],1.2),x+vx*d*3,y+vy*d*3,s+0.05*d,rt+d*4,al=0.6)
    p=ease((t-9.82)/0.25);fr=place(fr,T['push'],420,560-p*400,1,-22,al=min(1,p*3));p2=ease((t-9.95)/0.25)
    fr=place(fr,T['faster'],820,1000-p2*560,1,-22);return rotz(fr,-2+4*min(1,d/1.0),1.1)
def scene_E(t,i):
    tt=t-11.13;raw=grade(clip('c7',0.2+tt*0.9,0.2,2.2));m=matte(('E',int(t*15)),raw)
    l=raw.mean(2,keepdims=True);subj=np.clip((raw*0.4+l*0.6)*1.1,0,1)
    g=np.exp(-((XX-640)**2+(YY-245)**2)/(2*85**2))[...,None]*np.array([1,0.85,0.88])*0.9;subj=np.clip(subj+g,0,1)
    z=1.35-0.35*ease(tt/1.6);subj=zoomcrop(subj,z,640,300);m=zoomcrop(m,z,640,300)
    dx=-700*min(1,max(0,(t-12.85)/1.25))**2.2 if t>=12.85 else 0
    bg=REDE.copy()*(0.85 if t>=12.8 else 1.0)
    if t>=12.8:
        p=ease((t-12.8)/0.3);a=shiftx(LEGM,0.3*dx)*nm(p,0,6)[...,0]*(0.6+0.4*NF[4])*(1-ss(NF[1],0.66,0.76)*0.7)
        c=np.dstack([0.85+0.1*NF[3],0.25+0.2*NF[3],0.3+0.2*NF[3]]);bg=bg*(1-a[...,None])+c*a[...,None]
    fr=bg
    if dx!=0 and t<14.2:
        for k,al in ((2,0.25),(1,0.35)):
            mg=shiftx(m,dx+18*k)*al;fr=fr*(1-mg[...,None])+shiftx(subj,dx+18*k)*mg[...,None]
    ms=shiftx(m,dx);fr=fr*(1-ms[...,None])+shiftx(subj,dx)*ms[...,None]
    if t<12.0:
        for k,(L,ox) in enumerate(FOREV):
            tk=11.6+FT[k]*min(0.06,0.42/max(1,len(FOREV)));vis=t<tk or (t<tk+0.1 and int(t*30)%2==0)
            if k==len(FOREV)//2:vis=t<12.0
            if vis:fr=place(fr,L,640+ox,330,1+0.02*tt,behind=ms)
    elif t<13.45:
        fr=place(fr,T['heart'],470+dx,320);fr=place(fr,T['strong'],810+dx,320);bw=min(1,(t-12.0)/0.3)*110
        x1=int(395+dx);x2=int(885+dx)
        if x1-bw>0:fr[316:328,max(0,int(x1-bw)):max(0,x1)]=1.0
        if 0<x2<W:fr[316:328,x2:min(W,int(x2+bw))]=1.0
    if t>=12.8:
        q=ease((t-12.8)/0.15);fr=place(fr,T['always'],900+(760-900)*q+1.8*dx,-150+(90+150)*q)
        if t>=13.3:fr=place(fr,T['top'],1100+1.5*(dx-(-700*min(1,(13.3-12.85)/1.25)**2.2)),90,al=ease((t-13.3)/0.1))
        fr=place(fr,T['first'],640+dx,690,1,al=0.55*ease((t-12.85)/0.2))
        n=min(9,int((t-12.85)/0.07))
        if n>0 and t<13.7:fr=place(fr,txt(Wd['tag']+'-'*n,AN,60,(245,245,245),1,grad=False),1010+n*9+1.2*dx,345)
    if t>=13.6:
        if t<13.666:fr=place(fr,blurL(np.dstack([np.ones((160,220,3),np.float32),np.ones((160,220,1),np.float32)]),18),520,370)
        if t>=13.633:
            b=10 if t<13.7 else (4 if t<13.8 else 0);Lw=blurL(T['we'],b) if b else T['we'];gw=1.0 if t<13.7 else 0.75
            Lw=Lw.copy();Lw[...,:3]*=(gw if t<13.7 else 0.6);fr=place(fr,Lw,110-(t-13.633)*80,370,0.75)
        zw=1+0.3*ease((t-14.1)/0.2)-0.05*ease((t-14.3)/0.1)
        for k,(L,ox) in enumerate(BEL):
            tk=13.7+min(0.07,0.42/max(1,len(BEL)))*k
            if t>=tk:oy=BJ[k]*(1-ease((t-tk)/0.1))+BJ2[k];fr=place(fr,L,700+ox*zw,370+oy*zw,zw*(1.2-0.2*ease((t-tk)/0.07)))
    return fr
def frame(i):
    t=i/FPS
    if t<3.633:
        fr=grade(clip('c1',t*1.3,0,4.8))
        if 2.8<=t<3.1:
            p=(t-2.8)/0.3;pos=200+p*900;band=np.exp(-((XX+0.5*YY-pos-200)/45)**2)[...,None]*(np.abs(YY-300)<160)[...,None]
            fr=fr+band*np.array([0.9,0.7,1.0])*0.55;fr[...,0]+=np.roll(band[...,0],6,1)*0.3;fr[...,2]+=np.roll(band[...,0],-6,1)*0.3
        LASTA[0]=fr;return fr
    if t<4.5:return segB(t)
    if t<4.77:
        fr=segB(t);p=(t-4.5)/0.23;fr=leak(fr,min(1,p),t)
        return mix(fr,flood((1,0.93,0.94)),0.92) if t>=4.73 else fr
    if t<4.83:return mix(segC(t),flood((1,0.93,0.94)),(1-(t-4.77)/0.06)*0.8)
    if t<5.2:return segC(t)
    if t<5.4:return noisetr(segC(t),segR(t),(t-5.2)/0.2,0)
    if t<5.56:return segR(t)
    if t<5.73:return noisetr(segR(t),PFr(t),(t-5.56)/0.17,2)
    if t<7.33:return PFr(t)
    if t<7.40:
        d=np.sqrt(((XX-W/2)/W)**2+((YY-H/2)/H)**2)[...,None];rd=np.clip(np.array([0.95,0.02,0.05])*(1.1-d*1.2),0,1);return mix(PFr(t),rd,0.75)
    if t<7.43:return mix(segD(t,i),flood((0.8,0,0.05)),0.5)
    if t<9.42:return segD(t,i)
    if t<9.68:return G(t)
    if t<9.82:
        p=(t-9.68)/0.14;return mix(shatter(G(t),p),X(t),nm(max(0,p*1.3-0.3),1,8))
    if t<10.7:return X(t)
    if t<10.9:fr=X(t)*0.85;return place(fr,T['now'],640,360,1.8 if t<10.734 else 1.0)
    if t<11.13:
        p=(t-10.9)/0.23;fr=place(X(t)*0.85,T['now'],640,360);return bloom(fr,p)
    if t<14.52:
        fr=scene_E(t,i)
        if t<11.26:fr=bloom(fr,max(0,1-(t-11.13)/0.13)*0.6,640,245)
        return fr
    if t<14.6:fr=scene_E(14.5,i);e=int(min(1,(t-14.52)/0.06)*W);fr[:,:e]=np.array([1,0.97,0.97]);return fr
    tt=t-14.6;raw=grade(clip('c8',0.2+tt*0.9,0.2,2.8));raw=np.clip(raw**0.6*2.0,0,1);m=matte(('F',int(t*10)),raw)
    if FSH[0] is None:
        xs=np.nonzero(m>0.5)[1];FSH[0]=int(640-xs.mean()) if len(xs)>500 else 0
    raw=shiftx(raw,FSH[0]);m=shiftx(m,FSH[0]);fr=REDF*(1-m[...,None])+raw*m[...,None];fr=zoomcrop(fr,1.08-0.08*ease(tt/2.8),640,360)
    k=int(tt/0.3)
    if t<17.0 and k<len(T['w']):fr=place(fr,T['w'][k],640,400)
    return fr*(1-0.82*ease((t-15.6)/1.7))
ONLY=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else None
if ONLY:
    for i in ONLY:
        if i>=109 and LASTA[0] is None:frame(108)
        toI(post(np.asarray(frame(i),np.float32),i)).resize((480,270)).save(f'pv_{i}.jpg')
    print('PREVIEW OK');sys.exit()
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-']+(['-i',CFG['audio'],'-map','0:v','-map','1:a','-c:a','aac','-b:a','192k','-shortest'] if os.path.exists(CFG['audio']) else ['-an'])+['-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for i in range(N):
    enc.stdin.write((post(np.asarray(frame(i),np.float32),i)*255).astype(np.uint8).tobytes())
    if i%50==0:print('frame',i,flush=True)
enc.stdin.close();enc.wait();print('DONE',OUT)
