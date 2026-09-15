from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from llm import LLM


class State(TypedDict):
    question: str
    response: str


class ChatBot:

    def __init__(self):
        self.llm = LLM()

        # Build single-step workflow without persistent memory
        graph = StateGraph(State)

        graph.add_node("answer", self.answer)
        graph.add_edge(START, "answer")
        graph.add_edge("answer", END)

        self.app = graph.compile()

    def answer(self, state: State) -> dict:
        response = self.llm.ask(state["question"])
        return {"response": response}

    def ask(self, question: str) -> str:
        # Pass state directly without maintaining self.messages on the instance
        result = self.app.invoke({"question": question, "response": ""})
        return result["response"]