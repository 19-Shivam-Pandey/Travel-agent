import re
from graph import build_graph
import langchain
langchain.debug = True

def extract_basic_fields(user_query: str):
    # Simple fallback parsing so the graph starts with useful state.
    days = 3
    budget = 0.0

    day_match = re.search(r"(\d+)\s*day", user_query, re.I)
    if day_match:
        days = int(day_match.group(1))

    budget_match = re.search(r"(\d+(?:,\d+)?(?:\.\d+)?)", user_query.replace(",", ""))
    if budget_match:
        try:
            budget = float(budget_match.group(1))
        except Exception:
            budget = 0.0

    return days, budget


def main():
    app = build_graph()

    user_query = input("Enter your travel request: ").strip()
    days, budget = extract_basic_fields(user_query)

    input_state = {
        "user_query": user_query,
        "days": days,
        "budget": budget,
        "research_notes": "",
        "itinerary": "",
        "budget_breakdown": "",
        "validation_notes": ""
    }

    # -------- AGENT THINKING OUTPUT --------
    print("\n===== AGENT THINKING =====\n")

    for event in app.stream(input_state):
        for node, output in event.items():
            print(f"\n--- {node.upper()} ---")
            print(output)

    print("\n===== EXECUTION COMPLETE =====\n")
    # ---------------------------------------

    result = app.invoke(input_state)

    print("\n" + "=" * 80)
    print("FINAL TRAVEL ANSWER")
    print("=" * 80)
    print(result.get("final_answer", "No answer generated."))


if __name__ == "__main__":
    main()