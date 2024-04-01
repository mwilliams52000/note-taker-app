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
        for F in (LandingPage, TypedNotePage, DrawnNotePage):
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
        self.controller = controller
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
            ("New Drawn Note", lambda: self.new_drawn_note_navigate(controller)),
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
    
    # New Typed Note Navigate Function
    # Description: Changes the window title and switches to the TypedNotePage frame.
    # Preconditions: The controller must be passed as a parameter.
    # Postconditions: The TypedNotePage frame is displayed.
    def new_typed_note_navigate(self, controller):
        controller.title("untitled - Note-Taker App")
        controller.show_frame(TypedNotePage)
        menu_bar = self.buildTypedNoteMenu()
        # Configure the typed note page to use the menu bar
        controller.config(menu=menu_bar)
    
    # New Drawn Note Navigate Function
    # Description:
    # Preconditions:
    # Postconditions
    def new_drawn_note_navigate(self, controller):
        controller.title("untitled - Note-Taker App")
        controller.show_frame(DrawnNotePage)
        menu_bar = self.buildDrawnNoteMenu()
        # Configure the typed note page to use the menu bar
        controller.config(menu=menu_bar)
    
    # Build Typed Note Menu Function
    # Description:
    # Preconditions:
    # Postconditions:
    def buildTypedNoteMenu(self):
        # Create a menu bar
        menu_bar = tk.Menu(self)

        # Create file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="Underline Text", command=self.controller.frames[TypedNotePage].underline_text)
        edit_menu.add_command(label="Remove Underline", command=self.controller.frames[TypedNotePage].remove_underline_text)
        edit_menu.add_command(label="Add Bullet Point", command=self.controller.frames[TypedNotePage].add_bullet_point)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Create color menu
        color_menu = tk.Menu(menu_bar, tearoff=0)
        color_menu.add_command(label="Default")
        color_menu.add_command(label="Red")
        color_menu.add_command(label="Blue")
        color_menu.add_command(label="Green")
        color_menu.add_command(label="Yellow")
        color_menu.add_command(label="Purple")
        color_menu.add_command(label="White")
        menu_bar.add_cascade(label="Color", menu=color_menu)

        # Create transcribe speech menu
        transcribe_menu = tk.Menu(menu_bar, tearoff=0)
        transcribe_menu.add_command(label="Start Transcription")
        menu_bar.add_cascade(label="Transcribe Speech", menu=transcribe_menu)

        return menu_bar
    
    # Build Drawn Note Menu Function
    # Description:
    # Preconditions:
    # Postconditions:
    def buildDrawnNoteMenu(self):
        # Create a menu bar
        menu_bar = tk.Menu(self)

        # Create file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create color menu
        color_menu = tk.Menu(menu_bar, tearoff=0)
        color_menu.add_command(label="Default")
        color_menu.add_command(label="Red")
        color_menu.add_command(label="Blue")
        color_menu.add_command(label="Green")
        color_menu.add_command(label="Yellow")
        color_menu.add_command(label="Purple")
        color_menu.add_command(label="White")

        menu_bar.add_cascade(label="Color", menu=color_menu)

        return menu_bar

