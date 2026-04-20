# Streamlit + langchain + ollama (gemma2:2b)

import streamlit as st
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Step 1: Create Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond clearly to the question asked."),
        ("user", "question: {question}")
    ]
)

# Step 2: Streamlit UI
st.title("Langchain with Gemma2:2b model (Ollama)")
input_text = st.text_input("What question do you have in your mind?")

# Step 3: Load Ollama Model
llm = Ollama(model="gemma2:2b")

# Step 4: Output Parser
output_parser = StrOutputParser()

# Step 5: Create Chain
chain = prompt | llm | output_parser

# Step 6: Run Model
if input_text:
    response = chain.invoke({"question": input_text})
    st.write(response)