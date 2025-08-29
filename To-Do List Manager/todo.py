#!/usr/bin/env python3
import json
import os
import pyfiglet
from termcolor import colored

# File to store tasks
TASK_FILE = "tasks.json"

# Load tasks
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    return []

# Save tasks
def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# Banner
def banner():
    ascii_banner = pyfiglet.figlet_format("To-Do CLI")
    print(colored(ascii_banner, "cyan"))

# List tasks
def list_tasks(tasks):
    if not tasks:
        print(colored("No tasks found!", "red"))
        return
    print(colored("Your Tasks:", "yellow"))
    for i, task in enumerate(tasks, start=1):
        status = "✅" if task["done"] else "❌"
        print(colored(f"{i}. {task['task']} [{status}]", "green"))

# Add task
def add_task(tasks, task_text):
    tasks.append({"task": task_text, "done": False})
    save_tasks(tasks)
    print(colored(f"Task added: {task_text}", "cyan"))

# Remove task
def remove_task(tasks, index):
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        save_tasks(tasks)
        print(colored(f"Task removed: {removed['task']}", "red"))
    else:
        print(colored("Invalid task number!", "red"))

# Mark as done
def mark_done(tasks, index):
    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
        save_tasks(tasks)
        print(colored(f"Task completed: {tasks[index]['task']}", "green"))
    else:
        print(colored("Invalid task number!", "red"))

# CLI Menu
def main():
    tasks = load_tasks()
    banner()
    
    while True:
        print(colored("\nOptions:", "yellow"))
        print("1. List tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Mark task as done")
        print("5. Exit")
        
        choice = input(colored("Enter choice: ", "cyan")).strip()
        
        if choice == "1":
            list_tasks(tasks)
        elif choice == "2":
            task_text = input(colored("Enter task: ", "cyan"))
            add_task(tasks, task_text)
        elif choice == "3":
            list_tasks(tasks)
            try:
                index = int(input(colored("Enter task number to remove: ", "cyan"))) - 1
                remove_task(tasks, index)
            except ValueError:
                print(colored("Invalid input!", "red"))
        elif choice == "4":
            list_tasks(tasks)
            try:
                index = int(input(colored("Enter task number to mark done: ", "cyan"))) - 1
                mark_done(tasks, index)
            except ValueError:
                print(colored("Invalid input!", "red"))
        elif choice == "5":
            print(colored("Goodbye! ✅", "yellow"))
            break
        else:
            print(colored("Invalid choice! Try again.", "red"))

if __name__ == "__main__":
    main()
