from toolbox import process_user_request

class Agent:
    def __init__(self, client, model, api_type):
        self.client = client
        self.model = model
        self.api_type = api_type
        self.history = []

    def chat(self, user_input):
        prompt = self._generate_prompt(user_input)
        print("Prompt: ", prompt)
        response = process_user_request(self.client, self.model, prompt, self.api_type)
        print("Response: ", response)
        self._update_history(user_input, response)
        return response

    def _generate_prompt(self, user_input):
        # Generate the prompt for the LLM based on the user input and conversation history
        prompt = "Conversation history:\n"
        for user_msg, agent_msg in self.history:
            prompt += f"User: {user_msg}\nAgent: {agent_msg}\n"
        prompt += f"User: {user_input}\nAgent:"
        return prompt

    def _update_history(self, user_input, response):
        # Update the conversation history with the user input and agent response
        self.history.append((user_input, response))

    def clear_history(self):
        # Clear the conversation history
        self.history = []

class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name, agent):
        self.agents[name] = agent

    def get_agent(self, name):
        return self.agents.get(name)
    
# Usage example
if __name__ == "__main__":
    # Create an instance of the Agent class with the desired LLM client, model, and API type
    client = ...  # Initialize the LLM client (e.g., OpenAI, Anthropic, etc.)
    model = ...  # Specify the LLM model to use
    api_type = ...  # Specify the API type (e.g., "default", "anthropic", "ollama", etc.)
    agent = Agent(client, model, api_type)

    # Start the conversation loop
    while True:
        user_input = input("User: ")
        response = agent.chat(user_input)
        print(f"Agent: {response}")