import sys
import csv
import io
from tkinter import *
from PIL import Image, ImageTk
import base64
from io import BytesIO
import os
from datetime import datetime

def hide_console_window():
    if sys.platform == "win32":
        # Windows-specific: Hide the console window
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    elif sys.platform == "darwin":
        # macOS-specific: Redirect to /dev/null to hide terminal output (if running a GUI app)
        import os
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
    else:
        # For other platforms (Linux, etc.), no action
        pass

if __name__ == "__main__":
    hide_console_window()
    # Rest of your application logic
    
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import time  # Add this import at the top of the file


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("jQuizzle (A Top Gum Study Tool)")
        self.root.bind_class("Text", "<Tab>", self.focus_next_widget)
        self.root.bind_class("Text", "<Shift-Tab>", self.focus_prev_widget)

        # Initialize data
        self.questions = []  # To store questions, answers, options, and explanations
        self.flashcards = []  # To store flashcards
        self.current_edit_index = None  # To track which question is being edited

        # Create a Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)

        # Quiz Tab
        self.quiz_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.quiz_tab, text="Quiz")

        # Flashcards Tab
        self.flashcards_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.flashcards_tab, text="Flashcards")

        # Set up Quiz Tab
        self.setup_quiz_tab()

        # Set up Flashcards Tab
        self.setup_flashcards_tab()

        # Create custom styles for question tracker buttons
        style = ttk.Style()
        style.configure('Unanswered.TButton', background='gray')
        style.configure('Answered.TButton', background='blue')
        style.configure('Flagged.TButton', background='yellow')
        style.configure('FlaggedAndAnswered.TButton', background='#E6E6FA')  # Light purple
        style.configure('Correct.TButton', background='green')
        style.configure('Incorrect.TButton', background='red')
        
        # Create a style for flagged+answered with blue background and yellow border
        style.configure('FlaggedAnswered.TButton', 
                       background='blue',      # Inner color (answered)
                       bordercolor='yellow',   # Outer color (flagged)
                       borderwidth=3,          # Make border visible
                       relief='solid')         # Solid border style
        
        # Embedded icon (base64 string of your .png file)
        icon_base64 = """
        iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAi9SURBVHhe5VpbjxxHGe2qnoljs0pIsGMZNj3XXQsjwBHwQGIuQhHwBwwPxIp5SMQD4gUBDxFaWUK8EoS4BAkBUWKEjCLzCAnCRk4IWBvFDkm0653ZmVnjRSHxJUZx1jNdxTk13ePxarq7qncXzZizmqmq019Vfae66uuq6fWIubk5yQ/zBw8e9P+fuC1tfCK4XJVuIc5gqxrfLG44TbPLw21GQ4J5G2ithU0fthhV15UzzscXjxw5omhw7Nix0JZjmajfe29N+v79odYf0p63Rwhxm9bef9DDCspnCmF4emFl5UJkbsABYQpbmNzA3r17399bW/s4Lu5HG4GnvR2w6Wmh/4nLr2kpX2w2m+f61n1RLj4Pc4M74lKJeaYs18q1LwsdPgIFn/alLEINlcHnaGqgDKGeUuoqyGelkE+LbYW/LC4uvsnLMWZnZ3eGa2sHPC0OoeKDUso7INq0NUBUDpXq4top9PJEo9X6LS/l0UHODIBDJY284LXKdOUTfsH7gRTiAbqolTKik0AxsDU2GIyLqNGA2H/3L+pd+KpB9N0scsD4SQNsMU7CUzp8vud532y1Wn8j7yKenLlJruJrQfCIkP6PIaoIMbzsBA6GubtDsBE9ChwIrXRPKf315krrCXK24slJS/Gc9kZ8NQi+5fvFn4POJZ6IlsRNnzziCeOD8AqFov+zalD+dkRbiSdnbkOW+JirBMFXin7hKZXzbm0l4iUW9tTDjZXWkzbiyVkHwVqtVhehOgt6+7iJjxEtq2tY2PuXl5cXbbRZiWdZd8MfIYKPrXiCviEmbJehfjyiMrVlBUEucl2tVh/wlXdK6Xxr/n8NBsYw9A40O83n08STSw2Cg+daL3xU9PdMEwE+HoVQX2M+TTw5mWqAx/bu3bvfA+lfNNF2QsCZiuXwBfoeUSPFkxvskUcZEFO3T31ESHnPOK/99Yhiwa6pbVMfZTlJPLlE8eSYejqs8/EyaTC7ThnOMJ8knlzqNph5bFPvibYLEwb4rDz4nh4H0oMggGaKTCcROGQWmCaJJ5ceBAGsg8tYB8xOHOD1pSg7Uhu5zCDoeX5nEuXzQO5rucJ8knhyieLJMZVFeTYMw+vrT2/jDPpKnxV8ZzlJPDmjKs2AZZyyXvB9+clJ2Qv0d4Lqr81O6348EjEegkf5kTfb6jiM2fTrSZsBeHo9GefTtGUGQaK4Y9tRTKkLk7AfMEfiMFyVxeJRlqHDOD1KG7nUIBhzCwsLVxFUHhNiMCZjC/ootPju0tLS2zbaMg3IYW8pmu32r3ph7zTX17jCrH3Vm1/qLP8Cyzb1zsecf/LkSZ1mQO6zJ04I2r3vzrsv4lT4pXE9F5jpr9Q3Ll+58vqcZ/djr8gyiDmm9Xp9m+r2GujoA+M2CAx2SusL18Ne/fz589fI2WjLDIIxxzzW1ZrQ+rlxDIZ9n/SfXMSTswqCwxw6OYXx7mfHDJgF8M1ePDlH8YAQDc0TwpiBW18Ea/O6zFY8OXMrbcSTY1qZrnxY+tpsMccN0tP3nWu3X7YVT876xQg55gu+6jEdU6xFqZV4cmYG2Ignx3K9VLoPj9iXmN8IGLXNlhXgE2VTnira/1ij0zC+2Ygn5xwEcSDyY8fzghsWCF7UoT6EzdVD0L6w0Q0WfZIyND/e2Ionl2kwzBFC3rahX4iMeKWWtC8/hR3bU8udztP+9eIBDOziRgcB+wDTgK14ci6vxk0Q1Ep3meZFf7qrh5vN5hvsA5RYXF18Ew1/Fdc2tA6EVzT1bcWTcw6CuqCv5/XTxx1WSh9vdDovsO2oD64nQQ6De5w2eUCfQhm+ExWtxJNzDoJ8Saq7vdelkAXz7HUAp7hS4eca7fafUeSLWdM/+mBDul4ufwZr+QQGibQ12AiqhNoX+/hSlJyNeHLOQRAOXkHyjutmkEEKB5Xl9+7caXZraC8Wzz5M20ut1qlQ6aZzkDX2mnefvm1tEOx2u1fR3eWoaA3MGHyL5+bn57spfYRCe3/s27oBPl3yfd/4ZSuenFMQxDoT7Xb7XRT/5XyXzGZVnYgKI/sgsDvADHFcAvRFiDd4WGPZVjw5pyCIjoxnWngtpi7A9PcKnvca80l9MFVKnKGtC8wC8MQy8zY6hjnr4/AwhxH4h8sMiGwv3a51m5mkPpgP/fA8Rvmi2wyDrdavRgVrHeRyHIfRnfTOujwK+3fIW32l0zFvapL6YPnw4cNvw3rVRT4XFybnGeZtdcRcpsF6jqnn+y85vSyBHSzfikrJ0xQxJurjLdaxAa1CFXY1fGLZVkfMOQVBcsw3Go0VdP2q0zTV3lWTRP8eO6oP3kaTeAKzwA6CGycsSewsO2zbVkfMOQXBYQ6e/sFpAIQ2P1URSX3caPuGbRY4tzBuz5p8yhugJC5fEAQK0jvu9qqsP1h0MqkPpixL/NkC5wo4UzjOvKsOcs5BkBwSca7V+jsG4KztCQ7Tc/CuPqmPeHnEtlkwW2utXsGSfBHFxKWVxmUajOKYB7QU3k9NeLOCuIPfbCOtDwPh3RnlUsEliKX4E2QH/8fsooMcyyZyMqVBbJTFMZ2ent5eLZVXZspVXSuVEz/966XB74hpfRC1oPTyTCW7zWpQWtmzZ8+OqFouHbmDICD4GzwC1nesguHQtiGpj3gJAJkNsk8hxWOrq6s8BFm/4Bmhw23E1nNELSg/M1utjbxT/PBavVQxr6sJi/Z+mdVetVT6fWTu7PMwl6vSMMd03659U3Ds9Cin6+WK+cyUSvtpa9Mef3pHHcV669szg1kuz1erVRMn8vh8E5er0s2cma50CA7+jmuXTs5G6Uy58m4tCA7FdeI0q716EDyEutduagspBuWZIAjuos0GfB5wBpvQ0GDNzlQqD2K6/xB36Wi9XP0+hOwjH9mbf8+3aM8As+aDaOd7EP2bWqnyOPKfjy65+pfIbVpDMTcK8bWsurbtbcS/kX1kGdzK3JY2PhFcrkq3EGewVY2PPzcn/wup2W/EoqRDRQAAAABJRU5ErkJggg==
        """
        
        # Convert base64 to PhotoImage
        icon_data = base64.b64decode(icon_base64)
        icon_image = Image.open(BytesIO(icon_data))
        icon = ImageTk.PhotoImage(icon_image)
        
        self.root.iconphoto(True, icon)
        
        # OR Method 2: Using .ico file
        # self.root.iconbitmap('path/to/your/icon.ico')

    def focus_next_widget(self, event):
        """Move focus to the next widget."""
        event.widget.tk_focusNext().focus()
        return "break"

    def focus_prev_widget(self, event):
        """Move focus to the previous widget."""
        event.widget.tk_focusPrev().focus()
        return "break"

        
    def toggle_scrollbars(self, text_widget, v_scrollbar, h_scrollbar=None):
        content = text_widget.get("1.0", tk.END)
        lines = content.strip("\n").split("\n")

        # Vertical check
        text_height = len(lines)
        widget_height = int(text_widget.cget("height"))
        if text_height > widget_height:
            v_scrollbar.pack(side="right", fill="y")
        else:
            v_scrollbar.pack_forget()

        # Horizontal check only if h_scrollbar is provided
        if h_scrollbar:
            max_line_length = max((len(line) for line in lines), default=0)
            widget_width = int(text_widget.cget("width"))
            if max_line_length > widget_width:
                h_scrollbar.pack(side="bottom", fill="x")
            else:
                h_scrollbar.pack_forget()


    def update_question_bank_scrollbars(self):
        """
        Dynamically toggle the visibility of the scrollbars in the question bank.
        """
        total_items = self.question_listbox.size()
        visible_items = self.question_listbox["height"]

        # Show or hide the vertical scrollbar
        if total_items > visible_items:
            self.bank_scrollbar.pack(side="right", fill="y")
        else:
            self.bank_scrollbar.pack_forget()


    def setup_quiz_tab(self):
        # Quiz Tab Layout
        self.quiz_tab.columnconfigure(0, weight=1)
        self.quiz_tab.rowconfigure(0, weight=1)

        self.main_frame = ttk.Frame(self.quiz_tab)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure main_frame so the input area can expand horizontally
        self.main_frame.columnconfigure(0, weight=1)  # Input side
        self.main_frame.columnconfigure(1, weight=0)  # Question bank side (no horizontal expansion)
        self.main_frame.rowconfigure(0, weight=1)     # Allow vertical expansion

        # Left section: Input fields (Question, Explanation, Options)
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Make input_frame expandable
        self.input_frame.columnconfigure(0, weight=1)

        # Right section: Question Bank Listbox
        self.question_bank_frame = ttk.Frame(self.main_frame)
        self.question_bank_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        # Question Entry Area
        self.question_label = ttk.Label(self.input_frame, text="Enter Question:")
        self.question_label.grid(row=0, column=0, sticky="w")


        self.question_frame = ttk.Frame(self.input_frame)
        # Expand horizontally only (not vertically)
        self.question_frame.grid(row=1, column=0, pady=5, sticky="ew")

        self.question_text = tk.Text(self.question_frame, height=5, width=50, wrap="word")
        self.question_text.pack(side="left", fill="both", expand=True)
        self.question_text.bind(
            "<KeyRelease>",
            lambda e: self.toggle_scrollbars(self.question_text, self.question_scrollbar),
        )

        self.question_scrollbar = ttk.Scrollbar(self.question_frame, orient="vertical", command=self.question_text.yview)
        self.question_text.config(yscrollcommand=self.question_scrollbar.set)

        # Multiple Choice Options Area
        self.options_label = ttk.Label(self.input_frame, text=" Enter Choices (correct answers are marked with a * in front):")
        self.options_label.grid(row=2, column=0, sticky="w")

        self.options_frame = ttk.Frame(self.input_frame)
        # Expand horizontally only
        self.options_frame.grid(row=3, column=0, pady=5, sticky="ew")

        self.options_text = tk.Text(self.options_frame, height=8, width=50, wrap="none")
        self.options_text.pack(side="top", fill="both", expand=True)
        self.options_text.bind(
            "<KeyRelease>",
            lambda e: self.toggle_scrollbars(self.options_text, self.options_scrollbar, self.options_h_scrollbar),
        )

        self.options_scrollbar = ttk.Scrollbar(self.options_frame, orient="vertical", command=self.options_text.yview)
        self.options_h_scrollbar = ttk.Scrollbar(self.options_frame, orient="horizontal", command=self.options_text.xview)

        self.options_text.config(yscrollcommand=self.options_scrollbar.set, xscrollcommand=self.options_h_scrollbar.set)

        # Explanation Entry Area
        self.explanation_label = ttk.Label(self.input_frame, text="Enter Explanation:")
        self.explanation_label.grid(row=5, column=0, sticky="w")

        self.explanation_frame = ttk.Frame(self.input_frame)
        # Explanation should expand both horizontally and vertically
        self.explanation_frame.grid(row=6, column=0, pady=5, sticky="nsew")
        # Give the explanation row vertical weight so it expands vertically
        self.input_frame.rowconfigure(6, weight=1)
        self.explanation_frame.columnconfigure(0, weight=1)

        self.explanation_text = tk.Text(self.explanation_frame, height=5, width=50, wrap="word")
        self.explanation_text.pack(side="left", fill="both", expand=True)
        self.explanation_text.bind(
            "<KeyRelease>",
            lambda e: self.toggle_scrollbars(self.explanation_text, self.explanation_scrollbar),
        )

        self.explanation_scrollbar = ttk.Scrollbar(self.explanation_frame, orient="vertical", command=self.explanation_text.yview)
        self.explanation_text.config(yscrollcommand=self.explanation_scrollbar.set)

        # Buttons to add and clear question
        self.add_button = ttk.Button(self.input_frame, text="Add Question", command=self.add_or_save_question)
        self.add_button.grid(row=8, column=0, pady=5, sticky="w")

        self.clear_button = ttk.Button(self.input_frame, text="Clear", command=self.clear_fields)
        self.clear_button.grid(row=8, column=0, pady=5, sticky="e")

        # Question Bank Area with Dynamic Scrollbar
        self.question_bank_label = ttk.Label(self.question_bank_frame, text="Question Bank:")
        self.question_bank_label.grid(row=0, column=0, sticky="w")

        self.question_bank_frame.rowconfigure(1, weight=1)  # Allow vertical expansion
        self.question_bank_frame.columnconfigure(0, weight=1)

        self.listbox_frame = ttk.Frame(self.question_bank_frame)
        # Allow vertical expansion so listbox can grow taller
        self.listbox_frame.grid(row=1, column=0, pady=5, columnspan=2, sticky="nsew")

        self.question_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.EXTENDED, width=50, height=20)
        self.question_listbox.pack(side="left", fill="both", expand=True)
        self.question_listbox.bind('<Double-Button-1>', self.edit_question_on_double_click)

        self.question_bank_scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", command=self.question_listbox.yview)
        self.question_listbox.config(yscrollcommand=self.question_bank_scrollbar.set)

        # Buttons for Question Bank actions
        self.delete_button = ttk.Button(self.question_bank_frame, text="Delete Question", command=self.delete_question)
        self.delete_button.grid(row=2, column=0, pady=5, sticky="w")

        self.save_button = ttk.Button(self.question_bank_frame, text="Save Quiz", command=self.save_question_bank)
        self.save_button.grid(row=2, column=1, pady=5, sticky="e")

        self.import_button = ttk.Button(self.question_bank_frame, text="Import Quiz", command=self.handle_import_button)
        self.import_button.grid(row=3, column=0, pady=5, sticky="w")

        self.generate_button = ttk.Button(self.question_bank_frame, text="Generate Quiz", command=self.generate_quiz)
        self.generate_button.grid(row=3, column=1, pady=5, sticky="e")

    def setup_flashcards_tab(self):
        # Allow flashcards_tab to expand in both directions
        self.flashcards_tab.columnconfigure(0, weight=1)
        self.flashcards_tab.rowconfigure(0, weight=1)

        self.flashcards_main_frame = ttk.Frame(self.flashcards_tab)
        self.flashcards_main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Let flashcards_main_frame expand
        self.flashcards_main_frame.columnconfigure(0, weight=1)  # Input frame
        self.flashcards_main_frame.columnconfigure(1, weight=0)  # Bank frame doesn't expand horizontally
        self.flashcards_main_frame.rowconfigure(0, weight=1)     # Allows vertical expansion

        # Left section: Input fields (Question, Answer)
        self.flashcards_input_frame = ttk.Frame(self.flashcards_main_frame)
        self.flashcards_input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.flashcards_input_frame.columnconfigure(0, weight=1)
        self.flashcards_input_frame.rowconfigure(1, weight=1)
        self.flashcards_input_frame.rowconfigure(3, weight=1)

        # Right section: Flashcard Bank Listbox
        self.flashcard_bank_frame = ttk.Frame(self.flashcards_main_frame)
        self.flashcard_bank_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        # Flashcard Question Entry Area
        self.flash_question_label = ttk.Label(self.flashcards_input_frame, text="Enter Question:")
        self.flash_question_label.grid(row=0, column=0, sticky="w")

        self.flash_question_frame = ttk.Frame(self.flashcards_input_frame)
        self.flash_question_frame.grid(row=1, column=0, pady=5, sticky="nsew")
        self.flash_question_frame.columnconfigure(0, weight=1)
        self.flash_question_frame.rowconfigure(0, weight=1)

        self.flash_question_text = tk.Text(self.flash_question_frame, wrap="word")
        self.flash_question_text.grid(row=0, column=0, sticky="nsew")

        self.flash_question_scrollbar = ttk.Scrollbar(self.flash_question_frame, orient="vertical", command=self.flash_question_text.yview)
        self.flash_question_text.config(yscrollcommand=self.flash_question_scrollbar.set)

        # Flashcard Answer Entry Area
        self.flash_answer_label = ttk.Label(self.flashcards_input_frame, text="Enter Answer:")
        self.flash_answer_label.grid(row=2, column=0, sticky="w")

        self.flash_answer_frame = ttk.Frame(self.flashcards_input_frame)
        self.flash_answer_frame.grid(row=3, column=0, pady=5, sticky="nsew")
        self.flash_answer_frame.columnconfigure(0, weight=1)
        self.flash_answer_frame.rowconfigure(0, weight=1)

        self.flash_answer_text = tk.Text(self.flash_answer_frame, wrap="word")
        self.flash_answer_text.grid(row=0, column=0, sticky="nsew")

        self.flash_answer_scrollbar = ttk.Scrollbar(self.flash_answer_frame, orient="vertical", command=self.flash_answer_text.yview)
        self.flash_answer_text.config(yscrollcommand=self.flash_answer_scrollbar.set)

        # Buttons to add and clear flashcard
        self.add_flash_button = ttk.Button(self.flashcards_input_frame, text="Add Flashcard", command=self.add_or_save_flashcard)
        self.add_flash_button.grid(row=4, column=0, pady=5, sticky="w")

        self.clear_flash_button = ttk.Button(self.flashcards_input_frame, text="Clear", command=self.clear_flashcard_fields)
        self.clear_flash_button.grid(row=4, column=0, pady=5, sticky="e")

        # Flashcard Bank Area
        self.flashcard_bank_label = ttk.Label(self.flashcard_bank_frame, text="Flashcard Deck:")
        self.flashcard_bank_label.grid(row=0, column=0, sticky="w")

        # Creating Listbox with Dynamic Scrollbar
        self.flashcard_listbox_frame = ttk.Frame(self.flashcard_bank_frame)
        self.flashcard_listbox_frame.grid(row=1, column=0, pady=5, columnspan=2)

        self.flashcard_listbox = tk.Listbox(self.flashcard_listbox_frame, selectmode=tk.EXTENDED, width=50, height=20)
        self.flashcard_listbox.pack(side="left", fill="y")
        self.flashcard_listbox.bind('<Double-Button-1>', self.edit_flashcard_on_double_click)

        self.flashcard_scrollbar = ttk.Scrollbar(self.flashcard_listbox_frame, orient="vertical", command=self.flashcard_listbox.yview)
        self.flashcard_listbox.config(yscrollcommand=self.flashcard_scrollbar.set)
        self.flashcard_scrollbar.pack(side="right", fill="y")

        # Buttons for Flashcard Bank actions
        self.delete_flash_button = ttk.Button(self.flashcard_bank_frame, text="Delete Flashcard", command=self.delete_flashcard)
        self.delete_flash_button.grid(row=2, column=0, pady=5, sticky="w")
        self.save_flash_button = ttk.Button(self.flashcard_bank_frame, text="Save Deck", command=self.save_flashcard_bank)
        self.save_flash_button.grid(row=2, column=1, pady=5, sticky="e")
        self.import_flash_button = ttk.Button(self.flashcard_bank_frame, text="Import Deck", command=self.import_flashcard_deck)
        self.import_flash_button.grid(row=3, column=0, pady=5, sticky="w")
        self.generate_deck_button = ttk.Button(self.flashcard_bank_frame, text="Generate Deck", command=self.generate_flashcard_deck)
        self.generate_deck_button.grid(row=3, column=1, columnspan=2, pady=5, sticky="e")

    # Flashcard Methods
    def add_flashcard(self):
        question = self.flash_question_text.get("1.0", tk.END).strip()
        answer = self.flash_answer_text.get("1.0", tk.END).strip()

        if not question or not answer:
            messagebox.showwarning("Input Error", "Please enter both a question and an answer.")
            return

        self.flashcards.append({'question': question, 'answer': answer})
        self.update_flashcard_bank()
        self.clear_flashcard_fields()

    def clear_flashcard_fields(self):
        self.flash_question_text.delete("1.0", tk.END)
        self.flash_answer_text.delete("1.0", tk.END)

    def update_flashcard_bank(self):
        self.flashcard_listbox.delete(0, tk.END)
        for idx, card in enumerate(self.flashcards):
            self.flashcard_listbox.insert(tk.END, f"{idx + 1}. {card['question']}")

    def delete_flashcard(self):
        selected_indices = self.flashcard_listbox.curselection()
        for index in reversed(selected_indices):
            del self.flashcards[index]
        self.update_flashcard_bank()

    def save_flashcard_bank(self):
        """Save the flashcard bank in either TXT or CSV format."""
        file_types = [
            ("Text files", "*.txt"),
            ("CSV files", "*.csv")
        ]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=file_types
        )
        if not file_path:
            return

        if file_path.endswith('.csv'):
            # Add '_flash' before the .csv extension if not already present
            if not file_path.endswith("_flash.csv"):
                file_path = file_path.replace(".csv", "_flash.csv")
            self.save_flashcard_bank_csv(file_path)
        else:
            # Add '_flash' before the .txt extension if not already present
            if not file_path.endswith("_flash.txt"):
                file_path = file_path.replace(".txt", "_flash.txt")
            self.save_flashcard_bank_txt(file_path)

    def save_flashcard_bank_csv(self, file_path):
        """Save flashcards in CSV format."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Question', 'Answer'])  # Header row
                for card in self.flashcards:
                    writer.writerow([card['question'], card['answer']])
            messagebox.showinfo("Save Successful", "Flashcards have been saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the flashcards:\n{e}")

    def save_flashcard_bank_txt(self, file_path):
        """Save flashcards in TXT format."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for card in self.flashcards:
                    file.write(f"{card['question']}\n=\n{card['answer']}\n\n")
            messagebox.showinfo("Save Successful", "Flashcards have been saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the flashcards:\n{e}")

    def import_flashcard_bank(self, file_path, replace=True, popup=None):
        """Import flashcards from either TXT or CSV format."""
        try:
            if replace:
                self.flashcards.clear()

            if file_path.endswith('.csv'):
                self.import_flashcard_bank_csv(file_path)
            else:
                self.import_flashcard_bank_txt(file_path)

            self.update_flashcard_bank()
            if popup:
                popup.destroy()
            messagebox.showinfo("Import Successful", "Flashcards have been imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred while importing the flashcards:\n{e}")

    def import_flashcard_bank_csv(self, file_path):
        """Import flashcards from CSV format."""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) >= 2:  # Must have both question and answer
                    question = row[0].strip()
                    answer = row[1].strip()
                    if question and answer:
                        self.flashcards.append({
                            'question': question,
                            'answer': answer
                        })

    def import_flashcard_bank_txt(self, file_path):
        """Import flashcards from TXT format."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            raw_cards = content.split("\n\n")
            
            for raw_card in raw_cards:
                parts = raw_card.split("\n=\n")
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    if question and answer:
                        self.flashcards.append({
                            'question': question,
                            'answer': answer
                        })

    def import_flashcard_deck(self):
        """Handle the import deck button click."""
        file_types = [
            ("Flashcard files", "*.txt"),
            ("CSV files", "*.csv")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            if not self.flashcards:
                # If no existing flashcards, directly import with replacement
                self.import_flashcard_bank(file_path, replace=True)
            else:
                # If there are existing flashcards, show the popup
                self.import_flashcard_popup(file_path)

    def import_flashcard_popup(self, file_path):
        """Show popup for importing flashcards with options to replace or add."""
        popup = tk.Toplevel(self.root)
        popup.title("Import Flashcard Deck")
        popup.geometry("300x150")

        label = ttk.Label(popup, text="What would you like to do?")
        label.pack(pady=10)

        replace_button = ttk.Button(
            popup, 
            text="Replace Deck", 
            command=lambda: self.import_flashcard_bank(file_path, replace=True, popup=popup)
        )
        replace_button.pack(pady=5)

        add_button = ttk.Button(
            popup, 
            text="Add to Deck", 
            command=lambda: self.import_flashcard_bank(file_path, replace=False, popup=popup)
        )
        add_button.pack(pady=5)

        cancel_button = ttk.Button(popup, text="Cancel", command=popup.destroy)
        cancel_button.pack(pady=5)





    # Quiz Methods (unchanged from original)
    def edit_question_on_double_click(self, event):
        """
        Handle double-clicking a question for editing.
        """
        selected_indices = self.question_listbox.curselection()

        if len(selected_indices) != 1:
            return  # Do nothing if there are no or multiple selections

        index = selected_indices[0]
        question_data = self.questions[index]

        # Fill in the fields with the selected question's data for editing
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert(tk.END, question_data["question"])

        # Reconstruct options with correct answers marked with *
        options_with_asterisks = [
            f"*{opt}" if opt in question_data["correct"] else opt
            for opt in question_data["options"]
        ]
        self.options_text.delete("1.0", tk.END)
        self.options_text.insert(tk.END, "\n".join(options_with_asterisks))

        self.explanation_text.delete("1.0", tk.END)
        self.explanation_text.insert(tk.END, question_data["explanation"])

        # Keep track of the question being edited
        self.current_edit_index = index
        
        # Change Add button text and show Cancel button
        self.add_button.config(text="Save Changes")
        self.clear_button.config(text="Cancel Edit", command=self.cancel_question_edit)
        
    def cancel_question_edit(self):
        """Cancel editing and restore the original state."""
        self.clear_fields()
        self.clear_button.config(text="Clear", command=self.clear_fields)
        self.current_edit_index = None
        self.add_button.config(text="Add Question")

    def add_or_save_question(self):
        """
        Add a new question or save changes to an existing question.
        Parses options to separate correct answers based on an asterisk (*).
        """
        question = self.question_text.get("1.0", tk.END).strip()
        options = self.options_text.get("1.0", tk.END).strip().split("\n")
        options = [opt.strip() for opt in options if opt.strip()]  # Remove empty options

        if not question or len(options) < 2:
            messagebox.showwarning("Input Error", "Please enter a question and at least two options.")
            return

        correct = [opt.lstrip("*").strip() for opt in options if opt.startswith("*")]
        all_options = [opt.lstrip("*").strip() for opt in options]

        explanation = self.explanation_text.get("1.0", tk.END).strip()

        question_data = {
            "question": question,
            "options": all_options,
            "correct": correct,
            "explanation": explanation,
        }

        if self.current_edit_index is None:
            # Adding a new question
            self.questions.append(question_data)
        else:
            # Editing an existing question
            self.questions[self.current_edit_index] = question_data
            self.current_edit_index = None
            self.add_button.config(text="Add Question")

            # Restore the "Clear" button after editing
            self.clear_button.grid()

        self.update_question_bank()
        self.clear_fields()


    def clear_fields(self):
        """
        Clear all input fields after a question is added or edited.
        """
        self.question_text.delete("1.0", tk.END)  # Clear question input
        self.options_text.delete("1.0", tk.END)  # Clear multiple choice options input
        self.explanation_text.delete("1.0", tk.END)  # Clear explanation input

        # Reset the buttons only if not in edit mode
        if self.current_edit_index is None:
            self.add_button.config(text="Add Question")
            self.clear_button.config(text="Clear", command=self.clear_fields)


    def update_question_bank(self):
        self.question_listbox.delete(0, tk.END)
        for idx, q in enumerate(self.questions):
            self.question_listbox.insert(tk.END, f"{idx + 1}. {q['question']}")

    def delete_question(self):
        selected_indices = self.question_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a question to delete.")
            return

        for index in reversed(selected_indices):
            del self.questions[index]

        self.update_question_bank()

    def save_question_bank(self):
        """Save the question bank in either TXT or CSV format."""
        file_types = [
            ("Text files", "*.txt"),
            ("CSV files", "*.csv")
        ]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=file_types
        )
        if not file_path:
            return

        # Determine file format based on extension
        if file_path.endswith('.csv'):
            # Add '_quiz' before the .csv extension if not already present
            if not file_path.endswith("_quiz.csv"):
                file_path = file_path.replace(".csv", "_quiz.csv")
            self.save_question_bank_csv(file_path)
        else:
            # Add '_quiz' before the .txt extension if not already present
            if not file_path.endswith("_quiz.txt"):
                file_path = file_path.replace(".txt", "_quiz.txt")
            self.save_question_bank_txt(file_path)

    def save_question_bank_csv(self, file_path):
        """Save question bank in CSV format."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Question', 'Options', 'Explanation'])  # Header row
                
                for question in self.questions:
                    # Mark correct answers with asterisks
                    options = [f"*{opt}" if opt in question['correct'] else opt 
                             for opt in question['options']]
                    options_str = '\n'.join(options)
                    writer.writerow([
                        question['question'],
                        options_str,
                        question.get('explanation', '')
                    ])
            messagebox.showinfo("Save Successful", "Quiz has been saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the quiz:\n{e}")

    def save_question_bank_txt(self, file_path):
        """Save question bank in TXT format."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for question_data in self.questions:
                    question = question_data["question"]
                    options = "\n".join(
                        f"*{opt}" if opt in question_data["correct"] else opt
                        for opt in question_data["options"]
                    )
                    explanation = question_data["explanation"]
                    file.write(f"{question}\n=\n{options}\n==\n{explanation}\n\n")
            messagebox.showinfo("Save Successful", "Quiz has been saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the quiz:\n{e}")

    def handle_import_button(self):
        """Handle importing quiz from either TXT or CSV format."""
        file_types = [
            ("Quiz files", "*.txt"),
            ("CSV files", "*.csv")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            if not self.questions:
                self.import_question_bank(file_path, replace=True)
            else:
                self.import_popup(file_path)

    def import_popup(self, file_path):
        popup = tk.Toplevel(self.root)
        popup.title("Import Question Bank")
        popup.geometry("300x150")

        label = ttk.Label(popup, text="What would you like to do?")
        label.pack(pady=10)

        replace_button = ttk.Button(popup, text="Replace Bank", command=lambda: self.import_question_bank(file_path, replace=True, popup=popup))
        replace_button.pack(pady=5)

        add_button = ttk.Button(popup, text="Add to Bank", command=lambda: self.import_question_bank(file_path, replace=False, popup=popup))
        add_button.pack(pady=5)

        cancel_button = ttk.Button(popup, text="Cancel", command=popup.destroy)
        cancel_button.pack(pady=5)

    def import_question_bank(self, file_path, replace=True, popup=None):
        """Import question bank from either TXT or CSV format."""
        if replace:
            self.questions.clear()

        try:
            if file_path.endswith('.csv'):
                self.import_question_bank_csv(file_path)
            else:
                self.import_question_bank_txt(file_path)

            self.update_question_bank()
            if popup:
                popup.destroy()
            messagebox.showinfo("Import Successful", "Questions have been imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred while importing the quiz:\n{e}")

    def import_question_bank_csv(self, file_path):
        """Import question bank from CSV format."""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) >= 2:  # Must have at least question and options
                    question = row[0].strip()
                    options_raw = row[1].strip().split('\n')
                    explanation = row[2].strip() if len(row) > 2 else "No explanation provided."

                    # Process options
                    options = [opt.strip() for opt in options_raw if opt.strip()]
                    correct = [opt.lstrip('*').strip() for opt in options if opt.startswith('*')]
                    all_options = [opt.lstrip('*').strip() for opt in options]

                    if question and all_options:
                        self.questions.append({
                            "question": question,
                            "options": all_options,
                            "correct": correct,
                            "explanation": explanation
                        })

    def import_question_bank_txt(self, file_path):
        """Import question bank from TXT format."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            raw_questions = content.split("\n\n")
            
            for raw_question in raw_questions:
                parts = raw_question.split("\n=\n")
                if len(parts) != 2:
                    continue

                question, rest = parts
                options_and_explanation = rest.split("\n==\n")
                options_raw = options_and_explanation[0] if options_and_explanation else ""
                explanation = options_and_explanation[1] if len(options_and_explanation) > 1 else "No explanation provided."

                options = [opt.strip() for opt in options_raw.split("\n") if opt.strip()]
                correct = [opt.lstrip("*").strip() for opt in options if opt.startswith("*")]
                all_options = [opt.lstrip("*").strip() for opt in options]

                if question.strip() and all_options:
                    self.questions.append({
                        "question": question.strip(),
                        "options": all_options,
                        "correct": correct,
                        "explanation": explanation.strip()
                    })

    def generate_quiz(self):
        """Generate a quiz with randomized question and multiple-choice options order."""
        if not self.questions:
            messagebox.showwarning("No Questions", "There are no questions in the Question Bank.")
            return

        # Randomize question order
        quiz_questions = self.questions[:]
        random.shuffle(quiz_questions)

        # Randomize options for each question
        for question in quiz_questions:
            question["options"] = random.sample(question["options"], len(question["options"]))

        # Open quiz window
        self.root.withdraw()
        self.quiz_window = tk.Toplevel(self.root)
        self.quiz_window.title("Quiz Time")
        self.quiz_window.protocol("WM_DELETE_WINDOW", self.on_quiz_close)
        
        # Create QuizRunner instance
        quiz_runner = QuizRunner(self.quiz_window, quiz_questions)

    def on_quiz_close(self):
        """Handle the event when the quiz window is closed."""
        if hasattr(self, 'quiz_window') and self.quiz_window:
            self.quiz_window.destroy()  # Destroy the quiz window
        self.root.deiconify()  # Show the main application window





    def edit_flashcard_on_double_click(self, event):
        """Handle double-clicking a flashcard for editing."""
        selected_indices = self.flashcard_listbox.curselection()

        if len(selected_indices) != 1:
            return  # Do nothing if there are no or multiple selections

        index = selected_indices[0]
        flashcard_data = self.flashcards[index]

        # Fill in the fields with the selected flashcard's data for editing
        self.flash_question_text.delete("1.0", tk.END)
        self.flash_question_text.insert(tk.END, flashcard_data['question'])

        self.flash_answer_text.delete("1.0", tk.END)
        self.flash_answer_text.insert(tk.END, flashcard_data['answer'])

        # Keep track of the flashcard being edited
        self.current_edit_index = index
        
        # Change Add button text and show Cancel button
        self.add_flash_button.config(text="Save Changes")
        self.clear_flash_button.config(text="Cancel Edit", command=self.cancel_flashcard_edit)

    def cancel_flashcard_edit(self):
        """Cancel editing and restore the original state."""
        self.clear_flashcard_fields()
        self.clear_flash_button.config(text="Clear", command=self.clear_flashcard_fields)
        self.current_edit_index = None
        self.add_flash_button.config(text="Add Flashcard")

    def add_or_save_flashcard(self):
        """Add a new flashcard or save changes to an existing one."""
        question = self.flash_question_text.get("1.0", tk.END).strip()
        answer = self.flash_answer_text.get("1.0", tk.END).strip()

        if not question or not answer:
            messagebox.showwarning("Input Error", "Please enter both a question and an answer.")
            return

        flashcard_data = {'question': question, 'answer': answer}

        if self.current_edit_index is None:
            # Adding a new flashcard
            self.flashcards.append(flashcard_data)
        else:
            # Editing an existing flashcard
            self.flashcards[self.current_edit_index] = flashcard_data
            self.current_edit_index = None
            self.add_flash_button.config(text="Add Flashcard")

        self.update_flashcard_bank()
        self.clear_flashcard_fields()

        # Show the "Clear" button again
        self.clear_flash_button.grid()

    # Update the Flashcard Bank to Enable Double-Click Edit
        self.flashcard_listbox.bind('<Double-Button-1>', self.edit_flashcard_on_double_click)

    def generate_flashcard_deck(self):
        """Generate a deck of flashcards in a separate window."""
        if not self.flashcards:
            messagebox.showwarning("No Flashcards", "There are no flashcards in the Flashcard Bank.")
            return

        # Create the Flashcard Viewer Window
        self.deck_window = tk.Toplevel(self.root)
        self.deck_window.title("Flashcard Deck")
        self.deck_window.geometry("800x600")
        self.deck_window.minsize(600, 400)

        # Initialize variables
        self.current_flashcard_index = 0
        self.current_side = "question"
        self.start_with_question = True  # Toggle to control which side shows first

        # Create main container with padding
        main_container = ttk.Frame(self.deck_window, padding="20")
        main_container.pack(fill="both", expand=True)

        # Card display area (centered)
        card_frame = ttk.Frame(main_container)
        card_frame.pack(fill="both", expand=True)

        # Flashcard content
        self.flashcard_label = ttk.Label(
            card_frame,
            text="",
            wraplength=600,
            justify="center",
            font=("Helvetica", 14)
        )
        self.flashcard_label.pack(expand=True)

        # Navigation buttons - moved up and centered
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill="x", pady=(0, 20))  # Changed from pady=(20, 0)

        # Center container for buttons
        center_button_frame = ttk.Frame(button_frame)
        center_button_frame.pack(expand=True)

        # Style for larger buttons
        button_style = ttk.Style()
        button_style.configure('Large.TButton', padding=(20, 10))  # Increased padding

        # Previous button
        prev_button = ttk.Button(
            center_button_frame,
            text="← Previous",
            command=self.previous_flashcard,
            style='Large.TButton'
        )
        prev_button.pack(side="left", padx=10)  # Increased padding between buttons

        # Flip button
        flip_button = ttk.Button(
            center_button_frame,
            text="Flip Card",
            command=self.flip_flashcard,
            style='Large.TButton'
        )
        flip_button.pack(side="left", padx=10)

        # Next button
        next_button = ttk.Button(
            center_button_frame,
            text="Next →",
            command=self.next_flashcard,
            style='Large.TButton'
        )
        next_button.pack(side="left", padx=10)

        # Card tracker
        self.card_tracker_label = ttk.Label(
            main_container,
            text=f"Card 1 of {len(self.flashcards)}",
            font=("Helvetica", 10)
        )
        self.card_tracker_label.pack(pady=(10, 0))

        # Bind resize event
        self.deck_window.bind('<Configure>', self.on_deck_resize)

        # Show first flashcard
        self.update_flashcard_view()

        # Key bindings for navigation
        self.deck_window.bind('<Left>', lambda e: self.previous_flashcard())
        self.deck_window.bind('<Right>', lambda e: self.next_flashcard())
        self.deck_window.bind('<space>', lambda e: self.flip_flashcard())

    def on_deck_resize(self, event):
        # Dynamically update wraplength as the window is resized
        current_width = self.deck_window.winfo_width()
        self.flashcard_label.configure(wraplength=current_width - 100)

    def update_flashcard_view(self):
        """Update the flashcard view and tracker based on the current index and side."""
        if self.current_flashcard_index < 0 or self.current_flashcard_index >= len(self.flashcards):
            return

        flashcard = self.flashcards[self.current_flashcard_index]
        if self.start_with_question:
            self.flashcard_label.config(text=flashcard["question"])
            self.current_side = "question"
        else:
            self.flashcard_label.config(text=flashcard["answer"])
            self.current_side = "answer"

        # Update card tracker
        self.card_tracker_label.config(
            text=f"Card {self.current_flashcard_index + 1} of {len(self.flashcards)}"
        )

    def flip_flashcard(self):
        """Flip the flashcard to the other side."""
        if self.current_flashcard_index < 0 or self.current_flashcard_index >= len(self.flashcards):
            return

        flashcard = self.flashcards[self.current_flashcard_index]
        if self.current_side == "question":
            self.flashcard_label.config(text=flashcard["answer"])
            self.current_side = "answer"
        else:
            self.flashcard_label.config(text=flashcard["question"])
            self.current_side = "question"

    def next_flashcard(self):
        """Navigate to the next flashcard in the deck."""
        self.current_flashcard_index += 1
        if self.current_flashcard_index >= len(self.flashcards):
            self.current_flashcard_index = 0  # Loop back to the first flashcard
        self.update_flashcard_view()

    def previous_flashcard(self):
        """Navigate to the previous flashcard in the deck."""
        self.current_flashcard_index -= 1
        if self.current_flashcard_index < 0:
            self.current_flashcard_index = len(self.flashcards) - 1  # Loop back to the last flashcard
        self.update_flashcard_view()





