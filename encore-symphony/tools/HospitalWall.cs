using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

class HospitalWall {
    // This narrow window lies entirely above the counter. Its outer edges stay fixed.
    const int X0=466,Y0=0,W=194,H=147;
    static double Clip(double a,double l,double r){return Math.Max(l,Math.Min(a,r));}
    static double T(double x){return (x-486)/158.0;}
    static double Top(double x){return 93-85*T(x);}
    static double Bottom(double x){return 131-77*T(x);}
    static double Channel(Color co,int c){return c==0?co.R:c==1?co.G:co.B;}
    static double Sample(Bitmap im,double x,double y,int c) {
        x=Clip(x,0,im.Width-1.001);y=Clip(y,0,im.Height-1.001);
        int ix=(int)x,iy=(int)y;double dx=x-ix,dy=y-iy;
        return (1-dy)*((1-dx)*Channel(im.GetPixel(ix,iy),c)+dx*Channel(im.GetPixel(ix+1,iy),c))
            +dy*((1-dx)*Channel(im.GetPixel(ix,iy+1),c)+dx*Channel(im.GetPixel(ix+1,iy+1),c));
    }
    static double EdgeMedian(Bitmap im,int x,bool upper,int c) {
        double[] values=new double[25];int n=0;
        for(int dx=-2;dx<=2;dx++)for(int j=0;j<5;j++){
            int xx=x+dx,yy=(int)Math.Round(upper?Top(xx)-11+j:Bottom(xx)+6+j);
            values[n++]=Channel(im.GetPixel(xx,Math.Max(0,yy)),c);
        }
        Array.Sort(values);return values[12];
    }
    static int Byte(double d){return (int)Math.Round(Clip(d,0,255));}
    static void Main(string[] args) {
        using(var src=new Bitmap(args[0]))
        using(var clean=(Bitmap)src.Clone())
        using(var erased=new Bitmap(src.Width,src.Height,PixelFormat.Format32bppArgb)) {
            if(src.Width!=1280||src.Height!=720)throw new InvalidDataException("Unexpected source canvas");
            int[,] dist=new int[W,H];
            var mask=new bool[W,H];var bright=new double[W,H];var donor=new double[W,H,3];
            var light=new double[W,H,3];var delta=new double[W,H,3];var tmp=new double[W,H,3];
            for(int ix=0;ix<W;ix++){
                int x=ix+X0;double[] hi=new double[3],lo=new double[3];
                for(int c=0;c<3;c++){hi[c]=EdgeMedian(src,x,true,c);lo[c]=EdgeMedian(src,x,false,c);}
                for(int iy=0;iy<H;iy++){
                    int y=Y0+iy;Color p=src.GetPixel(x,y);double val=Clip((y-Top(x)+9)/(Bottom(x)-Top(x)+18),0,1),dark=0,lum=0;
                    // A single adjoining, unlettered stretch of the same plaster panel.
                    double u=T(x),sx=431+111*u,sy=y-29*(1-u);
                    for(int c=0;c<3;c++){
                        double bg=hi[c]*(1-val)+lo[c]*val,ink=Channel(p,c);
                        light[ix,iy,c]=bg;donor[ix,iy,c]=Sample(src,sx,sy,c);
                        dark=Math.Max(dark,bg-ink);lum=Math.Max(lum,ink-bg);
                    }
                    bright[ix,iy]=lum;dist[ix,iy]=9999;
                    if(x>=485&&x<=645&&y>=Top(x)-8&&y<=Bottom(x)+2&&dark>=13)dist[ix,iy]=0;
                }
            }
            var seeds=(int[,])dist.Clone();
            for(int x=0;x<W;x++)for(int y=0;y<H;y++){
                if(seeds[x,y]!=0)continue;
                for(int dx=-8;dx<=8;dx++)for(int dy=-8;dy<=8;dy++){
                    int px=x+dx,py=y+dy;if(px<0||px>=W||py<0||py>=H)continue;
                    dist[px,py]=Math.Min(dist[px,py],dx*dx+dy*dy);
                }
            }
            int count=0;
            using(var g=Graphics.FromImage(erased)){g.Clear(Color.Black);}
            for(int x=0;x<W;x++)for(int y=0;y<H;y++){
                int xx=x+X0,yy=y+Y0;
                bool owns=dist[x,y]<=30 || (dist[x,y]<=64&&bright[x,y]>5);
                mask[x,y]=owns;
                if(owns){erased.SetPixel(xx,yy,Color.White);count++;}
                for(int c=0;c<3;c++){
                    double baseValue=owns? light[x,y,c]:Channel(src.GetPixel(xx,yy),c);
                    delta[x,y,c]=tmp[x,y,c]=baseValue-donor[x,y,c];
                }
            }
            // Boundary-matched illumination preserves the grain in that one donor patch.
            for(int iter=0;iter<520;iter++) {
                double largest=0;
                for(int x=1;x<W-1;x++)for(int y=1;y<H-1;y++)if(mask[x,y])for(int c=0;c<3;c++) {
                    double v=(delta[x-1,y,c]+delta[x+1,y,c]+delta[x,y-1,c]+delta[x,y+1,c])*.25;
                    tmp[x,y,c]=v;largest=Math.Max(largest,Math.Abs(v-delta[x,y,c]));
                }
                var swap=delta;delta=tmp;tmp=swap;
                if(largest<.009)break;
            }
            for(int x=0;x<W;x++)for(int y=0;y<H;y++)if(mask[x,y]) {
                int r=Byte(donor[x,y,0]+delta[x,y,0]),g=Byte(donor[x,y,1]+delta[x,y,1]),b=Byte(donor[x,y,2]+delta[x,y,2]);
                clean.SetPixel(x+X0,y+Y0,Color.FromArgb(255,r,g,b));
            }
            if(count<1000||count>8000)throw new InvalidDataException("Unexpected text mask area "+count);
            clean.Save(Path.Combine(args[1],"clean.png"),ImageFormat.Png);
            erased.Save(Path.Combine(args[1],"source-mask.png"),ImageFormat.Png);
            Console.WriteLine("Restored source area: "+count+" pixels.");
        }
    }
}