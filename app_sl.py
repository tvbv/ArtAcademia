import os
import random
import re
import json

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import toml

from groq import Groq

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel

from langchain_groq import ChatGroq

from utils_prompt import clean_json, parse_json
from utils_display import display_tone, custom_progress_bar, icon, render_chat_history
from utils_report import generate_report_fct
from rag import create_rag, ask_question


class Answer(BaseModel):
    '''FIXME An answer to the user question along with justification for the answer.'''
    confidence: str
    feedback: str
    follow_up_question: str
    # TODO


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """

    MODEL = 'mixtral-8x7b-32768'

    SYSTEM_PROMPT = """
    You are assisting a candidate in preparing for a technical interview. The TOPIC the user wants  Your task is to ask specific probing questions to make the user figure out what they know from what they don't know.
    The goal is to help users think critically about the subject and identify areas where their knowledge may need reinforcement. Start with simple questions and get more detailed and advanced.

    OUTPUT FORMAT: ONLY answer in a JSON format with the following keys:

    "expected": The correct answer to the question that you would have expected from the user. Should be factual and concise.
    "confidence": Your judgement on the confidence level of the user's answer on a scale from 0 (very unconfident/insecure, usually the case for short answers with little content) to 10 (completely confident, usually a longer answer). Be critical!
    "tone": the phrasing tone of the answer, can be "Concerned", "Unassuming", "Formal", "Assertive", "Confident", "Informal"
    "question": A brief suggestion for improvement or a positive remark on their understanding, with ONE further targeted question challenging the user to further assess their comprehension. If the answer was very good before, the question should be more difficult. If the user was struggling with the answer, the next question should be related but a bit simpler.
