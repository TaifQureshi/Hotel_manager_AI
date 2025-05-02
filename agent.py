from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import json
from tools import TOOLS
from nodes import State, ask_user_for_info, should_continue
import numpy as np
import cv2

# ----- System Prompt -----
system_prompt = """
You are a helpful assistant named Larry. You work at Blue Pearl Hotel.
Your job is to help customers with their room bookings.
You are an assistant with access to tools.
If a tool is needed, respond only with a tool_call. Do not explain or confirm the action — just call the tool.
Greet the user first only at start.

IMPORTANT: Never assume or make up a customer's name or contact information.
Only use information explicitly provided by the user.

First check availability before creating bookings.
First check if booking exists before updating or canceling.
If user information is missing, ask for it clearly and wait for their response.

Do not show tool call messages to the user. Only respond naturally with relevant actions.
Do not simulate the tool call actually call them.

After checking for availability or if booking exists inform user. For the tool keep the date fromat as YYYY-MM-DD if the format is not correct
fix if before calling the tools
"""

llm = ChatOllama(model="cas/ministral-8b-instruct-2410_q4km")

llm_with_tools = llm.bind_tools(TOOLS)
sys_msg = SystemMessage(content=system_prompt)


def fill_user_info(last_user_msg: HumanMessage):
    prompt = f"""
    The user previously said: "{last_user_msg.content}"
    Please extract the user's name and contact number ONLY if explicitly provided.
    DO NOT make up or infer information that isn't clearly stated.
    If either is missing, return null for that field.
    Respond in JSON format: {{"name": ..., "contact": ...}}
    """
    result = llm.invoke(prompt)
    try:
        info = json.loads(result.content)
    except Exception as e:
        info = {"name": None, "contact": None}
    return info


def chatbot(state: State):
    # Check if this is a continuation (loopCheck would be True)
    # If it is, don't generate a new AI response
    last = state["messages"][-1]
    if state.get("loopCheck") and not isinstance(last, ToolMessage):
        return {"messages": state["messages"], "loopCheck": False}
    
    # Check if we need to modify tool calls based on missing information
    has_valid_info = state.get("name") or state.get("contact")
    info = {"name": None, "contact": None}
    if has_valid_info is None and isinstance(state["messages"][-1], HumanMessage):
        info = fill_user_info(state["messages"][-1])
    
    print("Name: ", state.get("name"), " Contact: ", state.get("contact"))
    print("Name: ", info.get("name"), " Contact: ", info.get("contact"))
    # Create filtered messages to avoid information hallucination
    filtered_messages = [sys_msg] + state["messages"]

    # Generate response
    message: AIMessage = llm_with_tools.invoke(filtered_messages)
            
    # If there are tool calls but information is missing, we need to modify the response
    if not has_valid_info and hasattr(message, "tool_calls") and message.tool_calls:
        booking_tools = ["create_booking", "check_booking",
                         "update_booking", "cancel_booking"]
        if any(call['name'] in booking_tools for call in message.tool_calls):
            # Replace with a message asking for the required information
            missing = []
            if not state.get("name"):
                if not info.get("name"):
                    missing.append("your name")
            if not state.get("contact"):
                if not info.get("name"):
                    missing.append("your contact information")

            if len(missing) > 0:
                content = f"I'd like to help you with your booking request. Before proceeding, could you please provide {' and '.join(missing)}?"
                message = AIMessage(content=content)

    # Set loopCheck to True to prevent the next iteration from generating another AI response
    # This will force the system to wait for user input
    data = {"messages": [message], "loopCheck": True}
    data.update(info)
    return data


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=TOOLS))
graph_builder.add_node("ask_user_for_info", ask_user_for_info)

# Connect START to chatbot
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", should_continue)
graph_builder.add_edge("tools", 'chatbot')
graph_builder.add_edge("ask_user_for_info", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Log the graph structure
# OPTIONAL: Visualize the graph
# try:
#     png_bytes = graph.get_graph().draw_mermaid_png()
#     img_array = np.frombuffer(png_bytes, dtype=np.uint8)
#     img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#     cv2.imshow("LangGraph", img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# except Exception as e:
#     print(e)


if __name__ == "__main__":
    # ----- Interactive Loop -----
    from langchain_core.runnables import RunnableConfig

    config = RunnableConfig(
        recursion_limit=10,
        configurable={"thread_id": "1"},
    )

    # config = {"configurable": {"thread_id": "1"}}

    while True:
        user_input = input("🧑 You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break
        print("🤖 Larry: ", end="\n")

        # Log the state before invoking the graph
        # Create initial state with loopCheck set to False
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "loopCheck": False  # Start with loopCheck as False
        }

        response = graph.invoke(initial_state, config)

        # Log the response state
        print(response["messages"][-1].content)
        print()