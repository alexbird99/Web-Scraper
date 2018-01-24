from tkinter import Tk, Label, Button, Text
import matplotlib.pyplot as plt
#set variable QT_PLUGIN_PATH  C:\Users\Alex\Anaconda3\Library\plugins

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        # self.label = Label(master, text="This is our first GUI!", width="30", height="5")
        # self.label.pack()

        self.text = Text(master, cnf={}, width="30", height="1")
        self.text.pack()

        self.submit_button = Button(master, text="Submit", command=self.submit)
        self.submit_button.pack()

        # self.close_button = Button(master, text="Close", command=master.quit)
        # self.close_button.pack()

    def submit(self):
        stockNo = self.text.get("1.0",'end-1c')
        #self.text.
        print(stockNo)    
        plt.title(stockNo)
        #plt.savefig(str(stockNo)+'.png')
        plt.show()
        

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()