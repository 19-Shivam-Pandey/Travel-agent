from langgraph.graph import StateGraph, START, END
from state import TravelState

from agents.supervisor import supervisor_node
from agents.researcher import research_agent
from agents.planner import planner_agent
from agents.budgeter import budget_agent
from agents.validator import validator_agent


def researcher_node(state: TravelState) -> TravelState:
    prompt = f"""
User request:
{state.get("user_query", "")}

Current known data:
- destination: {state.get("destination", "")}
- days: {state.get("days", "")}
- budget: {state.get("budget", "")}
- interests: {state.get("interests", [])}
- constraints: {state.get("constraints", [])}

Do live travel research and produce practical notes.
"""
    result = research_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    content = result["messages"][-1].content
    return {"research_notes": content}


def planner_node(state: TravelState) -> TravelState:
    prompt = f"""
Create a practical itinerary.

User request:
{state.get("user_query", "")}

Research notes:
{state.get("research_notes", "")}

Constraints:
{state.get("constraints", [])}
"""
    result = planner_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    content = result["messages"][-1].content
    return {"itinerary": content}


def budgeter_node(state: TravelState) -> TravelState:
    prompt = f"""
Estimate whether this trip fits the budget.

User request:
{state.get("user_query", "")}
Budget target: {state.get("budget", "")}

Itinerary:
{state.get("itinerary", "")}
"""
    result = budget_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    content = result["messages"][-1].content
    return {"budget_breakdown": content}


def validator_node(state: TravelState) -> TravelState:
    prompt = f"""
Validate this full trip plan.

User request:
{state.get("user_query", "")}

Research notes:
{state.get("research_notes", "")}

Itinerary:
{state.get("itinerary", "")}

Budget:
{state.get("budget_breakdown", "")}

Return:
1. validation notes
2. final polished answer
"""
    result = validator_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    content = result["messages"][-1].content
    return {
        "validation_notes": content,
        "final_answer": content
    }


def route_after_supervisor(state: TravelState) -> str:
    nxt = state.get("next_agent", "researcher")
    if nxt == "researcher":
        return "researcher"
    if nxt == "planner":
        return "planner"
    if nxt == "budgeter":
        return "budgeter"
    if nxt == "validator":
        return "validator"
    return "finish"


def loop_back(_: TravelState) -> str:
    return "supervisor"


def build_graph():
    builder = StateGraph(TravelState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("planner", planner_node)
    builder.add_node("budgeter", budgeter_node)
    builder.add_node("validator", validator_node)

    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "researcher": "researcher",
            "planner": "planner",
            "budgeter": "budgeter",
            "validator": "validator",
            "finish": END,
        }
    )

    builder.add_conditional_edges("researcher", loop_back, {"supervisor": "supervisor"})
    builder.add_conditional_edges("planner", loop_back, {"supervisor": "supervisor"})
    builder.add_conditional_edges("budgeter", loop_back, {"supervisor": "supervisor"})
    builder.add_conditional_edges("validator", loop_back, {"supervisor": "supervisor"})

    return builder.compile()