import os
import base64
import requests
from io import BytesIO
from typing import Any, Type
from datetime import datetime, timedelta
import pyautogui
from PIL import Image
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.schema import HumanMessage
from pydantic import BaseModel
from dotenv import load_dotenv
import dateparser

# Load environment variables
load_dotenv()


# # ===== Tool 1: Screenshot Analysis =====
# class ScreenshotTool(BaseTool):
#     name: str = "screenshot_analysis"
#     description: str = (
#         "Takes a screenshot of the current screen and analyzes it with the user's question using GPT-4o Vision"
#     )

#     def _run(self, query: str) -> str:
#         """Take a screenshot and analyze it with the user's question."""
#         try:
#             # Take screenshot
#             screenshot = pyautogui.screenshot()

#             # Convert to base64 for OpenAI API
#             buffered = BytesIO()
#             screenshot.save(buffered, format="PNG")
#             img_str = base64.b64encode(buffered.getvalue()).decode()

#             # Create OpenAI client
#             llm = ChatOpenAI(
#                 model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
#             )

#             # Create message with image and text
#             message = HumanMessage(
#                 content=[
#                     {
#                         "type": "text",
#                         "text": f"Please analyze this screenshot and answer the following question: {query}",
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": f"data:image/png;base64,{img_str}"},
#                     },
#                 ]
#             )

#             # Get response
#             response = llm.invoke([message])
#             return response.content

#         except Exception as e:
#             return f"Error analyzing screenshot: {str(e)}"

#     def _arun(self, query: str) -> str:
#         """Async version of the tool (not implemented for this use case)."""
#         raise NotImplementedError("Async not implemented")

# # ===== Tool 2: Schedule Workout =====
# def parse_future_date(text: str) -> str:
#     dt = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
#     if dt:
#         return dt.strftime('%Y-%m-%d')
#     return None

# class ScheduleWorkoutInput(BaseModel):
#     date: str  # ngày đầu vào (dạng văn bản, ví dụ: '3 tháng 8' hoặc '2025-08-03')

# class ScheduleWorkoutTool(BaseTool):
#     name: str = "schedule_workout"
#     description: str = (
#         "Dùng để đặt lịch tập luyện. Nhận đầu vào là ngày (có thể thiếu năm), và sẽ tự động hiểu thành ngày gần nhất trong tương lai. Trả về ngày dạng YYYY-MM-DD."
#     )
#     args_schema: Type[BaseModel] = ScheduleWorkoutInput

#     def _run(self, date: str) -> str:
#         parsed = parse_future_date(date)
#         if not parsed:
#             return "Không hiểu ngày bạn cung cấp."

#         payload = {
#             "name": "Workout with Everfit",
#             "Date": parsed
#         }
#         response = requests.post("https://hook.eu2.make.com/9ty1og2anuaz4f8xdpvde7pxtkc12sxq", json=payload)
#         return f"✅ Đã đặt lịch tập vào {parsed}" if response.status_code == 200 else "❌ Lỗi khi đặt lịch."

#     def _arun(self, *args, **kwargs):
#         raise NotImplementedError("Tool này không hỗ trợ chạy async")

# # ===== Tool 3: Send Message to Client =====
# class SendMessageInput(BaseModel):
#     message: str

# class SendMessageToClientTool(BaseTool):
#     name: str = "send_message_to_client"
#     description: str = "Dùng để gửi tin nhắn cho học viên. Nội dung tin nhắn nên theo phong cách HLV chuyên nghiệp."
#     args_schema: Type[BaseModel] = SendMessageInput

#     def _run(self, message: str) -> str:
#         url = "https://hook.us2.make.com/m8j6cxm9st36azfve84ve1x7fbgmxbtt"
#         payload = {
#             "message": message
#         }
#         response = requests.post(url, json=payload)
#         if response.status_code == 200:
#             return f"✅ Đã gửi tin nhắn: {message}"
#         else:
#             return f"❌ Gửi tin nhắn thất bại. Mã lỗi: {response.status_code}"

#     def _arun(self, *args, **kwargs):
#         raise NotImplementedError("Tool này không hỗ trợ chạy async")


class FloatingAppAgent:
    def __init__(self):
        """Initialize the LangChain agent with all tools."""
        # Comment out OpenAI integration for UI testing
        # self.llm = ChatOpenAI(
        #     model="gpt-4o", temperature=0.5, api_key=os.getenv("OPENAI_API_KEY")
        # )

        # self.tools = [
        #     ScreenshotTool(),
        #     ScheduleWorkoutTool(),
        #     SendMessageToClientTool()
        # ]

        # self.agent = initialize_agent(
        #     tools=self.tools,
        #     llm=self.llm,
        #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        #     verbose=False,
        #     handle_parsing_errors=True,
        # )
        pass

    def analyze_screenshot_with_question(self, question: str) -> str:
        """Analyze screenshot with user's question using the agent."""
        try:
            # Comment out agent call for UI testing
            # response = self.agent.invoke(
            #     {
            #         "input": f"Use the screenshot_analysis tool to answer this question: {question}"
            #     }
            # )
            # return response["output"]
            
            # Return fixed response for UI testing
            return f"Test Response: You asked '{question}' and I can see your screen. This is a test response for UI development without using OpenAI API."
        except Exception as e:
            return f"Error processing request: {str(e)}"
