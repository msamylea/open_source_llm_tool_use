from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from typing import Optional
import config as cfg

llm = cfg.llm_chat

CONVERSATION_FUNCTION = {
    "name": "chat_response",
    "description": (
        "Use chat responses if a conversation is appropriate instead of a function."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "response": {
                "type": "string",
                "description": "Standard chat response.",
            },
        },
        "required": ["response"],
    },
}

class CallingFormat(BaseModel):

    tool: str = Field(description="name of the selected tool")
    tool_input: Optional[str] = Field(description="parameters for the selected tool, matching the tool's JSON schema")

    def __init__(self, **data):
        super().__init__(**data)
        self.tool = data["tool"]
        self.tool_input = data["tool_input"]
    

    @staticmethod
    def generate_response(llm, user_prompt: str, tools, functions):
        parser = JsonOutputParser(pydantic_object=CallingFormat)
     
        prompt = ChatPromptTemplate.from_messages(

            [
                ("system", "You are a helpful assistant with access to these {tool} to answer the {user_prompt} question:"),
                ("system", "If you do not need to use a tool, you can response with {CONVERSATION_FUNCTION}"),
                ("system", "You must reply in JSON format as so {{tool: tool_name, tool_input: tool_input}}"),

            ]
      
        )
        
        chain = prompt | llm | parser
        data = chain.invoke({"tool": tools, "user_prompt": user_prompt, "CONVERSATION_FUNCTION": CONVERSATION_FUNCTION})

        return data