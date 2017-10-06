import tkinter as tk

def write_to_textwidget(tw, text):
    # Update the widget with the data we are going to send
    tw.config(state='normal')
    tw.insert(tk.END, text)
    tw.config(state='disabled')
    tw.see(tk.END)
    tw.update()
