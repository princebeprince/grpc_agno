# import grpc
# import agent_pb2, agent_pb2_grpc

# def ask_agent(query, host="localhost", port=50051):
# 	channel = grpc.insecure_channel(f"{host}:{port}")
# 	stub = agent_pb2_grpc.AgentServiceStub(channel)
# 	request = agent_pb2.AgentRequest(query=query)
# 	response = stub.AskAgent(request)
# 	for response in stub.AskAgentStream(request):
# 		print("→", response.response)
# 	return response.response

# if __name__ == "__main__":
# 	query = "What is the capital of France?"
# 	response = ask_agent(query)
# 	print("Response from Agent B:", response)




# agent2.py
import grpc
import agent_pb2, agent_pb2_grpc

def ask_agent_stream(query, host="localhost", port=50051):
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = agent_pb2_grpc.AgentServiceStub(channel)
    request = agent_pb2.AgentRequest(query=query)

    print("Agent B →", end=" ", flush=True)
    try:
        for response in stub.AskAgentStream(request):
            print(response.response, end="", flush=True)
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")

if __name__ == "__main__":
    query = "what is the capital of France?"
    ask_agent_stream(query)
