BACKGROUND_DATA_PROMPT = """
    Be detailed. Search about the following. 
    Give me back a very length response going into 
    details about everything regarding this topic.
"""


def generate_research_data(user_description: str) -> str:
    """
    Generates detailed research data about a given topic using the Gemini AI model.

    This function takes a user description/topic and sends it to Gemini AI with a prompt
    requesting detailed information. It handles the API call and returns the generated
    research content.

    Args:
        user_description (str): The topic or subject to research and generate content about

    Returns:
        str: The generated research content from Gemini AI

    Raises:
        Exception: If there is an error communicating with the Gemini AI API
    """
    import google.generativeai as genai
    import os
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    print("Generating research data")
    full_prompt = f"{BACKGROUND_DATA_PROMPT}\n\n{user_description}"
    try:
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")
