from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
from llm import invoke_llm , groq_llm
from prompts import (
    system_prompt_for_planner,
    system_prompt_for_modifier,
    system_prompt_for_formatter
)
import json
import re

load_dotenv()

# ---------------- SAFE JSON PARSER ---------------- #

def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        
        # Instead of raising error, return fallback
        return {"error": "Invalid JSON from model", "raw_output": text}



# ---------------- STATE ---------------- #

class PlannerState(TypedDict , total = False):
    goal: str
    current_level: str
    strengths: str
    weaknesses: str
    deadline: str
    additional_constraints: str

    structured_plan: dict
    formatted_plan: str
    modification_request: str
    plan_history: list[str]


# ---------------- NODES ---------------- #

def plan_generator(state: PlannerState) -> PlannerState:

    user_data = {
        "goal": state.get("goal", ""),
        "current_level": state.get("current_level", ""),
        "strengths": state.get("strengths", ""),
        "weaknesses": state.get("weaknesses", ""),
        "time_available_per_day": state.get("time_available_per_day", ""),
        "deadline": state.get("deadline", ""),
        "additional_constraints": state.get("additional_constraints", ""),
    }

    messages = [
        {"role": "system", "content": system_prompt_for_planner},
        {"role": "user", "content": json.dumps(user_data, indent=2)},
    ]

    response = invoke_llm(messages)

    parsed_plan = safe_json_parse(response)


    return {
        **state,
        "structured_plan": parsed_plan,
    }


def plan_modifier(state: PlannerState) -> PlannerState:

    user_data = {
        "goal": state.get("goal", ""),
        "current_level": state.get("current_level", ""),
        "strengths": state.get("strengths", ""),
        "weaknesses": state.get("weaknesses", ""),
        "deadline": state.get("deadline", ""),
        "additional_constraints": state.get("additional_constraints", ""),
    }

    messages = [
        {"role": "system", "content": system_prompt_for_modifier},
        {
            "role": "user",
            "content": f"""
        User Information:
        {json.dumps(user_data, indent=2)}

        Current Structured Plan:
        {json.dumps(state.get("structured_plan", {}), indent=2)}

        Modification Request:
        {state.get("modification_request", "")}
        """,
                },
            ]

    response = invoke_llm(messages)

    parsed_plan = safe_json_parse(response)

    return {
        **state,
        "structured_plan": parsed_plan,
        "modification_request": "",
    }


def plan_formatter(state: PlannerState) -> PlannerState:

    messages = [
        {"role": "system", "content": system_prompt_for_formatter},
        {"role": "user", "content": json.dumps(state.get("structured_plan", {}), indent=2)},
    ]

    response = groq_llm.invoke(messages)

    new_formatted_plan = response.content

    updated_history = state.get("plan_history", []).copy()
    updated_history.append(new_formatted_plan)

    return {
        **state,
        "formatted_plan": new_formatted_plan,
        "plan_history": updated_history,
    }

# ---------------- ROUTER ---------------- #

def router(state: PlannerState):
    if state.get("modification_request"):
        return "modify"
    return "generate"


# ---------------- GRAPH ---------------- #

graph = StateGraph(PlannerState)

graph.add_node("plan_generator", plan_generator)
graph.add_node("plan_modifier", plan_modifier)
graph.add_node("plan_formatter", plan_formatter)


graph.add_conditional_edges(
    START,
    router,
    {
        "modify": "plan_modifier",
        "generate": "plan_generator",
    },
)

graph.add_edge("plan_generator", "plan_formatter")
graph.add_edge("plan_modifier" , "plan_formatter")
graph.add_edge("plan_formatter", END)

app = graph.compile()



