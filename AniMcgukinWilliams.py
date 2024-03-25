# CMSC-3380-001 Note-Taker Project
# Ibrahim Al Ani, Joshua McGukin, Matthew Williams
# ala17357@pennwest.edu, mcg1027@pennwest.edu, wil1041@pennwest.edu

# Program imports
import tkinter as tk
from tkinter import ttk, Listbox, Scrollbar
from tkinter import filedialog
from spellchecker import SpellChecker
import pickle
import pyaudio
import wave

# Font for landing page title
LARGEFONT =("Verdana", 25)

# Code from article was referenced and modified as a starting 
# point for implementing basic screen navigation: 
# https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/
class noteTaker(tk.Tk):
    # Initialization Function
    # Description: Initializes the noteTaker class and creates a container for the frames.
    # Preconditions: None
    # Postconditions: None
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
         
        # Create a container
        container = tk.Frame(self)  
        container.pack(side = "top", fill = "both", expand = True) 
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        # Initialize frames to an empty array
        self.frames = {}  

        # Iterate through a tuple consiting of the classes of the pages
        for F in (LandingPage, TypedNotePage):
            frame = F(container, self)
            # Store the frame in the frames array
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")

        self.show_frame(LandingPage)
    
    # Show Frame Function
    # Source: https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/
    # Description: To display the current frame passed as a parameter.
    # Preconditions: The controller must be passed as a parameter.
    # Postconditions: The frame is displayed.
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class LandingPage(tk.Frame):
    # Initialization Function for LandingPage
    # Description: Initializes the LandingPage class
    # Preconditions: The parent and controller must be passed as parameters.
    # Postconditions: The LandingPage frame is displayed.
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Set size of window
        # Source: https://tkdocs.com/shipman/toplevel.html
        controller.geometry("350x300")

        # Set the minimum size of the window
        # Source: https://tkdocs.com/shipman/toplevel.html
        controller.minsize(350, 200)

        # Change the title of the window
        # Source: https://tkdocs.com/shipman/toplevel.html
        controller.title("Note-Taker App")

        # Label of frame layout
        label = ttk.Label(self, text="Note-Taker", font=LARGEFONT)
        label.grid(row=0, column=0, padx=10, pady=10)

        # Frame for buttons
        # Source: https://tkdocs.com/tutorial/widgets.html
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, padx=10, pady=10)

        # Button texts and commands placed in a list
        buttons = [
            ("New Typed Note", lambda: self.new_typed_note_navigate(controller)),
            ("New Drawn Note", None),
            ("Load Note", None)
        ]

        # Create and place buttons into the button frame using a loop
        # Retrieve enumerable objects from buttons list (access text and command tuple)
        # More on enumerated types: https://realpython.com/python-enumerate/
        for i, (text, command) in enumerate(buttons):
            button = ttk.Button(button_frame, text=text, command=command)
            button.pack(padx=10, pady=5)

        # Create a listbox and scrollbar for recently opened notes
        # Source: https://tkdocs.com/tutorial/morewidgets.html
        scrollbar = Scrollbar(self)
        scrollbar.grid(row=0, column=1, rowspan=4, sticky='ns')
        listbox = Listbox(self, yscrollcommand=scrollbar.set)
        listbox.grid(row=0, column=2, rowspan=4, sticky='nsew')
        scrollbar.config(command=listbox.yview)

        # Configure the rows and columns to expand proportionally when the window is resized
        # Source: https://tkdocs.com/shipman/root-resize.html
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
    
    # New Note Navigate Function
    # Description: Changes the window title and switches to the TypedNotePage frame.
    # Preconditions: The controller must be passed as a parameter.
    # Postconditions: The TypedNotePage frame is displayed.
    def new_typed_note_navigate(self, controller):
        controller.title("untitled - Note-Taker App")
        controller.show_frame(TypedNotePage)

class TypedNotePage(tk.Frame):
    # Initialization Function
    # Description: Initializes the TypedNotePage class
    # Preconditions: The parent and controller must be passed as parameters.
    # Postconditions: 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create text area to type notes
        text_area = tk.Text(self)
        text_area.pack(expand=True, fill='both')

# Driver Code
app = noteTaker()
app.mainloop()