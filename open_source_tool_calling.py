from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict


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
    model_config = ConfigDict(extra='ignore')
    tool: str
    tool_input: Optional[Dict] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.tool = data.get("tool")
        self.tool_input = data.get("tool_input")

    @staticmethod
    def generate_response(llm, user_prompt: str, tools):
    
        response = llm.chat.completions.create(
           model="meta-llama/Meta-Llama-3-70B-Instruct",
           messages=
            [
                {"role": "system", "content": f"You are a helpful assistant with access to these {tools} to answer the {user_prompt} question:"},
                {"role":"system", "content": f"If you do not need to use a tool, you can response with {CONVERSATION_FUNCTION}"},
                {"role":"system", "content":"You must reply in valid JSON format, with no other text. Example: {{\"tool\": \"tool_name\", \"tool_input\": \"tool_input\"}}"},
            ],
            max_tokens=4096,
            top_p=0.5,
            temperature=0.5,
            stop=["\n"],
        )
        response = response.choices[0].message.content
        valid_data = CallingFormat.model_validate_json(response)
        if valid_data:
            return response
        else:
            return "Please reply in valid JSON format."
    


