# CMSC-3380-001 Note-Taker Project
# Ibrahim Al Ani, Joshua McGukin, Matthew Williams
# ala17357@pennwest.edu, mcg1027@pennwest.edu, wil1041@pennwest.edu

# Program imports
import tkinter as tk
from tkinter import ttk, Listbox, Scrollbar
from tkinter import filedialog
from tkinter import messagebox
from spellchecker import SpellChecker
import threading
import pickle
import pyaudio
import os
import wave
import pyautogui
from tkinter import ttk, Listbox, Scrollbar, Menu
import speech_recognition as sr
from tkinter import ttk, Menu, font
import tkinter.font as tkFont

# Font for landing page title
LARGEFONT =("Verdana", 25)

# Code from article was referenced and modified as a starting 
# point for implementing basic screen navigation: 
# https://www.geeksforgeeks.org/tkinter-application-to-switch-between-different-page-frames/
class noteTaker(tk.Tk):
    # Initialization Function
    # Description: Initializes the noteTaker class and creates a container for the frames.
    # Preconditions: Self and arguments must be passed as parameters.
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

        # Get a list of all the notes in the current directory
        notes_list = self.get_drawn_and_typed_notes_list()

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
            ("Load Note", lambda: self.load_note_navigate(controller))
        ]

        # Create and place buttons into the button frame using a loop
        # Retrieve enumerable objects from buttons list (access text and command tuple)
        # More on enumerated types: https://realpython.com/python-enumerate/
        for i, (text, command) in enumerate(buttons):
            button = ttk.Button(button_frame, text=text, command=command)
            button.pack(padx=10, pady=5)

        # Create a listbox and scrollbar for notes in directory
        # Bind to an "on_select" function to handle selection of notes
        # Source: https://tkdocs.com/tutorial/morewidgets.html
        scrollbar = Scrollbar(self)
        scrollbar.grid(row=0, column=1, rowspan=4, sticky='ns')
        listbox = Listbox(self, yscrollcommand=scrollbar.set)
        # Insert each note into the listbox
        for note in notes_list:
            listbox.insert(tk.END, note)
        listbox.grid(row=0, column=2, rowspan=4, sticky='nsew')
        scrollbar.config(command=listbox.yview)
        listbox.bind('<<ListboxSelect>>', self.on_select)

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
    # Description: Changes the window title and switches to the DrawnNotePage frame.
    # Preconditions: The controller must be passed as a parameter.
    # Postconditions The DrawnNotePage frame is displayed.
    def new_drawn_note_navigate(self, controller):
        controller.title("untitled - Note-Taker App")
        controller.show_frame(DrawnNotePage)
        menu_bar = self.buildDrawnNoteMenu()
        # Configure the typed note page to use the menu bar
        controller.config(menu=menu_bar)
    
    # Load Note Navigate Function
    # Description: Opens a file dialog to select a file path. Then, loads the note based on the file path.
    # Preconditions: The controller must be passed as a parameter.
    # Postconditions: The note is loaded depending on the file path.
    def load_note_navigate(self, controller):
        file_path = self.get_file_path()
        # Determine if file extension is .typ, .dra, or something else
        if file_path.endswith(".typ"):
            # Get name of file path without the directory path or extension
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Set the window title to the file name
            controller.title(file_name + " - Note-Taker App")
            # Change frame
            controller.show_frame(TypedNotePage)
            menu_bar = self.buildTypedNoteMenu()
            # Configure the typed note page to use the menu bar
            controller.config(menu=menu_bar)
            # Open the pickle file and update text area
            controller.frames[TypedNotePage].open_pickle_file(file_path)
            # Show a success message
            tk.messagebox.showinfo("Success", "Typed note successfully opened!")
        elif file_path.endswith(".dra"):
            # Get name of file path without the directory path or extension
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Set the window title to the file name
            controller.title(file_name + " - Note-Taker App")
            controller.show_frame(DrawnNotePage)
            menu_bar = self.buildDrawnNoteMenu()
            # Configure the typed note page to use the menu bar
            controller.config(menu=menu_bar)
            # Open the pickle file and update canvas
            controller.frames[DrawnNotePage].open_pickle_file_drawn(file_path)
        elif file_path == "":
            # Show an error message the user did not open anything
            tk.messagebox.showerror("Error", f"No file selected!")
        else:
            # Show an error message if there's any issue with opening
            tk.messagebox.showerror("Error", f"Not a valid file type: {file_path}")

    # Get File Path Function
    # Description: Opens a file dialog to select a file path.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The file path is returned.
    def get_file_path(self):
        file_path = filedialog.askopenfilename(defaultextension=".typ", filetypes=[("Typed Note Files", "*.typ"), ("Drawn Note Files", "*.dra")], title="Load File")
        # If a file path is selected
        if file_path:
            try:
                return file_path
            except Exception as e:
                # Show an error message if there's any issue with opening
                tk.messagebox.showerror("Error", f"An error occurred while opening the note: {e}")
        return file_path

    # Get Drawn and Typed Notes List Function
    # Description: Returns a list of the drawn and typed notes within the local directory and notes folder.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The list of notes is returned.
    def get_drawn_and_typed_notes_list(self):
        # If there is not a folder called "notes" in the current directory, create one
        if not os.path.exists("notes"):
            os.mkdir("notes")
        # Get all files in the current directory
        files = os.listdir()
        # Initialize lists for typed and drawn notes
        notes_list = []
        # Iterate through all files in the directory
        for file in files:
            # If the file is a typed or drawn note, add to the typed notes list
            if (file.endswith(".typ") or file.endswith(".dra")):
                notes_list.append(file)
        # Ensure that the folder called "notes" is in the current directory
        if os.path.exists("notes"):
            # Get all files in the "notes" directory
            notes_files = os.listdir("notes")
            # Iterate through all files in the "notes" directory
            for file in notes_files:
                # If the file is a typed or drawn note, add to the typed notes list
                if (file.endswith(".typ") or file.endswith(".dra")):
                    notes_list.append("notes/" + file)
        return notes_list

    # Note Listbox Function
    # Description: Gets the selection an entry in listbox and opens it.
    # Preconditions: Self , controller, and file_path must be passed as a parameter.
    # Postconditions: The selected note is opened and loaded.
    def note_listbox(self, controller, file_path):
        # Determine if file extension is .typ, .dra, or something else
        if file_path.endswith(".typ"):
            # Get name of file path without the directory path or extension
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Set the window title to the file name
            controller.title(file_name + " - Note-Taker App")
            # Change frame
            controller.show_frame(TypedNotePage)
            menu_bar = self.buildTypedNoteMenu()
            # Configure the typed note page to use the menu bar
            controller.config(menu=menu_bar)
            # Open the pickle file and update text area
            controller.frames[TypedNotePage].open_pickle_file(file_path)
            # Show a success message
            tk.messagebox.showinfo("Success", "Typed note successfully opened!")
        elif file_path.endswith(".dra"):
            # Get name of file path without the directory path or extension
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Set the window title to the file name
            controller.title(file_name + " - Note-Taker App")
            # Change frame
            controller.show_frame(DrawnNotePage)
            menu_bar = self.buildDrawnNoteMenu()
            # Configure the typed note page to use the menu bar
            controller.config(menu=menu_bar)
            # Open the pickle file and update canvas
            controller.frames[DrawnNotePage].open_pickle_file_drawn(file_path)
        else:
            # Show an error message if there's any issue with opening
            tk.messagebox.showerror("Error", f"Not a valid file type: {file_path}")
    
    # On Select Function
    # Description: Controls the selection of entries in listbox.
    # Preconditions: Self and the selection event must be passed as a parameter.
    # Postconditions: The selected note is loaded.
    def on_select(self, event):
        try:
            # Use event.widget to refer to the listbox selection
            selected_note = event.widget.get(event.widget.curselection())
            # Get the controller from class
            controller = self.controller
            # Load the selected note from the listbox
            self.note_listbox(controller, selected_note)
        except:
            return
            
    # Build Typed Note Menu Function
    # Description:
    # Preconditions:
    # Postconditions:
    def buildTypedNoteMenu(self):
        # Create a menu bar
        menu_bar = tk.Menu(self)

        # Create file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command = lambda: self.controller.frames[TypedNotePage].load_note_driver())
        file_menu.add_command(label="Save", command = lambda: self.controller.frames[TypedNotePage].save_note_driver())
        file_menu.add_command(label="Export", command=self.controller.frames[TypedNotePage].export_typed_note)
        file_menu.add_separator()
    
        # Source: https://www.geeksforgeeks.org/how-to-close-a-window-in-tkinter/
        file_menu.add_command(label="Exit", command = lambda: self.controller.destroy())
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.controller.frames[TypedNotePage].typed_note_undo)
        edit_menu.add_command(label="Redo", command=self.controller.frames[TypedNotePage].typed_note_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Underline Text", command=self.controller.frames[TypedNotePage].underline_text)
        edit_menu.add_command(label="Remove Underline", command=self.controller.frames[TypedNotePage].remove_underline_text)
        edit_menu.add_command(label="Add Bullet Point", command=self.controller.frames[TypedNotePage].add_bullet_point)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.controller.frames[TypedNotePage].typed_note_cut)
        edit_menu.add_command(label="Copy", command=self.controller.frames[TypedNotePage].typed_note_copy)
        edit_menu.add_command(label="Paste", command=self.controller.frames[TypedNotePage].typed_note_paste)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Create color menu
        color_menu = tk.Menu(menu_bar, tearoff=0)
        color_menu.add_command(label="Default", command=lambda: self.controller.frames[TypedNotePage].change_color("black"))
        color_menu.add_command(label="Red", command=lambda: self.controller.frames[TypedNotePage].change_color("red"))
        color_menu.add_command(label="Blue", command=lambda: self.controller.frames[TypedNotePage].change_color("blue"))
        color_menu.add_command(label="Green", command=lambda: self.controller.frames[TypedNotePage].change_color("green"))
        color_menu.add_command(label="Yellow", command=lambda: self.controller.frames[TypedNotePage].change_color("yellow"))
        color_menu.add_command(label="Purple", command=lambda: self.controller.frames[TypedNotePage].change_color("purple"))
        color_menu.add_command(label="Pink", command=lambda: self.controller.frames[TypedNotePage].change_color("pink"))
        menu_bar.add_cascade(label="Color", menu=color_menu)

        # Create font menu
        font_menu = tk.Menu(menu_bar, tearoff=0)

        # Create a submenu with font options
        font_submenu = tk.Menu(font_menu, tearoff=0)
        
        # Get all available fonts
        available_fonts = list(tkFont.families())

        # Add each font as an option in the submenu
        for font in available_fonts:
            font_submenu.add_command(label=font, command=lambda f=font: self.controller.frames[TypedNotePage].change_font(f))

        # Add the submenu to the font menu
        font_menu.add_cascade(label="Change Font", menu=font_submenu)

        # Add the font menu to the menu bar
        menu_bar.add_cascade(label="Font", menu=font_menu)

        # Create transcribe speech menu
        transcribe_menu = tk.Menu(menu_bar, tearoff=0)
        transcribe_menu.add_command(label="Start Transcription", command=self.controller.frames[TypedNotePage].create_audio_window)
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
        file_menu.add_command(label="Open", command=self.controller.frames[DrawnNotePage].load_drawn_note_driver)
        file_menu.add_command(label="Save", command=self.controller.frames[DrawnNotePage].save_drawn_note_driver)
        file_menu.add_command(label="Export", command=self.controller.frames[DrawnNotePage].export_drawn_note)
        file_menu.add_separator()

        # Source: https://www.geeksforgeeks.org/how-to-close-a-window-in-tkinter/
        file_menu.add_command(label="Exit", command = lambda: self.controller.destroy())
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create color menu
        color_menu = tk.Menu(menu_bar, tearoff=0)
        color_menu.add_command(label="Default", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("black"))
        color_menu.add_command(label="Red", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("red"))
        color_menu.add_command(label="Blue", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("blue"))
        color_menu.add_command(label="Green", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("green"))
        color_menu.add_command(label="Yellow", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("yellow"))
        color_menu.add_command(label="Purple", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("purple"))
        color_menu.add_command(label="Pink", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("pink"))
        color_menu.add_command(label="Eraser", command=lambda: self.controller.frames[DrawnNotePage].set_line_color("white"))

        menu_bar.add_cascade(label="Color", menu=color_menu)

        return menu_bar
    
