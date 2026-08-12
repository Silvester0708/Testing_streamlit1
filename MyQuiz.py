from functools import reduce
import streamlit as st

class Question:
    # represent generic quiz question (parent for TextQuestion and ImageQuestion)
    def __init__(self, question_id, question_text, options, correct_answer):
        self.question_id = question_id
        self.question_text = question_text
        self.options = options # list of 4 strings
        self.correct_answer = correct_answer # letter of the correct answer (A, B, C, D)

    def display(self):
        st.write(f"**Question {self.question_id}**")
        st.write(self.question_text)

class TextQuestion(Question):
    # type A text only question
    def display(self):
        st.write(f"**Question {self.question_id}**")
        st.write(self.question_text)

class ImageQuestion(Question):
    # type B question with image
    def __init__(self, question_id, question_text, options, correct_answer, image_path):
        super().__init__(question_id, question_text, options, correct_answer)
        # path to the image file
        self.image_path = image_path  

    def display(self):
        st.write(f"**Question {self.question_id}**")
        st.image(self.image_path, width=300)
        st.write(self.question_text)

class Participant:
    # store participant's name, answers, and score
    def __init__(self, name):
        self.name = name
        self.answers = []
        self.score = 0

    def record_answer(self, selected_answer):
        self.answers.append(selected_answer)

    def set_score(self, score):
        self.score = score

class Quiz:
    # manage question bank and participants
    def __init__(self):
        self.questions = []

    def load_questions(self, filepath):
        # with file error handling
        self.questions = []  # clear existing questions

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Could not find the file '{filepath}'.")
            #return empty list and program doesnt crash
            return self.questions 
        except IOError as e:
            print(f"Error: Problem reading file '{filepath}':{e}")
            #return empty list and program doesnt crash
            return self.questions 

        for line in lines:
            line = line.strip()
            if line == "":
                # skip empty lines
                continue  

            parts = line.split(":")

            # index [0] = id, [1] = correct ans, [2]= question, [3-6] = answer options, [7] is img path
            question_id = parts[0]
            correct_answer = parts[1]
            question_text = parts[2]
            options = parts[3:7] # stop at 7
            image_path = parts[7]

            # if [7] is not empty then its image question
            if image_path.strip() != "":
                question = ImageQuestion(question_id, question_text, options, correct_answer, image_path.strip())
            else:
                question = TextQuestion(question_id, question_text, options, correct_answer)

            self.questions.append(question)
        return self.questions

    # lambda map() and reduce()
    def calculate_score(self, participant):
        # lambda map() converts each answer into 1 (correct) or 0 (incorrect)
        scores = list(map(
            lambda ans, q: 1 if ans == q.correct_answer else 0,
            participant.answers,
            self.questions
        ))
        # lambda reduce() sums up the 1s and 0s into a total score
        total = reduce(lambda x, y: x + y, scores)
        return total

    # recursive function to check if all questions are answered
    def all_questions_answered(self, participant, index=0):
        if index == len(self.questions):
            return True
        if index >= len(participant.answers):
            return False
        return self.all_questions_answered(participant, index + 1)

    def save_results(self, participant, filepath):
        # with file error handling
        try: 
            with open(filepath, "a") as f:
                # convert list to text
                answers_str = ",".join(participant.answers) 
                f.write(f"{participant.name}:{answers_str}:{participant.score}\n")
        except IOError as e:
            print(f"Error: Could not save results to '{filepath}': {e}")

    def get_correctness_list(self, participant):
        # lambda map() pair each ans with true/false
        return list(map(lambda ans, q: ans == q.correct_answer, participant.answers, self.questions))

    def count_correct(self, correctness_list):
        # lambda filter() keeps only true in the list, can return the size
        correct_only = list(filter(lambda is_correct: is_correct, correctness_list))
        return len(correct_only)

# ------------- Streamlit Config -------------
if "participant_name" not in st.session_state:
    st.session_state.participant_name = None

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "page" not in st.session_state:
    st.session_state.page = "quiz"

if "submitted" not in st.session_state:
    st.session_state.submitted = False

