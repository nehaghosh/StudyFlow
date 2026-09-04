import os
import json
from datetime import date

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


class StudyFlowAgent:

    def __init__(self, memory, tools):

        self.memory = memory
        self.tools = tools

        # Groq connection
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

        self.today = date.today().strftime("%Y-%m-%d")

        # =====================================================
        # TOOL 1 + TOOL 2 DEFINITIONS
        # =====================================================

        self.tool_schemas = [

            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": (
                        "Add a study assignment, project, exam or "
                        "academic task to memory."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {

                            "subject": {
                                "type": "string"
                            },

                            "task": {
                                "type": "string"
                            },

                            "deadline": {
                                "type": "string",
                                "description": "YYYY-MM-DD"
                            },

                            "estimated_hours": {
                                "type": "number"
                            }
                        },
                        "required": [
                            "subject",
                            "task",
                            "deadline",
                            "estimated_hours"
                        ]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "build_schedule",
                    "description": (
                        "Create a study schedule from the tasks "
                        "stored in memory."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {

                            "daily_hours": {
                                "type": "number",
                                "description": (
                                    "Normal study hours per day."
                                )
                            },

                            "start_date": {
                                "type": "string",
                                "description": "YYYY-MM-DD"
                            },

                            "custom_hours": {
                                "type": "object",
                                "description": (
                                    "Optional custom hours for "
                                    "specific dates."
                                ),
                                "additionalProperties": {
                                    "type": "number"
                                }
                            }
                        },
                        "required": [
                            "daily_hours",
                            "start_date"
                        ]
                    }
                }
            }
        ]

    # =========================================================
    # MEMORY
    # =========================================================

    def get_memory_context(self):

        return {
            "stored_tasks": self.memory.get_tasks(),
            "recent_conversation": (
                self.memory.get_conversation()[-10:]
            )
        }

    # =========================================================
    # EXECUTE TOOLS
    # =========================================================

    def execute_tool(self, tool_name, arguments):

        if tool_name == "add_task":

            return self.tools.add_task(
                subject=arguments["subject"],
                task=arguments["task"],
                deadline=arguments["deadline"],
                estimated_hours=arguments["estimated_hours"]
            )

        if tool_name == "build_schedule":

            return self.tools.build_schedule(
                daily_hours=arguments.get(
                    "daily_hours",
                    3
                ),

                start_date=arguments.get(
                    "start_date",
                    self.today
                ),

                custom_hours=arguments.get(
                    "custom_hours",
                    {}
                )
            )

        return {
            "success": False,
            "error": "Unknown tool."
        }

    # =========================================================
    # MAIN AGENT
    # =========================================================

    def run(self, user_request):

        # Save user message in memory
        self.memory.add_message(
            "user",
            user_request
        )

        # =====================================================
        # SYSTEM PROMPT
        # =====================================================

        system_prompt = f"""
You are StudyFlow, a specialized AI study-planning agent.

Today's date is {self.today}.

============================================================
SCOPE
============================================================

You ONLY help with:

- Study planning
- Assignments
- Projects
- Exams
- Deadlines
- Subjects
- Study schedules
- Study time
- Academic task prioritization
- Replanning
- Remembering study tasks

You are NOT a general-purpose chatbot.

If the user asks something unrelated to studying, DO NOT
answer that question.

Instead say:

"That is outside StudyFlow's scope. I can help you with
assignments, exams, deadlines, study schedules and study time."

Keep the response short.

============================================================
AGENT BEHAVIOUR
============================================================

You are an autonomous AGENT.

When a task requires an action:

1. Understand the user's goal.
2. Decide which tool is needed.
3. Call the tool.
4. Inspect the result.
5. Decide whether another tool is needed.
6. Give the final answer.

Do not pretend to call a tool.

============================================================
ADDING TASKS
============================================================

When the user gives a new assignment, project, exam or study
task, use add_task.

If multiple tasks are provided, add each task separately.

Never invent:
- Deadline
- Estimated hours
- Subject
- Task details

============================================================
SCHEDULING
============================================================

When the user asks for a study plan, use build_schedule.

The user controls their study hours.

3 hours per day is ONLY the default when the user does not
specify study hours.

The user can study 1, 2, 3, 5, 6 or any other reasonable
number of hours.

The user can also specify different hours for different days.

For example:

"I can study 6 hours today and 3 hours tomorrow."

Use custom_hours for this.

============================================================
MEMORY
============================================================

Use the stored tasks when the user refers to previous tasks.

For example:

"What assignments do I have?"

Use memory instead of asking the user to provide them again.

============================================================
FINAL ANSWERS
============================================================

Keep answers concise.

For study schedules show:

Date
Subject
Task
Study hours
Deadline

If a task cannot fit before its deadline, clearly warn the user.

============================================================
MEMORY DATA
============================================================

{json.dumps(self.get_memory_context(), indent=2)}

Stay strictly within StudyFlow's purpose.
"""

        # =====================================================
        # MESSAGES
        # =====================================================

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Previous conversation
        conversation = self.memory.get_conversation()

        for message in conversation[:-1][-10:]:

            messages.append({
                "role": message["role"],
                "content": message["content"]
            })

        # Current request
        messages.append({
            "role": "user",
            "content": user_request
        })

        # =====================================================
        # PLAN → ACT → OBSERVE LOOP
        # =====================================================

        trace = []

        for step in range(1, 9):

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_schemas,
                tool_choice="auto",
                temperature=0.2
            )

            message = response.choices[0].message

            # -------------------------------------------------
            # Agent finished
            # -------------------------------------------------

            if not message.tool_calls:

                final_answer = message.content

                if not final_answer:
                    final_answer = (
                        "I could not generate a response."
                    )

                self.memory.add_message(
                    "assistant",
                    final_answer
                )

                return {
                    "response": final_answer,
                    "trace": trace
                }

            # -------------------------------------------------
            # Agent requested a tool
            # -------------------------------------------------

            messages.append(message)

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name

                try:

                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                except json.JSONDecodeError:

                    arguments = {}

                    result = {
                        "success": False,
                        "error": "Invalid tool arguments."
                    }

                else:

                    result = self.execute_tool(
                        tool_name,
                        arguments
                    )

                # Save agent trace
                trace.append({
                    "step": step,
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result
                })

                # Send result back to LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        # =====================================================
        # SAFETY FALLBACK
        # =====================================================

        final_answer = (
            "I reached the maximum planning steps. "
            "Please try again."
        )

        self.memory.add_message(
            "assistant",
            final_answer
        )

        return {
            "response": final_answer,
            "trace": trace
        }