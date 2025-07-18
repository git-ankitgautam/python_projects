import tkinter as tk

def click(event):
    text = event.widget.cget("text")
    if text == "=":
        try:
            screen.set(str(eval(screen.get())))
        except Exception:
            screen.set("Error")
    elif text == "C":
        screen.set("")
    elif text == "DEL":
        current = screen.get()
        screen.set(current[:-1])
    else:
        screen.set(screen.get() + text)

root = tk.Tk()
root.title("Simple Calculator")
root.geometry("300x400")
root.resizable(False, False)

screen = tk.StringVar()
entry = tk.Entry(root, textvar=screen, font=("Arial", 20), bd=10, relief=tk.RIDGE, justify="right")
entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

# make rows/columns expand evenly
for i in range(1, 6):
    root.grid_rowconfigure(i, weight=1)
for j in range(4):
    root.grid_columnconfigure(j, weight=1)

# Button definitions: (text, row, col, colspan)
buttons = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("C", 4, 0), ("DEL", 4, 1), ("0", 4, 2), ("+", 4, 3),
    ("=", 5, 0, 4)
]

for btn in buttons:
    text = btn[0]
    row = btn[1]
    col = btn[2]
    colspan = btn[3] if len(btn) == 4 else 1

    b = tk.Button(root, text=text, font=("Arial", 18), relief=tk.GROOVE)
    b.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)
    b.bind("<Button-1>", click)

root.mainloop()
