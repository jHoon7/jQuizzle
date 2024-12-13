import streamlit as st
import random
import time
import io

# Initialize session state variables
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []

if 'current_edit_index_quiz' not in st.session_state:
    st.session_state.current_edit_index_quiz = None
if 'current_edit_index_flash' not in st.session_state:
    st.session_state.current_edit_index_flash = None

# For quiz generation and running
if 'quiz_mode' not in st.session_state:
    st.session_state.quiz_mode = False
if 'flash_mode' not in st.session_state:
    st.session_state.flash_mode = False

# For quiz running state
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_current_index' not in st.session_state:
    st.session_state.quiz_current_index = 0
if 'quiz_user_answers' not in st.session_state:
    st.session_state.quiz_user_answers = []
if 'quiz_start_time' not in st.session_state:
    st.session_state.quiz_start_time = 0
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

# For flashcard deck
if 'flash_deck' not in st.session_state:
    st.session_state.flash_deck = []
if 'flash_current_index' not in st.session_state:
    st.session_state.flash_current_index = 0
if 'flash_side_question' not in st.session_state:
    st.session_state.flash_side_question = True


# -----------------------------------------------
# Helper functions
# -----------------------------------------------
def update_question_bank():
    # Just a placeholder, as Streamlit updates in real-time.
    pass

def clear_question_fields():
    st.session_state['question_input'] = ""
    st.session_state['options_input'] = ""
    st.session_state['explanation_input'] = ""
    st.session_state.current_edit_index_quiz = None

def clear_flashcard_fields():
    st.session_state['flash_question_input'] = ""
    st.session_state['flash_answer_input'] = ""
    st.session_state.current_edit_index_flash = None

def parse_options(options_str):
    lines = [l.strip() for l in options_str.strip().split("\n") if l.strip()]
    correct = [opt.lstrip("*").strip() for opt in lines if opt.startswith("*")]
    all_opts = [opt.lstrip("*").strip() for opt in lines]
    return all_opts, correct

def add_or_save_question():
    q = st.session_state.get('question_input', "").strip()
    o = st.session_state.get('options_input', "").strip()
    e = st.session_state.get('explanation_input', "").strip()
    if not q or not o:
        st.warning("Please enter a question and at least two options.")
        return
    all_opts, correct = parse_options(o)
    if len(all_opts) < 2:
        st.warning("Please enter at least two options.")
        return

    question_data = {
        "question": q,
        "options": all_opts,
        "correct": correct,
        "explanation": e if e else "No explanation provided."
    }

    if st.session_state.current_edit_index_quiz is None:
        st.session_state.questions.append(question_data)
    else:
        st.session_state.questions[st.session_state.current_edit_index_quiz] = question_data
        st.session_state.current_edit_index_quiz = None

    clear_question_fields()

def edit_question(index):
    qdata = st.session_state.questions[index]
    st.session_state.question_input = qdata['question']
    # Reconstruct options with * for correct
    opts = []
    for opt in qdata['options']:
        if opt in qdata['correct']:
            opts.append("*" + opt)
        else:
            opts.append(opt)
    st.session_state.options_input = "\n".join(opts)
    st.session_state.explanation_input = qdata['explanation']
    st.session_state.current_edit_index_quiz = index

def delete_question(index):
    del st.session_state.questions[index]

def save_question_bank():
    # Format:
    # question
    # =
    # *correct_options or options
    # ==
    # explanation
    # (blank line)
    quiz_str = io.StringIO()
    for q in st.session_state.questions:
        quiz_str.write(f"{q['question']}\n=\n")
        for opt in q['options']:
            if opt in q['correct']:
                quiz_str.write(f"*{opt}\n")
            else:
                quiz_str.write(f"{opt}\n")
        quiz_str.write("==\n")
        quiz_str.write(f"{q['explanation']}\n\n")

    st.download_button(
        "Download Quiz",
        data=quiz_str.getvalue(),
        file_name="my_quiz_quiz.txt",
        mime="text/plain"
    )

