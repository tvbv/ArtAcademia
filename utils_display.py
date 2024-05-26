# utils_diplay.py
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

def display_tone(tone):
    """
    Display an emoji based on the tone of the message.
    """
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
    """ displays a custom progress bar based on the value passed (is used for confidence)"""
    if value < 3:
        color = 'red'
    elif value < 6:
        color = 'yellow'
    else:
        color = 'green'

    progress_html = f"""
    <div style='width: 100%; background: lightgray; border-radius: 10px;'>
        <div style='width: {value}%; height: 10px; background: {color}; border-radius: 5px;'></div>*
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


# Fonction pour afficher l'historique de conversation
def render_chat_history(chat_history):

    for msg in chat_history:

        msg_user = msg['human']
        msg_bot = msg['AI']

        try:
            print("----------------- affichage -----------------")
            print(msg_bot)

            # parse the JSON object

            msg_bot = json.loads(msg_bot)

            # TODO: work on the categories : confidence  /// grammarly
            # TODO 2: work on collecting the follow up questiosn

            # "expected", "confidence", "feedback"

            msg_bot_confidence = msg_bot['confidence']
            msg_bot_next_question = msg_bot['next_question']
            msg_bot_expected_output = msg_bot['expected']

            with st.chat_message("user", avatar='👨‍💻'):
                st.markdown(msg["human"])

            # progress bar for the confidence level
            # with st.spinner(f"Confidence level: {msg_bot_confidence}"):
            #     st.progress(int(msg_bot_confidence)*10)
                
            custom_progress_bar(int(msg_bot_confidence)*10)
            #display_tone(msg_bot_tone)

            with st.chat_message("user", avatar='🤖'):
                st.markdown(msg_bot_next_question)

        except Exception as e:
            st.error(e, icon="🚨")