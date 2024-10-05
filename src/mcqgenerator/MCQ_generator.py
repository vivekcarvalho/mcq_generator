# Loading required libraries
import os
import json
import pandas as pd
import traceback
from operator import itemgetter

# Importing LLM Module
import tqdm as notebook_tqdm
from langchain_google_genai import ChatGoogleGenerativeAI


# Importing langchain tools
    # from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.schema.runnable import RunnablePassthrough

    #Deprecated; use below implementation
    # from langchain.chains import LLMChain
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

    # from langchain.callbacks import get_openai_callback
import PyPDF2



# To take the Key from .env
from dotenv import load_dotenv

# Loading Enviorment variables from .env file
load_dotenv()

# Accessing environment variable 
gemini_key = os.getenv('GOOGLE_API_KEY')


llm = ChatGoogleGenerativeAI(
    model = 'gemini-1.5-flash',
    temperature=0.8, #Creativity index: 0 - less creative, 1 - highly Creative
    max_retries=2,
    timeout=None,
    google_api_key=gemini_key
)


# Creating Input prompt template and prompt object
TEMPLATE = """
Text : {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {difficulty} tone. \
Make sure that the questions are not repeated and check all the questions to be confirming the text as well. \
Make sure to format your response exactly like below and use it as a guide. \
ensure to make {number} MCQs

{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=['text', 'number', 'subject', 'difficulty', 'response_json'],
    template=TEMPLATE,
)


# Creating LLM chain / runnable for input prompt
    # Deprecated; use below implementation
    # quiz_chain = LLMChain(llm = llm, prompt = quiz_generation_prompt, output_key = 'quiz', verbose=True)
quiz_chain = quiz_generation_prompt | llm | StrOutputParser()
# type(quiz_chain)


# Creating second template for review task and prompt object
TEMPLATE2 = """
You are an export English gramrian and writer. Given an multiple choice quiz for {subject} students. \
You need to evaluate the complexity of the questions and give a complete analysis of the quiz. \
Use only at max 50 words for complexity. If quiz is not at par with the cognitive and analytical abilities of the students, \
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the students ability. \
Quiz MCQs:
{quiz} \

Check from an expert Englist writer of the above quiz:
"""

quiz_evalutaion_prompt = PromptTemplate(
    input_variables=['subject', 'quiz'],
    template=TEMPLATE2
)


#Creating LLM chain / runnable for Review Task
    # Deprecated; use below implementation
    # review_chain = LLMChain(llm = llm, prompt = quiz_evalutaion_prompt, output_key = 'review', verbose=True)
review_chain = quiz_evalutaion_prompt | llm | StrOutputParser()
# type(review_chain)


# Creating SequentialChain / RunnableSequence 
    # Deprecated; use below implementation
    # generate_evaluate_chain = SequentialChain(chains=[quiz_chain, review_chain], 
    #                                           input_variables=['text', 'number', 'subject', 'difficulty', 'response_json'],
    #                                           output_variables = ['quiz', 'review'], 
    #                                           verbose = True)

    # generate_evaluate_chain = quiz_chain | {
    #     'quiz' : quiz_chain,
    #     'review' : review_chain
    # }

generate_evaluate_chain = ({'quiz' : quiz_chain, 'subject': itemgetter('subject')} | RunnablePassthrough.assign(review = review_chain))
# type(generate_evaluate_chain)


# Getting the Token Usage using the Tracker (Currently only implemented for OpenAI)

# How to setup token usage tracking in Langchain
# with get_openai_callback() as cb:
#     response = generate_evaluate_chain(
#         {
#             'text' : text,
#             'number' : NUMBER,
#             'subject' : SUBJECT,
#             'difficulty': DIFFICULTY,
#             'response_json' : json.dumps(response_json)
#         }
#     )