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


# Fonction pour ajouter un message à l'historique
def add_message(role, message):
    st.session_state.chat_history.append({"role": role, "content": message})
    render_chat_history()


# Fonction pour afficher l'historique de conversation
def render_chat_history():
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="user-message">
                    <img src="user_avatar.png" class="avatar">
                    <span>{msg["content"]}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="bot-message">
                    <img src="bot_avatar.png" class="avatar">
                    <span>{msg["content"]}</span>
                </div>
            """, unsafe_allow_html=True)



def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # Get Groq API key
    groq_api_key = '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'

    # Display the Groq logo
    # spacer, col = st.columns([5, 1])  
    # with col:  
    #     st.image('groqcloud_darkmode.png')

    # The title and greeting message of the Streamlit application
    st.title("Prepare for your interview!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # Add customization options to the sidebar
    st.sidebar.title('Interview Report')

    #system_prompt = st.sidebar.text_input("System prompt:")
    # model = st.sidebar.selectbox(
    #     'Choose a model',
    #     ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
    # )

    SYSTEM_PROMPT = """

    You are an interviewer assisting a candidate in preparing for a technical interview and behavioral questions.
    Provide concise, structured feedback based on the user's input, making sure to express encouragement, assess their skill level, and prompt further thought. Responses should be designed to match the user's level of knowledge, offering clear and relevant suggestions for improvement when necessary, or acknowledging their understanding positively. Format responses in JSON with keys for "confidence" (expressing an assessment of their skill level or readiness), "feedback" (if applicable, a brief suggestion for improvement or a positive remark on their understanding), and "follow_up_question" (a simple question to encourage further discussion or thought related to their input). Maintain a professional yet approachable tone throughout. Ensure your feedback is succinct, aiming for no more than one sentence per key to keep the response concise and to the point. When feedback is not necessary due to the user's proficient understanding, you might exclude detailed suggestions for improvement, opting instead for a brief acknowledgment or none at all, and adjust the follow-up question to continue the engagement effectively.

    INSTRUCTIONS
    - Craft your response as a single JSON object, including the necessary keys. Ensure each section contains no more than one sentence. Tailor your feedback and questions to accurately reflect the user's current level of expertise, avoiding details or concepts that may confuse or overwhelm them.

    EXAMPLE
    user_input: I've started using databases, and I'm familiar with basic queries.
    ideal_output: {"confidence": "Moderate", "feedback": "Great start, try to explore more complex queries.", "follow_up_question": "How comfortable are you with joins and subqueries?"}

    The topic of is interview is about: 
    """

    model = 'mixtral-8x7b-32768'
    # conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)
    conversational_memory_length = 10

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    user_question = st.text_input("Ask a question:")

    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            memory.save_context(
                {'input':message['human']},
                {'output':message['AI']}
                )


    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )


    # If the user has asked a question,
    if user_question:

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
            llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
            prompt=prompt,  # The constructed prompt template.
            verbose=True,   # Enables verbose output, which can be useful for debugging.
            memory=memory,  # The conversational memory object that stores and manages the conversation history.
        )
        
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        response = conversation.predict(human_input=user_question)
        message = {'human':user_question,'AI':response}
        print(message)
        st.session_state.chat_history.append(message)
        
        # TODO APPEND INSTEAD OF WRITE AND ERASE ? HOW TO INSERT ?
        # Display the user question
        st.write("You:", user_question)

        # Display the chatbot's response
        st.write("Chatbot:", response)


    # Display the chat history


if __name__ == "__main__":
    main()




