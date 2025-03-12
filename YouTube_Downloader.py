import os, tkinter, time, sys, threading, re
from tkinter import scrolledtext
from yt_dlp import YoutubeDL

desktopPath = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")
dire = os.getcwd().replace(os.path.sep, "/")

class Data:
    status = "URLを入力してください"
    title = ""
    endFlag = 0
    exeFlag = 0
    stdOutFilePath =  f"{dire}/tmp"

class YoutubeDLG():
    def __init__(self, title = "YouTube_Downloader", sizeWidth = 800, sizeHeight = 600, bgColor = "white", fgColor = "black"):
        with ChangeStdOut(mode = "w"):
            print("", flush = True)
            
        Data.title = title
        self.body = tkinter.Tk()
        self.body.title(Data.title) # ウィンドウタイトル
        self.body.geometry(f"{str(sizeWidth)}x{str(sizeHeight)}") # ウィンドウサイズ
        self.body.configure(background = bgColor)
        self.body.iconbitmap(f"{dire}/YouTube.ico")
        self.body.resizable(0,0)
        
        #ボタン
        self.exeButton = tkinter.Button(self.body, text = "実行", command = self.dl_movie , font=("HGPｺﾞｼｯｸE", "12"))
        self.exeButton.pack(padx=10,pady = 40, anchor=tkinter.NE, ipadx=30)
        
        
        #テキストラベル
        self.statusLabel = tkinter.Label(self.body, text = Data.status, font = ("HGPｺﾞｼｯｸE", "10"), background = bgColor, foreground= fgColor, anchor="w", justify="left")
        self.statusLabel.place(x = 10, y = 10)
        
        
        #テキストボックス
        self.inputURL = tkinter.Entry(self.body, width = 50 , font=("HGPｺﾞｼｯｸE", "15"), relief = tkinter.SOLID, foreground= fgColor)
        self.inputURL.extra = "inputURL" # extraで変数名を登録
        self.inputURL.place(x = 40, y = 40)
        self.inputURL.bind("<Button-3>", self.right_click_menu)
        self.inputURL.bind("<Return>", self.download)
        
        # テキストエリア
        self.consoleText = scrolledtext.ScrolledText(
            self.body,
            font=("HGPｺﾞｼｯｸE", 10),
            height= int((sizeHeight - 80) / 13),
            width = int((sizeWidth - 10) / 7) - 2,
            background = bgColor,
            foreground= fgColor,
            insertbackground = fgColor,
        )
        self.consoleText.extra = "consoleText" # extraで変数名を登録
        self.consoleText.place(x = 10, y = 80)
        self.consoleText.bind("<Button-3>", self.right_click_menu)#右クリックが押されたら
        
        self.body.after(100, self.update_string)
        self.body.mainloop()
        
    def update_string(self):
        self.statusLabel["text"] = Data.status
        self.body.title(Data.title)
        if Data.exeFlag != 0:
            with open(Data.stdOutFilePath, mode = "r") as consoleDisp:
                consoleData = consoleDisp.read()
                self.consoleText.delete("1.0", "end")
                self.consoleText.insert("end", consoleData)
                self.consoleText.see('end')
            
        # マルチスレッドで動かしても正常終了出来るようにする
        if Data.endFlag != 0:
            self.end()
        else:
            self.body.after(100, self.update_string)
            
    
    def dl_movie(self):
        url = self.inputURL.get()
        #url = url.replace("x.com", "twitter.com")
        downloadThread = threading.Thread(
            target = download_youtube, 
            kwargs = { 
                "arrayURL" : [str(url)],
                "fileName"  : "%(id)s",
            }
        )
        
        downloadThread.start()
        self.inputURL.delete(0, tkinter.END)
    
    def download(self, event):
        self.dl_movie()
    
    def right_click_menu(self, event): #右クリック設定
        name = eval(f"self.{str(event.widget.extra)}") # extraの値取得
        rightMenu = tkinter.Menu(name, tearoff=0, font=("HGPｺﾞｼｯｸE", 10))
        rightMenu.add_command(label="コピー",command = lambda:self.copy_text(name))
        rightMenu.add_separator()
        rightMenu.add_command(label="貼り付け",command = lambda:self.paste_text(name))
        rightMenu.post(event.x_root, event.y_root)
    
    def copy_text(self, widgetName):
        try:
            widgetName.clipboard_clear()
            if widgetName == self.consoleText: # テキストエリアを使う場合の動作
                copyTxt = widgetName.get(tkinter.SEL_FIRST, tkinter.SEL_LAST)
            else:
                copyTxt = widgetName.selection_get()
            widgetName.clipboard_append(copyTxt)
            Data.status = f"コピー : {copyTxt}"
            
        except:
            Data.status = "コピー出来ませんでした"
            widgetName.clipboard_clear()
    
    def paste_text(self, widgetName):
        try:
            pasteTxt = widgetName.clipboard_get()
            widgetName.insert(tkinter.INSERT, pasteTxt)
            Data.status = f"貼り付け : {pasteTxt}"
        except:
            Data.status = "貼り付け出来ませんでした"
    
    def end(self):
        self.body.destroy()
        

def download_youtube(arrayURL = [], dir = str(desktopPath), fileName = "%(title)s"):
    movieName = str(re.sub(r"\\|\=|\?|\.|\:|\+|\*|\"|\!|\<|\>|\||/|@|：|／|　", "", fileName))[:20]
    downloadOption = {
        "outtmpl" : f"{dir}/{movieName}.%(ext)s",
        "title": movieName,
        "format" : "bestvideo+bestaudio/best",
        "cookiesfrombrowser" : ('firefox', None, None, None),
        "verbose" : True,
        "download" : True,
        "windowsfilenames" : True,
        "trim_file_name" : 60,
    }
    
    try:
        Data.exeFlag = 1
        errorFlag = 0
        Data.status = "ダウンロード中"
        with ChangeStdOut(mode = "w"):
            with YoutubeDL(downloadOption) as ydl:
                ydl.download(arrayURL)
            
    except Exception as errorText:
        Data.status = "失敗しました"
        with ChangeStdOut():
            print(errorText, flush=True)
        errorFlag = 1
        
    finally:
        time.sleep(1)
        Data.exeFlag = 0
        if errorFlag == 0:
            Data.status = "ダウンロード終了"

class ChangeStdOut(): # __enter__と__exit__でブロック構文利用可能
    def __init__(self, filename = f"{dire}/tmp", mode = "a"):
        Data.stdOutFilePath = filename
        self.mode = mode

    def __enter__(self):
        sys.stdout = open(Data.stdOutFilePath, self.mode)

    def __exit__(self, *args):
        sys.stdout = sys.__stdout__

if __name__ == "__main__":
    YoutubeDLG(bgColor = "black", fgColor = "#33FF00")
    