class QuizRunner:
    def __init__(self, root, quiz_questions):
        self.root = root
        self.quiz_questions = quiz_questions
        self.current_index = 0
        self.user_answers = [None] * len(self.quiz_questions)
        self.flagged_questions = set()  # Track flagged questions
        self.start_time = time.time()  # Add this line to fix the timer

        # Set a minimum size for the quiz window
        self.root.geometry("1020x620")  # Increased from 1000x600
        self.root.minsize(820, 520)  # Increased from 800x500

        # Create main container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create left frame for question tracker
        self.tracker_frame = ttk.Frame(self.main_frame, width=200)  # Increased width
        self.tracker_frame.pack(side="left", fill="both", padx=(0, 10))  # Changed to fill both
        self.tracker_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Create right frame for existing quiz content
        self.quiz_frame = ttk.Frame(self.main_frame)
        self.quiz_frame.pack(side="left", fill="both", expand=True)

        # Set up question tracker
        self.setup_question_tracker()
        
        # Set up original quiz layout in quiz_frame
        self.setup_quiz_content()

        self.update_question()
        self.update_timer()

        # Create custom styles for question tracker buttons
        style = ttk.Style()
        style.configure('Unanswered.TButton', background='gray')
        style.configure('Answered.TButton', background='blue')
        style.configure('Flagged.TButton', background='yellow')
        style.configure('FlaggedAndAnswered.TButton', background='#8B6BB2')  # Darker purple
        style.configure('Correct.TButton', background='green')
        style.configure('Incorrect.TButton', background='red')

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def enter(event):
            x = widget.winfo_rootx() + widget.winfo_width()
            y = widget.winfo_rooty()
            
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(
                self.tooltip, 
                text=text, 
                justify='left',
                background="#ffffe0", 
                relief='solid', 
                borderwidth=1
            )
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def setup_quiz_content(self):
        """Set up the original quiz content."""
        # Main content container with padding
        self.content_container = ttk.Frame(self.quiz_frame)  # Store reference
        self.content_container.pack(expand=True, fill="both")

        # Timer at top right
        self.timer_label = ttk.Label(self.content_container, text="Time Elapsed: 00:00")
        self.timer_label.pack(anchor="ne", padx=20, pady=10)

        # Center container for question and options
        self.center_container = ttk.Frame(self.content_container)  # Store reference
        self.center_container.pack(expand=True, fill="both", padx=50)

        # Question
        question_frame = ttk.Frame(self.center_container)
        question_frame.pack(fill="x", pady=20)
        
        self.question_label = ttk.Label(
            question_frame,
            text="",
            wraplength=600,
            justify="left",
            font=("Helvetica", 14, "bold")  # Reduced from 16 to 14
        )
        self.question_label.pack(anchor="w")

        # Options
        self.options_frame = ttk.Frame(self.center_container)
        self.options_frame.pack(fill="x", pady=20)

        # Create custom styles for larger buttons and options
        style = ttk.Style()
        style.configure('Large.TButton', padding=(20, 10), font=('Helvetica', 11))  # Larger navigation buttons
        style.configure('Large.TCheckbutton', font=('Helvetica', 12))  # Larger checkbuttons
        style.configure('Large.TRadiobutton', font=('Helvetica', 12))  # Larger radiobuttons

        # Navigation buttons at bottom
        nav_frame = ttk.Frame(self.content_container)
        nav_frame.pack(fill="x", pady=20)
        
        # Center the Previous/Next buttons
        nav_buttons = ttk.Frame(nav_frame)
        nav_buttons.pack(expand=True)
        
        self.prev_button = ttk.Button(
            nav_buttons, 
            text="← Previous", 
            command=self.previous_question,
            style='Large.TButton'  # Apply large button style
        )
        self.prev_button.pack(side="left", padx=10)  # Increased padding
        
        self.next_button = ttk.Button(
            nav_buttons, 
            text="Next →", 
            command=self.next_question,
            style='Large.TButton'  # Apply large button style
        )
        self.next_button.pack(side="left", padx=10)  # Increased padding
        
        # Submit button in bottom right corner
        self.submit_button = ttk.Button(
            self.content_container, 
            text="Submit Quiz", 
            command=self.submit_quiz,
            style='Large.TButton'  # Apply large button style
        )
        self.submit_button.pack(side="bottom", anchor="se", padx=20, pady=10)

    def update_question_status(self):
        """Update the visual status of question tracker buttons."""
        for i, btn in enumerate(self.tracker_buttons):
            if hasattr(self, 'quiz_submitted'):
                # After submission, colors are already set to green/red
                return
                
            is_flagged = i in self.flagged_questions
            is_answered = self.user_answers[i] and self.user_answers[i] != ""

            if is_flagged and is_answered:
                btn.configure(style='FlaggedAndAnswered.TButton')  # Light purple
                tooltip_text = "Flagged and Answered"
            elif is_flagged:
                btn.configure(style='Flagged.TButton')  # Yellow background
                tooltip_text = "Flagged for review"
            elif is_answered:
                btn.configure(style='Answered.TButton')  # Blue background
                tooltip_text = "Answered"
            else:
                btn.configure(style='Unanswered.TButton')  # Gray background
                tooltip_text = "Not answered yet"
            
            self.create_tooltip(btn, tooltip_text)

    def toggle_flag(self):
        """Toggle the flagged status of the current question."""
        if self.current_index in self.flagged_questions:
            self.flagged_questions.remove(self.current_index)
            self.flag_button.configure(text="Flag Question")
        else:
            self.flagged_questions.add(self.current_index)
            self.flag_button.configure(text="Unflag Question")
        
        # Update button text based on current question's status
        self.update_flag_button_text()
        self.update_question_status()

    def update_flag_button_text(self):
        """Update flag button text based on current question's status."""
        if hasattr(self, 'quiz_submitted'):
            return  # Don't update flag button if quiz is submitted
            
        if self.current_index in self.flagged_questions:
            self.flag_button.configure(text="Unflag Question")
        else:
            self.flag_button.configure(text="Flag Question")

    def jump_to_question(self, index):
        """Jump to a specific question when clicking its number."""
        self.save_user_answers()
        self.update_question_status()
        self.current_index = index
        self.update_question()
        if not hasattr(self, 'quiz_submitted'):  # Only update flag button if quiz isn't submitted
            self.update_flag_button_text()

    def update_question(self):
        current_question = self.quiz_questions[self.current_index]
        
        # Adjust font size if quiz is submitted
        question_font_size = 12 if hasattr(self, 'quiz_submitted') else 14
        self.question_label.config(
            text=f"Q{self.current_index + 1}: {current_question['question']}", 
            font=("Helvetica", question_font_size, "bold")
        )

        # Clear the options frame
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Create options with proper wrapping
        self.option_vars = []  # Initialize option_vars list
        option_font_size = 10 if hasattr(self, 'quiz_submitted') else 11
        
        if len(current_question['correct']) > 1:
            # Multiple choice logic with wrapped text
            for option in current_question['options']:
                var = tk.BooleanVar(value=False)
                var.trace_add('write', lambda *args: self.update_question_status())
                
                option_frame = ttk.Frame(self.options_frame)
                option_frame.pack(fill="x", anchor="w", padx=10, pady=4)
                
                cb = ttk.Checkbutton(
                    option_frame, 
                    variable=var,
                    style='Large.TCheckbutton'
                )
                cb.pack(side="left", anchor="nw")
                
                label = ttk.Label(
                    option_frame,
                    text=option,
                    wraplength=600,
                    justify="left",
                    font=('Helvetica', option_font_size)
                )
                label.pack(side="left", fill="x", padx=(5, 0))
                
                # Store both checkbox and label for disabling
                self.option_vars.append((option, var, cb, label))
        else:
            # Single choice logic with wrapped text
            var = tk.StringVar(value="")
            var.trace_add('write', lambda *args: self.update_question_status())
            self.option_vars.append(var)  # Add the StringVar to option_vars first
            
            self.radio_widgets = []  # Store radio buttons and labels
            for option in current_question['options']:
                option_frame = ttk.Frame(self.options_frame)
                option_frame.pack(fill="x", anchor="w", padx=10, pady=4)
                
                rb = ttk.Radiobutton(
                    option_frame,
                    variable=var,
                    value=option,
                    style='Large.TRadiobutton'
                )
                rb.pack(side="left", anchor="nw")
                
                label = ttk.Label(
                    option_frame,
                    text=option,
                    wraplength=600,
                    justify="left",
                    font=('Helvetica', option_font_size)
                )
                label.pack(side="left", fill="x", padx=(5, 0))
                
                self.radio_widgets.append((rb, label))

        # Restore user's previous answer
        if len(current_question['correct']) > 1:
            for option, var, _, _ in self.option_vars:
                if self.user_answers[self.current_index] and option in self.user_answers[self.current_index]:
                    var.set(True)
        else:
            if self.user_answers[self.current_index]:
                self.option_vars[0].set(self.user_answers[self.current_index])

        # If quiz is submitted, disable and gray out options
        if hasattr(self, 'quiz_submitted'):
            if len(current_question['correct']) > 1:
                for _, _, cb, label in self.option_vars:
                    cb.configure(state='disabled')
                    label.configure(foreground='gray')
            else:
                for rb, label in self.radio_widgets:
                    rb.configure(state='disabled')
                    label.configure(foreground='gray')

            # Add separator
            ttk.Separator(self.options_frame, orient='horizontal').pack(fill='x', pady=20)

            # Create scrollable frame for answer details
            details_container = ttk.Frame(self.options_frame)
            details_container.pack(fill='both', expand=True)

            # Create canvas and scrollbar
            details_canvas = tk.Canvas(details_container, height=250)  # Reduced from 300 to 250
            details_scrollbar = ttk.Scrollbar(details_container, orient='vertical', command=details_canvas.yview)

            # Create frame for content
            details_frame = ttk.Frame(details_canvas)
            
            # Configure scrolling
            details_canvas.configure(yscrollcommand=details_scrollbar.set)
            details_canvas.pack(side='left', fill='both', expand=True)
            details_scrollbar.pack(side='right', fill='y')
            
            # Create window in canvas with fixed width
            canvas_width = self.options_frame.winfo_width() - 50
            if canvas_width <= 0:
                canvas_width = 500
            
            details_canvas.create_window((0, 0), window=details_frame, anchor='nw', width=canvas_width)

            # Show user's answer with correctness indicator
            user_answer = self.user_answers[self.current_index]
            user_answer_display = ", ".join(user_answer) if isinstance(user_answer, list) else (user_answer or "No answer")
            
            answer_header_frame = ttk.Frame(details_frame)
            answer_header_frame.pack(anchor="w", fill='x', pady=(0, 5))
            
            ttk.Label(
                answer_header_frame, 
                text="Your Answer:", 
                font=("Helvetica", 11, "bold")
            ).pack(side="left")

            # Check if answer is correct
            is_correct = (isinstance(user_answer, list) and set(user_answer) == set(current_question['correct'])) or \
                        (not isinstance(user_answer, list) and user_answer in current_question['correct'])
            
            # Add Correct/Incorrect indicator
            tk.Label(
                answer_header_frame,
                text=" (Correct)" if is_correct else " (Incorrect)",
                font=("Helvetica", 11, "bold"),
                fg="green" if is_correct else "red"
            ).pack(side="left")
            
            ttk.Label(
                details_frame, 
                text=user_answer_display,
                font=("Helvetica", 10)
            ).pack(anchor="w", pady=(0, 10))

            # Show correct answer
            correct_answers = ", ".join(current_question['correct'])
            ttk.Label(
                details_frame, 
                text="Correct Answer(s):", 
                font=("Helvetica", 11, "bold")
            ).pack(anchor="w", pady=(0, 5))
            
            ttk.Label(
                details_frame, 
                text=correct_answers,
                font=("Helvetica", 10)
            ).pack(anchor="w", pady=(0, 10))

            # Show explanation
            ttk.Label(
                details_frame, 
                text="Explanation:", 
                font=("Helvetica", 11, "bold")
            ).pack(anchor="w", pady=(0, 5))
            
            ttk.Label(
                details_frame, 
                text=current_question.get('explanation', 'No explanation provided.'),
                font=("Helvetica", 10),
                wraplength=500,  # Slightly smaller than canvas width
                justify="left"
            ).pack(anchor="w", pady=(0, 10))

            # Update scroll region when content changes
            def configure_scroll_region(event):
                details_canvas.configure(scrollregion=details_canvas.bbox("all"))
            details_frame.bind("<Configure>", configure_scroll_region)

            # Enable mousewheel scrolling
            def on_mousewheel(event):
                details_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            details_canvas.bind_all("<MouseWheel>", on_mousewheel)

            # Unbind mousewheel when mouse leaves the canvas
            def unbind_mousewheel(event):
                details_canvas.unbind_all("<MouseWheel>")
            def bind_mousewheel(event):
                details_canvas.bind_all("<MouseWheel>", on_mousewheel)
                
            details_canvas.bind('<Enter>', bind_mousewheel)
            details_canvas.bind('<Leave>', unbind_mousewheel)

        # Update navigation buttons
        self.prev_button.config(state="normal" if self.current_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.current_index < len(self.quiz_questions) - 1 else "disabled")

    def next_question(self):
        self.save_user_answers()
        self.current_index += 1
        self.update_question()
        self.update_question_status()
        if not hasattr(self, 'quiz_submitted'):  # Only update flag button if quiz isn't submitted
            self.update_flag_button_text()

    def previous_question(self):
        self.save_user_answers()
        self.current_index -= 1
        self.update_question()
        self.update_question_status()
        if not hasattr(self, 'quiz_submitted'):  # Only update flag button if quiz isn't submitted
            self.update_flag_button_text()

    def save_user_answers(self):
        current_question = self.quiz_questions[self.current_index]
        if len(current_question['correct']) > 1:
            # Gather selected options for multiple correct answers
            self.user_answers[self.current_index] = [
                option for option, var in self.option_vars if var.get()
            ]
        else:
            # Save selected option for single correct answer
            self.user_answers[self.current_index] = self.option_vars[0].get()
        
        self.update_question_status()  # Update status immediately after saving

    def submit_quiz(self):
        """Submit the quiz and show results in the current window."""
        self.save_user_answers()
        self.stop_timer()  # Stop the timer
        self.quiz_submitted = True
        
        # Calculate score and time
        total_time = int(self.end_time - self.start_time)
        minutes, seconds = divmod(total_time, 60)
        total = len(self.quiz_questions)
        score = sum(1 for q, a in zip(self.quiz_questions, self.user_answers) 
                   if (isinstance(a, list) and set(a) == set(q['correct'])) 
                   or (not isinstance(a, list) and a in q['correct']))

        # Update tracker buttons to show correct/incorrect
        for i, (question, answer) in enumerate(zip(self.quiz_questions, self.user_answers)):
            is_correct = (isinstance(answer, list) and set(answer) == set(question['correct'])) or \
                        (not isinstance(answer, list) and answer in question['correct'])

            if is_correct:
                self.tracker_buttons[i].configure(style='Correct.TButton')
                self.create_tooltip(self.tracker_buttons[i], "Correct")
            else:
                self.tracker_buttons[i].configure(style='Incorrect.TButton')
                self.create_tooltip(self.tracker_buttons[i], "Incorrect")

        # Create and add results summary frame at the top
        self.results_frame = ttk.Frame(self.quiz_frame)
        self.results_frame.pack(before=self.center_container, fill="x", padx=20, pady=10)
        
        results_title = ttk.Label(
            self.results_frame,
            text="Quiz Results Summary",
            font=("Helvetica", 14, "bold")
        )
        results_title.pack(anchor="w", pady=(0, 10))

        score_label = ttk.Label(
            self.results_frame,
            text=f"Final Score: {score}/{total} ({score/total*100:.1f}%)",
            font=("Helvetica", 12, "bold")
        )
        score_label.pack(side="left", padx=20)

        time_label = ttk.Label(
            self.results_frame,
            text=f"Time Taken: {minutes:02d}:{seconds:02d}",
            font=("Helvetica", 12, "bold")
        )
        time_label.pack(side="left", padx=20)

        # Update timer display to be blank after submission
        self.timer_label.config(text="")
        
        # Remove the flag button and add Questions label
        self.flag_button.destroy()
        
        # Add Questions label
        self.questions_label = ttk.Label(
            self.title_frame,
            text="Questions:",
            font=("Helvetica", 11, "bold")
        )
        self.questions_label.pack(side="left", padx=5)

        # Disable submit button and options
        self.submit_button.config(state="disabled")
        
        # Resize window to show all content
        self.root.update_idletasks()  # Let the window process all changes
        required_height = self.root.winfo_reqheight() + 100  # Increased padding from 50 to 100
        current_width = self.root.winfo_width()
        
        # Get screen height
        screen_height = self.root.winfo_screenheight()
        
        # Limit height to 90% of screen height if needed
        if required_height > screen_height * 0.9:
            required_height = int(screen_height * 0.9)
        
        # Set minimum height to ensure buttons are visible
        min_height = 800  # Minimum height to ensure visibility of all elements
        required_height = max(required_height, min_height)
        
        self.root.geometry(f"{current_width}x{required_height}")
        
        # Force an update to ensure proper layout
        self.root.update()
        
        # Update current question display to show results
        self.update_question()

        # Remove the submit button completely
        self.submit_button.destroy()

        # Reduce the size of navigation buttons after grading
        style = ttk.Style()
        style.configure('GradedNav.TButton', padding=(10, 5), font=('Helvetica', 10))  # Smaller style for graded navigation
        
        self.prev_button.configure(style='GradedNav.TButton')
        self.next_button.configure(style='GradedNav.TButton')

        # After adding the time_label, add the export button
        export_button = ttk.Button(
            self.results_frame,
            text="Export Results",
            command=self.handle_export,
            style='Large.TButton'
        )
        export_button.pack(side="left", padx=20)

    def stop_timer(self):
        """Stop the timer and store end time."""
        self.end_time = time.time()
        self.root.after_cancel(self.timer_id)  # Cancel the timer update

    def update_timer(self):
        """Update the timer display."""
        if hasattr(self, 'quiz_submitted'):
            return  # Don't update if quiz is submitted
        
        elapsed_seconds = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed_seconds, 60)
        self.timer_label.config(text=f"Time Elapsed: {minutes:02d}:{seconds:02d}")
        self.timer_id = self.root.after(1000, self.update_timer)  # Store timer id for cancellation

    def update_progress(self):
        progress_text = f"Question {self.current_index + 1} of {len(self.quiz_questions)}"
        self.progress_label.config(text=progress_text)

    def setup_question_tracker(self):
        # Main container frame
        main_container = ttk.Frame(self.tracker_frame)
        main_container.pack(fill="both", expand=True)

        # Title frame at top (but don't add Questions label yet)
        self.title_frame = ttk.Frame(main_container)  # Store reference to add label later
        self.title_frame.pack(fill="x", pady=(0, 5))

        # Flag button frame at top
        flag_frame = ttk.Frame(main_container)
        flag_frame.pack(fill="x", pady=5)
        self.flag_button = ttk.Button(
            flag_frame,
            text="Flag Question",
            command=self.toggle_flag
        )
        self.flag_button.pack()

        # Scrollable frame for question buttons
        scroll_container = ttk.Frame(main_container)
        scroll_container.pack(fill="both", expand=True)

        # Create canvas and scrollbar
        canvas = tk.Canvas(scroll_container)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        
        # Create container for buttons
        self.tracker_buttons_frame = ttk.Frame(canvas)
        
        # Determine optimal number of columns
        total_questions = len(self.quiz_questions)
        if total_questions <= 95:
            questions_per_row = 5
        elif total_questions <= 114:
            questions_per_row = 6
        elif total_questions <= 133:
            questions_per_row = 7
        else:
            questions_per_row = 8

        # Calculate and set frame width
        button_width = 35
        frame_width = button_width * questions_per_row + 20
        self.tracker_frame.configure(width=frame_width)
        
        # Create question number buttons
        self.tracker_buttons = []
        for i in range(total_questions):
            row = i // questions_per_row
            col = i % questions_per_row
            
            btn = ttk.Button(
                self.tracker_buttons_frame,
                text=str(i + 1),
                width=3,
                command=lambda x=i: self.jump_to_question(x)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.tracker_buttons.append(btn)
            self.create_tooltip(btn, "Not answered yet")

        # Configure canvas with scrolling
        canvas.create_window((0, 0), window=self.tracker_buttons_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        self.tracker_buttons_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)

    def export_quiz_results(self):
        """Export quiz results to a text file including all answers and explanations."""
        try:
            # Calculate score
            total = len(self.quiz_questions)
            score = sum(1 for q, a in zip(self.quiz_questions, self.user_answers) 
                       if (isinstance(a, list) and set(a) == set(q['correct'])) 
                       or (not isinstance(a, list) and a in q['correct']))
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quiz_results_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write("Quiz Results Summary\n")
                f.write("=" * 50 + "\n\n")
                
                # Write score and time
                total_time = int(self.end_time - self.start_time)
                minutes, seconds = divmod(total_time, 60)
                f.write(f"Final Score: {score}/{total} ({score/total*100:.1f}%)\n")
                f.write(f"Time Taken: {minutes:02d}:{seconds:02d}\n\n")
                
                # Write detailed results for each question
                f.write("Detailed Question Analysis\n")
                f.write("=" * 50 + "\n\n")
                
                for i, (question, answer) in enumerate(zip(self.quiz_questions, self.user_answers), 1):
                    f.write(f"Question {i}:\n")
                    f.write(f"{question['question']}\n\n")
                    
                    # Write user's answer
                    if isinstance(answer, list):
                        user_ans = ", ".join(answer) if answer else "No answer provided"
                    else:
                        user_ans = answer if answer else "No answer provided"
                    f.write(f"Your Answer: {user_ans}\n")
                    
                    # Write correct answer
                    correct_ans = ", ".join(question['correct'])
                    f.write(f"Correct Answer: {correct_ans}\n")
                    
                    # Check if answer is correct
                    is_correct = (isinstance(answer, list) and set(answer) == set(question['correct'])) or \
                                (not isinstance(answer, list) and answer in question['correct'])
                    f.write(f"Status: {'Correct' if is_correct else 'Incorrect'}\n")
                    
                    # Write explanation
                    f.write(f"Explanation: {question.get('explanation', 'No explanation provided.')}\n")
                    f.write("\n" + "-" * 50 + "\n\n")
                
                return filename
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
            return None

    def handle_export(self):
        """Handle the export button click."""
        filename = self.export_quiz_results()
        if filename:
            if messagebox.askyesno(
                "Export Successful", 
                f"Quiz results have been exported to:\n{filename}\n\nWould you like to view the results?"
            ):
                try:
                    # Open the file with the default text editor
                    import os
                    if os.name == 'nt':  # Windows
                        os.startfile(filename)
                    else:  # macOS and Linux
                        import subprocess
                        subprocess.run(['xdg-open' if os.name == 'posix' else 'open', filename])
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open the file: {str(e)}")




if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set desired initial width and height
    app = QuizApp(root)
    root.mainloop()
