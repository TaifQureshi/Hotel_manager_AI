from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import ToolMessage
from langgraph.graph import END
from langgraph.graph.message import add_messages
from langchain.schema import AIMessage


# ----- Define State -----
class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    contact: str
    loopCheck: bool


# ----- Prompt for Missing Info -----
def ask_user_for_info(state: State):
    missing = []
    if not state.get("name"):
        missing.append("your name")
    if not state.get("contact"):
        missing.append("your contact information")

    ask = f"Before I can process your booking request, could you please provide {' and '.join(missing)}?"
    # Set loopCheck to True to prevent an AI-to-AI conversation loop
    return {"messages": [AIMessage(content=ask)], "loopCheck": True}


def validate_tool_calls(state: State) -> str:
    """
    Check if tool calls can be executed based on available user information.
    """

    last = state["messages"][-1]

    if not isinstance(last, AIMessage) or not hasattr(last, "tool_calls") or not last.tool_calls:
        return END

    booking_tools = ["create_booking", "check_booking",
                     "update_booking", "cancel_booking"]

    # Check if any tool call requires user info
    requires_user_info = any(
        call['name'] in booking_tools for call in last.tool_calls)

    # Check if we have the required user info
    has_user_info = bool(state.get("name") and state.get("contact"))
    if requires_user_info and not has_user_info:
        return "ask_user_for_info"
    return "tools"


# ----- Stop Condition Logic -----
def should_continue(state: State) -> str:
    """
    Decide the next node:
      - If the last AI message contains a tool call, validate if it can be executed
      - If the last message is from the user, try to extract any missing user info
      - Otherwise, end the process to prevent AI-to-AI loops
    """
    last = state["messages"][-1]

    # Continuously log detailed information about the current state
    # Log if there are tool calls in the last message
    has_tool_calls = isinstance(last, AIMessage) and hasattr(
        last, "tool_calls") and last.tool_calls

    # If the last message is an AI message with tool calls
    if has_tool_calls:
        next_node = validate_tool_calls(state)
        return next_node

    if isinstance(last, ToolMessage):
        return "chat"
    return END
