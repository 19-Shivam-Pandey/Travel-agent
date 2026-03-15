from typing import TypedDict, List, Dict, Any, Optional

class TravelState(TypedDict, total=False):
    user_query: str
    messages: List[Dict[str, Any]]

    destination: str
    days: int
    budget: float
    interests: List[str]
    constraints: List[str]

    research_notes: str
    itinerary: str
    budget_breakdown: str
    validation_notes: str
    final_answer: str

    next_agent: str
    done: bool