import sys

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
        # Let this input frame fill all available space on the left
        self.flashcards_input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.flashcards_input_frame.columnconfigure(0, weight=1)
        # We'll give both question and answer rows equal weight so they share vertical space
        # Let's say question is row 1 and answer is row 3, both get weight=1:
        self.flashcards_input_frame.rowconfigure(1, weight=1)
        self.flashcards_input_frame.rowconfigure(3, weight=1)

        # Right section: Flashcard Bank Listbox
        self.flashcard_bank_frame = ttk.Frame(self.flashcards_main_frame)
        self.flashcard_bank_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        # Flashcard Question Entry Area
        self.flash_question_label = ttk.Label(self.flashcards_input_frame, text="Enter Question:")
        self.flash_question_label.grid(row=0, column=0, sticky="w")

        self.flash_question_frame = ttk.Frame(self.flashcards_input_frame)
        # Allow the question frame to expand in both directions
        self.flash_question_frame.grid(row=1, column=0, pady=5, sticky="nsew")
        self.flash_question_frame.columnconfigure(0, weight=1)
        self.flash_question_frame.rowconfigure(0, weight=1)

        self.flash_question_text = tk.Text(self.flash_question_frame, wrap="word")
        self.flash_question_text.grid(row=0, column=0, sticky="nsew")

        self.flash_question_scrollbar = ttk.Scrollbar(self.flash_question_frame, orient="vertical", command=self.flash_question_text.yview)
        self.flash_question_text.config(yscrollcommand=self.flash_question_scrollbar.set)
        # No immediate grid for scrollbar; it will appear as before when needed by toggle_scrollbars.
        # If you rely on toggle_scrollbars, leave as is. If it doesn't show automatically, place it once:
        # self.flash_question_scrollbar.grid(row=0, column=1, sticky="ns")
        # and rely on toggle_scrollbars for visibility.

        # Flashcard Answer Entry Area
        self.flash_answer_label = ttk.Label(self.flashcards_input_frame, text="Enter Answer:")
        self.flash_answer_label.grid(row=2, column=0, sticky="w")

        self.flash_answer_frame = ttk.Frame(self.flashcards_input_frame)
        # Allow the answer frame to also expand
        self.flash_answer_frame.grid(row=3, column=0, pady=5, sticky="nsew")
        self.flash_answer_frame.columnconfigure(0, weight=1)
        self.flash_answer_frame.rowconfigure(0, weight=1)

        self.flash_answer_text = tk.Text(self.flash_answer_frame, wrap="word")
        self.flash_answer_text.grid(row=0, column=0, sticky="nsew")

        self.flash_answer_scrollbar = ttk.Scrollbar(self.flash_answer_frame, orient="vertical", command=self.flash_answer_text.yview)
        self.flash_answer_text.config(yscrollcommand=self.flash_answer_scrollbar.set)
        # If needed, grid the scrollbar once and rely on toggling:
        # self.flash_answer_scrollbar.grid(row=0, column=1, sticky="ns")

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

        # Buttons for Flashcard Bank actions
        self.delete_flash_button = ttk.Button(self.flashcard_bank_frame, text="Delete Flashcard", command=self.delete_flashcard)
        self.delete_flash_button.grid(row=2, column=0, pady=5, sticky="w")
        self.save_flash_button = ttk.Button(self.flashcard_bank_frame, text="Save Deck", command=self.save_flashcard_bank)
        self.save_flash_button.grid(row=2, column=1, pady=5, sticky="e")
        self.import_flash_button = ttk.Button(self.flashcard_bank_frame, text="Import Deck", command=self.import_flashcard_bank)
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
        """Save the flashcard bank where questions and answers are separated by '=' and cards are separated by an empty line."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Flashcard files", "*.txt")],
        )
        if not file_path:
            return  # If no file is selected, exit the function

        # Add '_flash' before the file extension if not already present
        if not file_path.endswith("_flash.txt"):
            file_path = file_path.replace(".txt", "_flash.txt")

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for card in self.flashcards:
                    question = card['question']
                    answer = card['answer']
                    file.write(f"{question}\n=\n{answer}\n\n")  # Use '=' to separate question and answer, and an empty line for each card

                messagebox.showinfo("Save Successful", "Flashcards have been saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the flashcards:\n{e}")






    def import_flashcard_bank(self):
        """Import flashcards with the option to add or replace the current deck."""
        file_path = filedialog.askopenfilename(filetypes=[("Flashcard files", "*.txt")])
        if not file_path:
            return  # Exit if no file is selected

        def process_import(replace):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read().strip()

                # Split flashcards using a single empty line
                raw_cards = content.split("\n\n")

                if replace:
                    self.flashcards.clear()  # Replace the current deck

                for raw_card in raw_cards:
                    lines = raw_card.strip().split("\n")
                    if "=" in lines:
                        delimiter_index = lines.index("=")
                        question = "\n".join(lines[:delimiter_index]).strip()
                        answer = "\n".join(lines[delimiter_index + 1:]).strip()
                        if question and answer:
                            self.flashcards.append({'question': question, 'answer': answer})

                self.update_flashcard_bank()
                messagebox.showinfo("Import Successful", "Flashcards have been imported successfully.")
            except Exception as e:
                messagebox.showerror("Import Error", f"An error occurred while importing the flashcards:\n{e}")

        if self.flashcards:
            # Prompt user to choose add or replace
            popup = tk.Toplevel(self.root)
            popup.title("Import Flashcards")
            popup.geometry("300x150")

            label = ttk.Label(popup, text="What would you like to do with the imported deck?")
            label.pack(pady=10)

            replace_button = ttk.Button(popup, text="Replace Deck", command=lambda: [process_import(True), popup.destroy()])
            replace_button.pack(pady=5)

            add_button = ttk.Button(popup, text="Add to Deck", command=lambda: [process_import(False), popup.destroy()])
            add_button.pack(pady=5)

            cancel_button = ttk.Button(popup, text="Cancel", command=popup.destroy)
            cancel_button.pack(pady=5)
        else:
            # If no current deck, directly process the import
            process_import(True)





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
        self.add_button.config(text="Save Changes")
    
        # Hide the "Clear" button while editing
        self.clear_button.grid_remove()

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

        self.add_button.config(text="Add Question")  # Reset the add button text
        self.current_edit_index = None  # Reset the editing index


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
        """Save the question bank in the specified format."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Quiz files", "*.txt")],
        )
        if not file_path:
            return  # If no file is selected, exit the function

        # Add '_quiz' before the file extension if not already present
        if not file_path.endswith("_quiz.txt"):
            file_path = file_path.replace(".txt", "_quiz.txt")

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
        file_path = filedialog.askopenfilename(filetypes=[("Quiz files", "*.txt")])
        if file_path:
            if not self.questions:
                # Directly call the import method with replacement
                self.import_question_bank(file_path, replace=True)
            else:
                # Show the import options popup if there are existing questions
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

    def import_question_bank(self, file_path, replace, popup=None):
        """Import question bank from a file."""
        if replace:
            self.questions.clear()

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            # Split questions using a single empty line
            raw_questions = content.split("\n\n")
            for raw_question in raw_questions:
                try:
                    parts = raw_question.split("\n=\n")
                    if len(parts) != 2:
                        raise ValueError(f"Malformed question: {raw_question}")

                    question, rest = parts
                    options_and_explanation = rest.split("\n==\n")
                    options_raw = options_and_explanation[0] if len(options_and_explanation) > 0 else ""
                    explanation = options_and_explanation[1] if len(options_and_explanation) > 1 else "No explanation provided."

                    # Process options, excluding `==`
                    options = [opt.strip() for opt in options_raw.split("\n") if opt.strip() and opt != "=="]
                    correct = [opt.lstrip("*").strip() for opt in options if opt.startswith("*")]
                    all_options = [opt.lstrip("*").strip() for opt in options]

                    if not question.strip() or not all_options:
                        raise ValueError(f"Missing question or options: {raw_question}")

                    self.questions.append(
                        {
                            "question": question.strip(),
                            "options": all_options,
                            "correct": correct,
                            "explanation": explanation.strip(),
                        }
                    )
                except Exception as e:
                    print(f"Error importing question: {e}")  # Debug: Print specific error

            # Debug: Print imported questions for verification
            print("Imported Questions:", self.questions)  # Debug Statement

            self.update_question_bank()
            if popup:
                popup.destroy()
            messagebox.showinfo("Import Successful", "Questions have been imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred while importing the quiz:\n{e}")



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
        self.quiz_window.protocol("WM_DELETE_WINDOW", self.on_quiz_close)  # Link to on_quiz_close
        QuizRunner(self.quiz_window, quiz_questions)


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
        self.add_flash_button.config(text="Save Changes")

        # Hide the "Clear" button while editing
        self.clear_flash_button.grid_remove()


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

        # Shuffle the flashcards
        random.shuffle(self.flashcards)

        # Prompt user to choose starting side
        start_side = messagebox.askquestion(
            "Starting Side",
            "Do you want to start with the questions? (Click 'Yes' for Questions, 'No' for Answers)",
        )

        self.start_with_question = start_side == "yes"

        # Create the Flashcard Viewer Window
        self.deck_window = tk.Toplevel(self.root)
        self.deck_window.title("Flashcard Deck")

        self.current_flashcard_index = 0

        self.flashcard_label = ttk.Label(self.deck_window, text="", wraplength=400, anchor="center", justify="center")
        self.flashcard_label.pack(pady=20)

        # Card Tracker
        self.card_tracker_label = ttk.Label(self.deck_window, text="")
        self.card_tracker_label.pack(pady=10)

        self.flip_button = ttk.Button(self.deck_window, text="Flip", command=self.flip_flashcard)
        self.flip_button.pack(pady=10)

        self.deck_navigation_frame = ttk.Frame(self.deck_window)
        self.deck_navigation_frame.pack(pady=10)

        self.prev_card_button = ttk.Button(self.deck_navigation_frame, text="Previous", command=self.previous_flashcard)
        self.prev_card_button.grid(row=0, column=0, padx=10)

        self.next_card_button = ttk.Button(self.deck_navigation_frame, text="Next", command=self.next_flashcard)
        self.next_card_button.grid(row=0, column=1, padx=10)

        self.update_flashcard_view()

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

        # Set a static grid layout for the quiz window
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

        # Set a fixed size for the quiz window
        self.root.geometry("800x400")
        
        # Create the question label without a fixed wraplength initially
        self.question_label = ttk.Label(
            self.root,
            text="",
            anchor="center",
            justify="center",
            font=("Helvetica", 18, "bold")
        )
        self.question_label.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

        # Bind the <Configure> event to dynamically update wraplength
        self.root.bind("<Configure>", self.on_resize)

        self.options_frame = ttk.Frame(self.root)
        # Options in the center
        self.options_frame.grid(row=2, column=0, columnspan=3, pady=10)

        # To support multiple or single choice answers dynamically
        self.option_vars = []  # Stores variables for Checkbuttons or Radiobuttons

        self.navigation_frame = ttk.Frame(self.root)
          # Navigation Buttons in the center
        self.navigation_frame.grid(row=4, column=0, columnspan=3, pady=10)

        self.prev_button = ttk.Button(self.navigation_frame, text="Previous", command=self.previous_question)
        self.prev_button.grid(row=0, column=0, padx=10)

        self.next_button = ttk.Button(self.navigation_frame, text="Next", command=self.next_question)
        self.next_button.grid(row=0, column=1, padx=10)

        self.submit_button = ttk.Button(self.root, text="Submit Quiz", command=self.submit_quiz)
        # Submit Quiz Button - Bottom-Right Corner
        self.submit_button.grid(row=3, column=2, padx=10, pady=10, sticky="se")

    
        self.update_question()
        


        # Timer variables
        self.start_time = time.time()  # Record the start time in seconds
        self.timer_label = ttk.Label(self.root, text="Time Elapsed: 00:00", anchor="center", justify="center")
        # Time Elapsed Timer - Top-Left Corner
        self.timer_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
    
        self.update_timer()

        # Progress tracker variables
        self.progress_label = ttk.Label(self.root, text="")
        # Progress Tracker - Bottom-Left Corner
        self.progress_label.grid(row=3, column=0, padx=10, pady=10, sticky="sw")
        
        
        self.update_progress()

    def on_resize(self, event):
        # Get the current width of the root window
        current_width = self.root.winfo_width()
        
        # Set wraplength to slightly less than the current width to allow margins
        # Adjust the subtraction as needed for desired margins
        self.question_label.configure(wraplength=current_width - 100)

    def update_question(self):
        current_question = self.quiz_questions[self.current_index]
        self.question_label.config(text=f"Q{self.current_index + 1}: {current_question['question']}")

        # Clear the options frame
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Dynamically create options (Radiobuttons or Checkbuttons based on the question)
        self.option_vars = []
        if len(current_question['correct']) > 1:
            # Use Checkbuttons for multiple correct answers
            for option in current_question['options']:
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(self.options_frame, text=option, variable=var)
                cb.pack(anchor="w", padx=10, pady=2)
                self.option_vars.append((option, var))
        else:
            # Use Radiobuttons for single correct answer
            var = tk.StringVar(value="")
            for option in current_question['options']:
                rb = ttk.Radiobutton(self.options_frame, text=option, variable=var, value=option)
                rb.pack(anchor="w", padx=10, pady=2)
            self.option_vars.append(var)

        # Restore user's previous answer
        if len(current_question['correct']) > 1:
            for option, var in self.option_vars:
                if self.user_answers[self.current_index] and option in self.user_answers[self.current_index]:
                    var.set(True)
        else:
            if self.user_answers[self.current_index]:
                self.option_vars[0].set(self.user_answers[self.current_index])

        self.prev_button.config(state="normal" if self.current_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.current_index < len(self.quiz_questions) - 1 else "disabled")

    def next_question(self):
        self.save_user_answers()
        self.current_index += 1
        self.update_question()
        self.update_progress()

    def previous_question(self):
        self.save_user_answers()
        self.current_index -= 1
        self.update_question()
        self.update_progress()

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

    def submit_quiz(self):
        self.save_user_answers()  # Ensure the last question's answers are saved
        self.stop_timer()  # Stop the timer
        total_time = int(time.time() - self.start_time)  # Calculate total time taken

        # Create a results window
        result_window = tk.Toplevel(self.root)
        result_window.title("Quiz Results")
        result_window.geometry("1200x600")  # Fixed size for the results window

        # Configure the results display area
        canvas = tk.Canvas(result_window)
        scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable scrolling with the mouse wheel
        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows and macOS
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))  # For Linux (scroll up)
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))  # For Linux (scroll down)


        # Define styling
        heading_font = ("Helvetica", 11, "bold")  # Reduced size by 1
        text_font = ("Helvetica", 10)
        question_spacing = 15  # Space between questions

        # Add results
        score = 0
        total = len(self.quiz_questions)
        row_counter = 0

        tk.Label(
            scrollable_frame,
            text="Quiz Results",
            font=("Helvetica", 14, "bold"),
            anchor="w",
        ).grid(row=row_counter, column=0, columnspan=2, pady=(10, 20), sticky="w")
        row_counter += 1

        for idx, (question, user_answer) in enumerate(zip(self.quiz_questions, self.user_answers)):
            correct_answers = ", ".join(question['correct'])
            explanation = question.get('explanation', "No explanation provided.").strip()

            # Question heading
            tk.Label(
                scrollable_frame,
                text=f"Q{idx + 1}: {question['question']}",
                font=heading_font,
                anchor="w",
                wraplength=1100,
            ).grid(row=row_counter, column=0, columnspan=2, sticky="w", pady=(0, 5))
            row_counter += 1

            # User's answer
            user_answer_display = (
                ", ".join(user_answer) if isinstance(user_answer, list) else user_answer
            )
            tk.Label(
                scrollable_frame, text="Your Answer:", font=heading_font, anchor="w"
            ).grid(row=row_counter, column=0, sticky="w")
            tk.Label(
                scrollable_frame, text=f"{user_answer_display or 'No answer'}", font=text_font, anchor="w"
            ).grid(row=row_counter, column=1, sticky="w")
            row_counter += 1

            # Correct answer(s)
            tk.Label(
                scrollable_frame, text="Correct Answer(s):", font=heading_font, anchor="w"
            ).grid(row=row_counter, column=0, sticky="w")
            tk.Label(
                scrollable_frame, text=f"{correct_answers}", font=text_font, anchor="w"
            ).grid(row=row_counter, column=1, sticky="w")
            row_counter += 1

            # Result
            # Normalize user answers and correct answers for comparison
            normalized_user_answer = set(
                [ans.strip().lower() for ans in user_answer] if isinstance(user_answer, list) else [user_answer.strip().lower()]
            )
            normalized_correct_answer = set([ans.strip().lower() for ans in question['correct']])

            if normalized_user_answer == normalized_correct_answer:
                score += 1
                result_text = "Correct"
                result_color = "green"
            else:
                result_text = "Incorrect"
                result_color = "red"


            tk.Label(
                scrollable_frame, text="Result:", font=heading_font, anchor="w"
            ).grid(row=row_counter, column=0, sticky="w")
            tk.Label(
                scrollable_frame,
                text=result_text,
                font=(heading_font[0], heading_font[1], "bold"),
                fg=result_color,  # Set text color
                anchor="w",
            ).grid(row=row_counter, column=1, sticky="w")
            row_counter += 1


            # Explanation
            tk.Label(
                scrollable_frame, text="Explanation:", font=heading_font, anchor="w"
            ).grid(row=row_counter, column=0, sticky="nw")
            tk.Label(
                scrollable_frame,
                text=f"{explanation}",
                font=text_font,
                wraplength=1100,
                anchor="w",
                justify="left",
            ).grid(row=row_counter, column=1, sticky="w")
            row_counter += 1

            # Add spacing between questions
            tk.Label(scrollable_frame, text="", font=text_font).grid(
                row=row_counter, column=0, pady=question_spacing
            )
            row_counter += 1

        # Final score and time
        tk.Label(
            scrollable_frame, text=f"Final Score: {score}/{total}", font=heading_font, anchor="w"
        ).grid(row=row_counter, column=0, columnspan=2, pady=(20, 5), sticky="w")
        row_counter += 1

        minutes, seconds = divmod(total_time, 60)
        tk.Label(
            scrollable_frame,
            text=f"Time Taken: {minutes:02d}:{seconds:02d}",
            font=heading_font,
            anchor="w",
        ).grid(row=row_counter, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # Ensure quiz window closes when results window is closed
        result_window.protocol(
            "WM_DELETE_WINDOW", lambda: self.on_results_close(result_window)
        )





    def on_results_close(self, result_window):
        result_window.destroy()
        self.root.destroy()  # Close the quiz window
        app.root.deiconify()  # Show the main application window

    def update_timer(self):
        elapsed_seconds = int(time.time() - self.start_time)  # Calculate elapsed time
        minutes, seconds = divmod(elapsed_seconds, 60)
        self.timer_label.config(text=f"Time Elapsed: {minutes:02d}:{seconds:02d}")
        self.root.after(1000, self.update_timer)  # Schedule the next update

    def stop_timer(self):
        self.end_time = time.time()  # Record the end time if needed

    def update_progress(self):
        progress_text = f"Question {self.current_index + 1} of {len(self.quiz_questions)}"
        self.progress_label.config(text=progress_text)



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set desired initial width and height
    app = QuizApp(root)
    root.mainloop()
