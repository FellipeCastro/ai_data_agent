from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def pick_llm(level: str):
    if level.lower() == "low":
        llm = ChatOpenAI(model_name="gpt-5.6-luna", temperature=0)
    elif level.lower() == "medium":
        llm = ChatOpenAI(model_name="gpt-5.6-terra", temperature=0)
    elif level.lower() == "high":
        llm = ChatOpenAI(model_name="gpt-5.6-sol", temperature=0)
    else:
        raise ValueError("Invalid level. Please choose from 'low', 'medium', or 'high'.")

    return llm

# # testing the function
# llm_obj = pick_llm("low")  
# print(llm_obj.invoke("What is the capital of France?"))