class TypedNotePage(tk.Frame):
    # Initialization Function
    # Description: Initializes the TypedNotePage class
    # Preconditions: The parent and controller must be passed as parameters.
    # Postconditions: 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Create text area to type notes
        self.text_area = tk.Text(self)
        self.text_area.pack(expand=True, fill='both')

        # Bind keyboard actions to buttons
        # Sources: https://tkdocs.com/tutorial/text.html
        # https://www.geeksforgeeks.org/python-binding-function-in-tkinter/

        # When the user releases the enter key or return key, check if the previous line is bulleted
        # If it is, bullet this current line as well
        self.text_area.bind("<KeyRelease-Return>", lambda event: self.is_prev_line_bulleted())

        # When the user types into the keybaord, check if the previous character is underlined
        # If it is, underline this current character as well
        self.text_area.bind("<Key>", lambda event: self.is_prev_char_underlined())
    
    # Underline Text Function
    # Description: Underlines the selected text in the text area.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The selected text is underlined.
    def underline_text(self):
        # Get the current selection
        current_selection = self.text_area.tag_ranges(tk.SEL)
        # If there is a selection, underline the text
        if current_selection:
            # Give this selection the "underline" tag so it is recognized as underlined
            # This tag will prove useful for saving and reloading notes
            # and is used to determine if the text following should be underlined
            # Source: https://tkdocs.com/tutorial/text.html#tags
            self.text_area.tag_add("underline", current_selection[0], current_selection[1])
            self.text_area.tag_configure("underline", underline=True)
    
    # Remove Underline Text Function
    # Description: Removes the underline from the selected text in the text area.
    # Preconditions:
    # Postconditions: The underline is removed from the selected text.
    def remove_underline_text(self):
        # Get the current selection
        current_selection = self.text_area.tag_ranges(tk.SEL)
        # If there is a selection, underline the text
        if current_selection:
            self.text_area.tag_remove("underline", current_selection[0], current_selection[1])
            self.text_area.tag_configure("", underline=False)
    
    # Add Bullet Point Function
    # Description: Adds a bullet point at the start of the current line.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: A bullet point is added at the start of the current line.
    def add_bullet_point(self):
        # Get the current index of the typing cursor within the text_area
        current_index = self.text_area.index(tk.INSERT)
        # Get the start index of the current line of the text_area
        line_start_index = "{}.0".format(current_index.split('.')[0])
        # Insert bullet point at the start of the line
        # \u2022 is the unicode escape for a bullet point character
        # Source: https://www.ascii-code.com/character/%E2%80%A2
        self.text_area.insert(line_start_index, u'\u2022' + ' ')
    
    # Is Previous Line Bulleted Function
    # Description: Checks if the previous line is bulleted. If it is, bullet the current line.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The current line is bulleted if the previous line is bulleted.
    def is_prev_line_bulleted(self):
        # Get the current index of the typing cursor
        current_index = self.text_area.index(tk.INSERT)
        # Get the start index of the current line
        line_start_index = "{}.0".format(current_index.split('.')[0])
        # If the line start index is not 1.0, then this current line is not the first line
        if not(line_start_index == "1.0"):
            # Get the previous line index
            prev_line_index = "{}.0".format(int(current_index.split('.')[0]) - 1)
            # Check if the first character of the previous line is a bullet point
            if self.text_area.get(prev_line_index, f"{prev_line_index} + 1 char") == u'\u2022':
                # If it is, bullet this current line as well
                self.add_bullet_point()
    
    # Is Previous Character Underlined
    # Description: Checks if the previous character is underlined. If it is, underline the current character.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The current character is underlined if the previous character is underlined.
    def is_prev_char_underlined(self):
        # Get the current index of the typing cursor
        current_index = self.text_area.index(tk.INSERT)
        # Get the index of the previous character
        prev_char_index = "{}.{}".format(current_index.split('.')[0], int(current_index.split('.')[1]) - 1)

        # Check if the previous character has the "underline" tag
        if "underline" in self.text_area.tag_names(prev_char_index):
            # If it is, underline the current character as well
            self.text_area.tag_add("underline", current_index)
            self.text_area.tag_configure("underline", underline=True)
        
class DrawnNotePage(tk.Frame):
    # Initialization Function
    # Description: Initializes the DrawnNotePage class
    # Preconditions: None
    # Postconditions: None
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Create canvas area to draw notes
        self.canvas = tk.Canvas(self)
        self.canvas.pack(expand=True, fill='both')

        # Bind mouse dragging event to canvas
        self.canvas.bind("<Button-1>", self.save_posn)
        self.canvas.bind("<B1-Motion>", self.add_line)

        self.lastx, self.lasty = None, None

    # Save Position Function
    # Description:
    # Preconditions:
    # Postconditions:
    def save_posn(self, event):
        self.lastx, self.lasty = event.x, event.y

    # Add Line Function
    # Description:
    # Preconditions:
    # Postconditions:
    def add_line(self, event):
        if self.lastx and self.lasty:
            self.canvas.create_line(self.lastx, self.lasty, event.x, event.y)
        self.save_posn(event)


# Driver Code
app = noteTaker()
app.mainloop()