from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from llm import LLM


class Message:
    def __init__(self, question: str, response: str = ""):
        self.question = question
        self.response = response

    def __repr__(self):
        return f"Message(question='{self.question}', response='{self.response}')"


class State(TypedDict):
    question: str
    messages: List[Message]


class ChatBot:

    def __init__(self):
        # Create the LLM instance
        self.llm = LLM()
        self.messages: List[Message] = []

        # Build LangGraph workflow
        graph = StateGraph(State)

        graph.add_node("question", self.question)
        graph.add_node("answer", self.answer)

        graph.add_edge(START, "question")
        graph.add_edge("question", "answer")
        graph.add_edge("answer", END)

        self.app = graph.compile()

    def question(self, state: State):
        messages = list(state.get("messages", []))
        message = Message(state["question"])
        messages.append(message)

        # Only track last 10 messages
        if len(messages) > 10:
            messages = messages[-10:]

        return {"messages": messages}

    def answer(self, state: State):
        messages = list(state.get("messages", []))
        if not messages:
            return {"messages": messages}

        message = messages[-1]

        # Call the LLM
        response = self.llm.ask(message.question)
        message.response = response

        return {"messages": messages}

    def ask(self, question: str) -> str:
        result = self.app.invoke({
            "question": question,
            "messages": self.messages
        })

        # Keep updated message history on instance
        self.messages = result["messages"]

        return self.messages[-1].response