class TypedNotePage(tk.Frame):
    # Initialization Function
    # Description: Initializes the TypedNotePage class
    # Preconditions: The parent and controller must be passed as parameters.
    # Postconditions: 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.windowNum = 0
        self.controller = controller

        # Create word lists for TypedNotePage class
        self.wordsList = []

        # Create text area to type notes
        self.text_area = tk.Text(self, undo=True)
        self.text_area.pack(expand=True, fill='both')

        # Bind keyboard actions to buttons
        # Sources: https://tkdocs.com/tutorial/text.html
        # https://www.geeksforgeeks.org/python-binding-function-in-tkinter/

        # When the user types into the keybaord, check if the previous character is underlined
        # If it is, underline this current character as well
        self.text_area.bind("<Key>", lambda event: self.key_control())

        # When the user types into the keyboard, manage the strings in the text area
        self.text_area.bind("<KeyRelease>", lambda event: self.manage_text_area_strings())
        self.text_area.bind("<Button-1>", lambda event: self.button1_control())

        # When the user types enter, check if the previous line is bulleted and identify misspelled words
        self.text_area.bind("<KeyRelease-Return>", lambda event: self.key_release_return_control())

        # When the user taps left or right key, add visible spelling errors
        self.text_area.bind("<Left>", lambda event: self.identify_misspelled_words())
        self.text_area.bind("<Right>", lambda event: self.identify_misspelled_words())

        # When the user types space or enter, add visible spelling errors
        self.text_area.bind("<space>", lambda event: self.space_control())

    # Key Release Return Control Function
    # Description: Checks if the previous line is bulleted and identifies misspelled words by calling related functions.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The current line is bulleted if needed and misspelled words are identified.
    def key_release_return_control(self):
        self.is_prev_line_bulleted()
        self.identify_misspelled_words()
        self.is_prev_char_font()
    
    # Button 1 Control Function
    # Description: Manages the text area strings and identifies misspelled words by calling related functions.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The text area strings are managed and misspelled words are identified.
    def button1_control(self):
        self.manage_text_area_strings()
        self.identify_misspelled_words()
    
    # Space Control Function
    # Description: Identifies misspelled words and checks if the previous character is underlined or colored 
    # by calling related functions.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: Misspelled words are identified and the current character is underlined or colored if needed.
    def space_control(self):
        self.identify_misspelled_words()
        self.is_prev_char_underlined()
        self.is_prev_char_colored()
        self.is_prev_char_font()
    
    # Key Control Function
    # Description: Checks if the previous character is underlined or colored by calling related functions.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The current character is underlined or colored if needed.
    def key_control(self):
        self.is_prev_char_underlined()
        self.is_prev_char_colored()
        self.is_prev_char_font()

    # Change Font Function
    # Description: Changes the font of the TypedNotePage.
    # Preconditions: Self and the font must be passed as parameters.
    # Postconditions: The font of the TypedNotePage is changed.
    def change_font(self, font):
        # Get the current selection
        current_selection = self.text_area.tag_ranges(tk.SEL)
        # If there is a selection, change the font
        if current_selection:
            self.text_area.tag_add(font, current_selection[0], current_selection[1])
            self.text_area.tag_configure(font, font=(font, 12))
        else:
            # No selection, so change the font of the whole text area
            self.text_area.configure(font=(font, 12))

    # Is Previous Character Font Function
    # Description: Checks if the previous character is a font. If it is, change the current character to that font.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The current character is changed to the font of the previous character.
    def is_prev_char_font(self):
        # Get the current index of the typing cursor
        current_index = self.text_area.index(tk.INSERT)
        # Get the index of the previous character
        prev_char_index = "{}.{}".format(current_index.split('.')[0], int(current_index.split('.')[1]) - 1)
        # Get the tags of the previous character
        prev_char_tags = self.text_area.tag_names(prev_char_index)
        # Check if the previous character has any tags
        if prev_char_tags:
            # If it does, get the font of the first tag
            prev_char_font = self.text_area.tag_cget(prev_char_tags[0], "font")
            # Apply the same font to the current character
            self.text_area.tag_add(prev_char_tags[0], current_index)
            self.text_area.tag_configure(prev_char_tags[0], font=prev_char_font)

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
    
    # Change Color Function
    # Description: This function changes the color of the highlighted text to the new passed in one.
    # Preconditions: Self and the color string must be passed as parameters.
    # Postconditions: The color of the text is changed.
    def change_color(self, color):
        # Get the current selection
        current_selection = self.text_area.tag_ranges(tk.SEL)
    
        # List of supported colors
        colors = ["red", "blue", "green", "yellow", "purple", "pink", "black"]
    
        # For every color in the list of colors, remove the tag if it is present
        for col in colors:
            if current_selection:
                if col in self.text_area.tag_names(current_selection[0]):
                    self.text_area.tag_remove(col, current_selection[0], current_selection[1])
    
        # If there is a selection, add the color
        if current_selection:
            self.text_area.tag_add(color, current_selection[0], current_selection[1])
            self.text_area.tag_config(color, foreground = color)

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
    
    # Is Previous Character Colored
    # Description: Checks if the previous character is colored If it is, color the current character.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The current character is colored if the previous character is colored.
    def is_prev_char_colored(self):
        # Get the current index of the typing cursor
        current_index = self.text_area.index(tk.INSERT)
        # Get the index of the previous character
        prev_char_index = "{}.{}".format(current_index.split('.')[0], int(current_index.split('.')[1]) - 1)

        # Check if the previous character has the color tag
        if "red" in self.text_area.tag_names(prev_char_index):
            # If it is, color the current character as well
            self.text_area.tag_add("red", current_index)
            self.text_area.tag_configure("red", foreground = "red")
        elif "blue" in self.text_area.tag_names(prev_char_index):
            # If it is, color the current character as well
            self.text_area.tag_add("blue", current_index)
            self.text_area.tag_configure("blue", foreground = "blue")
        elif "green" in self.text_area.tag_names(prev_char_index):
            # If it is, color the current character as well
            self.text_area.tag_add("green", current_index)
            self.text_area.tag_configure("green", foreground = "green")
        elif "yellow" in self.text_area.tag_names(prev_char_index):
            # If it is, color the current character as well
            self.text_area.tag_add("yellow", current_index)
            self.text_area.tag_configure("yellow", foreground = "yellow")
        elif "purple" in self.text_area.tag_names(prev_char_index):
            # If it is, color the current character as well
            self.text_area.tag_add("purple", current_index)
            self.text_area.tag_configure("purple", foreground = "purple")
        elif "pink" in self.text_area.tag_names(prev_char_index):
            # If it is, color the current character as well
            self.text_area.tag_add("pink", current_index)
            self.text_area.tag_configure("pink", foreground = "pink")
        else:
            # Use default color
            self.text_area.tag_add("black", current_index)
            self.text_area.tag_configure("black", foreground = "black")
    
    # Manage Text Area Strings
    # Description: Adds and removes strings into the class's list of words.
    # Precondition: Self must be passed as a parameter.
    # Postconditions: The class's list of words is updated.
    def manage_text_area_strings(self):
        currentWordsList = []
        # Get all characters in the text area as one long string
        allText = self.text_area.get("1.0", "end-1c")
        # Remove punctuation from the text
        cleanedText = ''
        for char in allText:
            if char.isalnum() or char.isspace():
                cleanedText += char
        # Split the characters and put into a list
        currentWordsList = cleanedText.split()
        # Remove any words in the class's word list that are not in the current words list
        for i in self.wordsList:
            if (not(i in currentWordsList)):
                self.wordsList.remove(i)
        # Add any words that are in the current words list that are not in the class's word list
        for i in currentWordsList:
            if (not(i in self.wordsList)):
                self.wordsList.append(i)
        # Sort the class's word list
        self.wordsList.sort()
    
    # Identify Misspelled Words Function
    # Description: This function identifies unknown words in the class's word list and then adds a visible indictaor
    # and tags to corresponding position in the text area.
    # Preconditions: Class self must be passed as a parameter.
    # Postconditions: Unknown words are identified and tagged in text area.
    def identify_misspelled_words(self):
        # Update wordsList
        self.manage_text_area_strings()
        # Get SpellChecker object
        spell = SpellChecker()
        # From the class's word list, find words not in dictionary
        unknownWordList = spell.unknown(self.wordsList)
        # From the class's word list, find words in dictionary
        knownWordList = spell.known(self.wordsList)
        # Set tags for known words and remove unknown word tag if necessary
        for word in knownWordList:
            startIndex = "1.0"
            loop = True
            while loop:
                # Sets start index to the start of the unknown word
                startIndex = self.text_area.search(word, startIndex, stopindex="end")
                if not startIndex:
                    loop = False
                else:
                    endIndex = f"{startIndex}+{len(word)}c"
                    self.text_area.tag_remove("unknown_word", startIndex, endIndex)
                    # Make it bold and italicized
                    self.text_area.tag_config("known_word", font=font.Font())
                    # Sets start index to next word to look for repeat occurances
                    startIndex = endIndex
        self.mispelledWords = False
        # Find unknown words in text area and add "unknown_word" tag
        for word in unknownWordList:
            startIndex = "1.0"
            loop = True
            while loop:
                # Sets start index to the start of the unknown word
                startIndex = self.text_area.search(word, startIndex, stopindex="end")
                if not startIndex:
                    loop = False
                else:
                    self.mispelledWords = True
                    endIndex = f"{startIndex}+{len(word)}c"
                    self.text_area.tag_add("unknown_word", startIndex, endIndex)
                    # Make it bold and italicized
                    self.text_area.tag_config("unknown_word", font=("Helvetica", 10, "bold italic"), foreground="red")
                    # Sets start index to next word to look for repeat occurances
                    startIndex = endIndex

    # Create Audio Window Function
    # Description: Creates a new window for audio recording.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: A new window for audio recording is built and launched.
    def create_audio_window(self):
        # Only create window if there are no other ones currently open
        if (self.windowNum == 0):
            # Create a new window for audio recording
            self.audio_window = tk.Toplevel(self)
            self.audio_window.title("Audio Recorder")
            self.audio_window.geometry("300x200")

            # Bind the close event to the toggle_recording function
            # Source: https://tkdocs.com/tutorial/windows.html
            # Intercepting the close button section
            self.audio_window.protocol("WM_DELETE_WINDOW", self.toggle_recording_exit)

            # Create a label to provide user directions
            label = tk.Label(self.audio_window, text="Select the microphone icon to start recording audio")
            label.pack()

            # Create a record button that will start recording audio
            self.record_button = tk.Button(self.audio_window, text="🎤", font=("Arial", 25, "bold"), command=self.toggle_recording, fg='black')
            self.record_button.pack()
            self.recording = False

            # Add blank message label field
            self.message_label = tk.Label(self.audio_window, text="")
            self.message_label.pack()

            # Add an "Undo button" to undo the last action
            undo_button = tk.Button(self.audio_window, text="Undo Addition", command=self.typed_note_undo)
            undo_button.pack()

            # Increment count of windows
            self.windowNum = self.windowNum + 1

    # Toggle Recording Function
    # This function was partially adapted from this source: https://www.youtube.com/watch?v=u_xNvC9PpHA& 
    # Description: Toggles the recording of audio.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The audio recording is toggled to be True or False.
    def toggle_recording(self):
        # If recording is already in process, stop recording by setting recording to False
        # This will interrupt the thread that is recording audio
        if self.recording:
            self.message_label.config(text="")
            self.recording = False
            self.record_button.config(fg='black')
        # If recording is not in process, start recording by setting recording to True
        # This will also start a new thread to record audio
        else:
            self.message_label.config(text="Recording in process...")
            self.recording = True
            # This source was used to learn how to start a new thread to record audio
            # https://www.youtube.com/watch?v=u_xNvC9PpHA
            threading.Thread(target=self.take_audio).start()
            self.record_button.config(fg='red')
    
    # Toggle Recording Exit Function
    # Description: This function is binded to the record audio window exit. It stops the recording of audio if it is in process.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The audio recording is set to False if it is True.
    def toggle_recording_exit(self):
        if self.recording:
            self.recording = False
        # Decrement count of recording windows
        self.windowNum = self.windowNum - 1
        # Source: https://www.geeksforgeeks.org/how-to-close-a-window-in-tkinter/
        self.audio_window.destroy()

    # Take Audio Function
    # This function was partially adapted from this source: https://www.youtube.com/watch?v=u_xNvC9PpHA& 
    # Description:
    # Preconditions:
    # Postconditions:
    def take_audio(self):
        # Takes audio while the thread is running
        audio = pyaudio.PyAudio()
        # Try block catches errors, such as a lack of a microphone connected or an unexpected issue while recording
        try:
            stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                input=True, frames_per_buffer=1024)
        except OSError as e:
            self.recording = False
            audio.terminate()
            self.record_button.config(fg='black')
            self.message_label.config(text="Error: No microphone detected")
            return
        
        # For tracking the time of recording
        frames = []

        # While recording (the thread is running)
        while self.recording:
            data = stream.read(1024)
            frames.append(data)

        # Arrives here when the thread is interrupted (the user selects the record button to stop)
        # Stops audio stream and terminates
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Creates audio file
        input_text = "audio.wav"
        sound_file = wave.open(input_text, "wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b"".join(frames))
        sound_file.close()
        
        audio = self.open_audio_file()
        # If the audio file was found and opened successfully, transcribe the speech
        if (not(audio == False)):
            text = self.transcribe_speech(audio)
            # If the text was successfully transcribed, insert it into the text area and delete the audio file
            if (not(text == False)):
                self.text_area.insert(tk.END, text)
                self.delete_audio_file()
    
    # Transcribe Speech Function
    # Source: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
    # Description:
    # Preconditions:
    # Postconditions:
    def transcribe_speech(self, audio):
        r = sr.Recognizer()
        # recognize speech using Google Speech Recognition
        try:
            message = r.recognize_google(audio, language="english")
            # Debug message
            print("Google thinks you said '" + message + "'.")
            return message
        except sr.UnknownValueError:
            # Debug message
            print("Google could not understand audio")
            return False
        except sr.RequestError as e:
            # Debug message
            print(f"Could not request results from Google; {e}")
            return False
    
    # Open Audio File Function
    # Description: Opens the audio file.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The audio file is opened and returned if it can be opened. Else, False is returned.
    def open_audio_file(self):  
        try:
            with wave.open("Audio.wav", "rb") as audio_file:
                # Convert raw data to AudioData
                audio_data = sr.AudioData(audio_file.readframes(audio_file.getnframes()), audio_file.getframerate(), audio_file.getsampwidth())
                return audio_data
        except FileNotFoundError:
            # Debug message
            print("Error: Audio file not found")  
            return False
    
    # Delete Audio File Function
    # Description: Deletes the audio file.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The audio file is deleted.
    def delete_audio_file(self):
        try:
            os.remove("Audio.wav")
        except FileNotFoundError:
            # Debug message
            print("Error: Audio file not found")
    
    # Export Typed Note Function
    # Source: https://tkdocs.com/shipman/tkFileDialog.html
    # Description: Allows the user to export the typed note to a .txt file
    # Preconditions: Self must be passed as a parameter
    # Postconditions: The typed note is exported to a .txt file
    def export_typed_note(self):

        typed_note_content = self.text_area.get("1.0", tk.END)

        # Open a file dialog for the user to select the save location
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Export as")

        # If a file path is selected
        if file_path:
            try:
                # Write the typed note content to the selected file
                with open(file_path, "w") as file:
                    file.write(typed_note_content)
                # Show a success message
                tk.messagebox.showinfo("Success", "Typed note exported successfully!")
            except Exception as e:
                # Show an error message if there's any issue with exporting
                tk.messagebox.showerror("Error", f"An error occurred while exporting the typed note: {e}")
    
    # Save Typed Note Function
    # Description: Opens a file dialog for the user to select the save location. They can select a .typ file to save.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The file path is returned if a file is selected.
    def save_typed_note(self):
        default_path = None
        # Set default path to notes folder if it exists
        if os.path.isdir("notes"):
            default_path = "notes"
        # Open a file dialog for the user to select the save location
        file_path = filedialog.asksaveasfilename(defaultextension=".typ", filetypes=[("Typed Note Files", "*.typ")], title="Save as", initialdir=default_path)
        # If a file path is selected
        if file_path:
            try:
                # Show a success message
                tk.messagebox.showinfo("Success", "Typed note saved successfully!")
                # Get name of file path without the directory path or extension
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                # Set the window title to the file name
                self.controller.title(file_name + " - Note-Taker App")
                return file_path
            except Exception as e:
                # Show an error message if there's any issue with saving
                tk.messagebox.showerror("Error", f"An error occurred while saving the typed note: {e}")
    
    # Load Typed Note Function
    # Description: Opens a file dialog for the user to select the load location. They can select a .typ file to load.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The file path is returned if a file is selected.
    def load_typed_note(self):
        # Open a file dialog for the user to select the load location
        file_path = filedialog.askopenfilename(defaultextension=".typ", filetypes=[("Typed Note Files", "*.typ")], title="Load File")
        # If a file path is selected
        if file_path:
            try:
                # Show a success message
                tk.messagebox.showinfo("Success", "Typed note successfully opened!")
                # Get name of file path without the directory path or extension
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                # Set the window title to the file name
                self.controller.title(file_name + " - Note-Taker App")
                return file_path
            except Exception as e:
                # Show an error message if there's any issue with opening
                tk.messagebox.showerror("Error", f"An error occurred while opening the typed note: {e}")

    # Create Pickle File Function
    # Description: Creates a pickle file with the typed note content and the underlined/color sequences.
    # Preconditions: Self and the file name must be passed as parameters.
    # Postconditions: A pickle file is created with the typed note content and the underlined/color sequences saved as a string and tuples.
    def create_pickle_file(self, file_name):
        try:
            # Open file for binary writing
            data_file = open(file_name, 'wb')
            # Get note content
            typed_note_content = self.text_area.get("1.0", tk.END)
            # Add typed note content to pickle file
            pickle.dump(typed_note_content, data_file)
            # Get index of every underlined sequence and put into a tuple
            underline_ranges = tuple(str(index) for index in self.text_area.tag_ranges("underline"))
            # Add underlined sequences to pickle file
            pickle.dump(underline_ranges, data_file)
            # Repeat the process for other colors
            red_ranges = tuple(str(index) for index in self.text_area.tag_ranges("red"))
            pickle.dump(red_ranges, data_file)
            blue_ranges = tuple(str(index) for index in self.text_area.tag_ranges("blue"))
            pickle.dump(blue_ranges, data_file)
            green_ranges = tuple(str(index) for index in self.text_area.tag_ranges("green"))
            pickle.dump(green_ranges, data_file)
            yellow_ranges = tuple(str(index) for index in self.text_area.tag_ranges("yellow"))
            pickle.dump(yellow_ranges, data_file)
            purple_ranges = tuple(str(index) for index in self.text_area.tag_ranges("purple"))
            pickle.dump(purple_ranges, data_file)
            pink_ranges = tuple(str(index) for index in self.text_area.tag_ranges("pink"))
            pickle.dump(pink_ranges, data_file)
            # Create a dictionary to store font settings for each text range
            font_settings = {}
            # Increment through text area tags
            for tag_name in self.text_area.tag_names():
                # For each index in range
                for index in self.text_area.tag_ranges(tag_name):
                    # Get font
                    font = self.text_area.tag_cget(tag_name, "font")
                    # If font is set, add to dictionary with index as key
                    if font:  
                        font_settings[str(index)] = font
            # Add font settings to pickle file
            pickle.dump(font_settings, data_file)

            # Close file
            data_file.close()
        except:
            return
    
    # Open Pickle File Function
    # Description: Loads information from a pickle file. It inserts the typed note content into the text area and then adds the underlined/color sequences back to the text area.
    # Preconditions: Self and the file name must be passed as parameters.
    # Postconditions: The typed note content is updated to be the content of the pickle file.
    def open_pickle_file(self, file_name):
        try:
            # Open file for binary reading
            data_file = open(file_name, 'rb')
            # Load typed note content
            typed_note_content = pickle.load(data_file)
            # Load underlined sequences
            underline_ranges = pickle.load(data_file)
            # Load color sequences
            red_ranges = pickle.load(data_file)
            blue_ranges = pickle.load(data_file)
            green_ranges = pickle.load(data_file)
            yellow_ranges = pickle.load(data_file)
            purple_ranges = pickle.load(data_file)
            pink_ranges = pickle.load(data_file)
            # Load font settings
            font_settings = pickle.load(data_file)
            # Close file
            data_file.close()
            # Wipe text area clean
            self.text_area.delete("1.0", tk.END)
            # Insert typed note content into text area
            self.text_area.insert(tk.END, typed_note_content)
            # Prevent user from undoing the insertion of the typed note content
            self.text_area.edit_reset()
            # Add underlined sequences back to text area
            i = 0
            # Add underlined sequences back to text area
            while(i < len(underline_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("underline", underline_ranges[i], underline_ranges[i+1])
                self.text_area.tag_configure("underline", underline=True)
                i += 2
            # Add red sequences back to text area
            i = 0
            while(i < len(red_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("red", red_ranges[i], red_ranges[i+1])
                self.text_area.tag_configure("red", foreground = "red")
                i += 2
            # Add blue sequences back to text area
            i = 0
            while(i < len(blue_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("blue", blue_ranges[i], blue_ranges[i+1])
                self.text_area.tag_configure("blue", foreground = "blue")
                i += 2
            # Add green sequences back to text area
            i = 0
            while(i < len(green_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("green", green_ranges[i], green_ranges[i+1])
                self.text_area.tag_configure("green", foreground = "green")
                i += 2
            # Add yellow sequences back to text area
            i = 0
            while(i < len(yellow_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("yellow", yellow_ranges[i], yellow_ranges[i+1])
                self.text_area.tag_configure("yellow", foreground = "yellow")
                i += 2
            # Add purple sequences back to text area
            i = 0
            while(i < len(purple_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("purple", purple_ranges[i], purple_ranges[i+1])
                self.text_area.tag_configure("purple", foreground = "purple")
                i += 2
            # Add pink sequences back to text area
            i = 0
            while(i < len(pink_ranges) - 1):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                self.text_area.tag_add("pink", pink_ranges[i], pink_ranges[i+1])
                self.text_area.tag_configure("pink", foreground = "pink")
                i += 2
            # Convert font settings dictionary to tuple
            font_settings_tuple = tuple(font_settings.items())
            # Add font settings back to text area
            i = 0
            while(i < len(font_settings_tuple)):
                # As the tuple consists of start and end pairs, add the tag to the text area
                # in pairs of two, then increment i counter by 2
                # Get index and font from first tuple item
                font_setting = font_settings_tuple[i]
                font = font_setting[1]
                index_lower = font_setting[0]
                # Get index from second tuple item
                font_setting = font_settings_tuple[i + 1]
                index_upper = font_setting[0]
                # Add font settings to text area using font and lower/upper index
                self.text_area.tag_add("font", index_lower, index_upper)
                self.text_area.tag_configure("font", font=font)
                i += 2
        except:
            return
    
    # Typed Note Paste Function
    # Partially adapted from this source: https://stackoverflow.com/questions/73059188/copying-and-pasting-text-displayed-on-tkinter-text-widget:
    # Description: This function pastes the copied text into the text area.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The copied text is pasted into the text area.
    def typed_note_paste(self):
        # If there is an item in the clipboard, paste it into the text area
        try:
            self.text_area.insert('end', self.selection_get(selection='CLIPBOARD'))
        except:
            return
    
    # Typed Note Copy Function
    # Partially adapted from this source: https://stackoverflow.com/questions/73059188/copying-and-pasting-text-displayed-on-tkinter-text-widget:
    # Description: This function copies the selected text in the text area.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The selected text is copied.
    def typed_note_copy(self):
        # If there is a selection, copy it to clipboard
        try:
            content = self.selection_get()
            self.clipboard_clear()
            self.clipboard_append(content)  
        except:
            return
    
    # Typed Note Cut Function
    # Partially adapted from this source: https://stackoverflow.com/questions/73059188/copying-and-pasting-text-displayed-on-tkinter-text-widget:
    # Description: This function cuts the selected text in the text area.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The selected text is cut.
    def typed_note_cut(self):
        # If there is a selection, cut it from the text area
        try:
            content = self.selection_get()
            self.clipboard_clear()
            self.clipboard_append(content)
            self.text_area.delete('sel.first', 'sel.last')
        except:
            return
    
    # Typed Note Undo Function
    # Source: https://tkdocs.com/tutorial/text.html
    # See section "Modifications, Undo and Redo"
    # Description: This function undoes the last action in the text area.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The last action is undone.
    def typed_note_undo(self):
        try:
            self.text_area.edit_undo()
        except:
            return
    
    # Typed Note Redo Function
    # Source: https://tkdocs.com/tutorial/text.html
    # See section "Modifications, Undo and Redo"
    # Description: This function redoes the last action in the text area.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The last action is redone.
    def typed_note_redo(self):
        try:
            self.text_area.edit_redo()
        except:
            return
    
    # Save Note Driver Function
    # Description: This function is the driver for saving a typed note.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The typed note is saved.
    def save_note_driver(self):
        # Launch window for user to save a typed note
        # Set "saved_file" to file location
        saved_file = self.save_typed_note()
        # Create a pickle file and save it to file location
        self.create_pickle_file(saved_file)
    
    # Load Note Driver Function
    # Description: This function is the driver for loading a typed note.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The typed note is loaded.
    def load_note_driver(self):
        # Launch window for user to load a typed note
        opened_file = self.load_typed_note()
        # Open a pickle file and load it
        self.open_pickle_file(opened_file)

class DrawnNotePage(tk.Frame):
    # Initialization Function
    # Description: Initializes the DrawnNotePage class
    # Preconditions: 
    # Postconditions: 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Set default line color
        self.color = "black"
        
        # Create canvas area to draw notes
        self.canvas = tk.Canvas(self)
        self.canvas.pack(expand=True, fill='both')

        # Bind mouse dragging event to canvas
        self.canvas.bind("<Button-1>", self.save_posn)
        self.canvas.bind("<B1-Motion>", self.add_line)

        self.lastx, self.lasty = None, None
        # A stored tuple of actions
        self.actions = []

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
            self.canvas.create_line((self.lastx, self.lasty, event.x, event.y), fill=self.color)
            # Save the line to the list of actions
            self.actions.append(('line', self.lastx, self.lasty, event.x, event.y, self.color))
        self.save_posn(event)
    
    # Set Line Color Function
    # Description:
    # Preconditions:
    # Postconditions:
    def set_line_color(self, line_color):
        self.color = line_color

    # Export Drawn Note Function
    # Refered to this documentation to create screenshots using PYAutoGUI: https://pyautogui.readthedocs.io/en/latest/screenshot.html
    # Description: Allows the user to export the drawn note to a .png file.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The drawn note is exported to a .png file.
    def export_drawn_note(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])

        if file_path:  # If user selected a file path
            try:
                # Get the position and size of the canvas
                x = self.canvas.winfo_rootx()
                y = self.canvas.winfo_rooty()
                width = self.canvas.winfo_width()
                height = self.canvas.winfo_height()
                # Capture the contents of the canvas
                img = pyautogui.screenshot(region=(x, y, width, height))
                # Save the image as a PNG file
                img.save(file_path)
                tk.messagebox.showinfo("Success", "Drawn note exported successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred while exporting the drawn note: {e}")

    # Save Drawn Note Function
    # Description: Opens a file dialog for the user to select the save location. They can select a . file to save.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The file path is returned if a file is selected.
    def save_drawn_note(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".dra", filetypes=[("Drawn Note Files", "*.dra")], title="Save as")

        if file_path:  # If a file path is selected
            try:
                tk.messagebox.showinfo("Success", "Drawn note saved successfully!")
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                self.controller.title(file_name + " - Note-Taker App")
                return file_path
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred while saving the drawn note: {e}")
    
    # Load Drawn Note Function
    # Description: Opens a file dialog for the user to select the load location. They can select a . file to load.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The file path is returned if a file is selected.
    def load_drawn_note(self):
        # Open a file dialog for the user to select the load location
        file_path = filedialog.askopenfilename(defaultextension=".dra", filetypes=[("Drawn Note Files", "*.dra")], title="Load File")
        # If a file path is selected
        if file_path:
            try:
                # Get name of file path without the directory path or extension
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                # Set the window title to the file name
                self.controller.title(file_name + " - Note-Taker App")
                return file_path
            except Exception as e:
                # Show an error message if there's any issue with opening
                messagebox.showerror("Error", f"An error occurred while opening the drawn note: {e}")
    
    # Create Pickle File Function
    # Description: Creates a pickle file with the drawn note content.
    # Preconditions: Self and the file name must be passed as parameters.
    # Postconditions: A pickle file is created with the drawn note content saved.
    def create_pickle_file_drawn(self, file_name):
        try:
            # Open file for binary writing
            data_file = open(file_name, 'wb')
            # Add actions to pickle file
            pickle.dump(self.actions, data_file)
            data_file.close()
        except:
            return
    
    # Open Pickle File Function
    # Description: Loads information from a pickle file. It inserts the drawn note content into the canvas.
    # Preconditions: Self and the file name must be passed as parameters.
    # Postconditions: The drawn note content is updated to be the content of the pickle file.
    def open_pickle_file_drawn(self, file_name):
        try:
            # Open file for binary writing
            data_file = open(file_name, 'rb')
            # Wipe any existing actions
            self.actions = []
            # Load actions
            self.actions = pickle.load(data_file)
            data_file.close()
            self.canvas.delete("all")  # Clear the canvas before redrawing
            # Replicate actions that were loaded from the pickle file into the current canvas
            for action in self.actions:
                # Make sure the first element is "line"
                if action[0] == 'line':
                    # Elements 1 through 5 of action are the x and y coordinates of the line and the color
                    self.canvas.create_line(action[1:5], fill=action[5])
            tk.messagebox.showinfo("Success", "Drawn note opened successfully!")
        except: 
            return
      
    # Save Drawn Note Driver Function
    # Description: This function is the driver for saving a drawn note.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The drawn note is saved.
    def save_drawn_note_driver(self):
        # Launch window for user to save a drawn note
        # Set "saved_file" to file location
        saved_file = self.save_drawn_note()
        # Create a pickle file and save it to file location
        self.create_pickle_file_drawn(saved_file)

    # Load Drawn Note Driver Function
    # Description: This function is the driver for loading a drawn note.
    # Preconditions: Self must be passed as a parameter.
    # Postconditions: The note is loaded.
    def load_drawn_note_driver(self):
        # Launch window for user to load a drawn note
        opened_file = self.load_drawn_note()
        # Open a pickle file and load it
        self.open_pickle_file_drawn(opened_file)

# Driver Code
app = noteTaker()
app.mainloop() 