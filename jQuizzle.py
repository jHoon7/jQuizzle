import sys
import csv
import io

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
        style.configure('Answered.TButton', background='green')
        style.configure('Flagged.TButton', background='yellow')

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

        # Shuffle the flashcards
        random.shuffle(self.flashcards)

        # Prompt user to choose starting side
        start_side = messagebox.askquestion(
            "Starting Side",
            "Do you want to start with the questions? (Click 'Yes' for Questions, 'No' for Answers)"
        )

        self.start_with_question = start_side == "yes"

        # Create the Flashcard Viewer Window
        self.deck_window = tk.Toplevel(self.root)
        self.deck_window.title("Flashcard Deck")
        self.deck_window.geometry("800x600")  # Make the deck window larger

        # Bind the resize event to dynamically adjust wrap length
        self.deck_window.bind("<Configure>", self.on_deck_resize)

        self.current_flashcard_index = 0

        # Increase font size
        self.flashcard_label = ttk.Label(self.deck_window, text="", font=("Helvetica", 24), anchor="center", justify="center")
        self.flashcard_label.pack(pady=20, expand=True, fill="both")

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
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)

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
        content_container = ttk.Frame(self.quiz_frame)
        content_container.pack(expand=True, fill="both")

        # Timer at top right
        self.timer_label = ttk.Label(content_container, text="Time Elapsed: 00:00")
        self.timer_label.pack(anchor="ne", padx=20, pady=10)

        # Center container for question and options
        center_container = ttk.Frame(content_container)
        center_container.pack(expand=True, fill="both", padx=50)  # Added horizontal padding

        # Question
        question_frame = ttk.Frame(center_container)
        question_frame.pack(fill="x", pady=20)
        
        self.question_label = ttk.Label(
            question_frame,
            text="",
            wraplength=600,
            justify="left",
            font=("Helvetica", 12, "bold")
        )
        self.question_label.pack(anchor="w")  # Align to left

        # Options
        self.options_frame = ttk.Frame(center_container)
        self.options_frame.pack(fill="x", pady=20)

        # Navigation buttons at bottom
        nav_frame = ttk.Frame(content_container)
        nav_frame.pack(fill="x", pady=20)
        
        # Center the Previous/Next buttons
        nav_buttons = ttk.Frame(nav_frame)
        nav_buttons.pack(expand=True)
        
        self.prev_button = ttk.Button(nav_buttons, text="Previous", command=self.previous_question)
        self.prev_button.pack(side="left", padx=5)
        
        self.next_button = ttk.Button(nav_buttons, text="Next", command=self.next_question)
        self.next_button.pack(side="left", padx=5)
        
        # Submit button in bottom right corner
        self.submit_button = ttk.Button(content_container, text="Submit Quiz", command=self.submit_quiz)
        self.submit_button.pack(side="bottom", anchor="se", padx=20, pady=10)

    def update_question_status(self):
        """Update the visual status of question tracker buttons."""
        for i, btn in enumerate(self.tracker_buttons):
            if i in self.flagged_questions:
                btn.configure(style='Flagged.TButton')
                tooltip_text = "Flagged for review"
            elif self.user_answers[i] and self.user_answers[i] != "":  # Check if actually answered
                btn.configure(style='Answered.TButton')
                tooltip_text = "Answered"
            else:
                btn.configure(style='Unanswered.TButton')
                tooltip_text = "Not answered yet"
            
            # Update tooltip
            self.create_tooltip(btn, tooltip_text)

    def toggle_flag(self):
        """Toggle the flagged status of the current question."""
        if self.current_index in self.flagged_questions:
            self.flagged_questions.remove(self.current_index)
            self.flag_button.configure(text="Flag Question")
        else:
            self.flagged_questions.add(self.current_index)
            self.flag_button.configure(text="Unflag Question")
        self.update_question_status()

    def jump_to_question(self, index):
        """Jump to a specific question when clicking its number."""
        self.save_user_answers()
        self.current_index = index
        self.update_question()

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

        self.update_question_status()
        # Update flag button text based on current question's status
        if self.current_index in self.flagged_questions:
            self.flag_button.configure(text="Unflag Question")
        else:
            self.flag_button.configure(text="Flag Question")

    def next_question(self):
        self.save_user_answers()
        self.current_index += 1
        self.update_question()
        self.update_question_status()

    def previous_question(self):
        self.save_user_answers()
        self.current_index -= 1
        self.update_question()
        self.update_question_status()

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
        """Submit the quiz and show results."""
        self.save_user_answers()
        self.stop_timer()
        total_time = int(time.time() - self.start_time)
        minutes, seconds = divmod(total_time, 60)

        # Store the initial window position
        self.last_window_pos = None

        def create_results_window(page=0):
            # Calculate total questions first
            total = len(self.quiz_questions)
            QUESTIONS_PER_PAGE = 100
            start_idx = page * QUESTIONS_PER_PAGE
            end_idx = min(start_idx + QUESTIONS_PER_PAGE, total)
            total_pages = (total - 1) // QUESTIONS_PER_PAGE + 1

            # Calculate score (all in one line to avoid indentation issues)
            score = sum(1 for q, a in zip(self.quiz_questions, self.user_answers) if (isinstance(a, list) and set(a) == set(q['correct'])) or (not isinstance(a, list) and a in q['correct']))

            # Create results window
            result_window = tk.Toplevel(self.root)
            result_window.title(f"Quiz Results - Page {page + 1} of {total_pages}")
            result_window.geometry("1200x800")

            # If we have a stored position, use it
            if self.last_window_pos:
                result_window.geometry(f"+{self.last_window_pos[0]}+{self.last_window_pos[1]}")

            # Create main container
            main_container = ttk.Frame(result_window)
            main_container.pack(fill="both", expand=True)

            # Create stats frame at top
            stats_frame = ttk.Frame(main_container)
            stats_frame.pack(fill="x", padx=20, pady=10)

            # Add title and stats
            ttk.Label(
                stats_frame,
                text=f"Quiz Results Summary (Questions {start_idx + 1}-{end_idx} of {total})",
                font=("Helvetica", 14, "bold")
            ).pack(anchor="w", pady=(0, 10))

            stats_info = ttk.Frame(stats_frame)
            stats_info.pack(fill="x")

            ttk.Label(
                stats_info,
                text=f"Final Score: {score}/{total} ({score/total*100:.1f}%)",
                font=("Helvetica", 12, "bold")
            ).pack(side="left", padx=20)

            ttk.Label(
                stats_info,
                text=f"Time Taken: {minutes:02d}:{seconds:02d}",
                font=("Helvetica", 12, "bold")
            ).pack(side="left", padx=20)

            ttk.Separator(main_container, orient="horizontal").pack(fill="x", pady=10)

            # Create scrollable frame for questions
            scroll_frame = ttk.Frame(main_container)
            scroll_frame.pack(fill="both", expand=True, padx=20)

            canvas = tk.Canvas(scroll_frame)
            scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
            results_frame = ttk.Frame(canvas)

            # Display questions for current page
            for idx in range(start_idx, end_idx):
                q_frame = ttk.Frame(results_frame)
                q_frame.pack(fill="x", pady=10)

                question = self.quiz_questions[idx]
                user_answer = self.user_answers[idx]

                ttk.Label(
                    q_frame,
                    text=f"Q{idx + 1}: {question['question']}",
                    font=("Helvetica", 11, "bold"),
                    wraplength=1000
                ).pack(anchor="w")

                # User's answer
                user_answer_display = ", ".join(user_answer) if isinstance(user_answer, list) else (user_answer or "No answer")
                ttk.Label(q_frame, text="Your Answer:", font=("Helvetica", 11, "bold")).pack(anchor="w")
                ttk.Label(q_frame, text=user_answer_display, font=("Helvetica", 10)).pack(anchor="w")

                # Correct answer
                correct_answers = ", ".join(question['correct'])
                ttk.Label(q_frame, text="Correct Answer(s):", font=("Helvetica", 11, "bold")).pack(anchor="w")
                ttk.Label(q_frame, text=correct_answers, font=("Helvetica", 10)).pack(anchor="w")

                # Result
                is_correct = (isinstance(user_answer, list) and set(user_answer) == set(question['correct'])) or \
                           (not isinstance(user_answer, list) and user_answer in question['correct'])
                
                result_text = "Correct" if is_correct else "Incorrect"
                result_color = "green" if is_correct else "red"

                ttk.Label(q_frame, text="Result:", font=("Helvetica", 11, "bold")).pack(anchor="w")
                tk.Label(
                    q_frame,
                    text=result_text,
                    font=("Helvetica", 11, "bold"),
                    fg=result_color
                ).pack(anchor="w")

                # Explanation
                ttk.Label(q_frame, text="Explanation:", font=("Helvetica", 11, "bold")).pack(anchor="w")
                ttk.Label(
                    q_frame,
                    text=question.get('explanation', 'No explanation provided.'),
                    font=("Helvetica", 10),
                    wraplength=1000
                ).pack(anchor="w")

                ttk.Separator(results_frame, orient="horizontal").pack(fill="x", pady=5)

            # Configure scrolling
            canvas.create_window((0, 0), window=results_frame, anchor="nw")
            results_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Navigation buttons
            nav_frame = ttk.Frame(main_container)
            nav_frame.pack(fill="x", pady=10)

            if page > 0:
                ttk.Button(
                    nav_frame,
                    text="← Previous Page",
                    command=lambda: [store_pos(), create_results_window(page - 1)]
                ).pack(side="left", padx=20)

            ttk.Label(
                nav_frame,
                text=f"Page {page + 1} of {total_pages}",
                font=("Helvetica", 10)
            ).pack(side="left", expand=True)

            if end_idx < total:
                ttk.Button(
                    nav_frame,
                    text="Next Page →",
                    command=lambda: [store_pos(), create_results_window(page + 1)]
                ).pack(side="right", padx=20)

            def store_pos():
                self.last_window_pos = (result_window.winfo_x(), result_window.winfo_y())
                result_window.destroy()

            def on_window_close():
                self.last_window_pos = None
                self.on_results_close(result_window)

            result_window.protocol("WM_DELETE_WINDOW", on_window_close)

        # Start with first page
        create_results_window(0)





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

    def setup_question_tracker(self):
        """Set up the question tracker panel with adaptive columns and scrolling."""
        # Main container frame
        main_container = ttk.Frame(self.tracker_frame)
        main_container.pack(fill="both", expand=True)

        # Title frame at top
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(title_frame, text="Questions:").pack(side="left", padx=5)

        # Flag button frame at top (below title)
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



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set desired initial width and height
    app = QuizApp(root)
    root.mainloop()
