import streamlit as st
import os
from groq import Groq
import random

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from audio_recorder_streamlit import audio_recorder
from langchain_core.pydantic_v1 import BaseModel
import json


class Answer(BaseModel):
    '''FIXME An answer to the user question along with justification for the answer.'''
    confidence: str
    feedback: str
    follow_up_question: str
    # TODO


def display_tone(tone):
    if tone == 'Accusatory':
        st.markdown(":exclamation:", unsafe_allow_html=True)
    elif tone == 'Unassuming':
        st.markdown(":question:", unsafe_allow_html=True)
    elif tone == 'Formal':
        st.markdown(":necktie:", unsafe_allow_html=True)
    elif tone == 'Assertive':
        st.markdown(":muscle:", unsafe_allow_html=True)
    elif tone == 'Confident':
        st.markdown(":sunglasses:", unsafe_allow_html=True)
    elif tone == 'Informal':
        st.markdown(":smile:", unsafe_allow_html=True)
    else:
        # for unknown tone
        st.markdown(":grey_question:", unsafe_allow_html=True)


def custom_progress_bar(value):
    if value < 3:
        color = 'red'
    elif value < 6:
        color = 'yellow'
    else:
        color = 'green'

    progress_html = f"""
    <div style='width: 100%; background: lightgray; border-radius: 10px;'>
        <div style='width: {value}%; height: 10px; background: {color}; border-radius: 5px;'></div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

# Fonction pour afficher l'historique de conversation


def render_chat_history():

    for msg in st.session_state.chat_history:

        msg_user = msg['human']
        msg_bot = msg['AI']

        try:
            print(msg_bot)
            # parse the JSON object
            def parse_json(json_string):
                # split to get only up to the closing bracket
                return json_string.split("}")[0] + "}"
            msg_bot = parse_json(msg_bot)
            msg_bot = json.loads(msg_bot)
            # TODO: work on the categories : confidence  /// grammarly
            # TODO 2: work on collecting the follow up questiosn
            msg_bot_confidence = msg_bot['confidence']
            msg_bot_tone = msg_bot['tone']
            msg_bot_feedback = msg_bot['feedback']
            msg_bot_follow_up = msg_bot['follow_up_question']
            msg_bot_expected_output = msg_bot['expected_output']

            with st.chat_message("user", avatar='👨‍💻'):
                st.markdown(msg["human"])
            # progress bar for the confidence level
            # with st.spinner(f"Confidence level: {msg_bot_confidence}"):
            #     st.progress(int(msg_bot_confidence)*10)
            custom_progress_bar(int(msg_bot_confidence)*10)
            display_tone(msg_bot_tone)

            with st.chat_message("user", avatar='🤖'):
                st.markdown(msg_bot_follow_up)
        except Exception as e:
            st.error(e, icon="🚨")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )
def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """

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

    if enter_demo:
        if subject:
            st.session_state.button_clicked = True
            st.session_state.chosen_subject = subject
        else:
            st.error("Please enter a subject to continue.")
    if not st.session_state.button_clicked:
        # Show starting page elements
        # Two columns: 1 for text field to choose the subject with the button to enter the demo and 1 for a file uploader to upload a file
        st.title("Welcome to Socrateqzdqzds!")
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


        SYSTEM_PROMPT = """

        You are an interviewer assisting a candidate in preparing for a technical interview and behavioral questions.
        Provide concise, structured feedback based on the user's input, making sure to express encouragement, assess their skill level, and prompt further thought. Responses should be designed to match the user's level of knowledge, with the goal of moving forward through the interview, offering hints to the user when necessary, or acknowledging their understanding positively.
        ONLY answer in JSON format (starting with a { bracket and finishing with a } bracket) with following keys:
        
        - "confidence" (expressing an assessment of their skill level or readiness) on a scale of 0 to 10 (1 being the lowest and 10 the highest). A 1 means your next question should be very basic, while a 10 means you can ask a more advanced question.
        - "tone" in the form of "Accusatory", "Unassuming", "Formal", "Assertive", "Confident", "Informal"
        - "feedback" (if applicable, a brief suggestion for improvement or a positive remark on their understanding)
        - "follow_up_question" (the most important part: the follow-up question based on the judgment you have of the user response. If you feel the answer was bad, just ask a simpler question, otherwise more difficult).
        - "expected_output" (if applicable, the expected output of the follow-up question you are asking). Should be factual and concise.

        Ensure your feedback is succinct, aiming for no more than one sentence per key to keep the response concise and to the point.
        When feedback is not necessary due to the user's proficient understanding, you might exclude detailed suggestions for improvement, opting instead for a brief acknowledgment or none at all, and adjust the follow-up question to continue the engagement effectively.
        Craft your response as a single JSON object, including the necessary keys. Tailor your feedback and questions to accurately reflect the user's current level of expertise, avoiding details or concepts that may confuse or overwhelm them, and providing hints or guidance where necessary.

        The user has chosen to review the following subject:
        """
        SYSTEM_PROMPT += st.session_state.chosen_subject

        # st.write(f"Subject: {subject}")
        # Add customization options to the sidebar
        st.sidebar.title('Interview Report')

        # generate a button to generate the report
        generate_report = st.sidebar.button('Generate Report')
        if generate_report:
            # call function to generate the report
            def generate_report():
                # generate a random report
                ...
                st.sidebar.write("Report generated!")
                st.sidebar.write(st.session_state.chat_history)

            generate_report()

    # FIXME: see Ena's prompt
    #    ideal_output: {"confidence": "Moderate", "feedback": "Great start, try to explore more complex queries.", "follow_up_question": "How comfortable are you with joins and subqueries?"}

        model = 'mixtral-8x7b-32768'
        # FIXME: test whether the context length is enough
        conversational_memory_length = 10

        memory = ConversationBufferWindowMemory(
            k=conversational_memory_length, memory_key="chat_history", return_messages=True)

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
            message = {'human': user_answer, 'AI': response}
            st.session_state.chat_history.append(message)

            # Display the chat sequentially
            render_chat_history()


if __name__ == "__main__":
    main()
