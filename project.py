from colorama import Fore
from datetime import date
from typing import Union
import csv
import os
import pandas as pd
import re
import sys
import time

main_prompt_a = """
        
Welcome to the Task Manager!

Do you have an existing task list file(.csv)? Y/N


Note: You can type "exit" to close the program anytime :)
      You can\'t name files you create "exit"
            
"""

main_prompt_b = f"""

Please choose an option (1-6):
1: View Tasks
2: Add Task        
3: Mark Task as Done
4: Export Task to Excel/PDF
5: Remove Task
6: Create New File
7: Load New File
8: Exit

"""

fieldnames = ["id", "task", "status", "due_date", "time_left"]

# Set a delay time (in seconds) between operations
delay = 1.5


class Taskfile():
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    @property
    def filepath(self) -> str:
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: str) -> None:
        invalid_chars = r'[<>:"/\\|?*]'
        name, ext = os.path.splitext(filepath)

        if re.match(r"^\..*$", name) or re.match(r"^.*\.$", name):
            raise ValueError

        if re.search(invalid_chars, name):
            raise ValueError
        
        if ext != ".csv" and ext !="":
            raise ValueError
        
        if ext == "":
            self._filepath = filepath + ".csv"
        else:
            self._filepath = filepath

    @classmethod
    def create_file(cls, filepath: str) -> "Taskfile":
        task_file = cls(filepath)
        with open(task_file.filepath, "x", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        return task_file

    @classmethod
    def load_file(cls, filepath: str) -> "Taskfile":
        with open(filepath, "r"):
            pass
        return cls(filepath)
    

    def update_tasks(self, filepath: str) -> None:
        try:
            with open(filepath, "r") as file:
                reader = csv.DictReader(file)
                task_list = list(reader)

            updated_time_left = []
            for task in task_list:
                date_entry = map(int, task["due_date"].split("-"))
                updated_time_left.append(
                    (date.__sub__((date(*date_entry)), date.today())).days
                )

            for task in task_list:
                task["id"] = task_list.index(task) + 1
                task["time_left"] = updated_time_left[0]
                updated_time_left.pop(0)

                if task["time_left"] < 0 and task["status"] != "Done":
                    task["status"] = "Overdue"

            with open(filepath, "w", newline="") as file:
                fieldnames = ["id", "task", "status", "due_date", "time_left"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for task in task_list:
                    writer.writerow(task)
        except OSError:
            print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")


def main() -> None:
    while True:
        match get_user_answer_on_file():
            case "Y":
                task_file = load_new_file()
                break
            case "N":
                task_file = create_new_file()
                break
            case "EXIT":
                exit()

    while True:
        match get_user_choice(task_file.filepath):
            case 1:
                view_task()
            case 2:
                if add_task(task_file.filepath):
                    print(
                        Fore.GREEN
                        + "\nTask added successfully! Returning to Main Menu..."
                    )
                else:
                    print(Fore.RED + "\nFailed to add task. Returning to Main Menu...")
            case 3:
                mark_task_as_done()
            case 4:
                save_task()
            case 5:
                remove_task()
            case 6:
                create_new_file()
            case 7:
                task_file = load_new_file()
            case 8:
                exit()

        time.sleep(delay)


def get_user_answer_on_file() -> str:
    while True:
        answer = input(Fore.WHITE + main_prompt_a).strip().upper()
        try:
            return answer_is_valid(answer)
        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter Y or N.")
            time.sleep(delay)
            continue


def answer_is_valid(answer: str):
    """Validates the user's yes/no answer.

    Args:
        answer (str): The user's input answer.

    Raises:
        ValueError: If the answer is not 'Y' or 'N'.
    """
    if not re.search(r"^([YN]|EXIT)$", answer):
        raise ValueError
    return answer


def check_file_access(filepath: str) -> Union["Taskfile", bool]:
    try:
        return Taskfile.load_file(filepath)
    except FileNotFoundError:
        print(Fore.RED + "\nFile not found. Please ensure the file exists.")
        return False
    except IsADirectoryError:
        print(Fore.RED + "\nThe specified path is a directory, not a file.")
        return False
    except PermissionError:
        print(Fore.RED + "\nYou do not have permission to access this file")
        return False
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return False
    except ValueError:
        print(Fore.RED + "\nInvalid file name or extension.")
        return False


def filename_is_valid(source: str) -> Union["Taskfile", bool]:
    if os.path.exists(source):
        print(Fore.RED + "\nFile already exists. Please choose a different name.")
        return False

    try:
        return Taskfile.create_file(source)
    except ValueError:
        print(Fore.RED + "\nInvalid file name or extension. Please avoid special characters.")
        return False 
    except FileExistsError:
        print(Fore.RED + "\nFile already exists. Please choose a different name.")
        return False


def get_user_choice(source: str) -> int:
    """Gets the user's choice from the main menu.

    Loops until a valid choice (1-7) is entered.

    Returns:
        int: The user's menu choice, an integer between 1 and 6.
    """
    while True:
        choice = input(
            Fore.WHITE + f"\n\nLoaded File: {source}" +
            Fore.WHITE + main_prompt_b
        ).strip()
        if choice.lower() == "exit":
            exit()

        try:
            return int(choice_is_valid(choice))
        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter a number between 1 and 6.")
            continue


def choice_is_valid(choice: str) -> str:
    """Validates the user's menu choice.

    Args:
        choice (str): The user's input choice.

    Returns:
        str: The validated choice if it's between 1 and 6.

    Raises:
        ValueError: If the choice is not between 1 and 6.
    """
    if not re.search(r"^[1-8]$", choice):
        raise ValueError

    return choice


# Function to add tasks
def add_task(source: str) -> bool:
    task_to_add = input(Fore.WHITE + "\nWhat is the task you want to add? ").strip()
    if task_to_add.lower() == "exit":
        exit()
    task_due_date = get_due_date()
    time_left = (date.__sub__(task_due_date, date.today())).days

    try:
        with open(source, "r") as file:
            reader = csv.DictReader(file)
            task_list = list(reader)

        with open(source, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow(
                {
                    "id": len(task_list) + 1,
                    "task": task_to_add,
                    "status": "Pending",
                    "due_date": str(task_due_date),
                    "time_left": str(time_left),
                }
            )
        return True
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return False


def get_due_date() -> date:
    """Prompts the user to enter a due date and validates the input.

    Loops until a valid date in YYYY-MM-DD format is provided.

    Returns:
        date: The validated due date as a date object.
    """
    while True:
        due_date_input = input(
            Fore.WHITE + "\nEnter the due date (YYYY-MM-DD): "
        ).strip()

        if due_date_input.lower() == "exit":
            exit()

        try:
            return date_is_valid(due_date_input)
        except (TypeError, ValueError):
            print(
                Fore.RED + "\nInvalid date. Please enter the date in YYYY-MM-DD format."
            )
            continue


def date_is_valid(date_input: str) -> date:
    """Validates the input string and returns a date object.

    Converts string in "YYYY-MM-DD" format into a date object.
    Raises exceptions if the input is invalid.

    Args:
        date_input (str): The user's input in "YYYY-MM-DD" format.

    Returns:
        date: The validated due date as a date object.

    Raises:
        TypeError: If the date components cannot be converted to integers.
        ValueError: If the date is not valid.
    """
    due_date = map(int, date_input.split("-"))
    return date(*due_date)


# Function to view tasks
def view_task(): ...


# Function to Mark task as done
def mark_task_as_done(): ...


# Function to Remove tasks
def remove_task(): ...


# Function to save tasks
def save_task(): ...


def create_new_file():
    while True:
        filepath = input(Fore.WHITE + "\n\nEnter the new file name (csv): ").strip()
        if filepath.lower() == "exit":
            exit()
        elif task_file := filename_is_valid(filepath):
            print(Fore.GREEN + "\nFile created successfully! Proceeding to Main Menu...")
            time.sleep(delay)
            return task_file
        else:
            time.sleep(delay)
            continue


def load_new_file():
    while True:
        filepath = input(Fore.WHITE + "\n\nPlease enter the file name (with .csv extension): ").strip()
        if filepath.lower() == "exit":
            exit()
        elif task_file := check_file_access(filepath):
            task_file.update_tasks(task_file.filepath)
            print(Fore.GREEN + "\nFile accessed successfully! Proceeding to Main Menu...")
            time.sleep(delay)
            return task_file
        else:
            time.sleep(delay)
            continue
    

# Function to exit
def exit() -> None:
    """Terminates the program with a thank you message."""
    sys.exit(Fore.GREEN + "\nThank you for using Task Manager!")


if __name__ == "__main__":
    main()
