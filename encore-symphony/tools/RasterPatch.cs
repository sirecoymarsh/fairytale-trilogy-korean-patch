using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using RaiLTools;
class RasterPatch {
    static readonly FieldInfo BitmapField=typeof(WcgImage).GetField("_Bitmap",BindingFlags.Instance|BindingFlags.NonPublic);
    static byte[] CopyPixels(Bitmap bmp, Rectangle rect,out int stride) {
        BitmapData data=bmp.LockBits(rect,ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
        try {stride=data.Stride;if(stride<0)throw new InvalidDataException("negative stride");var result=new byte[stride*bmp.Height];Marshal.Copy(data.Scan0,result,0,result.Length);return result;}
        finally {bmp.UnlockBits(data);}
    }
    public static void Main(string[] args) {
        Parallel.ForEach(File.ReadAllLines(args[0]),new ParallelOptions{MaxDegreeOfParallelism=5},line=>{
            string[] p=line.Split('\t');using(var src=WcgImage.FromFile(p[0]))
            using(var desired=new Bitmap(p[1]))
            using(var mask=new Bitmap(p[2])) {
                var bitmap=(Bitmap)BitmapField.GetValue(src);
                var rect=new Rectangle(0,0,src.Width,src.Height);
                if(desired.Size!=rect.Size || mask.Size!=rect.Size)throw new Exception("Geometry mismatch "+p[0]);
                int ds,ms;var colors=CopyPixels(desired,rect,out ds);var ownership=CopyPixels(mask,rect,out ms);
                BitmapData b=bitmap.LockBits(rect,ImageLockMode.ReadWrite,PixelFormat.Format32bppArgb);
                try {
                    var outbuf=new byte[b.Stride*rect.Height];Marshal.Copy(b.Scan0,outbuf,0,outbuf.Length);
                    for(int y=0;y<rect.Height;y++)for(int x=0;x<rect.Width;x++)if(ownership[y*ms+x*4]!=0)Array.Copy(colors,y*ds+x*4,outbuf,y*b.Stride+x*4,4);
                    Marshal.Copy(outbuf,0,b.Scan0,outbuf.Length);
                } finally {bitmap.UnlockBits(b);}
                src.Save(p[3]);
            }
            using(var saved=WcgImage.FromFile(p[3]))
            using(var img=saved.ToImage()) img.Save(p[4],ImageFormat.Png);
        });
    }
}
