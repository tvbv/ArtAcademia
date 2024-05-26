# utils_report.py

import os
import random
import re
import json

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline

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


def generate_report_fct(chat_history):
                # generate a random report
                pointer = get_pointer(chat_history)
                plot_DK_curve(chat_history)
                st.sidebar.write("Report generated!")
                st.sidebar.markdown("A small tip for you :" + pointer)
                st.sidebar.image('./DK_curve.png')

                #st.sidebar.write(st.session_state.chat_history)


def text_analysis(human_msg):
    """Generates a pointer for the user's message based on the model response."""

    client = Groq(
        api_key='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',
    )

    system_prompt = '''you are a world class expert on communication on technical aspect. You are a jury rating the quality of delivery of the user. You HAVE TO GIVE one pointer to bring the delivery to the best level possible to a knowledgeable audience.
    
    EXAMPLE:
        user_input: i like innputs and girls, but i prefer blokes.
        output : Main point: your message is not clear you should refine the main message that you want to convey. 

        The output MUST be a SINGLE sentence.'''

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": human_msg
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=2*128,
    )

    return chat_completion.choices[0].message.content


def get_pointer(chat_history):

    user_deliveries = []
    for i in range(len(chat_history)):
        user_deliveries.append(chat_history[i]['human'])
    user_deliveries = ' ;'.join(user_deliveries)

    return text_analysis(user_deliveries)


def get_similarity_rating(human_msg, ai_msg):
    """Generates a similarity rating between two sentences."""

    client = Groq(
        api_key='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',
    )

    system_prompt = '''you are a jury rating on an integer scale from 0 to 10 the similarity in meaning of the two sentences that i am going to give you. Your aim is only to output a number between 0 and 10.
    INSTRUCTIONS: You will output the integer rating in the following pattern: "0-10".
    
    EXAMPLE:
        user_input: Sentence 1): i like apples ; Sentence 2): the sky is blue
        ideal_output: 0
    IMPORTANT: The output must be a number between 0 and 10 in the pattern "0". IF YOU START THE MESSAGE WITH ANYTHING ELSE THAN NUMBERS, YOU WILL BE KILLED.'''

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "Sentence 1): " + human_msg + " Sentence 2): " + ai_msg
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=3,
    )
    msg = chat_completion.choices[0].message.content
    def is_number_with_newline(input_string):
        return bool(re.match(r'^\d', input_string))

    if not is_number_with_newline(msg):
        print(msg)
        chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "Sentence 1): " + human_msg + " Sentence 2): " + ai_msg + " JUST OUTPUT THE NUMBER :"
            }
        ],
        model="mixtral-8x7b-32768",
        max_tokens=3,
        )
        msg = chat_completion.choices[0].message.content
        print(msg)

    return int(float(msg))


def plot_DK_curve(chat_history):
    # Define the points
    x_points = np.array([0, 2, 3.5, 10])
    y_points = np.array([0, 8, 4, 10])

    # Create a cubic spline interpolation
    cspl = CubicSpline(x_points, y_points, bc_type='clamped')

    # Generate x values for the full range
    x = np.linspace(0, 10, 500)
    y = cspl(x)

    # Ensure the y values stay within the range [0, 10]

    dk_dict = {"rating": [], "confidence": []}
    for i in range(len(chat_history)-1):
        human_msg = chat_history[i+1]['human']
        ai_msg = json.loads(chat_history[i]['AI'])["expected"]
        rating = get_similarity_rating(human_msg, ai_msg)
        dk_dict['rating'].append(int(rating))
        confidence = json.loads(chat_history[i+1]['AI'])["confidence"]
        dk_dict['confidence'].append(int(confidence))

    # Plotting
    plt.figure(figsize=(10, 6),facecolor='gray')
    plt.plot(dk_dict['rating'], dk_dict['confidence'], 'o', color='orange', markersize=20, alpha=0.4)
    plt.plot(x, y, '--',color='white',linewidth=3)

    # Customizing the plot
    plt.gca().set_facecolor('gray')
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['left'].set_color('white')
    plt.gca().spines['left'].set_linewidth(2)
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['bottom'].set_linewidth(2)
    plt.gca().tick_params(axis='x', colors='white')
    plt.gca().tick_params(axis='y', colors='white')
    plt.gca().xaxis.label.set_color('white')
    plt.gca().xaxis.label.set_fontsize(14)
    plt.gca().yaxis.label.set_fontsize(14)
    plt.gca().yaxis.label.set_color('white')
    plt.gca().title.set_color('darkgray')

    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.xlabel('Knowledge', weight='bold')
    plt.ylabel('Confidence', weight='bold')
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    plt.savefig('./DK_curve.png', facecolor='darkgray')