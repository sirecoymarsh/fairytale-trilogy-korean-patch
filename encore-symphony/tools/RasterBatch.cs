using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;
using System.Threading.Tasks;
using RaiLTools;
class RasterBatch {
    static void Main(string[] args) {
        var rows=File.ReadAllLines(args[0]);
        Parallel.ForEach(rows,new ParallelOptions {MaxDegreeOfParallelism=6}, line=>{
            var f=line.Split('\t'); var src=f[0]; var dst=f[3];
            if(File.Exists(dst))return;
            var p=new byte[int.Parse(f[2])];
            using(var input=File.OpenRead(src)) {
                input.Seek(long.Parse(f[1]),SeekOrigin.Begin);
                int got=0; while(got<p.Length){int n=input.Read(p,got,p.Length-got);if(n==0)throw new EndOfStreamException();got+=n;}
            }
            using(var wcg=WcgImage.FromBytes(p))
            using(var img=wcg.ToImage()) {
                int limit=int.Parse(f[4]);
                if(limit==0 || (img.Width<=limit && img.Height<=limit))img.Save(dst,ImageFormat.Png);
                else {
                    double scale=Math.Min((double)limit/img.Width,(double)limit/img.Height);
                    using(var little=new Bitmap(Math.Max(1,(int)Math.Round(img.Width*scale)),Math.Max(1,(int)Math.Round(img.Height*scale)),PixelFormat.Format32bppArgb))
                    using(var graph=Graphics.FromImage(little)) {
                        graph.InterpolationMode=InterpolationMode.HighQualityBicubic;
                        graph.PixelOffsetMode=PixelOffsetMode.HighQuality;
                        graph.DrawImage(img,new Rectangle(0,0,little.Width,little.Height));
                        little.Save(dst,ImageFormat.Png);
                    }
                }
            }
        });
    }
}