quiz = Quiz()
quiz.load_questions("Questions.txt")

if st.session_state.participant_name is None:
    st.title("Malaysian Food Knowledge Quiz")
    st.write("") # push down
    st.write("This quiz consists of 4 questions. Each question has 4 options, and only one option is correct. Please select the correct answer for each question. Good luck!")
    col1, col2 = st.columns([4, 1])

    with col1:
        name_input = st.text_input("Enter participant name:")

    with col2:
        st.write("")
        st.write("")
        start_clicked = st.button("Start quiz")

    if start_clicked:
        # if input is empty show warning
        if name_input.strip() == "": 
            st.warning("Please enter a name.")
        else: 
            st.session_state.participant_name = name_input.strip()
            st.session_state.participant = Participant(name_input.strip())
            st.rerun()
else:
    st.title("Malaysian Food Knowledge Quiz")
    st.divider()

    if st.session_state.page == "quiz":
        st.subheader(f"Welcome, {st.session_state.participant_name}!")

        # index using current_index to access question
        current_question = quiz.questions[st.session_state.current_index] 
        current_question.display()

        participant = st.session_state.participant
        index = st.session_state.current_index

        labels = ["A", "B", "C", "D"]
        option_display = [f"{labels[i]}. {current_question.options[i]}" for i in range(4)]

        default_index = 0
        # check if this question is answered or not
        # if bigger means answered
        if index < len(participant.answers): 
            previous_answer = participant.answers[index]
            default_index = labels.index(previous_answer)

        choice = st.radio("Select your answer:", option_display, index=default_index)
        selected_letter = labels[option_display.index(choice)]

        # space between answer and buttons (next/previous/submit)
        st.write("")
        st.write("")

        def save_answer():
            if index < len(participant.answers):
                # update existing ans
                participant.answers[index] = selected_letter 
            else:
                # append new ans
                participant.record_answer(selected_letter) 

        col1, col2 = st.columns(2)

        with col1:
            # if from 2nd question
            if index > 0: 
                if st.button("Previous"):
                    save_answer()
                    st.session_state.current_index -= 1
                    st.rerun()

        with col2:
            last_question = index == len(quiz.questions) - 1
            # space button is to push button to right side (for aesthetic reason)
            space_button, button_col = st.columns([2, 1]) 

            with button_col:
                if st.button("Next"):
                    save_answer()
                    if last_question:
                        participant.set_score(quiz.calculate_score(participant))
                        st.session_state.page = "result"
                        st.session_state.submitted = False
                    else:
                        st.session_state.current_index += 1
                    st.rerun()

    elif st.session_state.page == "result":
        participant = st.session_state.participant
        st.subheader(f"Congratulations, {participant.name}!")
        st.subheader("Quiz result")

        # score processing using lambda functions (map(), filter())
        correctness = quiz.get_correctness_list(participant)
        correct_count = quiz.count_correct(correctness)
        incorrect_count = len(quiz.questions) - correct_count

        with st.container(border=True):
            col1, col2 = st.columns([1,1])
            with col1:
                st.write("Score result:")
            with col2:
                st.markdown(f"### {participant.score}")

            st.write("")

            col3, col4 = st.columns([1, 1])
            with col3:
                st.write(f"Correct: {correct_count}")
            with col4:
                st.write(f"Incorrect: {incorrect_count}")

        st.write("")

        col_submit, col_quit = st.columns(2)

        with col_submit:
            if st.button("Submit", disabled=st.session_state.submitted):
                if quiz.all_questions_answered(participant):
                    quiz.save_results(participant, "Answers.txt")
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.error("Not all questions have been answered yet.")

        with col_quit:
            # reset to new participant (become a loop)
            if st.button("Quit", disabled=not st.session_state.submitted):
                st.session_state.participant_name = None
                st.session_state.participant = None
                st.session_state.current_index = 0
                st.session_state.page = "quiz"
                st.rerun()

        if st.session_state.submitted:
            st.success("You have submitted your answers. You can now quit the program.")
        else:
            st.warning("You need to submit your answer to quit the program.")