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



def invoke_and_run(model, invoke_arg, tools=tools, functions=functions):
    result = generate_response(model, invoke_arg, tools, functions)
    
    function_name = result['tool']
    print(function_name)
    arguments = result['tool_input']
    function = functions[function_name]
    if function_name == 'get_stock_price':
        runnable = RunnableLambda(function)
        stock_ticker = arguments['stock_ticker']
        if isinstance(stock_ticker, str):
            runnable.invoke(stock_ticker)
        else:
            runnable.map().invoke(stock_ticker)
    else:
        if 'time' in arguments:
            if isinstance(arguments['time'], dict):
                try:
                    if isinstance(arguments['time'], dict) and '$date' in arguments['time']:
                        arguments['time'] = arguments['time']['$date']
                    else:
                        arguments['time'] = arguments['time']['time']
                except KeyError:
                    raise ValueError("The 'time' dictionary does not have a key named 'time' or '$date'")
            elif not isinstance(arguments['time'], str):
                raise ValueError("The 'time' value must be a string")
        function(**arguments)

invoke_and_run(model,{"query": "What is the current stock price of Apple (AAPL)?"})
```
