import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import read_data_tool

# Load the environment variables BEFORE initializing the LLM
load_dotenv()

llm = LLM(
    model="gpt-4o-mini",   
    temperature=0.0
)

financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze financial documents using only provided data.",
    backstory="Professional financial analyst with expertise in earnings reports.",
    verbose=True,
    tools=[read_data_tool],
    llm=llm,
    max_iter=2,
    allow_delegation=False
)