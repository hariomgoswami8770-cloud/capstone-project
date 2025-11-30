1. Project Overview

This is a simple, command-line interface (CLI) application built purely in Python that utilizes the Gemini API for generative AI tasks. The application features a versatile chatbot and a dynamic, structured quiz generator.

Technology Stack

Language: Python 3

API: Google Gemini API (Model: gemini-2.5-flash-preview-09-2025)

Library: requests for handling API communication.

2. Key Features

Chatbot Mode (Option 1): A general-purpose conversational assistant. It uses Google Search Grounding to provide up-to-date and factual responses to your queries.

Quiz Generator (Option 2): Generates a custom multiple-choice quiz on any topic and runs the quiz directly in the terminal. This feature leverages Gemini's Structured Output to ensure reliable and correctly formatted JSON data.

3. Setup and Installation

Prerequisites

You need Python 3 installed on your system.

3.1. Install Dependencies

Open your terminal or command prompt and run the following command to install the necessary requests library:

pip install requests


3.2. API Key Configuration (Crucial Step)

The application requires a valid Gemini API Key to function. You must set this key in the ai_application.py file.

Security Note: Never commit your API key directly to a public code repository (like GitHub).

Obtain Key: Get a new Gemini API key from the Google AI Studio or Google Cloud Console.

Update File: Open ai_application.py and replace the placeholder value on line 7 with your actual key:

# python.py (Configuration Section)
API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY_HERE"


(Note: For development, the key was temporarily set as: API_KEY = "AIzaSyA-n8B8Kg2QqEq-Ea4JzxHB-3-LUnHsx2Y")

4. Execution

4.1. How to Run

Ensure your terminal is in the directory containing the Python.py file.

Execute the application using the Python interpreter:

python ai_application.py


5. Usage Guide

Once the application is running, the main menu will appear:

===========================================
 study ai agent (Python Only) 
==========================================
--- Main Menu ---
1. Start Chatbot
2. Generate and Take a Quiz
3. Exit Application
Enter your choice (1-3): 


5.1. Chatbot Mode (Option 1)

Select 1 and enter your questions. The chatbot will use the Gemini model to generate responses.

Exit: Type exit or quit to return to the Main Menu.

5.2. Quiz Generator (Option 2)

Select 2. The application will prompt you for:

Quiz Topic (e.g., Quantum Physics, History of India)

Number of Questions (1-10)

The AI will generate the questions and present them one by one. Enter the corresponding letter (A, B, C, or D) for your answer. Your score will be displayed at the end.
