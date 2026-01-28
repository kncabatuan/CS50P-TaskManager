from colorama import Fore
from datetime import date
import csv
import os
import re
import sys
import time

main_prompt = """
        
Welcome to the Task Manager!
            
Please choose an option:
1: View Tasks
2: Add Task        
3: Mark Task as Done
4: Export Task to Excel/PDF
5: Remove Task
6: Exit
            
"""

fieldnames = ["id", "task", "status", "due_date", "time_left"]


def main() -> None:
    """Main function to run the Task Manager application.

    Runs an infinite loop to display the main menu and handle user choices.

    """
    # Set a delay time (in seconds) between operations
    delay = 2

    while True:
        match get_user_choice():
            case 1:
                view_task()
            case 2:
                if add_task():
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
                exit()

        time.sleep(delay)


def get_user_choice() -> int:
    """Gets the user's choice from the main menu.

    Loops until a valid choice (1-6) is entered.

    Returns:
        int: The user's menu choice, an integer between 1 and 6.
    """
    while True:
        choice = input(Fore.WHITE + main_prompt).strip()
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
    if not re.search(r"^[1-6]$", choice):
        raise ValueError

    return choice


# Function to add tasks
def add_task() -> bool:
    """Adds a new task to either an existing file or a new file.

    Loops until the user provides a valid response regarding existing file.

    Returns:
        bool: True if the task was added successfully, False otherwise.
    """
    while True:
        is_existing = (
            input(Fore.WHITE + "\nDo you have an existing task list file(.csv)? Y/N: ")
            .strip()
            .upper()
        )

        try:
            answer_is_valid(is_existing)

            if is_existing == "Y":
                return write_task_existing_file()
            else:
                return write_task_new_file()

        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter Y or N.")
            continue


def answer_is_valid(answer: str):
    """Validates the user's yes/no answer.

    Args:
        answer (str): The user's input answer.

    Raises:
        ValueError: If the answer is not 'Y' or 'N'.
    """
    if not re.search(r"^[YN]$", answer):
        raise ValueError


# Function to view tasks
def view_task(): ...


# Function to Mark task as done
def mark_task_as_done(): ...


# Function to Remove tasks
def remove_task(): ...


# Function to save tasks
def save_task(): ...


# Function to exit
def exit() -> None:
    """Terminates the program with a thank you message."""
    sys.exit(Fore.GREEN + "\nThank you for using Task Manager!")


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


def update_tasks(source: str) -> bool:
    """Updates the id, status, and time_left of tasks in the given CSV file.

    Opens the csv file, recalculates the time_left for each task, updates the status,
    re-numbers the ids, and writes the updated tasks back to the file.

    Args:
        source (str): The path to the CSV file containing tasks.

    Returns:
        bool: True if the tasks were updated successfully, False if the file was not found.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If there are permission issues accessing the file.
        IsADirectoryError: If the specified path is a directory, not a file.
        OSError: For other OS-related errors.
    """
    try:
        with open(source, "r") as file:
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

        with open(source, "w", newline="") as file:
            fieldnames = ["id", "task", "status", "due_date", "time_left"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for task in task_list:
                writer.writerow(task)

        return True
    except FileNotFoundError:
        print(Fore.RED + "\nFile not found. Please ensure the file exists.")
        return False
    except PermissionError:
        print(Fore.RED + "\nYou do not have permission to access this file")
        return False
    except IsADirectoryError:
        print(Fore.RED + "\nThe specified path is a directory, not a file.")
        return False
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return False


def write_task_existing_file() -> bool:
    """Adds a new task to an existing CSV file after updating existing tasks.

    Prompts the user for the file name, updates existing tasks, and appends the new task.

    Returns:
        bool: True if the task was added successfully, False otherwise.
    """
    filepath = input(
        Fore.WHITE + "\nPlease enter the file name (with .csv extension): "
    ).strip()

    if not update_tasks(filepath):
        return False

    task_to_add = input(Fore.WHITE + "\nWhat is the task you want to add? ").strip()
    task_due_date = get_due_date()
    time_left = (date.__sub__(task_due_date, date.today())).days

    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        task_list = list(reader)

    with open(filepath, "a", newline="") as file:
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


def write_task_new_file() -> bool:
    """Creates a new CSV file and adds a new task to it.

    Prompts the user for a new file name, validates it, and writes the new task.

    Returns:
        bool: True if the task was added successfully, False otherwise.
    """
    while True:
        filepath = input(Fore.WHITE + "\nEnter the new file name (csv): ").strip()

        if not filename_is_valid(filepath):
            print(
                Fore.RED
                + "\nInvalid file name or extension. Please avoid special characters."
            )
            continue

        if not re.search(r"\.csv$", filepath):
            filepath += ".csv"

        if os.path.exists(filepath):
            print(Fore.RED + "\nFile already exists. Please choose a different name.")
            continue
        break

    task_to_add = input(Fore.WHITE + "\nWhat is the task you want to add? ").strip()
    task_due_date = get_due_date()
    time_left = (date.__sub__(task_due_date, date.today())).days

    with open(filepath, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "id": 1,
                "task": task_to_add,
                "status": "Pending",
                "due_date": str(task_due_date),
                "time_left": str(time_left),
            }
        )

    return True


def filename_is_valid(source: str) -> bool:
    """Validates the provided filename for invalid characters and correct extension.

    Args:
        source (str): The filename to validate.

    Returns:
        bool: True if the filename is valid, False otherwise.
    """
    invalid_chars = r'[<>:"/\\|?*]'

    if re.search(r"\.", source):
        try:
            name, ext = source.split(".")
        except ValueError:
            return False

        if re.search(invalid_chars, name):
            return False

        if ext != "csv":
            return False
    else:
        if re.search(invalid_chars, source):
            return False

    return True


if __name__ == "__main__":
    main()
