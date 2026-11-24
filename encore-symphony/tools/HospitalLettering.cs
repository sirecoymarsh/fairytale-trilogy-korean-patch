using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;

class HospitalLettering {
    const int NS=8, Width=1280, Height=720;
    const double Xstart=.08, Xstep=.214, InkWidth=.190, Ystart=.060, InkHeight=.885;
    static int Byte(double a){return (int)Math.Round(Math.Max(0,Math.Min(255,a)));}
    static void Main(string[] args) {
        string root=args[0];
        using(var master=new Bitmap(Path.Combine(root,"sign-master.png")))
        using(var ground=new Bitmap(Path.Combine(root,"clean.png")))
        using(var sourceMask=new Bitmap(Path.Combine(root,"source-mask.png")))
        using(var final=(Bitmap)ground.Clone())
        using(var layer=new Bitmap(Width,Height,PixelFormat.Format32bppArgb))
        using(var mask=(Bitmap)sourceMask.Clone()) {
            if(ground.Width!=Width||ground.Height!=Height)throw new InvalidDataException("Unexpected canvas");
            int mw=master.Width,mh=master.Height;
            var data=master.LockBits(new Rectangle(0,0,mw,mh),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
            int stride=data.Stride;
            var bytes=new byte[stride*mh];Marshal.Copy(data.Scan0,bytes,0,bytes.Length);master.UnlockBits(data);
            // Keep each independent jamo with its parent syllable for optical spacing on the wall.
            var visited=new bool[mw*mh];var owner=new byte[mw*mh];var queue=new int[mw*mh];
            int[] left={mw,mw,mw,mw},right={0,0,0,0};int top=mh,bot=0;
            int[] dx={-1,0,1,-1,1,-1,0,1},dy={-1,-1,-1,0,0,1,1,1};
            for(int i=0;i<mw*mh;i++) {
                int ix=i%mw,iy=i/mw;if(visited[i]||bytes[iy*stride+ix*4+3]<12)continue;
                int head=0,tail=1;long sumX=0;queue[0]=i;visited[i]=true;
                while(head<tail){
                    int pos=queue[head++],x=pos%mw,y=pos/mw;sumX+=x;
                    for(int k=0;k<8;k++){
                        int xx=x+dx[k],yy=y+dy[k];if(xx<0||xx>=mw||yy<0||yy>=mh)continue;
                        int q=yy*mw+xx;if(visited[q]||bytes[yy*stride+xx*4+3]<12)continue;
                        visited[q]=true;queue[tail++]=q;
                    }
                }
                if(tail<1200)continue;
                double center=(double)sumX/tail/mw;
                int group=center<.285?0:center<.50?1:center<.71?2:3;
                for(int j=0;j<tail;j++){
                    int pos=queue[j],x=pos%mw,y=pos/mw;owner[pos]=(byte)(group+1);
                    left[group]=Math.Min(left[group],x);right[group]=Math.Max(right[group],x);
                    top=Math.Min(top,y);bot=Math.Max(bot,y);
                }
            }
            foreach(int l in left)if(l>=mw)throw new InvalidDataException("Missing Hangul syllable");
            const int x0=478,x1=651,y0=1,y1=141;
            int width=x1-x0+1,height=y1-y0+1;
            var rgba=new double[width,height,4];
            for(int x=x0;x<=x1;x++)for(int y=y0;y<=y1;y++) {
                double aa=0,rr=0,gg=0,bb=0;
                for(int ax=0;ax<NS;ax++)for(int ay=0;ay<NS;ay++){
                    double xx=x+(ax+.5)/NS-.5,yy=y+(ay+.5)/NS-.5,t=(xx-486)/158.0,q=38.0/46;
                    double u=t/(q+(1-q)*t),v=(yy-93+85*t)/(38+8*t);
                    int group=(int)Math.Floor((u-Xstart)/Xstep);
                    if(group<0||group>3)continue;
                    double within=(u-Xstart-group*Xstep)/InkWidth,vert=(v-Ystart)/InkHeight;
                    if(within<0||within>=1||vert<0||vert>=1)continue;
                    int sx=left[group]+(int)(within*(right[group]-left[group]+1));
                    int sy=top+(int)(vert*(bot-top+1));
                    if(owner[sy*mw+sx]!=group+1)continue;
                    int off=sy*stride+sx*4;double a=bytes[off+3]/255.0;
                    double r=bytes[off+2],g=bytes[off+1],b=bytes[off];
                    double f=Math.Max(0,Math.Min(1,(.3*r+.59*g+.11*b-95)/100));
                    aa+=a;rr+=a*Byte(r-7+4*f);gg+=a*Byte(g+1+7*f);bb+=a*Byte(b+5+13*f);
                }
                int ix=x-x0,iy=y-y0;
                rgba[ix,iy,3]=aa/(NS*NS);
                if(aa>0){rgba[ix,iy,0]=rr/aa;rgba[ix,iy,1]=gg/aa;rgba[ix,iy,2]=bb/aa;}
            }
            int pixels=0;var box=Rectangle.Empty;
            for(int ix=1;ix<width-1;ix++)for(int iy=1;iy<height-1;iy++){
                double a=rgba[ix,iy,3];
                double adjacent=Math.Max(Math.Max(rgba[ix-1,iy,3],rgba[ix+1,iy,3]),Math.Max(rgba[ix,iy-1,3],rgba[ix,iy+1,3]));
                double rim=.48*adjacent*(1-a),coverage=a+rim;
                int alpha=Byte(255*coverage);if(alpha==0)continue;
                int[] edge={146,141,132};int[] ink=new int[3];
                for(int ch=0;ch<3;ch++)ink[ch]=Byte((rgba[ix,iy,ch]*a+edge[ch]*rim)/coverage);
                int x=ix+x0,y=iy+y0;var bg=ground.GetPixel(x,y);
                layer.SetPixel(x,y,Color.FromArgb(alpha,ink[0],ink[1],ink[2]));
                double mix=alpha/255.0;
                final.SetPixel(x,y,Color.FromArgb(255,Byte(bg.R*(1-mix)+ink[0]*mix),Byte(bg.G*(1-mix)+ink[1]*mix),Byte(bg.B*(1-mix)+ink[2]*mix)));
                mask.SetPixel(x,y,Color.White);pixels++;
                Rectangle pixel=new Rectangle(x,y,1,1);box=box.IsEmpty?pixel:Rectangle.Union(box,pixel);
            }
            if(pixels<1000||pixels>6500||box.Top<1||box.Bottom>135)throw new InvalidDataException("Letter bounds "+box+" area "+pixels);
            layer.Save(Path.Combine(root,"target-layer.png"),ImageFormat.Png);
            final.Save(Path.Combine(root,"final.png"),ImageFormat.Png);
            mask.Save(Path.Combine(root,"ownership.png"),ImageFormat.Png);
            Console.WriteLine("Registered Hangul: "+box+" area "+pixels);
        }
    }
}
