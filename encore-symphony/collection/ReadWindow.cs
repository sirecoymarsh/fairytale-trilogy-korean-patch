using System;
using System.Windows.Automation;
using System.Threading;
class ReadWindow{
 [STAThread]static void Main(string[] a){
 if(a.Length>1){var f=new System.IO.StreamWriter(a[1]);f.AutoFlush=true;Console.SetOut(f);}
var root=AutomationElement.FromHandle((IntPtr)Int32.Parse(a[0]));
 for(int i=0;i<2;i++){
 foreach(AutomationElement el in root.FindAll(TreeScope.Descendants,Condition.TrueCondition)){
 try{if(el.Current.ControlType==ControlType.Slider){var v=((RangeValuePattern)el.GetCurrentPattern(RangeValuePattern.Pattern)).Current;Console.WriteLine("SLIDER "+v.Value+" / "+v.Maximum);}
 else if(el.Current.ControlType==ControlType.Button||el.Current.ControlType==ControlType.Text)Console.WriteLine(el.Current.ControlType.ProgrammaticName+" "+el.Current.Name);}catch(ElementNotAvailableException){}
 }if(i==0)Thread.Sleep(1200);}
 }}

