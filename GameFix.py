import tkinter as tk
import AutoHP
import keyboard
import time
import threading


        

def scriptStart():
     global scriptOn
     scriptOn.set(True)
     scriptOnMessage.set("Script is ON")
     root.update()
     scriptController()


def scriptStop():
     global scriptOn
     scriptOn.set(False)
     scriptOnMessage.set("Script is OFF")
     root.update()

     
def scriptController():
    global scriptOn
    if scriptOn.get():
        print("looping")
        AutoHP.main()
    root.after(500, scriptController)


def toggle():
    global scriptOn
    if not scriptOn.get():
        print("Toggle on")
        scriptStart()
    else:
        print("Toggle off")
        scriptStop()


root = tk.Tk()
root.geometry("500x300")
root.title("MapleLegends Fix")
scriptOn = tk.BooleanVar()
scriptOnMessage = tk.StringVar()
scriptOn.set(False)
scriptOnMessage.set("Script is OFF")
runLabel = tk.Label( root, textvariable =  scriptOnMessage, font = ("Arial", 12))
runLabel.pack(pady=10)
onButton = tk.Button( root, text = "Start Script", font = ("Arial", 12), command = scriptStart)
offButton = tk.Button( root, text = "Stop Script", font = ("Arial", 12), command = scriptStop)
onButton.pack()
offButton.pack()
keyboard.add_hotkey('F10', toggle)

#function = threading.Thread(target = scriptController)
#function.start()
scriptController()
root.mainloop()


    



