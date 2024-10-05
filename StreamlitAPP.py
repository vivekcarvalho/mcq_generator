import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from src.mcqgenerator.MCQ_generator import generate_evaluate_chain
from src.mcqgenerator.logger import logging, log_filepath

# Loading response json format
response_filepath = os.path.join(os.getcwd(), 'response.json')
with open(response_filepath, 'r') as file:
    response_json = json.load(file)


# Creating title for the App
st.title('MCQ Generator APP 🦜🔗')

# Create a form using st.form
with st.form('user_inputs'):
    # File upload utility
    uploaded_file = st.file_uploader('Upload pdf of txt file')

    # Input Fields
    # Required number of questions
    mcq_count = st.number_input('Required number of MCQs', 
                                min_value=3,
                                max_value=30)
    
    # Subject of the MCQs
    subject = st.text_input('Enter the subject of the MCQs',
                            max_chars = 25)
    
    # Difficulty Level
    difficulty = st.selectbox('Difficulty levels of the questions',
                              ('Easy', 'Intermediate', 'Hard'))
    
    # Add Button
    button = st.form_submit_button('Generate MCQs')

    #Checking if button is clicked and all the input fields has input provided

    logging.info(f"Subject : {subject} | number of requested MCQs : {mcq_count} | Difficulty Level : {difficulty}")
    
    if button and uploaded_file is not None and mcq_count and subject and difficulty:
        with st.spinner('Generating ...'):
            try:
                text = read_file(uploaded_file)

                # counting tokens and cost of the API
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

                response = generate_evaluate_chain.invoke(
                    {
                        'text' : text,
                        'number' : mcq_count,
                        'subject' : subject,
                        'difficulty': difficulty,
                        'response_json' : json.dumps(response_json)
                    }
                )

                logging.info(f"Response Text : {response}")

                # st.write(response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error('Error', icon="🔥")

            else:
                # print(f'Total Tokens: {cb.total_tokens}')
                # print(f'Prompt Tokens: {cb.prompt_tokens}')
                # print(f'Response Tokens: {cb.completion_tokens}')
                # print(f'Total Cost: {cb.total_cost}')

                if isinstance(response, dict):
                    # Extracting Quiz data from response
                    start_pt = response.get('quiz').find("{")
                    end_pt = response.get('quiz').rfind("}", )+1

                    # st.write(json.loads(response))
                    # quiz = json.loads(response.get('quiz'))
                    quiz = response.get('quiz')[start_pt:end_pt].replace('*', '')
                    # try:
                    #     # quiz = json.loads(response.get('quiz')[start_pt:end_pt].replace('*', ''))
                    #     # quiz = json.loads(response.get('quiz'))
                    # except Exception as e:
                    #     st.write(response['quiz'])

                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index+1
                            st.table(df)

                            # Display a review in a text box
                            st.text_area(label="MCQ Review", value=response.get('review').replace('*', '').replace('#', ''))
                        
                        else:
                            st.error('Error in Response')

                else:
                    st.write(response)