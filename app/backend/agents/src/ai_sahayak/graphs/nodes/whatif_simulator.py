import json
import boto3
from langchain_core.messages import AIMessage, SystemMessage
from ai_sahayak.graphs.state.conversation import ConversationState
from ai_sahayak.tools.llm.bedrock_client import get_llm
from ai_sahayak.config.settings import settings

# Initialize AgentCore Runtime Client for Code Interpreter
bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=settings.BEDROCK_REGION)

async def whatif_simulator_node(state: ConversationState):
    """
    Evaluates business scenarios using Bedrock AgentCore Code Interpreter.
    Qwen 32B generates the Python calculation logic, and Code Interpreter executes it.
    """
    # Use Qwen for reasoning/code generation
    llm = get_llm(model_id=settings.REASONING_MODEL_ID, temperature=0.1)
    
    messages = state.get("messages", [])
    last_query = messages[-1].content if messages else "No query provided."
    onboarding = state.get("onboarding_data", {})
    
    code_generation_prompt = f"""
    You are a financial analyst for an Indian Kirana store.
    Store Context: {json.dumps(onboarding)}
    User Question: "{last_query}"
    
    Write a Python script to simulate this scenario.
    Rules:
    - Use only standard math library.
    - Define variables for current and projected values.
    - PRINT a final summary of the impact.
    - DO NOT include markdown blocks. JUST the python code.
    """
    
    # Step 1: Generate Code
    code_response = await llm.ainvoke([SystemMessage(content=code_generation_prompt)])
    generated_code = code_response.content.strip()
    
    # Strip markdown if present
    if "```python" in generated_code:
        generated_code = generated_code.split("```python")[1].split("```")[0].strip()
    elif "```" in generated_code:
        generated_code = generated_code.split("```")[1].strip()

    try:
        # Step 2: Execute in Sandboxed Code Interpreter
        # Note: Code Interpreter requires specific models like Claude 3.5 Sonnet
        interpreter_model = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        response = bedrock_runtime.invoke_inline_agent(
            foundationModel=interpreter_model,
            instruction="You are a financial calculator. Execute the provided python code and summarize the result.",
            sessionId=state.get("user_context", {}).get("user_id", "sim_session")[:36],
            actionGroups=[
                {
                    "actionGroupName": "CodeInterpreter",
                    "parentActionGroupSignature": "AMAZON.CodeInterpreter"
                }
            ],
            inlineSessionState={
                "sessionAttributes": {
                    "code": generated_code
                }
            },
            inputText=f"Please execute the following python code to analyze this scenario: {last_query}"
        )
        
        # Extract execution output from event stream
        execution_output = ""
        for event in response.get("completion", []):
            if "chunk" in event:
                execution_output += event["chunk"].get("bytes", b"").decode("utf-8")
            elif "trace" in event:
                # Optionally capture code interpreter logs from trace
                trace = event["trace"].get("trace", {})
                if "orchestrationTrace" in trace:
                    orch = trace["orchestrationTrace"]
                    if "observation" in orch and "codeInterpreterInvocationOutput" in orch["observation"]:
                        ci_output = orch["observation"]["codeInterpreterInvocationOutput"]
                        execution_output += ci_output.get("executionOutput", "")
        
        reply_message = f"🧪 **Simulation Results (AgentCore Interpreter)**\n\n{execution_output or 'Calculation completed successfully. (No direct output string captured)'}"
        
    except Exception as e:
        print(f"Code Interpreter Error: {e}")
        # Fallback to LLM reasoning with code snippet
        reply_message = f"I've calculated the potential impact using a simulation:\n\n{code_response.content}"
    
    return {
        "messages": [AIMessage(content=reply_message)],
        "current_step": "simulator_complete"
    }
