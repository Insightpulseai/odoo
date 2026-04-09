"""Finance copilot agent — queries Databricks gold marts via Azure OpenAI."""

import json
import os
import sys

from openai import AzureOpenAI

from tools import TOOL_DEFINITIONS, TOOL_DISPATCH

SYSTEM_PROMPT = (
    "You are a finance copilot for InsightPulse AI. You answer questions about "
    "project profitability, portfolio health, budgets, and expenses using governed "
    "analytical data from Databricks gold marts. Be concise and cite specific numbers."
)


class FinanceCopilotAgent:
    def __init__(self) -> None:
        self.client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2024-06-01",
        )
        self.deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=self.messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        assistant_msg = response.choices[0].message

        while assistant_msg.tool_calls:
            self.messages.append(assistant_msg.model_dump())
            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                fn = TOOL_DISPATCH.get(fn_name)
                if fn is None:
                    result = json.dumps({"error": f"Unknown tool: {fn_name}"})
                else:
                    try:
                        result = fn(**fn_args)
                    except Exception as exc:
                        result = json.dumps({"error": str(exc)})
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=self.messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            assistant_msg = response.choices[0].message

        reply = assistant_msg.content or ""
        self.messages.append({"role": "assistant", "content": reply})
        return reply


def main() -> None:
    agent = FinanceCopilotAgent()
    print("Finance Copilot (type 'quit' to exit)")
    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input or user_input.lower() in ("quit", "exit"):
            break
        reply = agent.chat(user_input)
        print(f"\n{reply}")


if __name__ == "__main__":
    main()
