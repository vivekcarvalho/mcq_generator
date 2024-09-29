from setuptools import find_packages, setup

setup(
    name = 'mcqgenerator',
    version = '0.0.1',
    author = 'Vivek Carvalho',
    author_email = 'vivek_carvalho@yahoo.co.in',
    install_requires = ['google.generativeai', 'langchain', 'streamlit', 'python-dotenv', 'PyPDF2'],
    packages = find_packages()
)