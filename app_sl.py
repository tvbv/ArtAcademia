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


# Fonction pour afficher l'historique de conversation
def render_chat_history():

    for msg in st.session_state.chat_history:

        msg_user = msg['human']
        msg_bot = msg['AI']

        try:
            # parse the JSON object
            msg_bot = json.loads(msg_bot)
            # TODO: work on the categories : confidence  /// grammarly
            # TODO 2: work on collecting the follow up questiosn
            msg_bot_confidence = msg_bot['confidence']
            msg_bot_feedback = msg_bot['feedback']
            msg_bot_follow_up = msg_bot['follow_up_question']
            msg_bot_expected_output = msg_bot['expected_output']

            with st.chat_message("user", avatar='👨‍💻'):
                st.markdown(msg["human"])
            with st.chat_message("user", avatar='🤖'):
                st.markdown(msg["AI"])
        except Exception as e:
            st.error(e, icon="🚨")


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """

    # Get Groq API key #FIXME env variable
    groq_api_key = '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'


    st.set_page_config(page_icon="💬", layout="wide",  page_title="Socrates...")
    st.title("Prepare for your interview!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")
    # TODO: SOCRATES LOGO DESIGN !!! + BACKGROUND? st.image('groqcloud_darkmode.png')

    audio_bytes = audio_recorder()

    if audio_bytes:
        # st.audio(audio_bytes, format="audio/wav") 
        # transcribed_text = transcribe(...)
    def icon(emoji: str):
        """Shows an emoji as a Notion-style page icon."""
        st.write(
            f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
            unsafe_allow_html=True,
        )

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

    SYSTEM_PROMPT = """

    You are an interviewer assisting a candidate in preparing for a technical interview and behavioral questions.
    Provide concise, structured feedback based on the user's input, making sure to express encouragement, assess their skill level, and prompt further thought. Responses should be designed to match the user's level of knowledge, with the goal of moving forward through the interview, offering hints to the user when necessary, or acknowledging their understanding positively.
    ALWAYS answer in JSON format with following keys:
    - "confidence" (expressing an assessment of their skill level or readiness) on a scale of 1 to 10 (1 being the lowest and 10 the highest). A 1 means your next question should be very basic, while a 10 means you can ask a more advanced question.
    - "tone" in the form of "Accusatory", "Unassuming", "Formal", "Assertive", "Confident", "Informal", 
    - "feedback" (if applicable, a brief suggestion for improvement or a positive remark on their understanding)
    - "follow_up_question" (a simple question to encourage further discussion or thought related to their input).
    - "expected_output" (if applicable, the expected output of the user's code or query). Should be factual and concise.

    Ensure your feedback is succinct, aiming for no more than one sentence per key to keep the response concise and to the point.
    When feedback is not necessary due to the user's proficient understanding, you might exclude detailed suggestions for improvement, opting instead for a brief acknowledgment or none at all, and adjust the follow-up question to continue the engagement effectively.

    INSTRUCTIONS
    - Craft your response as a single JSON object, including the necessary keys. Ensure each section contains no more than one sentence. Tailor your feedback and questions to accurately reflect the user's current level of expertise, avoiding details or concepts that may confuse or overwhelm them.

    EXAMPLE
    user_input: I've started using databases, and I'm familiar with basic queries.
    ideal_output: How comfortable are you with joins and subqueries?
    """

# FIXME: see Ena's prompt
#    ideal_output: {"confidence": "Moderate", "feedback": "Great start, try to explore more complex queries.", "follow_up_question": "How comfortable are you with joins and subqueries?"}

    model = 'mixtral-8x7b-32768'
    conversational_memory_length = 10 # FIXME: test whether the context length is enough

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
    # groq_chat = groq_chat.with_structured_output(Answer)

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