def import_quiz_file(file_content, mode):
    # mode: 'replace' or 'add'
    if mode == 'replace':
        st.session_state.questions.clear()
    content = file_content.decode('utf-8').strip()
    raw_questions = content.split("\n\n")
    for raw_q in raw_questions:
        if not raw_q.strip():
            continue
        try:
            parts = raw_q.split("\n=\n")
            if len(parts) != 2:
                continue
            question, rest = parts
            opt_exp = rest.split("\n==\n")
            options_raw = opt_exp[0] if len(opt_exp) > 0 else ""
            explanation = opt_exp[1] if len(opt_exp) > 1 else "No explanation provided."

            opts = [o.strip() for o in options_raw.split("\n") if o.strip() and o.strip() != '==']
            correct = [x.lstrip("*").strip() for x in opts if x.startswith("*")]
            all_opts = [x.lstrip("*").strip() for x in opts]

            if not question.strip() or not all_opts:
                continue

            qdata = {
                "question": question.strip(),
                "options": all_opts,
                "correct": correct,
                "explanation": explanation.strip()
            }
            st.session_state.questions.append(qdata)
        except:
            pass
    st.info("Questions imported successfully.")

def generate_quiz():
    if not st.session_state.questions:
        st.warning("No questions in the Question Bank.")
        return
    # Setup quiz
    st.session_state.quiz_questions = st.session_state.questions[:]
    random.shuffle(st.session_state.quiz_questions)
    for q in st.session_state.quiz_questions:
        q["options"] = random.sample(q["options"], len(q["options"]))
    st.session_state.quiz_user_answers = [None]*len(st.session_state.quiz_questions)
    st.session_state.quiz_current_index = 0
    st.session_state.quiz_start_time = time.time()
    st.session_state.quiz_submitted = False
    st.session_state.quiz_mode = True

def add_or_save_flashcard():
    question = st.session_state.get('flash_question_input', "").strip()
    answer = st.session_state.get('flash_answer_input', "").strip()
    if not question or not answer:
        st.warning("Please enter both a question and an answer.")
        return
    fc = {'question': question, 'answer': answer}
    if st.session_state.current_edit_index_flash is None:
        st.session_state.flashcards.append(fc)
    else:
        st.session_state.flashcards[st.session_state.current_edit_index_flash] = fc
        st.session_state.current_edit_index_flash = None
    clear_flashcard_fields()

def edit_flashcard(index):
    card = st.session_state.flashcards[index]
    st.session_state.flash_question_input = card['question']
    st.session_state.flash_answer_input = card['answer']
    st.session_state.current_edit_index_flash = index

def delete_flashcard(index):
    del st.session_state.flashcards[index]

def save_flashcard_deck():
    # question
    # =
    # answer
    # (blank line)
    fc_str = io.StringIO()
    for c in st.session_state.flashcards:
        fc_str.write(f"{c['question']}\n=\n{c['answer']}\n\n")

    st.download_button(
        "Download Deck",
        data=fc_str.getvalue(),
        file_name="my_deck_flash.txt",
        mime="text/plain"
    )

def import_flashcards(file_content, mode):
    # mode: 'replace' or 'add'
    if mode == 'replace':
        st.session_state.flashcards.clear()
    content = file_content.decode('utf-8').strip()
    raw_cards = content.split("\n\n")
    for rc in raw_cards:
        lines = rc.strip().split("\n")
        if "=" in lines:
            i = lines.index("=")
            q = "\n".join(lines[:i]).strip()
            a = "\n".join(lines[i+1:]).strip()
            if q and a:
                st.session_state.flashcards.append({'question': q, 'answer': a})
    st.info("Flashcards imported successfully.")

def generate_flash_deck():
    if not st.session_state.flashcards:
        st.warning("No flashcards in the Flashcard Deck.")
        return
    st.session_state.flash_deck = st.session_state.flashcards[:]
    random.shuffle(st.session_state.flash_deck)
    st.session_state.flash_current_index = 0
    # Ask user side - in Streamlit we can just start with question by default
    start_side = st.radio("Start with:", ["Question", "Answer"])
    st.session_state.flash_side_question = (start_side == "Question")
    st.session_state.flash_mode = True

