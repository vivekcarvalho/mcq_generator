import os
import PyPDF2
import json
import traceback

# Get the Data
def read_file(file):
    if file.name.lower().endswith('pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        
        except Exception as e:
            raise Exception('Error Reading the PDF file', e)
        
    elif file.name.lower().endswith('txt'):
        return file.read().decode('utf-8')
    
    else:
        raise Exception("File format not supported\nOnly pdf and txt files are supported")


# Collecting MCQ response in a table form
def get_table_data(quiz_str):
    try:
        # Converting quiz from text to dictionary
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        # Iterate over the quiz dictionary and extract the required information
        for key, value in quiz_dict.items():
            mcq = value['mcq']
            options = " | ".join(

                [f"{option} : {answer}" for option, answer in value['option'].items()]
            )
            correct_option = value['correct option']

            quiz_table_data.append({'MCQ': mcq, 'OPTIONS': options, 'CORRECT CHOICE' : correct_option})

        return quiz_table_data
    
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)

