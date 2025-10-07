import grpc ,os
from concurrent import futures
import agent_pb2, agent_pb2_grpc
from agno.agent import Agent
from agno.models.google import Gemini
# Agent B

# Provide your API key here
gemini_model = Gemini("gemini-2.5-flash", api_key="AIzaSyD6v6dOt-hxwzcZWhwrizKfgM_oiwJjXTw")
agent_b = Agent(model=gemini_model, name="InfoAgent", instructions="Provide answers.")

os.environ["GOOGLE_API_KEY"] = "AIzaSyD6v6dOt-hxwzcZWhwrizKfgM_oiwJjXTw"

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),   # You can also use "gemini-1.5-pro"
    name="GeminiAgent",
    instructions="You are a helpful assistant that summarizes and answers questions."
)


def extract_response_text(response):
    """
    Extracts the main response text from an agno RunOutput or returns a fallback string.
    """
    try:
        if hasattr(response, "content") and response.content:
            return response.content
        elif hasattr(response, "text") and response.text:
            return response.text
        elif isinstance(response, dict) and "content" in response:
            return response["content"]
        else:
            return str(response)
    except Exception as e:
        return f"[Error extracting response: {str(e)}]"


class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
    def AskAgent(self, request, context):
        try:
            print(request)
            query = request.query
            if not query.strip():
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Query cannot be empty")

            # Pass query directly to the agent with correct format
            print("Sending query to agent:", query)
            response_text = agent_b.run(query)
            resp = extract_response_text(response_text)
            print("Received response from agent:", resp)

            return agent_pb2.AgentResponse(response=resp)

        except Exception as e:
            print(f"Error: {str(e)}")
            context.abort(grpc.StatusCode.UNKNOWN, str(e))





server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
agent_pb2_grpc.add_AgentServiceServicer_to_server(AgentServicer(), server)
server.add_insecure_port("[::]:50052")
server.start()
print("Agent B gRPC server running on port 50052...")
server.wait_for_termination()
