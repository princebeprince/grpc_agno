import grpc
import agent_pb2, agent_pb2_grpc
from agno.agent import Agent 
from agno.team import Team
from agno.models.google import Gemini

# ----------------------------
# Step 1: gRPC streaming tool
# ----------------------------
def ask_agent_stream_tool(query: str) -> str:
    """
    Calls Agent 1 via gRPC streaming and returns full output.
    
    Args:
        query: The question or query to send to Agent 1
        
    Returns:
        The response from Agent 1
    """
    host = "localhost"
    port = 50051
    
    print(f"\n{'🔧 TOOL INVOKED: ask_agent_stream_tool':=^60}")
    print(f"   Query: {query}")
    print(f"   Host: {host}:{port}")
    print("="*60)
    
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = agent_pb2_grpc.AgentServiceStub(channel)
    request = agent_pb2.AgentRequest(query=query)

    output = ""
    try:
        print("\n[Agent 1] Streaming → ", end="", flush=True)
        for response in stub.AskAgentStream(request):
            print(response.response, end=" ", flush=True)
            output += response.response + " "
        print()
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        output += f"\nError: {e}"

    print(f"{'✅ TOOL COMPLETED: ask_agent_stream_tool':=^60}\n")
    return output.strip()

def ask_agent_stream_tool2(query: str) -> str:
    """
    Calls Agent 2 via gRPC streaming and returns full output.
    
    Args:
        query: The question or query to send to Agent 2
        
    Returns:
        The response from Agent 2
    """
    host = "localhost"
    port = 50052
    
    print(f"\n{'🔧 TOOL INVOKED: ask_agent_stream_tool2':=^60}")
    print(f"   Query: {query}")
    print(f"   Host: {host}:{port}")
    print("="*60)
    
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = agent_pb2_grpc.AgentServiceStub(channel)
    request = agent_pb2.AgentRequest(query=query)

    output = ""
    try:
        print("\n[Agent 2] Streaming → ", end="", flush=True)
        for response in stub.AskAgentStream(request):
            print(response.response, end=" ", flush=True)
            output += response.response + " "
        print()
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        output += f"\nError: {e}"

    print(f"{'✅ TOOL COMPLETED: ask_agent_stream_tool2':=^60}\n")
    return output.strip()


# ----------------------------
# Step 2: Initialize Gemini
# ----------------------------
gemini_model = Gemini("gemini-2.5-flash", api_key="AIzaSyD6v6dOt-hxwzcZWhwrizKfgM_oiwJjXTw")

# ----------------------------
# Step 3: Create Individual Agents
# ----------------------------
agent_z = Agent(
    name="QuestionAnswerAgent",
    model=gemini_model,
    instructions="Must use available tools to answer questions. If a tool is used, process its output before replying.",
    tools=[ask_agent_stream_tool]
)

agent_y = Agent(
    name="SummarizerAgent",
    model=gemini_model,
    instructions="Must use available tools to answer questions. If a tool is used, process its output before replying.",
    tools=[ask_agent_stream_tool2]
)

# ----------------------------
# Step 4: Create Team (Master Agent)
# ----------------------------
agent_master = Team(
    name="MasterAgent",
    model=gemini_model,
    instructions="Must use the team members to answer the query. Delegate tasks appropriately to QuestionAnswerAgent and SummarizerAgent.",
    members=[agent_y, agent_z]
)


# ----------------------------
# Step 5: Streaming Function Options
# ----------------------------

def run_with_streaming(agent_or_team, query):
    """
    Runs the agent/team with streaming output - tries multiple methods.
    """
    print(f"\n{'='*60}")
    print(f"🚀 Master Agent Processing: {query}")
    print(f"{'='*60}\n")
    
    full_response = ""
    
    try:
        # First, let's see what run() actually returns
        print("📞 Calling agent_or_team.run()...")
        result = agent_or_team.run(query)
        
        print(f"\n[DEBUG] Result type: {type(result)}")
        print(f"[DEBUG] Result value: {result}")
        
        # Check if tools were invoked by looking at result attributes
        if hasattr(result, 'tool_calls'):
            print(f"[DEBUG] Tool calls: {result.tool_calls}")
        if hasattr(result, 'messages'):
            print(f"[DEBUG] Messages: {len(result.messages) if result.messages else 0}")
        
        if result is None:
            print("\n⚠️ Warning: run() returned None. Checking for alternative outputs...")
            # Check if there's a response attribute
            if hasattr(agent_or_team, 'last_response'):
                full_response = str(agent_or_team.last_response) if agent_or_team.last_response is not None else "No response"
            elif hasattr(agent_or_team, 'response'):
                full_response = str(agent_or_team.response) if agent_or_team.response is not None else "No response"
            else:
                full_response = "No response available"
        elif hasattr(result, 'content'):
            full_response = str(result.content) if result.content is not None else ""
        elif hasattr(result, 'response'):
            full_response = str(result.response) if result.response is not None else ""
        elif hasattr(result, 'output'):
            full_response = str(result.output) if result.output is not None else ""
        elif hasattr(result, 'text'):
            full_response = str(result.text) if result.text is not None else ""
        else:
            full_response = str(result) if result is not None else ""
        
        print(f"\n📝 Response:\n{full_response}")
            
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        full_response = f"Error: {e}"
    
    print(f"\n{'='*60}")
    return full_response


def run_with_print_capture(agent_or_team, query):
    """
    Alternative: Capture printed output since the agents print their responses.
    """
    print(f"\n{'='*60}")
    print(f"🚀 Master Agent Processing: {query}")
    print(f"{'='*60}\n")
    
    import io
    import sys
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    try:
        result = agent_or_team.run(query)
        
        # Restore stdout
        sys.stdout = old_stdout
        
        # Get captured output
        output = captured_output.getvalue()
        
        print(output)  # Print what was captured
        
        # Try to get the actual response
        if result is not None:
            if hasattr(result, 'content') and result.content is not None:
                response = str(result.content)
            elif hasattr(result, 'response') and result.response is not None:
                response = str(result.response)
            else:
                response = str(result) if result else output
        else:
            response = output if output else "No response captured"
            
        print(f"\n{'='*60}")
        return response
        
    except Exception as e:
        sys.stdout = old_stdout
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}"


# ----------------------------
# Step 6: Example usage
# ----------------------------
if __name__ == "__main__":
    # First, let's check what the agent_master object looks like
    print("Available attributes on agent_master:")
    # print([attr for attr in dir(agent_master) if not attr.startswith('_')])
    print()
    
    queries = [
        "What is the capital of France and summarize it?"
    ]
    
    for query in queries:
        print("\n" + "="*60)
        print("Method 1: Direct run()")
        print("="*60)
        response = run_with_streaming(agent_master, query)
        print(f"\n✅ Final Response Length: {len(response)} chars")
        
        print("\n" + "="*60)
        print("Method 2: Capturing printed output")
        print("="*60)
        # response2 = run_with_print_capture(agent_master, query)
        # print(f"\n✅ Final Response Length: {len(response2)} chars")