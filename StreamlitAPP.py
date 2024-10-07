import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from src.mcqgenerator.MCQ_generator import generate_evaluate_chain, ConsoleCallbackHandler
from src.mcqgenerator.logger import logging, log_filepath

# Loading response json format
response_filepath = os.path.join(os.getcwd(), 'response.json')
with open(response_filepath, 'r') as file:
    response_json = json.load(file)


# Creating title for the App
st.title('   🦜🔗    MCQ Generator App   🦜🔗')

# Create a form using st.form
with st.form('user_inputs'):
    # File upload utility
    uploaded_file = st.file_uploader('Upload pdf or txt file')

    # Input Fields
    # Subject of the MCQs
    subject = st.text_input('Enter the subject of the MCQs',
                            max_chars = 25)
    
    # Required number of questions
    mcq_count = st.number_input('Required number of MCQs', 
                                min_value=3,
                                max_value=30)
    
    # Required number of options
    option_count = st.number_input('Enter number of options in each MCQ',
                                   min_value = 2)
    
    # Difficulty Level
    difficulty = st.selectbox('Difficulty levels of the questions',
                              ('Easy', 'Intermediate', 'Hard'))
    
    # Add Button
    button = st.form_submit_button('Generate MCQs')

    #Checking if button is clicked and all the input fields has input provided

logging.info(f"Subject : {subject} | number of requested MCQs : {mcq_count} | Number of options in each MCQ : {option_count} \
                 : Difficulty Level : {difficulty}")
    
if button and uploaded_file is not None and mcq_count and subject and difficulty and option_count:
    with st.spinner('Generating ...'):
        try:
            text = read_file(uploaded_file)

            # counting tokens and cost of the API
            # with get_openai_callback() as cb:
            #         response = generate_evaluate_chain(
            #             {
            #                 'text' : text,
            #                 'mcq_count' : MCQ_COUNT,
            #                 'option_count' : option_count,
            #                 'subject' : SUBJECT,
            #                 'difficulty': DIFFICULTY,
            #                 'response_json' : json.dumps(response_json)
            #             }
            #         )

            response = generate_evaluate_chain.invoke(
                {
                    'text' : text,
                    'mcq_count' : mcq_count,
                    'option_count' : option_count,
                    'subject' : subject,
                    'difficulty': difficulty,
                    'response_json' : json.dumps(response_json)
                },
                # to get the 'verbose' equivalent
                config = {'callbacks' : [ConsoleCallbackHandler]}
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
                ## if StrOutputParser is used :
                # start_pt = response.get('quiz').find("{")
                # end_pt = response.get('quiz').rfind("}", )+1

                # quiz = response.get('quiz')[start_pt:end_pt].replace('*', '').replace('#', '')
                # st.write(json.loads(response))
                # quiz = json.loads(response.get('quiz'))

                ## if StrOutputParser is not used
                quiz_data = response.get('quiz').content
                start_pt = quiz_data.find("{")
                end_pt = quiz_data.rfind("}", )+1
                quiz = quiz_data[start_pt:end_pt].replace('*', '').replace('#', '')

                # st.write(json.loads(response))
                # quiz = json.loads(quiz)
                quiz_metadata = response.get('quiz').usage_metadata

                review_data = response.get('review').content
                review_metadata = response.get('review').usage_metadata

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
                        df_dnld = df
                        df = df.applymap(lambda x : x.replace(' | ', '<br>'))

                        st.write('<br><b>Questionnaire : </b>', unsafe_allow_html=True)
                        # st.table(df)
                        # st.write(df)
                        st.markdown(df.to_html(escape = False), unsafe_allow_html=True)

                        @st.cache_data
                        def convert_csv(df):
                            return df.to_csv().encode('utf-8')

                        mcq_out = convert_csv(df_dnld)

                        st.download_button('Download csv', mcq_out, file_name = f"{subject} MCQ.csv", mime='text/csv')

                        # Display a review in a text box
                        ## when strOuputParser is used
                        # st.text_area(label="MCQ Review", value=response.get('review').replace('*', '').replace('#', ''))

                        ## when strOuputParser is not used
                        st.text_area(label="MCQ Review", value=review_data.replace('*', '').replace('#', ''))

                        total_usage_metadata = quiz_metadata.copy()
                        for attr, val in review_metadata.items():
                            if attr in total_usage_metadata:
                                total_usage_metadata[attr] += val
                            else:
                                total_usage_metadata[attr] = val

                        usage_df = pd.DataFrame([quiz_metadata, review_metadata, total_usage_metadata])
                        usage_df.index = ['Quiz', 'Review', 'Total']
                        usage_df.columns = [str.title(col).replace('_', ' ') for col in usage_df.columns]

                        st.write('<br><u>Word Count Summary</u>', unsafe_allow_html=True)
                        st.table(usage_df)
                    
                    else:
                        st.error('Error in Response')

            else:
                st.write(response)
