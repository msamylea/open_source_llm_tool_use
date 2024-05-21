# Example use
```python
import open_source_tool_calling

generate_response = ostc.CallingFormat.generate_response

def get_stock_price(stock_ticker: str) -> float:
    current_price = stock_info.get_live_price(stock_ticker)
    print("The current price is ", "$", round(current_price, 2))

def create_meeting(attendee, time):
    try:
        time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    print(f"Scheduled a meeting with {attendee} on {time}")



tools = [
        { 
            "name": "get_stock_price",
            "description": "Get the current price of the given stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_ticker": {
                        "type": "string",
                        "description": "The stock ticker to pass into the function"
                    }
                },
                "required": ["stock_ticker"]
            }
        },
        {
            "name": "create_meeting",
            "description": "Schedule a meeting for the user with the specified details",
            "parameters": {
                "type": "object",
                "properties": {
                    "attendee": {
                        "type": "string",
                        "description": "The person to schedule the meeting with"
                    },
                    "time": {
                        "type": "datetime",
                        "description": "The date and time of the meeting"
                    }
                },
                "required": [
                    "attendee",
                    "time"
                ]
            },
        },
    ],



def invoke_and_run(llm, invoke_arg, tools=tools):
    result = generate_response(llm, invoke_arg, tools)
    result = json.loads(result)
    function_name = result['tool']
    print(function_name)
    arguments = result['tool_input']
    function = functions[function_name]
    if arguments is None:
        function()
    else:
        function(**arguments)

invoke_and_run(llm,{"query": "What is the current stock price of Apple (AAPL)?"})
```
