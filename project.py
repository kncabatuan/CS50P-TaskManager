from colorama import Fore
from datetime import date
from typing import Union
import csv
import os
import re
import sys
import time

# Main prompts
main_prompt_a = """
        
Welcome to the Task Manager!

Do you have an existing task list file(.csv)? Y/N


Note: You can type "exit" to close the program anytime :)
      You can\'t name files you create "exit"
            
"""

main_prompt_b = f"""

Please choose an option (1-8):
1: View Tasks
2: Add Task        
3: Mark Task as Done
4: Export Task to Excel/PDF
5: Remove Task
6: Create New File
7: Load New File
8: Exit

"""

# CSV field names
fieldnames = ["id", "task", "status", "due_date", "time_left"]

# Delay time (in seconds) between operations
delay = 1.5


class Taskfile:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, filename: str) -> None:
        """Validates the file name and extension.

        Args:
            filename (str): The file path to validate.

        Raises:
            ValueError: If the file name or extension is invalid.
        """
        invalid_chars = r'[<>:"/\\|?*]'
        name, ext = os.path.splitext(filename)

        if re.match(r"^\..*$", name) or re.match(r"^.*\.$", name):
            raise ValueError

        if re.search(invalid_chars, name):
            raise ValueError

        if ext != ".csv" and ext != "":
            raise ValueError

        if ext == "":
            self._filename = filename + ".csv"
        else:
            self._filename = filename

    @classmethod
    def create_file(cls, filename: str) -> "Taskfile":
        """Creates a new CSV file with the specified field names.

        Args:
            filename (str): The name of the file to be created.

        Returns:
            Taskfile: An instance of Taskfile representing the created file.

        Raises:
            ValueError: If the file name or extension is invalid.
            FileExistsError: If the file already exists.
            PermissionError: If there are insufficient permissions to create the file.
            OSError: If an unexpected error occurs during file creation.
        """
        task_file = cls(filename)
        with open(task_file.filename, "x", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        return task_file

    @classmethod
    def load_file(cls, filename: str) -> "Taskfile":
        """Opens the specified file to ensure it exists and is accessible.

        Args:
            filename (str): The name of file to load.

        Returns:
            Taskfile: An instance of Taskfile representing the loaded file.

        Raises:
            FileNotFoundError: If the file does not exist.
            IsADirectoryError: If the specified path is a directory.
            PermissionError: If there are insufficient permissions to access the file.
            OSError: If an unexpected error occurs during file access.
        """
        with open(filename, "r"):
            pass
        return cls(filename)

    def update_tasks(self, filename: str) -> None:
        """Overwrites csv file with updated task information.

        Recalculates the time left for each task and updates the status of overdue tasks.

        Args:
            filename (str): The name of task list file to update.
        """
        try:
            with open(filename, "r") as file:
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

            with open(filename, "w", newline="") as file:
                fieldnames = ["id", "task", "status", "due_date", "time_left"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for task in task_list:
                    writer.writerow(task)
        except OSError:
            print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")


def main() -> None:
    """Main function to run the Task Manager program.

    Handles user interaction for loading/creating task files and performing task operations.
    """
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
        match get_user_choice(task_file.filename):
            case 1:
                view_task()
            case 2:
                if add_task(task_file.filename):
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
    """Gets the user's yes/no answer on whether they have an existing task list file.

    Returns:
        str: The user's answer, either 'Y', 'N', or 'EXIT'.
    """
    while True:
        answer = input(Fore.WHITE + main_prompt_a).strip().upper()
        try:
            return answer_is_valid(answer)
        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter Y, N, or exit.")
            time.sleep(delay)
            continue


def answer_is_valid(answer: str) -> str:
    """Validates the user's yes/no answer.

    Args:
        answer (str): The user's input answer.

    Returns:
        str: The validated answer.

    Raises:
        ValueError: If the answer is not 'Y', 'N', or 'EXIT'.
    """
    if not re.search(r"^([YN]|EXIT)$", answer):
        raise ValueError
    return answer


def load_new_file() -> "Taskfile":
    """Prompts the user to load an existing task list file.

    Loops until a valid file name is provided and the file is loaded.

    Returns:
        Taskfile: An instance of Taskfile representing the loaded file.
    """
    while True:
        filename = input(
            Fore.WHITE + "\n\nPlease enter the file name (with .csv extension): "
        ).strip()
        if filename.lower() == "exit":
            exit()
        elif task_file := check_file_access(filename):
            task_file.update_tasks(task_file.filename)
            print(
                Fore.GREEN + "\nFile accessed successfully! Proceeding to Main Menu..."
            )
            time.sleep(delay)
            return task_file
        else:
            time.sleep(delay)
            continue


def check_file_access(filename: str) -> Union["Taskfile", bool]:
    """Validates the file name and attempts to load the file.

    Args:
        filename (str): The file name provided by the user.

    Returns:
        Taskfile: An instance of Taskfile if the file is loaded successfully.
        bool: False if the file loading fails due to validation or other errors.
    """
    try:
        return Taskfile.load_file(filename)
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


def create_new_file() -> "Taskfile":
    """Prompts the user to create a new task list file.

    Loops until a valid file name is provided and the file is created.

    Returns:
        Taskfile: An instance of Taskfile representing the created file.
    """
    while True:
        filename = input(Fore.WHITE + "\n\nEnter the new file name (csv): ").strip()
        if filename.lower() == "exit":
            exit()
        elif task_file := filename_is_valid(filename):
            print(
                Fore.GREEN + "\nFile created successfully! Proceeding to Main Menu..."
            )
            time.sleep(delay)
            return task_file
        else:
            time.sleep(delay)
            continue


def filename_is_valid(filename: str) -> Union["Taskfile", bool]:
    """Validates the file name and attempts to create the file.

    Args:
        filename (str): The file name provided by the user.

    Returns:
        Taskfile: An instance of Taskfile if the file is created successfully.
        bool: False if the file creation fails due to validation or other errors.
    """
    try:
        return Taskfile.create_file(filename)
    except ValueError:
        print(
            Fore.RED
            + "\nInvalid file name or extension. Please avoid special characters."
        )
        return False
    except FileExistsError:
        print(Fore.RED + "\nFile already exists. Please choose a different name.")
        return False
    except PermissionError:
        print(Fore.RED + "\nYou do not have permission to create this file.")
        return False
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while creating the file.")
        return False


def get_user_choice(filename: str) -> int:
    """Gets the user's choice from the main menu.

    Loops until a valid choice (1-8) is entered.
    Closes program if user types "exit".

    Args: 
        filename (str): The name of the currently loaded task list file.

    Returns:
        int: The user's menu choice, an integer between 1 and 8.
    """
    while True:
        choice = input(
            Fore.WHITE + f"\n\nLoaded File: {filename}" + Fore.WHITE + main_prompt_b
        ).strip()

        try:
            choice = choice_is_valid(choice)
            if choice == "exit":
                exit()
            else:
                return int(choice)
        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter a number between 1 and 8, or \"exit\".")
            continue


def choice_is_valid(choice: str) -> str:
    """Validates the user's menu choice.

    Args:
        choice (str): The user's input choice.

    Returns:
        str: The validated choice (1-8) or "exit".

    Raises:
        ValueError: If the choice is not between 1 and 8.
    """
    if not re.search(r"^([1-8]|exit)$", choice.lower()):
        raise ValueError
    return choice.lower()


# Function to add tasks
def add_task(filename: str) -> bool:
    """Prompts the user for the new task to add and due date.
    
    Calculates the time left for the task
    Appends new data to the specified CSV file.
    Closes the program if the user types "exit" at any prompt.
    
    Args:
        filename (str): The name of the task list file to which the task will be added.
        
    Returns:
        bool: True if the task is added successfully, False otherwise.
    """
    task_to_add = input(Fore.WHITE + "\nWhat is the task you want to add? ").strip()
    if task_to_add.lower() == "exit":
        exit()
    task_due_date = get_due_date()
    time_left = (date.__sub__(task_due_date, date.today())).days

    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            task_list = list(reader)

        with open(filename, "a", newline="") as file:
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
    Closes program if user types "exit".

    Returns:
        date: The validated due date as a date object.
    """
    while True:
        due_date_input = input(
            Fore.WHITE + "\nEnter the due date (YYYY-MM-DD): "
        ).strip().lower()

        try:
            due_date = date_is_valid(due_date_input)
            if due_date == "exit":
                exit()
            else:
                return due_date
        except (TypeError, ValueError):
            print(
                Fore.RED + "\nInvalid date. Please enter the date in YYYY-MM-DD format."
            )
            continue


def date_is_valid(date_input: str) -> Union[date, str]:
    """Validates the input string and returns a date object.

    Converts string in "YYYY-MM-DD" format into a date object.
    Raises exceptions if the input is invalid.

    Args:
        date_input (str): The user's input in "YYYY-MM-DD" format.

    Returns:
        date: The validated due date as a date object.
        str: "exit" if the user wants to exit.

    Raises:
        TypeError: If the date components cannot be converted to integers.
        ValueError: If the date is not valid.
    """
    if date_input == "exit":
        return "exit"
    else:
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


# Function to exit
def exit() -> None:
    """Terminates the program with a thank you message."""
    sys.exit(Fore.GREEN + "\nThank you for using Task Manager!")


if __name__ == "__main__":
    main()
