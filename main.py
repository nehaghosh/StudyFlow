from memory import AgentMemory
from tools import StudyTools
from agent import StudyFlowAgent


def main():

    print("=" * 60)
    print("                 📚 STUDYFLOW")
    print("          Agentic AI Study Planner")
    print("=" * 60)

    memory = AgentMemory()
    tools = StudyTools(memory)
    agent = StudyFlowAgent(memory, tools)

    print("\nStudyFlow is ready!")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower().strip() == "exit":
            print("\nGoodbye! 👋")
            break

        if not user_input.strip():
            continue

        try:

            result = agent.run(user_input)

            print("\nStudyFlow:")
            print(result["response"])

            print("\n" + "-" * 60)
            print("Agent actions:")

            for step in result["trace"]:

                print(
                    f"Step {step['step']} → "
                    f"{step['tool']}"
                )

            print("-" * 60)

        except Exception as error:

            print("\n❌ Something went wrong:")
            print(error)


if __name__ == "__main__":
    main()