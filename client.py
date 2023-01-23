import socket
import tkinter as tk
import tkinter.messagebox as msb
import tkinter.simpledialog as smp
from tkinter.scrolledtext import ScrolledText
import tkinter.filedialog as fd
import threading
import time
import datetime
from PIL import Image,ImageTk,ImageFile
import io
import random
import platform

DEFAULT_PORT = 33535

ImageFile.LOAD_TRUNCATED_IMAGES = True

START_TEXT = """
Welcome to tkChat!

Please keep the chat civil and polite!

Type /online to get online users!
"""

class Client():
    def __init__(self,host,port,name,wid):
        self.host = host
        self.port = port
        self.username = name
        self.wid=wid
        self.last = None
        self.images = []

    def time(self):
        return datetime.datetime.now().strftime("%H:%M")

    def create_connection(self):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.s.connect((self.host,self.port))

        self.s.send(self.username.encode())
        
        message_handler = threading.Thread(target=self.handle_messages,args=())
        message_handler.daemon=True
        message_handler.start()
        self.notify(START_TEXT)

    def get_tag(self,name):
        if name == " "+self.username+" ":
            tag = 'you'
        elif name == " System ":
            tag = 'sys'
        else:
            tag = 'oth'
        return tag

    def handle_messages(self):
        global client
        while True:
            try:
                try:
                    msg = self.s.recv(9999999)
                    msg = msg.decode()
                except:
                    try:
                        self.wid['state']="normal"
                        fp = " "+msg.split(b" - ")[0].decode()+" "
                        lp = b" - ".join(msg.split(b" - ")[1:])
                        bio = io.BytesIO(lp)
                        img = Image.open(bio)
                        imgtk = ImageTk.PhotoImage(img)
                        self.wid.insert("end",self.time()+" ",'time')
                        self.wid.insert("end",fp,self.get_tag(fp))
                        self.wid.image_create("end",image=imgtk)
                        self.wid.photo = imgtk
                        self.images.append(imgtk)
                        self.wid.insert("end","\n\n")
                        self.wid.see("end")
                        self.wid['state']="disabled"
                        continue
                    except Exception as e:
                        self.notify(str(e))
                        continue
            except:
                self.wid['state']="normal"
                self.wid.insert("end",self.time()+" ",'time')
                self.wid.insert("end"," Client ","sys")
                self.wid.insert("end"," - Connection reset!")
                self.wid.see("end")
                self.wid['state']="disabled"
                client = None
                return
            if not msg:
                continue
            if msg.startswith("!"):
                cmd = msg[1:].split(" ")[0]
                if cmd == "ONLINE":
                    members = msg[1:].split(" ")[1:]
                    self.notify("ONLINE MEMBERS: "+str(members[:-1]))
                continue
            msg += "\n\n"
            user = " "+msg.split(' - ')[0]+" "
            text = ' - '+(' - '.join(msg.split(" - ")[1:]))
            self.wid['state']="normal"
            self.wid.insert("end",self.time()+" ",'time')
            self.wid.insert("end",user,self.get_tag(user))
            self.wid.insert("end",text)
            self.wid.see("end")
            self.wid['state']="disabled"

    def notify(self,text):
        self.wid['state']="normal"
        self.wid.insert("end",self.time()+" ",'time')
        self.wid.insert("end"," Client ","sys")
        self.wid.insert("end", " - "+text+"\n\n")
        self.wid.see("end")
        self.wid['state']="disabled"

    def send(self,text,with_name=True):
        if self.last:
            if abs(self.last - time.time()) < 0.5:
                self.notify("Please wait!")
                return
        if not isinstance(text, bytes):
            if text.startswith("/"):
                if text.lower().strip() == "/online":
                    self.s.send(b"ONLINE")
                    return
            if with_name:
                self.s.send(f"{self.username} - {text}".encode())
            else:
                self.s.send(text.encode())
        else:
            try:
                if not with_name:
                    raise Exception
                text = f"{self.username} - ".encode()+text
            except:
                pass
            self.s.send(text)
        self.last = time.time()


root = tk.Tk()
root.title("tkChat")
if platform.system()=="Windows":
    root.geometry("600x350")
else:
    root.geometry("600x300")
root.resizable(False,False)

client=None

def connect():
    global client
    try:
        host = smp.askstring("Connect", "Enter host:")
        #port = smp.askinteger("Connect", "Enter port:")
        port = DEFAULT_PORT
        name = smp.askstring("Connect", "Enter Username:").replace(" ","_")
        if len(name) == 0:
            name = "anon"+str(random.randint(100,999))
        if len(name)>20:
            name=name[0:20]
        if name.startswith("@"):
            name = name.replace("@","*")
        if name.startswith("!"):
            name = name.replace("!","*")
        client = Client(host, port, name, chat)
        client.create_connection()
        connb['state'] = 'disabled'
        userl['text'] = name
    except:
        client=None
        msb.showwarning("Connect","Can't connect to the chat!\nTry again later.")

def send():
    if client:
        msg = message.get()
        if len(msg)>1024:
            msg=msg[0:1024]
        if not msg.isspace() and msg != "":
            client.send(msg)
    message.delete(0,"end")

images = []

def send_attach(tp):
    if not client:
        return
    if tp == "photo":
        file = fd.askopenfilename(filetypes=[("PNG",".png"),("JPEG",".jpeg"),("JPG",".jpg")])
        if not file:
            return
        img = Image.open(file)
        img.thumbnail((300,300))
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        client.send(bio.getvalue())

def leave():
    if client:
        client.send('LEAVE',False)
    root.destroy()
    quit()

root.wm_protocol("WM_DELETE_WINDOW",leave)

connb = tk.Button(root,text="Connect",command=connect)
connb.pack()

chatframe = tk.Frame(root,width=200,height=200,bg="white",highlightthickness=1,highlightbackground="lightgrey")
chatframe.pack()
chat = ScrolledText(chatframe,state="disabled",height=18)
chat.pack(fill="x")

chat.tag_configure("sys",background="red",foreground="#ffffff")
chat.tag_configure("oth",background="blue",foreground="#ffffff")
chat.tag_configure("you",background="green",foreground="#ffffff")
chat.tag_configure("time",foreground="#A9A9A9")

msgf = tk.Frame(root,bg="white",highlightthickness=0,highlightbackground="lightgrey")
msgf.pack(fill="x")

userl = tk.Label(msgf,text="-")
userl.pack(side="left")
userl.bind("<Button-1>",lambda ev:[root.clipboard_clear(),root.clipboard_append(userl['text'])])

message = tk.Entry(msgf,width=30)
message.pack(side="left")
message.bind("<Return>",lambda ev:send())

popup = tk.Menu(root, tearoff=0)
popup.add_command(label="Photo",command=lambda:send_attach("photo"))

snd = tk.Button(msgf,text="Send",font="sans-serif 20 bold",height=1,command=send,fg="grey")
snd.pack(side="left")

sm = tk.Button(msgf,text=u"\u270B",font="sans-serif 30 bold",height=1,width=2,command=lambda:message.insert("end",u"\u270B"))
sm.pack(side="left")

def menu():
    popup.post(add.winfo_rootx(), add.winfo_rooty())

add = tk.Button(msgf,text="+",font="sans-serif 30 bold",height=1,width=2,command=menu)
add.pack(side="left")

root.mainloop()