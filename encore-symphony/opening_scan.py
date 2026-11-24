from assets import *
from PIL import Image
import cv2, numpy as np
from collections import Counter
SRC=source('Encore')/'mov/0001.mpg'
OUT=ROOT/'opening'; OUT.mkdir(exist_ok=True)
def gray(im):return cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
def features(img):
    roi=gray(img); flat=np.max(img,2)-np.min(img,2)
    white=((roi>=238)&(flat<12)).astype('uint8')
    contours=cv2.findContours(white,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
    if not contours:return 0,None,None,False
    cont=max(contours,key=cv2.contourArea);area=cv2.contourArea(cont)
    mask=np.zeros_like(white);cv2.drawContours(mask,[cont],0,255,cv2.FILLED)
    x,y,w,h=cv2.boundingRect(cont)
    ellipse=cv2.fitEllipse(cont) if len(cont)>=5 else None
    clipped=(x==0 or y==0 or x+w==1280 or y+h==720)
    return area,mask,ellipse,clipped
def main():
    d=OUT/'samples';d.mkdir(exist_ok=True)
    cap=cv2.VideoCapture(str(SRC));i=0;info={};take={0,2100,2115,2120,2125,2130,2145,2160,2202,2208,2214,2220,2225,2230,2240,2250,2260,2270,2280,2290,2300,2310,2320,2330,2340,2350,2360,2370,2380,2390,2400,2410,2430,2450,2470,2490,2500,2510,2520,3500,3530,3590,3650,3695,3740}
    while cap.grab():
        if 2070<=i<=2530 or 3440<=i<=3800 or i in take:
            ok,im=cap.retrieve();assert ok
            if 2070<=i<=2530:
                area,m,el,cl=features(im)
                info[i]=dict(area=round(area),ellipse=el,clipped=cl,white=round(float((gray(im)>242).mean()),4))
            if i in take:cv2.imwrite(str(d/f'{i}.jpg'),im,[cv2.IMWRITE_JPEG_QUALITY,93])
        i+=1
    cap.release();save('audit/op_frame_scan.json',dict(frames=i,stats=info))
    print('Frames',i,[(j,info[j]['area']) for j in sorted(info) if j%10==0 and 2110<=j<=2530])
if __name__=='__main__':main()

