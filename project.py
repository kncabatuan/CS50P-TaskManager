from colorama import Fore
from datetime import date
from prettytable.colortable import ColorTable, Themes
from typing import Union
import csv
import os
import pandas as pd
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
4: Export Task to MS Excel
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

    def __repr__(self) -> str:
        return f"Taskfile(filename = {self._filename})"

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

        if name == "":
            raise ValueError

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
            PermissionError: If there are insufficient permissions to access the file.
            OSError: If an unexpected error occurs during file access.
            ValueError: If the file name or extension is invalid.
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

                if int(task["time_left"]) < 0 and task["status"] != "Done":
                    task["status"] = "Overdue"

            with open(filename, "w", newline="") as file:
                fieldnames = ["id", "task", "status", "due_date", "time_left"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for task in task_list:
                    writer.writerow(task)
        except OSError:
            print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")


# Error used for id input validation in mark_task_as_done and remove_task
class IdNotFoundError(Exception):
    pass


class YesNoError(Exception):
    pass


def main() -> None:
    """Main function to run the Task Manager program.

    Handles user interaction for loading/creating task files and performing task operations.
    """
    while True:
        match get_user_answer():
            case "Y":
                task_file = load_new_file()
                time.sleep(delay)
                break
            case "N":
                task_file = create_new_file()
                time.sleep(delay)
                break
            case "EXIT":
                exit()

    while True:
        match get_user_choice(task_file.filename):
            case 1:
                view_task(task_file.filename)
            case 2:
                if add_task(task_file.filename):
                    print(
                        Fore.GREEN
                        + "\nTask added successfully! Returning to Main Menu..."
                    )
                else:
                    print(Fore.RED + "\nFailed to add task. Returning to Main Menu...")
            case 3:
                mode = "mark_task_as_done"
                if modify_tasks(task_file.filename, mode):
                    print(
                        Fore.GREEN
                        + "\nTasks updated successfully! Returning to Main Menu..."
                    )
                else:
                    print(
                        Fore.RED + "\nFailed to update tasks. Returning to Main Menu..."
                    )
            case 4:
                if export_task(task_file.filename):
                    print(
                        Fore.GREEN
                        + "\nCSV file successfully exported to MS Excel! Returning to Main Menu..."
                    )
                else:
                    print(
                        Fore.RED
                        + "\nFailed to export CSV file to MS Excel. Returning to Main Menu..."
                    )
            case 5:
                mode = "remove_task"
                if modify_tasks(task_file.filename, mode):
                    print(
                        Fore.GREEN
                        + "\nTask removed successfully! Returning to Main Menu..."
                    )
                else:
                    print(
                        Fore.RED + "\nFailed to Remove Task. Returning to Main Menu..."
                    )
            case 6:
                task_file = create_new_file()
            case 7:
                task_file = load_new_file()
            case 8:
                exit()

        time.sleep(delay)


def get_user_answer() -> str:
    """Gets the user's yes/no answer on whether they have an existing task list file.

    Returns:
        str: The user's answer, either 'Y', 'N', or 'EXIT'.
    """
    while True:
        answer = input(Fore.WHITE + main_prompt_a).strip().upper()
        try:
            return answer_is_valid(answer)
        except YesNoError:
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
        YesNoError: If the answer is not 'Y', 'N', or 'EXIT'.
    """
    if not re.search(r"^([YN]|EXIT)$", answer):
        raise YesNoError
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
            return task_file
        else:
            time.sleep(delay)
            continue


def check_file_access(filename: str) -> Union["Taskfile", None]:
    """Validates the file name and attempts to load the file.

    Args:
        filename (str): The file name provided by the user.

    Returns:
        Taskfile: An instance of Taskfile if the file is loaded successfully.
        None: If an exception occurs
    """
    try:
        return Taskfile.load_file(filename)
    except FileNotFoundError:
        print(Fore.RED + "\nFile not found. Please ensure the file exists.")
        return None
    except PermissionError:
        print(Fore.RED + "\nYou do not have permission to access this file")
        return None
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return None
    except ValueError:
        print(Fore.RED + "\nInvalid file name or extension.")
        return None


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
            return task_file
        else:
            time.sleep(delay)
            continue


def filename_is_valid(filename: str) -> Union["Taskfile", None]:
    """Validates the file name and attempts to create the file.

    Args:
        filename (str): The file name provided by the user.

    Returns:
        Taskfile: An instance of Taskfile if the file is created successfully.
        None: If an exception occurs
    """
    try:
        return Taskfile.create_file(filename)
    except ValueError:
        print(
            Fore.RED
            + "\nInvalid file name or extension. Please avoid special characters."
        )
        return None
    except FileExistsError:
        print(Fore.RED + "\nFile already exists. Please choose a different name.")
        return None
    except PermissionError:
        print(Fore.RED + "\nYou do not have permission to create this file.")
        return None
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while creating the file.")
        return None


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
            Fore.BLUE + f"\n\nLoaded File: {filename}" + Fore.WHITE + main_prompt_b
        ).strip()

        try:
            choice = choice_is_valid(choice)
            if choice == "exit":
                exit()
            else:
                return int(choice)
        except ValueError:
            print(
                Fore.RED
                + '\nInvalid input. Please enter a number between 1 and 8, or "exit".'
            )
            time.sleep(delay)
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
        due_date_input = (
            input(Fore.WHITE + "\nEnter the due date (YYYY-MM-DD): ").strip().lower()
        )
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
        str: "exit" if the user wants to exit.

    Raises:
        SystemExit: If the user input is "exit"
        TypeError: If the date components cannot be converted to integers.
        ValueError: If the date is not valid.
    """
    if date_input == "exit":
        raise SystemExit
    else:
        due_date = map(int, date_input.split("-"))
        return date(*due_date)


def view_task(filename: str) -> None:
    """Displays the tasks from the specified CSV file in a formatted table.

    Displays tasks with color coding based on their status

    Args:
        filename (str): The name of the task list file to view.
    """
    table = ColorTable(theme=Themes.OCEAN)
    table.field_names = [s.upper() for s in fieldnames]

    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            for task in reader:
                if task["status"] == "Done":
                    table.add_row(
                        [
                            Fore.GREEN + task["id"],
                            Fore.GREEN + task["task"].capitalize(),
                            Fore.GREEN + task["status"].capitalize(),
                            Fore.GREEN + task["due_date"],
                            Fore.GREEN + task["time_left"],
                        ]
                    )
                elif task["status"] == "Overdue":
                    table.add_row(
                        [
                            Fore.RED + task["id"],
                            Fore.RED + task["task"].capitalize(),
                            Fore.RED + task["status"].capitalize(),
                            Fore.RED + task["due_date"],
                            Fore.RED + task["time_left"],
                        ]
                    )
                else:
                    table.add_row(
                        [
                            Fore.WHITE + task["id"],
                            Fore.WHITE + task["task"].capitalize(),
                            Fore.WHITE + task["status"].capitalize(),
                            Fore.WHITE + task["due_date"],
                            Fore.WHITE + task["time_left"],
                        ]
                    )

        print(table)
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")


def modify_tasks(filename: str, mode: str) -> bool:
    """Prompts the user to enter the ID(s) of tasks to modify.

    Loops until valid ids are entered by the user. Then, modifies and
    overwrites the task file depending on what mode this function is called:
    mark_task_as_done or remove_task

    Args:
        filename (str): The name of the task list file to update.
        mode (str): Either mark_task_as_done or remove_task

    Returns:
        bool: True if tasks are updated successfully, False otherwise.
    """
    try:
        with open(filename, "r") as file:
            reader = csv.DictReader(file)
            task_list = list(reader)
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return False

    while True:
        try:
            valid_ids = range(1, len(task_list) + 1)

            if mode == "mark_task_as_done":
                prompt = (
                    Fore.WHITE
                    + "\nEnter the ID/s of completed task/s (comma-separated): "
                )
            elif mode == "remove_task":
                prompt = (
                    Fore.WHITE
                    + "\nEnter the ID/s of task/s to be removed (comma-separated): "
                )

            id_input = input(prompt).strip().lower()

            if id_input == "exit":
                exit()
            else:
                ids = id_is_valid(id_input, valid_ids)

            if mode == "mark_task_as_done":
                for task in task_list:
                    if task["id"] in ids:
                        if task["status"] == "Done":
                            print(Fore.RED + f"\nTask {task["id"]} is already done")
                        else:
                            task["status"] = "Done"
            elif mode == "remove_task":
                print(Fore.RED + "\nAre you sure you want to remove these tasks? Y/N\n")
                for task in task_list:
                    if task["id"] in ids:
                        print(f"Task {task["id"]}: {task["task"]}")

                answer = answer_is_valid((input(Fore.WHITE + "\n")).strip().upper())
                if answer == "Y":
                    for task in task_list:
                        if task["id"] in ids:
                            task_list.remove(task)
                elif answer == "N":
                    return False
                else:
                    exit()
            break
        except (ValueError, TypeError):
            print(
                Fore.RED
                + "\nInvalid input. Please enter valid task ID/s (comma-separated)."
            )
            continue
        except IdNotFoundError:
            print(
                Fore.RED
                + "\nOne or more task IDs not found. Please enter valid task ID/s."
            )
            continue
        except YesNoError:
            print(Fore.RED + "\nInvalid input. Please enter Y, N, or exit.")
            continue

    try:
        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for task in task_list:
                writer.writerow(task)
        return True
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return False


def id_is_valid(id_input: str, valid_ids: range) -> Union[list, str]:
    """Validates the input string of task IDs.

    Args:
        id_input (str): The user's input string of task IDs.
        valid_ids (range): A range object representing valid task IDs.

    Returns:
        list: A list of validated task IDs
        or
        str: "exit" if the user wants to exit.

    Raises:
        ValueError: If the input contains special characters.
        IdNotFoundError: If any of the provided IDs are not found in valid_ids.
    """
    if re.search(r"[\.!@#$%^&*()_+=\[\]{};:\"\\|<>/?~`]", id_input):
        raise ValueError

    id_list = map(str.strip, id_input.split(","))
    validated_ids = []
    for id in id_list:
        if not isinstance(int(id), int):
            raise ValueError
        if not int(id) in valid_ids:
            raise IdNotFoundError
        validated_ids.append(id)
    return validated_ids


def export_task(filename: str) -> bool:
    """Creates an xlsx file and exports the contents of the CSV file into it
    
    Args:
        filename (str): Name of the CSV file to be exported
        
    Returns:
        bool: True if export is successful, False otherwise
        
    Raises:
        OSError: If an unexpected error occurred while accessing the file.
        PermissionError: If not enough permission to access the file
    """
    try:
        df = pd.read_csv(filename)
        df.to_excel(get_xlsx_name(), sheet_name="Tasks", index=False)
        return True
    except OSError:
        print(Fore.RED + "\nAn unexpected error occurred while accessing the file.")
        return False
    except PermissionError:
        print(Fore.RED + "\nYou do not have permission to access this file")
        return False
    

def get_xlsx_name() -> str:
    """Prompts user to input a name for the new xlsx file
    
    Returns:
        str: Name of the xlsx file
    """
    while True:
        try:
            excel_name = input(Fore.WHITE + "\nPlease enter a name for your excel file (no extension):").strip()
            if excel_name.lower() == "exit":
                exit()
            return validate_xlsx_name(excel_name)
        except ValueError:
            print(Fore.RED + "\nInvalid file name. Please avoid special characters")
            continue
        except FileExistsError:
            print(Fore.RED + "\nFile already exists. Please choose a different name.")
            continue
    

def validate_xlsx_name(filename: str) -> str:
    """Validates the user input for the xlsx file
    
    Args:
        filename (str): User input for the name of the xlsx file
        
    Returns:
        str: The validated name of the xlsx file with .xlsx extension
        
    Raises:
        ValueError: If there are invalid characters in the name
        FileExistsError: If the file already exists
    """
    invalid_chars = r'[<>:"/\\|?*]'

    if filename == "":
        raise ValueError

    if re.match(r"^\..*$", filename) or re.match(r"^.*\.$", filename):
        raise ValueError

    if re.search(invalid_chars, filename):
        raise ValueError
    
    if os.path.exists(f"{filename}.xlsx"):
        raise FileExistsError
    
    return f"{filename}.xlsx"
    

def exit() -> None:
    """Terminates the program with a thank you message."""
    sys.exit(Fore.GREEN + "\nThank you for using Task Manager!")


if __name__ == "__main__":
    main()
