class AgentMemory:
    def __init__(self):
        self.tasks = {}
        self.conversation = []

    def add_task(self, task):
        task_id = len(self.tasks) + 1
        self.tasks[task_id] = task
        return task_id

    def get_tasks(self):
        return self.tasks

    def add_message(self, role, content):
        self.conversation.append({
            "role": role,
            "content": content
        })

    def get_conversation(self):
        return self.conversation