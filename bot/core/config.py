import json


# Тоен вашего бота 
API_TOKEN = "5826587922:AAGcKRyNx-dQqsUnmdKKxMVC39z0G_f5XDw"
# Tasks
with open("core/data.json", "r") as data:
    data = json.loads(data.read())


tasks_data = data['tasks']
tasks = len(tasks_data)


# Modes
modes = data["modes"]