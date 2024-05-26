import os
import random
import re
import json

import streamlit as st
from audio_recorder_streamlit import audio_recorder

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

    You are assisting a candidate in preparing for a technical interview. Your task is to ask specific probing questions to make the user figure out what they know from what they don't know.
    The goal is to help users think critically about the subject and identify areas where their knowledge may need reinforcement. Start with simple questions and get more detailed and advanced.

    OUTPUT FORMAT: ONLY answer in a JSON format with the following keys: "expected", "confidence", "next_question"

    IF YOU DONT ANSWER WHITH THESE KEYS IN A JSON READABLE FORMAT YOU WILL BE PENALIZED. BE WARRY OF BAD CHARACTER FOR JSON FORMAT.

    "expected": The correct answer to the question that you would have expected from the user. Should be factual and concise.
    "confidence": Your judgement on the confidence level of the user's answer on a scale from 0 (very unconfident/insecure) to 10 (completely confident)
    "tone": the phrasing tone of the answer, can be "Accusatory", "Unassuming", "Formal", "Assertive", "Confident", "Informal"
    "question": A brief suggestion for improvement or a positive remark on their understanding, with ONE further targeted question challenging the user to further assess their comprehension. If the answer was very good before, the question should be more difficult. If the user was struggling with the answer, the next question should be related but a bit simpler.

    The user has chosen to review the following subject:
        """
    CONVERSATIONAL_MEMORY_LENGHT = 10

    # Get Groq API key #FIXME env variable
    groq_api_key = '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'

    client_groq = Groq(api_key=groq_api_key)




    st.set_page_config(page_icon="💬", layout="wide",  page_title="Socrates...")




    ### STARTING PAGE ###
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
        st.session_state.chosen_subject = None

    placeholder_button = st.empty()
    with placeholder_button:
        enter_demo = st.button("Enter the demo")
    placeholder_starting_page = st.empty()
    with placeholder_starting_page:
        st.subheader("Choose a subject to review")
        subject = st.text_input("Enter the subject here...")


    ### DEMO ENTRY ###

    # CHECK IF THE USER HAS ENTERED A SUBJECT
    if enter_demo:
        if subject:
            st.session_state.button_clicked = True
            st.session_state.chosen_subject = subject
        else:
            st.error("Please enter a subject to continue.")


    if not st.session_state.button_clicked:
        # Show starting page elements
        # Two columns: 1 for text field to choose the subject with the button to enter the demo and 1 for a file uploader to upload a file
        st.title("Welcome to Socrates!")
        # text field with a submit button to enter the demo
        # col1, col2 = st.columns([2, 1])
        # with col1:
        #     st.write("Hello! What subject to you want to review?")
        #     subject = st.text_input("Enter the subject here...")
        # with col2:
        #     uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'docx']) #TODO
        #     if uploaded_file is not None:
        #         # save the file
        #         with open("file.txt", "wb") as f:
        #             f.write(uploaded_file.read())
        #         st.write("File uploaded successfully!")

    else:
        # Clear the starting page
        placeholder_button.empty()
        placeholder_starting_page.empty()
        st.title("Prepare for your interview!")
        st.subheader("Subject: " + st.session_state.chosen_subject)
        with st.chat_message("user", avatar='🤖'):
            # TODO: replace that with the first question
            st.markdown("Hi! Can you please introduce yourself?")

        # TODO: SOCRATES LOGO DESIGN !!! + BACKGROUND? st.image('groqcloud_darkmode.png')

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



        SYSTEM_PROMPT += st.session_state.chosen_subject

        # st.write(f"Subject: {subject}")
        # Add customization options to the sidebar


        ### REPORT ###
        st.sidebar.title('Interview Report')

        # generate a button to generate the report
        generate_report = st.sidebar.button('Generate Report')
        if generate_report:
            # call function to generate the report

            generate_report_fct(chat_history = st.session_state.chat_history)


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

            # Construct a chat prompt template using various components
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content=SYSTEM_PROMPT
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

            print("response after rid of trail----------------------- \n",response)

            # response = clean_json(response)

            # print("response after clean----------------------- \n",response)

            message = {'human': user_answer, 'AI': response}

            st.session_state.chat_history.append(message)

            print(st.session_state.chat_history)

            # Display the chat sequentially
            render_chat_history(chat_history = st.session_state.chat_history)


if __name__ == "__main__":
    main()
