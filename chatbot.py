from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from llm import LLM


class State(TypedDict):
    question: str
    context: str
    response: str


class ChatBot:

    def __init__(self):
        self.llm = LLM()

        # Build workflow with context-grounded response and verification nodes
        graph = StateGraph(State)

        # 1. Add nodes
        graph.add_node("answer", self.answer)
        graph.add_node("check_hallucination", self.check_hallucination)

        # 2. Define the execution flow: START -> answer -> check_hallucination -> END
        graph.add_edge(START, "answer")
        graph.add_edge("answer", "check_hallucination")
        graph.add_edge("check_hallucination", END)

        self.app = graph.compile()

    def answer(self, state: State) -> dict:
        """Generates an answer strictly grounded in the provided context."""
        prompt = (
            "You are an expert Islamic textual scholar. Answer the question using STRICTLY and "
            "EXCLUSIVELY the provided context below.\n\n"
            "STRICT CONSTRAINTS:\n"
            "1. Grounding: Every statement MUST be directly supported by a specific verse or Hadith "
            "from the provided context. Do NOT use outside knowledge or unprovided sources.\n"
            "2. Zero Hallucination: If a concept is not explicitly mentioned in the context, do NOT infer or invent it.\n"
            "3. Citations: Explicitly cite the source (e.g., 'Surah 19:33', 'Sahih Muslim 897') for every claim.\n"
            "4. Format: Provide a direct scholar-level summary. Do NOT include polite commentary or critique.\n\n"
            f"Context:\n{state['context']}\n\n"
            f"Question:\n{state['question']}"
        )
        response = self.llm.ask(prompt)
        return {"response": response}

    def check_hallucination(self, state: State) -> dict:
        """Verifies and strips any external knowledge or ungrounded claims."""
        prompt = (
            "You are a strict textual auditor. Review the draft response against the source context.\n\n"
            "TASK:\n"
            "1. Remove any claims, facts, or concepts NOT directly supported by the source context.\n"
            "2. Ensure every point cites its source from the context.\n"
            "3. Remove meta-commentary, compliments, or general advice.\n"
            "4. Return ONLY the finalized, verified textual analysis.\n\n"
            f"Source Context:\n{state['context']}\n\n"
            f"Draft Response:\n{state['response']}"
        )
        verified_response = self.llm.ask(prompt)
        return {"response": verified_response}

    def ask(self, question: str, context: str = "") -> str:
        print(f"Question: {question}")

        # Detect translation requests
        is_translation = question.strip().lower().startswith(
            "translate the following text"
        )

        if is_translation:
            prompt = (
                f"{question}\n\n"
                "Return ONLY the English translation. "
                "Do not provide explanations, context, commentary, or additional text."
            )

            return self.llm.ask(prompt).strip()

        # Normal Quran/Hadith RAG workflow
        result = self.app.invoke(
            {
                "question": question,
                "context": context,
                "response": ""
            }
        )

        return result["response"]