# -----------------------------------------------
# Quiz Running Section
# -----------------------------------------------
def show_quiz():
    if st.session_state.quiz_submitted:
        show_quiz_results()
        return

    # Navigation and timer
    elapsed = int(time.time() - st.session_state.quiz_start_time)
    minutes, seconds = divmod(elapsed, 60)
    st.write(f"**Time Elapsed:** {minutes:02d}:{seconds:02d}")

    idx = st.session_state.quiz_current_index
    q = st.session_state.quiz_questions[idx]
    st.write(f"**Question {idx+1}/{len(st.session_state.quiz_questions)}:** {q['question']}")

    # Render options
    # If multiple correct answers, use multiselect
    # else use radio
    if len(q['correct']) > 1:
        selected = st.multiselect("Select all correct answers:", q['options'], default=st.session_state.quiz_user_answers[idx] if st.session_state.quiz_user_answers[idx] else [])
    else:
        selected = st.radio("Select the correct answer:", q['options'], index=q['options'].index(st.session_state.quiz_user_answers[idx]) if st.session_state.quiz_user_answers[idx] and st.session_state.quiz_user_answers[idx] in q['options'] else 0)
    
    # Save user answer on change
    if len(q['correct']) > 1:
        st.session_state.quiz_user_answers[idx] = selected
    else:
        st.session_state.quiz_user_answers[idx] = selected

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Previous", disabled=(idx == 0)):
            st.session_state.quiz_current_index -= 1
            st.experimental_rerun()
    with col2:
        if st.button("Next", disabled=(idx == len(st.session_state.quiz_questions)-1)):
            st.session_state.quiz_current_index += 1
            st.experimental_rerun()
    with col3:
        if st.button("Submit Quiz"):
            st.session_state.quiz_submitted = True
            st.experimental_rerun()

def show_quiz_results():
    elapsed = int(time.time() - st.session_state.quiz_start_time)
    minutes, seconds = divmod(elapsed, 60)
    score = 0
    total = len(st.session_state.quiz_questions)
    st.write("## Quiz Results")
    st.write(f"**Time Taken:** {minutes:02d}:{seconds:02d}")
    for i,(q,u) in enumerate(zip(st.session_state.quiz_questions, st.session_state.quiz_user_answers)):
        st.write(f"**Q{i+1}:** {q['question']}")
        if isinstance(u, list):
            user_display = ", ".join(u) if u else "No answer"
        else:
            user_display = u if u else "No answer"
        correct = ", ".join(q['correct'])

        st.write(f"**Your Answer:** {user_display}")
        st.write(f"**Correct Answer(s):** {correct}")

        normalized_user = set(ans.strip().lower() for ans in (u if isinstance(u,list) else [u]) if ans)
        normalized_correct = set(c.strip().lower() for c in q['correct'])

        if normalized_user == normalized_correct:
            st.write("**Result:** :green[Correct]")
            score += 1
        else:
            st.write("**Result:** :red[Incorrect]")
        st.write(f"**Explanation:** {q['explanation']}")
        st.write("---")

    st.write(f"**Final Score:** {score}/{total}")
    if st.button("Close Results"):
        st.session_state.quiz_mode = False
        st.experimental_rerun()


# -----------------------------------------------
# Flashcards Running Section
# -----------------------------------------------
def show_flash_deck():
    st.write(f"**Card {st.session_state.flash_current_index+1}/{len(st.session_state.flash_deck)}**")
    card = st.session_state.flash_deck[st.session_state.flash_current_index]
    if st.session_state.flash_side_question:
        st.write(card['question'])
    else:
        st.write(card['answer'])

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Previous"):
            st.session_state.flash_current_index = (st.session_state.flash_current_index - 1) % len(st.session_state.flash_deck)
            st.experimental_rerun()
    with col2:
        if st.button("Flip"):
            st.session_state.flash_side_question = not st.session_state.flash_side_question
            st.experimental_rerun()
    with col3:
        if st.button("Next"):
            st.session_state.flash_current_index = (st.session_state.flash_current_index + 1) % len(st.session_state.flash_deck)
            st.experimental_rerun()

    if st.button("Close Deck"):
        st.session_state.flash_mode = False
        st.experimental_rerun()

# -----------------------------------------------
# Main UI
# -----------------------------------------------
st.title("jQuizzle (Streamlit Version)")

# If quiz mode or flash mode is on, show those UIs and return.
if st.session_state.quiz_mode:
    show_quiz()
    st.stop()

if st.session_state.flash_mode:
    show_flash_deck()
    st.stop()

tabs = st.tabs(["Quiz", "Flashcards"])

