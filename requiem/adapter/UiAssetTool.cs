using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Reflection;
using RaiLTools;

namespace ForestUiAssetTool
{
    internal static class Program
    {
        private static int Usage()
        {
            Console.Error.WriteLine(
                "Usage:\n" +
                "  UiAssetTool wcg2png <input.wcg> <output.png>\n" +
                "  UiAssetTool png2wcg <input.png> <output.wcg>\n" +
                "  UiAssetTool wcg-roundtrip-pixels <input.wcg> <output.wcg>\n" +
                "  UiAssetTool wcg-apply-patch <input.wcg> <patch.png> <mask.png> <output.wcg>\n" +
                "  UiAssetTool lwg-extract-raw <input.lwg> <output-dir>\n" +
                "  UiAssetTool lwg-extract-png <input.lwg> <output-dir>\n" +
                "  UiAssetTool lwg-pack-raw <input-dir> <output.lwg>\n" +
                "  UiAssetTool lwg-pack-png <input-dir> <output.lwg>\n" +
                "  UiAssetTool lwg-roundtrip <input.lwg> <output.lwg>");
            return 2;
        }

        private static int ApplyWcgPatch(string input, string patchPath, string maskPath, string output)
        {
            EnsureParent(output);

            using (var wcg = WcgImage.FromFile(input))
            using (var patch = new Bitmap(patchPath))
            using (var mask = new Bitmap(maskPath))
            {
                var bitmapField = typeof(WcgImage).GetField(
                    "_Bitmap",
                    BindingFlags.Instance | BindingFlags.NonPublic);

                if (bitmapField == null)
                    throw new InvalidOperationException("WcgImage bitmap field not found.");

                var target = bitmapField.GetValue(wcg) as Bitmap;
                if (target == null)
                    throw new InvalidOperationException("WcgImage bitmap is unavailable.");

                if (patch.Width != target.Width || patch.Height != target.Height ||
                    mask.Width != target.Width || mask.Height != target.Height)
                    throw new InvalidDataException("Base, patch, and mask dimensions must match.");

                int changed = 0;
                for (int y = 0; y < target.Height; y++)
                {
                    for (int x = 0; x < target.Width; x++)
                    {
                        Color m = mask.GetPixel(x, y);
                        if (m.R == 0 && m.G == 0 && m.B == 0)
                            continue;

                        target.SetPixel(x, y, patch.GetPixel(x, y));
                        changed++;
                    }
                }

                wcg.Save(output);
                Console.WriteLine("patched_pixels=" + changed);
            }

            Console.WriteLine(output);
            return 0;
        }

        private static void EnsureParent(string path)
        {
            string parent = Path.GetDirectoryName(Path.GetFullPath(path));
            if (!Directory.Exists(parent))
                Directory.CreateDirectory(parent);
        }

        private static int Main(string[] args)
        {
            if (args.Length < 1)
                return Usage();

            string command = args[0];

            if (command == "wcg-apply-patch")
            {
                if (args.Length != 5)
                    return Usage();
                return ApplyWcgPatch(
                    Path.GetFullPath(args[1]),
                    Path.GetFullPath(args[2]),
                    Path.GetFullPath(args[3]),
                    Path.GetFullPath(args[4]));
            }

            if (args.Length != 3)
                return Usage();

            string input = Path.GetFullPath(args[1]);
            string output = Path.GetFullPath(args[2]);

            switch (command)
            {
                case "wcg2png":
                    EnsureParent(output);
                    using (var wcg = WcgImage.FromFile(input))
                    using (var image = wcg.ToImage())
                        image.Save(output, ImageFormat.Png);
                    break;

                case "png2wcg":
                    EnsureParent(output);
                    using (var image = Image.FromFile(input))
                    using (var wcg = WcgImage.FromImage(image))
                        wcg.Save(output);
                    break;

                case "wcg-roundtrip-pixels":
                    EnsureParent(output);
                    using (var wcg = WcgImage.FromFile(input))
                        wcg.Save(output);
                    break;

                case "lwg-extract-raw":
                    LwgCanvas.FromFile(input).ExportToDirectory(output, false);
                    break;

                case "lwg-extract-png":
                    LwgCanvas.FromFile(input).ExportToDirectory(output, true);
                    break;

                case "lwg-pack-raw":
                    EnsureParent(output);
                    LwgCanvas.FromDirectory(input, false).Save(output);
                    break;

                case "lwg-pack-png":
                    EnsureParent(output);
                    LwgCanvas.FromDirectory(input, true).Save(output);
                    break;

                case "lwg-roundtrip":
                    EnsureParent(output);
                    LwgCanvas.FromFile(input).Save(output);
                    break;

                default:
                    return Usage();
            }

            Console.WriteLine(output);
            return 0;
        }
    }
}
