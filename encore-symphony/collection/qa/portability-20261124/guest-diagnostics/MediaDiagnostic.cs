using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Web.Script.Serialization;

internal static class MediaDiagnostic {
    [STAThread] static void Main(string[] args) {
        if(Environment.UserName!="WDAGUtilityAccount"||args.Length!=2)return;
        string output=Path.Combine(args[1],"windows-media.json");
        var report=new Dictionary<string,object>();
        Action save=()=>File.WriteAllText(output,new JavaScriptSerializer().Serialize(report));
        try {
            string system=Environment.GetFolderPath(Environment.SpecialFolder.System);
            var moduleNames=new[]{"wmp.dll","mfplat.dll","quartz.dll","wmploc.dll","msmpeg2vdec.dll"};
            report["components"]=moduleNames.ToDictionary(k=>k,k=>File.Exists(Path.Combine(system,k)));
            var app=new Application();var window=new Window{Width=640,Height=400,Title="Media compatibility check"};
            window.Loaded+=async (s,e)=>{
                try{
                    var paths=new List<string>{Path.Combine(args[0],@"Cinema\Encore\0001.mpg")};
                    var local=Directory.GetFiles(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows),"Media"),"*.wav").FirstOrDefault();
                    if(local!=null)paths.Add(local);
                    foreach(var path in paths) {
                        var result=new Dictionary<string,object>();report[path]=result;result["size"]=new FileInfo(path).Length;
                        var media=new MediaElement{LoadedBehavior=MediaState.Manual,UnloadedBehavior=MediaState.Manual,Volume=.1};
                        media.MediaFailed+=(ms,me)=>{var err=me.ErrorException.GetBaseException();result["error"]=err.Message;result["hr"]=err.HResult.ToString("X8");save();};
                        media.MediaOpened+=(ms,me)=>{result["opened"]=true;save();};
                        media.MediaEnded+=(ms,me)=>{result["ended"]=true;save();};
                        window.Content=media;await Task.Delay(100);media.Source=new Uri(path);media.Play();
                        await Task.Delay(2600);result["t1"]=media.Position.TotalSeconds;
                        await Task.Delay(2400);result["t2"]=media.Position.TotalSeconds;result["width"]=media.NaturalVideoWidth;
                        result["height"]=media.NaturalVideoHeight;if(media.NaturalDuration.HasTimeSpan)result["duration"]=media.NaturalDuration.TimeSpan.TotalSeconds;
                        media.Close();save();
                    }
                }catch(Exception e1){report["error"]=e1.ToString();}
                finally{save();window.Close();}
            };
            app.Run(window);
        } catch(Exception ex){report["error"]=ex.ToString();save();}
    }
}