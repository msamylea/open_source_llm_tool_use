import json
from functools import wraps
from typing import Callable, Any, Union, List, Dict
import inspect
from langchain_anthropic import AnthropicLLM
from langchain_core.prompts import PromptTemplate

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, func: Callable) -> Callable:
        self.tools[func.__name__] = func
        return func

    def get_tools(self) -> Dict[str, Callable]:
        return self.tools

tool_registry = ToolRegistry()

def tool(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    tool_registry.register(wrapper)
    return wrapper

class ToolInvoker:
    def __init__(self, func: Callable):
        self.func = func

    def invoke(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

def parse_tool_invocation(raw_invocation: str) -> Union[dict, None]:
    try:
        invocation = json.loads(raw_invocation)
        if isinstance(invocation, dict) and 'tool' in invocation and 'tool_input' in invocation:
            return invocation
    except json.JSONDecodeError:
        pass
    return None

class ToolNotFoundException(Exception):
    pass

def invoke_tools(tool_invocations: List[Dict]) -> List[Dict]:
    results = []
    for invocation in tool_invocations:
        tool_name = invocation["tool"]
        tool_input = invocation["tool_input"]
        try:
            tool_func = tool_registry.get_tools()[tool_name]
            invoker = ToolInvoker(tool_func)
            result = invoker.invoke(**tool_input)
            results.append({"tool_name": tool_name, "result": result})
        except KeyError:
            results.append({"tool_name": tool_name, "error": f"Tool '{tool_name}' not found."})
        except TypeError as e:
            results.append({"tool_name": tool_name, "error": f"Invalid arguments for tool '{tool_name}': {e}"})
        except Exception as e:
            results.append({"tool_name": tool_name, "error": f"Error executing tool '{tool_name}': {e}"})

    return results

def tool_metadata(func: Callable) -> dict:
    signature = inspect.signature(func)
    docs = func.__doc__ or ""
    
    params = {}
    for name, param in signature.parameters.items():
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else Any
        description = ""
        if param.default is not inspect.Parameter.empty:
            description += f" (default: {param.default})"
        params[name] = {"type": str(annotation), "description": description}
    
    return_annotation = signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else Any
    
    return {
        "name": func.__name__,
        "description": docs,
        "parameters": params,
        "returns": str(return_annotation)
    }

def generate_tool_metadata(as_json=True) -> Union[str, List[Dict]]:
    metadata = [tool_metadata(func) for func in tool_registry.get_tools().values()]
    return json.dumps(metadata, indent=2) if as_json else metadata

def generate_tool_prompt() -> str:
    return f"""
    Available tools:
    {generate_tool_metadata()}
    
    Analyze the user's input to determine which tool (if any) should be invoked.
    
    If a tool is relevant, provide its name and the necessary parameters in JSON format:
    {{
        "tool": "<tool_name>",
        "tool_input": {{<param1>: <value1>, <param2>: <value2>, ...}} 
    }}

    It is important to provide the correct tool name and parameters to ensure the tool is invoked correctly.
    Remember, you can find the list of tools here: {generate_tool_metadata()}
    If no tool is relevant, respond with an empty JSON object:
    {{}}
    """
def parse_tool_invocation_ollama(response: str) -> Union[dict, None]:

    try:
        tool_invocation = json.loads(response)
        if isinstance(tool_invocation, dict) and 'tool' in tool_invocation and 'tool_input' in tool_invocation:
            return [tool_invocation]
    except json.JSONDecodeError:
        pass
    return None

def parse_tool_invocation_watsonx(response: str) -> Union[dict, None]:

    try:
        tool_invocation = json.loads(response)
        if isinstance(tool_invocation, dict) and 'tool' in tool_invocation and 'tool_input' in tool_invocation:
            return [tool_invocation]
    except json.JSONDecodeError:
        pass
    return None

def parse_tool_invocation_llama_cpp(response: str) -> Union[dict, None]:

    try:
        tool_invocation = json.loads(response)
        if isinstance(tool_invocation, dict) and 'tool' in tool_invocation and 'tool_input' in tool_invocation:
            return [tool_invocation]
    except json.JSONDecodeError:
        pass
    return None

def parse_tool_invocation_anthropic(response: str) -> Union[dict, None]:

    try:
        tool_invocation = json.loads(response)
        if isinstance(tool_invocation, dict) and 'tool' in tool_invocation and 'tool_input' in tool_invocation:
            return [tool_invocation]
    except json.JSONDecodeError:
        pass
    return None

def get_tool_invocation_from_llm(client: object, model: str, prompt: str, api_type: str = "default") -> Union[dict, None]:
    if api_type == "ollama":
        ollama_prompt = f"{generate_tool_prompt()}\nUser: {prompt}\nAssistant:"
        response = client.invoke(ollama_prompt)
        tool_invocation = parse_tool_invocation_ollama(response)
    elif api_type == "watsonx":
        watsonx_prompt = f"{generate_tool_prompt()}\nUser: {prompt}\nAssistant:"
        response = client.invoke(watsonx_prompt)
        tool_invocation = parse_tool_invocation_watsonx(response)
    elif api_type == "llama-cpp":
        llama_cpp_prompt = f"{generate_tool_prompt()}\nUser: {prompt}\nAssistant:"
        response = client.invoke(llama_cpp_prompt)
        tool_invocation = parse_tool_invocation_llama_cpp(response)
    elif api_type == "anthropic":
        template = """Question: {question}
        Answer: Let's think step by step."""
        prompt_template = PromptTemplate.from_template(template)
        chain = prompt_template | client
        response = chain.invoke({"question": prompt})
        tool_invocation = parse_tool_invocation_anthropic(response)
    else:
        messages = [{"role": "system", "content": generate_tool_prompt()}, {"role": "user", "content": prompt}]
        response = client.chat.completions.create(model=model, messages=messages, stream=False)
        try:
            tool_invocation = json.loads(response.choices[0].message.content)
            if isinstance(tool_invocation, dict):
                tool_invocation = [tool_invocation]
        except json.JSONDecodeError:
            tool_invocation = None
    print("Tool Invocation: ", tool_invocation)
    return response, tool_invocation

def generate_final_response(tool_invocations, tool_results, client, model, user_prompt, api_type="default"):
    if tool_results is not None:
        if api_type == "ollama":
            print("OLLAMA INVOKED")
            response = client.invoke(f"Based on the data retrieved from the following tool invocations, provide an appropriate response to the user's question(s). \n **** \n The result of invoking {tool_invocations} is {tool_results}.\nUser: {user_prompt}\nAssistant:")
            return response, response
        elif api_type == "watsonx":
            response = client.invoke(f"Based on the data retrieved from the following tool invocations, provide an appropriate response to the user's question(s). \n **** \n The result of invoking {tool_invocations} is {tool_results}.\nUser: {user_prompt}\nAssistant:")
            return response, response
        elif api_type == "llama-cpp":
            response = client.invoke(f"Based on the data retrieved from the following tool invocations, provide an appropriate response to the user's question(s). \n **** \n The result of invoking {tool_invocations} is {tool_results}.\nUser: {user_prompt}\nAssistant:")
            return response, response
        elif api_type == "anthropic":
            template = """Question: Based on the data retrieved from the following tool invocations, provide an appropriate response to the user's question(s).
            
            The result of invoking {tool_invocations} is {tool_results}.
            
            Original user question: {question}
            
            Answer: Let's think step by step."""
            prompt_template = PromptTemplate.from_template(template)
            chain = prompt_template | client
            response = chain.invoke({"question": user_prompt, "tool_invocations": tool_invocations, "tool_results": tool_results})
            return response, response
        else:
            messages = [
                {"role": "system", "content": f"Based on the data retrieved from the following tool invocations, provide an appropriate response to the user's question(s). \n **** \n The result of invoking {tool_invocations} is {tool_results}."},
                {"role": "user", "content": user_prompt},
            ]
            full_response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
            )
            return full_response, full_response.choices[0].message.content
    return None, None

def handle_llm_error(error, client, model, prompt, api_type="default"):
    error_message = str(error)
    
    if api_type == "ollama":
        response = client.invoke(f"The previous response contained malformed JSON. Please review the error carefully and provide a valid JSON response.\nExample of valid JSON format: {generate_tool_prompt()}\nError: {error_message}\nOriginal prompt: {prompt}\nAssistant:")
        return response
    elif api_type == "watsonx":
        response = client.invoke(f"The previous response contained malformed JSON. Please review the error carefully and provide a valid JSON response.\nExample of valid JSON format: {generate_tool_prompt()}\nError: {error_message}\nOriginal prompt: {prompt}\nAssistant:")
        return response
    elif api_type == "llama-cpp":
        response = client.invoke(f"The previous response contained malformed JSON. Please review the error carefully and provide a valid JSON response.\nExample of valid JSON format: {generate_tool_prompt()}\nError: {error_message}\nOriginal prompt: {prompt}\nAssistant:")
        return response
    elif api_type == "anthropic":
        template = """Question: The previous response contained malformed JSON. Please review the error carefully and provide a valid JSON response.
        
        Example of valid JSON format: {generate_tool_prompt()}
        
        Error: {error}
        Original prompt: {prompt}
        
        Answer: Let's think step by step."""
        prompt_template = PromptTemplate.from_template(template)
        chain = prompt_template | client
        response = chain.invoke({"error": error_message, "prompt": prompt})
        return response
    else:
        messages = [
            {"role": "system", "content": "The previous response contained malformed JSON. Please review the error carefully and provide a valid JSON response."},
            {"role": "system", "content": f"Example of valid JSON format: {generate_tool_prompt()}"},
            {"role": "user", "content": f"Error: {error_message}\nOriginal prompt: {prompt}"},
        ]
        retry_response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
        )
        
        try:
            tool_invocation = json.loads(retry_response.choices[0].message.content)
            if isinstance(tool_invocation, dict):
                tool_invocation = [tool_invocation]
            tool_results = invoke_tools(tool_invocation)
            full_response, answer = generate_final_response(tool_invocation, tool_results, client, model, prompt, api_type)
            return answer
        except json.JSONDecodeError:
            return "Apologies, I encountered an error while processing your request. Please try rephrasing your question."
def process_user_request(client, model, prompt, api_type="default"):
    response, tool_invocation = get_tool_invocation_from_llm(client, model, prompt, api_type)
    
    if tool_invocation is not None:
        try:
            if isinstance(tool_invocation, str):
                tool_invocation = json.loads(tool_invocation)
            if isinstance(tool_invocation, dict):
                tool_invocation = [tool_invocation]
            tool_results = invoke_tools(tool_invocation)
            full_response, answer = generate_final_response(tool_invocation, tool_results, client, model, prompt, api_type)
            return answer
        except json.JSONDecodeError as e:
            return handle_llm_error(e, client, model, prompt, api_type)
        except Exception as e:
            return "Apologies, an unexpected error occurred while processing your request. Please try again later."