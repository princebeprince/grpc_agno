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


# class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
#     def AskAgent(self, request, context):
#         try:
#             print(request)
#             query = request.query
#             if not query.strip():
#                 context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Query cannot be empty")

#             # Pass query directly to the agent with correct format
#             print("Sending query to agent:", query)
#             response_text = agent_b.run(query)
#             resp = extract_response_text(response_text)
#             print("Received response from agent:", resp)

#             return agent_pb2.AgentResponse(response=resp)

#         except Exception as e:
#             print(f"Error: {str(e)}")
#             context.abort(grpc.StatusCode.UNKNOWN, str(e))

# import time
# class AgentServicer(agent_pb2_grpc.AgentServiceServicer):
#     def AskAgentStream(self, request, context):
#         query = request.query.strip()
#         if not query:
#             context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Query cannot be empty")

#         yield agent_pb2.AgentResponse(response="Stage 1: Received query ✅")
#         time.sleep(0.5)

#         yield agent_pb2.AgentResponse(response="Stage 2: Sending query to Gemini 🤖")
#         time.sleep(0.5)

#         try:
#             response = agent_b.run(query)
#             yield agent_pb2.AgentResponse(response="Stage 3: Response received from Gemini 🧠")
#             final_text = extract_response_text(response)
#             yield agent_pb2.AgentResponse(response=f"Stage 4: Final Answer ➜ {final_text}")
#         except Exception as e:
#             yield agent_pb2.AgentResponse(response=f"❌ Error: {str(e)}")





# server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
# agent_pb2_grpc.add_AgentServiceServicer_to_server(AgentServicer(), server)
# server.add_insecure_port("[::]:50051")
# server.start()
# print("Agent B gRPC server running on port 50051...")
# server.wait_for_termination()



############## Gemini streamline
import grpc , time
from concurrent import futures
import agent_pb2, agent_pb2_grpc
from agno.agent import Agent
from agno.models.google import Gemini

# Initialize Gemini model
gemini_model = Gemini("gemini-2.5-flash", api_key="AIzaSyD6v6dOt-hxwzcZWhwrizKfgM_oiwJjXTw")

# Create agent
agent_b = Agent(
    model=gemini_model,
    name="InfoAgent",
    instructions="Provide answers clearly and concisely."
)

class AgentService(agent_pb2_grpc.AgentServiceServicer):
    def AskAgentStream(self, request, context):
        query = request.query.strip()
        print(query)
        if not query:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Query cannot be empty")

        # --- Stage 1: Received query ---
        yield agent_pb2.AgentResponse(response="Stage 1: ✅ Received query")
        time.sleep(0.3)

        # --- Stage 2: Sending query to Gemini ---
        yield agent_pb2.AgentResponse(response="Stage 2: 🤖 Processing with Gemini")
        time.sleep(0.3)

        try:
            # --- Stage 3: Run the agent ---
            response = agent_b.run(query)

            # Extract text from RunOutput
            text = getattr(response, "content", None) or str(response)

            # --- Stage 4: Sending final answer in chunks ---
            yield agent_pb2.AgentResponse(response="Stage 3: 🧠 Gemini responded")
            time.sleep(0.2)

            chunk_size = 50  # split the final response for streaming feel
            for i in range(0, len(text), chunk_size):
                yield agent_pb2.AgentResponse(response=text[i:i+chunk_size])

            yield agent_pb2.AgentResponse(response="Stage 4: ✅ Final Answer Sent")

        except Exception as e:
            yield agent_pb2.AgentResponse(response=f"❌ Error: {e}")




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_pb2_grpc.add_AgentServiceServicer_to_server(AgentService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("✅ Agent 3  gRPC server streaming on port 50052...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
