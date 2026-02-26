from crewai import Task
from agents import financial_analyst
from tools import read_data_tool

financial_analysis_task = Task(
    description="""
    Read the financial document located at {file_path}
    using the available tool.
    
    Based strictly on the document contents:
    
    - Summarize financial performance
    - Identify key financial metrics (revenue, profit, debt, growth, etc.)
    - Highlight stated risks or uncertainties
    - Extract relevant market insights, industry trends, and competitive positioning
    - Provide balanced investment considerations.
    
    If information is missing, explicitly state that it is not available.
    Do not fabricate data.
    
    User Query: {query}
    """,
    
    expected_output="""
    1. Executive Summary
    2. Financial Highlights
    3. Market Insights & Industry Trends
    4. Key Risks
    5. Investment Considerations
    6. Conclusion
    """,
    
    agent=financial_analyst,
    tools=[read_data_tool],
)