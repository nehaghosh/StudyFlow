# 📚 StudyFlow — Agentic AI Study Planner

StudyFlow is an AI-powered study planning agent that helps students manage academic tasks, deadlines and study schedules. Unlike a normal chatbot, StudyFlow can decide when to use tools, store tasks in memory, create schedules and use information from previous interactions.

StudyFlow uses two tools: `add_task` stores assignments, projects and other study tasks with their deadlines and estimated effort, while `build_schedule` creates a deadline-aware study plan. The user can customize their normal daily study time and provide different study hours for individual days when needed.

StudyFlow maintains session memory for stored tasks and conversation history. It also demonstrates an honest failure case by rejecting invalid deadline formats. The project uses Groq's OpenAI-compatible API and a Plan → Act → Observe loop to demonstrate agentic behaviour.

## Features

- AI study-planning agent
- Two real tools
- Plan → Act → Observe loop
- Session memory
- Deadline-aware scheduling
- Custom study hours
- Failure handling
- Jupyter Notebook demonstration

## Tools

### 1. `add_task`

Stores a study task in memory with:

- Subject
- Task
- Deadline
- Estimated hours

### 2. `build_schedule`

Creates a study schedule using:

- Stored tasks
- Deadlines
- Daily study hours
- Custom hours for specific dates

## Memory

StudyFlow remembers tasks and conversation history during the current session.

For example, after adding a DBMS assignment, the user can later ask:

> What assignments do I have?

The agent can use the stored memory instead of asking for the task again.

## Honest Failure

If an invalid deadline is provided, such as:

`not-a-date`

the tool rejects it and returns:

`Deadline must be in YYYY-MM-DD format.`

## ⚠️ Out-of-Scope Handling

StudyFlow is designed specifically for academic planning.
It should not behave like a general-purpose chatbot.

This test checks whether the agent correctly refuses a
non-academic question.

## Project Structure

```text
StudyFlow/
├── agent.py
├── tools.py
├── memory.py
├── main.py
├── test_tools.py
├── StudyFlow_Demo.ipynb
├── README.md
├── requirements.txt
├── .gitignore
└── .env
