from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

def mentor_chat(user_input):
    prompt = f"""
    You are an AI career mentor.

    Guide the user in improving skills, career growth, and learning path.

    User Question:
    {user_input}
    """

    response = llm.invoke(prompt)
    return response.content
