import requests
import json
import time
import os

# --- Configuration ---

# **IMPORTANT: Please replace the key below with a fresh, newly generated Gemini API Key.**
# The 400 error strongly suggests the current key is invalid or unauthorized.
API_KEY = "AIzaSyDAagqHtCFFW_q5A5cdmTfenAR5bCG934M" # <-- Nayi key yahan daalen!
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
HEADERS = {'Content-Type': 'application/json'}

def call_api_with_backoff(payload, max_retries=5):
    """Handles the API call with exponential backoff for reliability."""
    if not API_KEY or API_KEY == "YOUR_NEW_API_KEY_HERE":
        print("FATAL ERROR: API_KEY is missing or the placeholder is still present.")
        return None

    # Construct the full API URL including the API key
    url = f"{BASE_URL}?key={API_KEY}"
    
    for attempt in range(max_retries):
        try:
            # Note: We use the data=json.dumps(payload) argument for POST requests
            response = requests.post(url, headers=HEADERS, data=json.dumps(payload), timeout=30)
            
            # Check for specific 400 error details
            if response.status_code == 400:
                print(f"FATAL ERROR (400 Bad Request): Your API Key is likely invalid or the Gemini API is not enabled in your Google Cloud Project.")
                print("Response detail:", response.text)
                # Print the payload that caused the issue for better debugging
                print("Sent Payload:", json.dumps(payload, indent=2)) 
                return None
                
            response.raise_for_status()  # Raise an exception for other bad status codes (4xx or 5xx)

            result = response.json()
            candidate = result.get('candidates', [None])[0]

            if not candidate:
                print(f"API Error (Attempt {attempt + 1}): No candidate response. Full response: {result}")
                return None

            # Check for structured JSON output
            if 'responseMimeType' in payload.get('generationConfig', {}) and payload['generationConfig']['responseMimeType'] == 'application/json':
                text_part = candidate.get('content', {}).get('parts', [{}])[0].get('text')
                if text_part:
                    return json.loads(text_part)
                return None

            # Standard text output
            return candidate.get('content', {}).get('parts', [{}])[0].get('text', 'The AI did not return a response.')

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Request failed (Attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Fatal API Error after {max_retries} attempts: {e}")
                return None
        except json.JSONDecodeError:
             print(f"API Response Error: Could not parse JSON response.")
             return None

    return None

def generate_content(prompt, system_instruction=None, response_schema=None):
    """A generic function to prepare the Gemini API payload."""
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        # TOOLS and SYSTEM INSTRUCTION ko ab seedhe top-level payload mein daala jata hai
        "tools": [{"google_search": {}}] # Use Google Search for grounding/up-to-date info
    }
    
    if system_instruction:
        # systemInstruction is also top-level now
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if response_schema:
        # Configuration for structured JSON output (generationConfig ke andar hi rahega)
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }

    return call_api_with_backoff(payload)

def chatbot_mode():
    """Starts a simple conversational chatbot."""
    print("\n--- Chatbot Mode ---")
    print("Ask me anything! Type 'exit' or 'quit' to return to the main menu.")
    
    system_prompt = "You are a helpful, friendly, and knowledgeable AI assistant. Keep your answers concise and accurate, utilizing up-to-date web knowledge when necessary."
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        if not user_input.strip():
            continue

        try:
            print("AI: Thinking...")
            response_text = generate_content(user_input, system_prompt)
            
            if response_text:
                print(f"AI: {response_text}")
            else:
                print("AI: Sorry, I couldn't generate a response right now.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print("\nExiting Chatbot Mode.")

def quiz_generator_mode():
    """Generates a multiple-choice quiz and runs it."""
    print("\n--- Quiz Generator Mode ---")
    
    topic = input("Enter the topic for the quiz (e.g., 'Python programming', 'World War II history'): ")
    
    while True:
        try:
            num_questions = int(input("How many questions do you want (max 10)? "))
            if 1 <= num_questions <= 10:
                break
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    print(f"\nGenerating a {num_questions}-question quiz on '{topic}'...")

    # Define the JSON schema for structured output (mandatory for reliable quiz generation)
    quiz_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "question": { "type": "STRING", "description": "The quiz question text." },
                "options": {
                    "type": "ARRAY",
                    "description": "An array of 4 multiple-choice options.",
                    "items": { "type": "STRING" }
                },
                "correct_answer": { "type": "STRING", "description": "The text of the correct option." }
            },
            "propertyOrdering": ["question", "options", "correct_answer"]
        }
    }
    
    prompt = (
        f"Generate a multiple-choice quiz on the topic of '{topic}'. "
        f"The quiz must have exactly {num_questions} questions. "
        "Each question must have 4 options. Return the result strictly as a JSON array "
        "following the provided schema."
    )
    
    system_prompt = "You are a quiz master. Your task is to generate challenging, clear, and engaging multiple-choice quizzes on any topic. Strictly adhere to the requested JSON format."

    quiz_data = generate_content(prompt, system_prompt, quiz_schema)

    if not quiz_data:
        print("Failed to generate quiz data. Please try again.")
        return

    # --- Run the Quiz ---
    print("\n--- Start Quiz ---")
    score = 0
    
    try:
        for i, item in enumerate(quiz_data):
            question = item.get('question', 'N/A')
            options = item.get('options', [])
            correct_answer = item.get('correct_answer', '')
            
            if not question or not options or not correct_answer:
                print(f"Skipping malformed question {i+1}.")
                continue

            print(f"\nQuestion {i + 1}: {question}")
            
            # Map options to letters for user interface
            option_map = {}
            for j, option in enumerate(options):
                letter = chr(ord('A') + j)
                option_map[letter] = option
                print(f"  {letter}. {option}")
                
            # Find the correct letter for comparison
            correct_letter = next((l for l, opt in option_map.items() if opt == correct_answer), None)

            if not correct_letter:
                # Fallback if correct_answer text doesn't match an option (shouldn't happen with strict JSON adherence)
                print(f"  [Error: Could not determine correct letter for question {i+1}]")
                continue

            user_choice = input("Your answer (A, B, C, or D): ").strip().upper()

            if user_choice in option_map:
                if option_map[user_choice] == correct_answer:
                    print("✅ Correct!")
                    score += 1
                else:
                    print(f"❌ Incorrect. The correct answer was {correct_letter}: {correct_answer}")
            else:
                print(f"⚠️ Invalid choice. The correct answer was {correct_letter}: {correct_answer}")

        # --- Quiz Results ---
        print("\n--- Quiz Finished ---")
        print(f"Your final score is: {score}/{len(quiz_data)}")
        if score == len(quiz_data):
            print("Fantastic! A perfect score!")
        elif score >= len(quiz_data) / 2:
            print("Well done! You have a good grasp of the topic.")
        else:
            print("Good effort. Time for some more study!")

    except Exception as e:
        print(f"An error occurred while processing the quiz: {e}")


def main():
    """The main entry point for the application."""
    print("===========================================")
    print(" Gemini LLM CLI Application (Python Only) ")
    print("===========================================")
    print("Model used: gemini-2.5-flash-preview-09-2025")
    
    while True:
        print("\n--- Main Menu ---")
        print("1. Start Chatbot")
        print("2. Generate and Take a Quiz")
        print("3. Exit Application")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            chatbot_mode()
        elif choice == '2':
            quiz_generator_mode()
        elif choice == '3':
            print("\nThank you for using the Gemini CLI application. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
