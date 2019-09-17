from tkinter import Tk, Label, Button, StringVar, Text, Scrollbar, PhotoImage,Entry
from tkinter import Frame, filedialog, messagebox
import socket
import threading
import os

class Lapchat:
    def __init__(self, master):
        master.title("Lapchat")
        master.resizable(False, False)
        master.geometry("400x450")
        #master.iconbitmap("4.ico")
        master.configure(bg="#3D9970")

        #==============Initializing communication==============
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        self.port = 12345
        self.client = (self.host, self.port)

        self.top_frame = Frame(master, width=400, height=45, bg="#6666ff")
        self.top_frame.place(x=0, y=0)

        self.message_count = 1.5
        self.filename = None

        self.message_session = Text(master, bd=3, relief="flat", font=("consolas", 12, "italic"), undo=True, wrap="word")
        self.message_session.config(width=35, height=15,bg="#AAAAAA", fg="blue")
        self.overscroll = Scrollbar(master, command=self.message_session.yview)
        self.overscroll.config(width=20)
        self.message_session["yscrollcommand"] = self.overscroll.set

        self.message = Entry(bg="#ffffff", width=30, bd=5, relief="flat")
        self.message.bind("<Return>", self.send_msg)

        self.send_message = Button(master, text="send", fg="blue", width=10, height=1, relief="flat")
        self.send_message.configure(command=self.send_msg)

        self.attachment = Button(master, text="File", fg="red", width=5, height=1, relief="flat")
        self.attachment.configure(command=self.select_file)

        self.file_label = Label(master, fg="#008080", font=("verdana", 7), width=50 )

        self.message_session.place(x=40, y=50)
        self.overscroll.place(x=360, y=50)
        self.message.place(x=40, y = 345)
        self.send_message.place(x=240, y = 345)
        self.attachment.place(x=325, y=345)

    def get_filename(self, folder):
        self.temp_filename = folder.split("/")
        self.temp_filename = self.temp_filename[-1]
        return self.temp_filename


    def select_file(self, event=None):
        self.select_file = filedialog.askopenfilename()
        self.filename = self.select_file
        self.temp_filename = self.get_filename(self.select_file)
        self.file_label.config(text=self.temp_filename)
        self.file_label.place(x=40, y=380)

    def receive_sms_txt(self, receive_txt=None):
        print("Receiving sms again")
        print(self.received_message)
        if receive_txt:
            self.sm = receive_txt
        else:
            self.sm = self.received_message
            self.message.delete(0, "end")
        self.sm ="client:"+self.sm+"\n"
        self.message_session.insert(self.message_count, self.sm)
        self.message_count+=1.5
        self.received_message=None

    def receive_file(self, size, name):
        with open(name, "wb") as rec_file:
            print(size)
            print(name)
            while size>0:
                received_buffer = self.server.recv(1024)
                rec_file.write(received_buffer)
                size = size-len(received_buffer)
                print(size)

        print("File received successful")
        self.server.send(("ready_received").encode())
        self.received_message = None


    def try_sample1(self):
        self.receive_sms_thread= threading.Thread(target=self.receive_file, args=(self.received_size, self.received_name))
        self.receive_sms_thread.start()
        self.receive_sms_thread.join()


    def receive_sms(self):
        while True:
            try:
                self.server.connect(self.client)
                while True:
                    try:
                        print("receiving messages")
                        self.received_message = self.server.recv(1024).decode()
                        print(self.received_message)
                        if "&&&" in self.received_message:
                            self.received_message = self.received_message.split("&&&")
                            self.received_size = self.received_message[0]
                            self.received_name = self.received_message[1]
                            self.received_size = int(self.received_size)
                            self.receive_sms_txt(receive_txt="File Received")
                            self.try_sample1()

                        else:
                            if self.received_message:
                                self.receive_sms_txt()
                    except:
                        continue
            except:
                continue


    def send_sms_txt(self, file_message=None):
        if file_message:
            self.sms = file_message
        else:
            self.sms= self.message.get()
            self.server.send(self.sms.encode())
            self.message.delete(0, "end")

        self.sms = "you:"+self.sms+"\n"
        self.message_session.insert(self.message_count, self.sms)
        self.message_count+=1.5
        print("Message sent succeful")

    def send_file(self, size):
        print(size)
        with open(self.filename, "rb") as file:
            size = int(size)
            while size>0:
                buffer = file.read()
                self.server.send(buffer)
                buffer_size = len(buffer)
                break
        print("File successful sent")



    def receive_sms_txt(self, receive_txt=None):
        print("Receiving sms again")
        print(self.received_message)
        if receive_txt:
            self.sm = receive_txt
        else:
            self.sm = self.received_message
            self.message.delete(0, "end")
        self.sm ="client:"+self.sm+"\n"
        self.message_session.insert(self.message_count, self.sm)
        self.message_count+=1.5
        self.received_message=None


    def try_sample(self):
        sendfile_thread = threading.Thread(target=self.send_file, args=(self.filesize,))
        sendfile_thread.start()
        sendfile_thread.join()
        self.filename = None
        self.file_label.place_forget()
        print("Thread stopped")


    def send_msg(self, event=None):
        try:
            if self.filename:
                self.ask_send = messagebox.askyesno("Confirm", "Do want to send message with file")
                print(self.ask_send)
                if self.ask_send:
                    self.file_name = self.get_filename(self.filename)
                    self.filesize = str(os.stat(self.filename).st_size)
                    print("file size is : {}".format(self.filesize))
                    self.embedded_filename = self.filesize+"&&&"+self.file_name
                    self.send_sms_txt()
                    self.send_sms_txt(file_message="File has been sent")
                    self.server.send(self.embedded_filename.encode())
                    self.try_sample()
                else:
                    self.filename = None
                    self.file_label.place_forget()
                    self.send_sms_txt()

            else:
                self.send_sms_txt()

        except:
            self.show_error =messagebox.showerror("No connection", "Time out , no connection found")



root = Tk()
app = Lapchat(root)
receive_thread = threading.Thread(target=app.receive_sms)
receive_thread.start()
root.mainloop()
