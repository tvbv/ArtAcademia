"""
app.py
"""
import os

import gradio as gr
from groq import Groq

client = Groq(
    api_key='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')


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


def autocomplete(text, starting_topic="database management"):
    if text != "":
        response = client.chat.completions.create(
            model='gemma-7b-it',
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + starting_topic
                },
                {
                    "role": "user",
                    "content": text
                }],
            stream=True
        )
        print(response)

        # response, content = parse_response(response)
        partial_message = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + \
                    chunk.choices[0].delta.content
                yield partial_message


def parse_response(response):
    """
    Parse the response from the Groq API (it is a JSON object with a list of chunks)
    """
    response_parsed = []
    for chunk in response:
        response_parsed.append(chunk)
    return response_parsed

css = """
.generating {
    display: none
}
"""

# Create the Gradio interface with live updates
iface = gr.Interface(
    fn=autocomplete,
    inputs=gr.Textbox(lines=2,
                      placeholder="Hello 👋",
                      label="Input Sentence"),
    outputs=gr.Markdown(),
    title="Catch Me If You Can 🐰",
    description="Powered by Groq & Gemma",
    live=False,  # Set live to True for real-time feedback
    allow_flagging="never",  # Disable flagging
    #    css=css
)
# iface.dependencies[0]['show_progress'] = "hidden"
# iface.dependencies[2]['show_progress'] = "hidden"

# Launch the app
iface.launch()