Examples:
    ----
    1.

    The user answered the question "What is a SELECT statement used for?" with "IDK, sorry."

    Your output:
    {
        "expected": "The 'SELECT' statement is used to fetch data from a database.",
        "confidence": 0,
        "tone": "Concerned",
        "question": "No worries, let's start simple. What SQL command is used to retrieve data from a database table?"
    }

    ----
    2.

    The user answered the question "What does the SQL query SELECT * FROM employees; do?"

    Your output:
    {
        "expected": "This query retrieves all columns from the 'employees' table.",
        "confidence": 9,
        "tone": "Confindent",
        "question": "Good understanding! Can you write a SQL query that retrieves all columns from the 'employees' table where the 'age' is greater than 30?"
    }


    MAKE SURE TO ALWAYS ANSWER ONLY WITH A JSON WITH THE KEYS "expected", "confidence", "tone", "question". NEVER INCLUDE ANY MORE TEXT. BE WARRY OF BAD CHARACTER FOR JSON FORMAT (avoid at all cost \ in the text).

    The TOPIC the user wants to be asked questions on is:
        """
    CONVERSATIONAL_MEMORY_LENGHT = 10

    # Load the configuration file
    config = toml.load('config.toml')

    # Access the keys
    groq_api_key = config['GROQ']['API_KEY']

    client_groq = Groq(api_key=groq_api_key)

    st.set_page_config(page_icon="💬", layout="wide",  page_title="Socrates...")

    ### STARTING PAGE ###
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
        st.session_state.chosen_subject = None
        st.session_state.mode = None
        st.session_state.uploaded_file = None
        st.session_state.system_prompt = SYSTEM_PROMPT
        st.session_state.rag = None

    placeholder_logos = st.empty()
    with placeholder_logos:
        st.title("Welcome to Socrates!")
        st.subheader(
            "A conversational AI to help you prepare for your technical interviews!")

    col1, col2 = st.columns([1, 2])
    placeholder_columns = st.empty()
    with placeholder_columns:
        with col1:
            st.image('mistralailogo.png', width=100)
        with col2:
            st.image('socrates.png', width=100)

    placeholder_button = st.empty()
    with placeholder_button:
        enter_demo = st.button("Enter the demo")
    placeholder_starting_page = st.empty()
    with placeholder_starting_page:
        st.subheader("Choose a subject to review")
        subject = st.text_input(
            "Enter the subject here (You can assume Mixtral knows about it!)...")
    placeholder_pdf = st.empty()
    with placeholder_pdf:
        # pdf uploader
        # hash the name of the file to avoid conflicts

        uploaded_file = st.file_uploader(
            "... Or upload a university course / cool ML book directly!", type=['pdf'])
        if uploaded_file is not None:
            # hash the name of the file to avoid conflicts
            import hashlib
            m = hashlib.sha256()
            m.update(uploaded_file.name.encode())
            file_hash = m.hexdigest()
            folder_name = f"documents_{file_hash}"
            print('folder_name:', folder_name)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            else:
                st.write("File already uploaded!")

            # save the file in the documents folder (# FIXME move this to a documents_hash folder to avoid conflicts with multiple users uploading the same file name)
            with open(f"{folder_name}/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.read())
            st.write("File uploaded successfully!")

    ### DEMO ENTRY ###

    # CHECK IF THE USER HAS ENTERED A SUBJECT
    if enter_demo:
        if subject:
            st.session_state.button_clicked = True
            st.session_state.chosen_subject = subject
            st.session_state.mode = "Interview"
            st.session_state.system_prompt += st.session_state.chosen_subject

        elif uploaded_file:
            st.session_state.button_clicked = True
            st.session_state.mode = "RAG"
            # TODO summarize the subject nicely using the RAG????
            st.session_state.chosen_subject = "PDF document: " + uploaded_file.name

            # do a loading spinner while the RAG is being created
            with st.spinner("Creating the RAG..."):
                rag = create_rag(document_folder=folder_name)
                st.session_state.rag = rag
                st.success("RAG created successfully!")
            # TODO summarize it!
            st.session_state.system_prompt += ask_question(
                rag, "What is the document about? (Answer concisely in one sentence.)")
        else:
            st.error("Please enter a subject or upload a document to continue.")

    if st.session_state.button_clicked:
        # Clear the starting page
        placeholder_logos.empty()
        placeholder_columns.empty()
        placeholder_button.empty()
        placeholder_starting_page.empty()
        placeholder_pdf.empty()
        st.title("Prepare for your interview!")
        st.subheader("Subject: " + st.session_state.chosen_subject)
        with st.chat_message("user", avatar='🤖'):
            # TODO: replace that with the first question
            st.markdown("Hi! Can you please introduce yourself?")

        # TODO: see how can ask the model whether it is a written or spoken answer:
        # FIXME: need to ask the groq team to have access the private beta about the whisper model for audio transcription!!
        # audio_bytes = audio_recorder()
        # if audio_bytes:
        #     # save the audio file
        #     with open("audio.wav", "wb") as f:
        #         f.write(audio_bytes)

        #     # st.audio(audio_bytes, format="audio/wav") # audio playback for debugging
        #     # convert the audio file to text
        #     with open("audio.wav", "rb") as file:
        #         transcription = client_groq.audio.transcriptions.create(
        #             file=("audio.wav", file.read()), model="whisper-large-v3")
        #     st.write(transcription.text)

        ### REPORT ###
        st.sidebar.title('Interview Report')

        # generate a button to generate the report
        generate_report = st.sidebar.button('Generate Report')
        if generate_report:
            # call function to generate the report
            generate_report_fct(chat_history=st.session_state.chat_history)
            render_chat_history(chat_history=st.session_state.chat_history)

    # FIXME: see Ena's prompt
    #    ideal_output: {"confidence": "Moderate", "feedback": "Great start, try to explore more complex queries.", "follow_up_question": "How comfortable are you with joins and subqueries?"}

        ### MODEL DEFINITION ###

        model = MODEL

        # FIXME: test whether the context length is enough
        memory = ConversationBufferWindowMemory(
            k=CONVERSATIONAL_MEMORY_LENGHT, memory_key="chat_history", return_messages=True)

        # session state variable
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        else:
            for message in st.session_state.chat_history:
                memory.save_context(
                    {'input': message['human']},
                    {'output': message['AI']}
                )

        # Initialize Groq Langchain chat object and conversation
        groq_chat = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model,
        )

        # FIXME: ask the groq team how to structure the output of the model using a pydantic schema?
        # groq_chat = groq_chat.with_structured_output(method="json_mode")

        # If the user has asked a question,
        if user_answer := st.chat_input("Enter your prompt here..."):

            if st.session_state.mode == "Interview":

                # Construct a chat prompt template using various components
                prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content=st.session_state.system_prompt
                        ),  # This is the persistent system prompt that is always included at the start of the chat.

                        MessagesPlaceholder(
                            variable_name="chat_history"
                        ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                        HumanMessagePromptTemplate.from_template(
                            "{human_input}"
                        ),  # This template is where the user's current input will be injected into the prompt.
                    ]
                )
            else:

                user_deliveries = []
                for i in range(len(st.session_state.chat_history)):
                    if st.session_state.chat_history[i]['human']:
                        user_deliveries.append(
                            st.session_state.chat_history[i]['human'])
                    if st.session_state.chat_history[i]['AI']:
                        user_deliveries.append(
                            st.session_state.chat_history[i]['AI'])
                user_deliveries = ' ;'.join(user_deliveries)
                # RAG MODE:
                RAG_TOPIC_QUESTION = """
                Based on the following previous subjects mentioned by the user:
                
                """ + user_deliveries + """

                What would you like to ask the user about? Add quotes to the document"""

                topics = ask_question(st.session_state.rag, RAG_TOPIC_QUESTION)

                prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content=st.session_state.system_prompt + topics
                        ),  # This is the persistent system prompt that is always included at the start of the chat.

                        MessagesPlaceholder(
                            variable_name="chat_history"
                        ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                        HumanMessagePromptTemplate.from_template(
                            "{human_input}"
                        ),  # This template is where the user's current input will be injected into the prompt.
                    ]
                )

            # Create a conversation chain using the LangChain LLM (Language Learning Model)
            conversation = LLMChain(
                # The Groq LangChain chat object initialized earlier.
                llm=groq_chat,
                prompt=prompt,  # The constructed prompt template.
                # Enables verbose output, which can be useful for debugging.
                verbose=True,
                # The conversational memory object that stores and manages the conversation history.
                memory=memory,
            )
            # The chatbot's answer is generated by sending the full prompt to the Groq API.
            response = conversation.predict(human_input=user_answer)

            print("response : \n", repr(response))
            response = parse_json(response)
            print("response after rid of trail----------------------- \n", response)

            message = {'human': user_answer, 'AI': response}

            st.session_state.chat_history.append(message)

            print(st.session_state.chat_history)

            # Display the chat sequentially
            render_chat_history(chat_history=st.session_state.chat_history)


if __name__ == "__main__":
    main()