with tabs[0]:
    st.subheader("Quiz")

    # Input section
    with st.expander("Add/Edit Question"):
        question_col, bank_col = st.columns([2,1])

        with question_col:
            st.text("Enter Question:")
            question_input = st.text_area(" ", key='question_input', height=100)

            st.text("Enter Choices (correct answers start with *)")
            options_input = st.text_area(" ", key='options_input', height=150)

            st.text("Enter Explanation:")
            explanation_input = st.text_area(" ", key='explanation_input', height=100)

            if st.session_state.current_edit_index_quiz is not None:
                btn_label = "Save Changes"
            else:
                btn_label = "Add Question"

            c1, c2 = st.columns(2)
            with c1:
                if st.button(btn_label, on_click=add_or_save_question):
                    pass
            with c2:
                if st.button("Clear", on_click=clear_question_fields):
                    pass

        with bank_col:
            st.write("Question Bank:")
            # Display question bank as a list with edit/delete options
            if st.session_state.questions:
                for i,q in enumerate(st.session_state.questions):
                    st.write(f"{i+1}. {q['question']}")
                    ed_col, del_col = st.columns([1,1])
                    with ed_col:
                        if st.button("Edit", key=f"edit_q_{i}", on_click=edit_question, args=(i,)):
                            pass
                    with del_col:
                        if st.button("Delete", key=f"del_q_{i}", on_click=delete_question, args=(i,)):
                            pass
                st.write("---")
            else:
                st.write("No questions in the bank.")

    # Import/Export/Generate Section
    st.subheader("Import/Export/Generate Quiz")

    c1,c2,c3,c4 = st.columns(4)

    with c1:
        uploaded_quiz = st.file_uploader("Import Quiz", type=["txt"], key="quiz_import")
        if uploaded_quiz:
            mode = st.radio("Import Mode", ["Replace Bank", "Add to Bank"])
            if st.button("Import", key="import_quiz"):
                import_quiz_file(uploaded_quiz.getvalue(), "replace" if mode=="Replace Bank" else "add")
                st.experimental_rerun()

    with c2:
        save_question_bank()

    with c3:
        if st.button("Generate Quiz", on_click=generate_quiz):
            st.experimental_rerun()

with tabs[1]:
    st.subheader("Flashcards")

    # Input section for flashcards
    with st.expander("Add/Edit Flashcard"):
        flash_col, deck_col = st.columns([2,1])

        with flash_col:
            st.text("Enter Question:")
            flash_q = st.text_area(" ", key='flash_question_input', height=100)
            st.text("Enter Answer:")
            flash_a = st.text_area(" ", key='flash_answer_input', height=100)

            if st.session_state.current_edit_index_flash is not None:
                flash_btn_label = "Save Changes"
            else:
                flash_btn_label = "Add Flashcard"

            c1, c2 = st.columns(2)
            with c1:
                if st.button(flash_btn_label, on_click=add_or_save_flashcard):
                    pass
            with c2:
                if st.button("Clear", on_click=clear_flashcard_fields):
                    pass

        with deck_col:
            st.write("Flashcard Deck:")
            if st.session_state.flashcards:
                for i,fc in enumerate(st.session_state.flashcards):
                    st.write(f"{i+1}. {fc['question']}")
                    ed_col, del_col = st.columns([1,1])
                    with ed_col:
                        if st.button("Edit", key=f"edit_fc_{i}", on_click=edit_flashcard, args=(i,)):
                            pass
                    with del_col:
                        if st.button("Delete", key=f"del_fc_{i}", on_click=delete_flashcard, args=(i,)):
                            pass
                st.write("---")
            else:
                st.write("No flashcards in the deck.")

    # Import/Export/Generate for flashcards
    st.subheader("Import/Export/Generate Deck")

    c1,c2,c3,c4 = st.columns(4)

    with c1:
        uploaded_fc = st.file_uploader("Import Deck", type=["txt"], key="fc_import")
        if uploaded_fc:
            mode = st.radio("Import Mode (Flashcards)", ["Replace Deck", "Add to Deck"])
            if st.button("Import Deck", key="import_fc"):
                import_flashcards(uploaded_fc.getvalue(), "replace" if mode=="Replace Deck" else "add")
                st.experimental_rerun()

    with c2:
        save_flashcard_deck()

    with c3:
        if st.button("Generate Deck", on_click=generate_flash_deck):
            st.experimental_rerun()
