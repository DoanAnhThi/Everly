import os
import base64
from io import BytesIO
from typing import Any
import pyautogui
from PIL import Image
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.schema import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ScreenshotTool(BaseTool):
    name: str = "screenshot_analysis"
    description: str = "Takes a screenshot of the current screen and analyzes it with the user's question using GPT-4o Vision"

    def _run(self, query: str) -> str:
        """Take a screenshot and analyze it with the user's question."""
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert to base64 for OpenAI API
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create OpenAI client
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Create message with image and text
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"Please analyze this screenshot and answer the following question: {query}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_str}"
                        }
                    }
                ]
            )
            
            # Get response
            response = llm.invoke([message])
            return response.content
            
        except Exception as e:
            return f"Error analyzing screenshot: {str(e)}"

    def _arun(self, query: str) -> str:
        """Async version of the tool (not implemented for this use case)."""
        raise NotImplementedError("Async not implemented")

class FloatingAppAgent:
    def __init__(self):
        """Initialize the LangChain agent with screenshot analysis tool."""
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.tools = [ScreenshotTool()]
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True
        )
    
    def analyze_screenshot_with_question(self, question: str) -> str:
        """Analyze screenshot with user's question using the agent."""
        try:
            response = self.agent.invoke({
                "input": f"Use the screenshot_analysis tool to answer this question: {question}"
            })
            return response["output"]
        except Exception as e:
            return f"Error processing request: {str(e)}" 