from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='AI Chatbot',
    version='0.1.0',
    description='AI ChatBox Coursework',
    author='Alexander Taberner, Martin Wat, Prakrit Wongphayabal',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.6',
    install_requires=[
        'Flask>=1.1',
        'Flask-Bootstrap4>=4',
        'dill',
        'spacy',
        'selenium',
        'requests',
        'lxml',
        'numpy',
        'matplotlib',
        'sklearn',
        'durable',
        'beautifulsoup4',
        'dateparser',
        'sense2vec'
    ],
    entry_points={
        'console_scripts': [
            'ai_chatbot = ai_chatbot.main:main'
        ],
    }
)
