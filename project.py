from colorama import Fore
from datetime import date
import csv
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


def main():
    delay = 1.5

    match get_user_choice():
        case 1:
            view_task()
        case 2:
            if add_task():
                print(Fore.GREEN + "\nTask added successfully!")
                time.sleep(delay)
                main()
            else:
                print(Fore.RED + "\nFailed to add task.")
                time.sleep(delay)
                main()
        case 3:
            mark_task_as_done()
        case 4:
            save_task()
        case 5:
            remove_task()
        case 6:
            exit()


def get_user_choice():
    while True:
        try:
            choice = int(input(Fore.WHITE + main_prompt).strip())

            if choice not in range(1, 7):
                raise ValueError

            return choice
        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter a number between 1 and 6.")
            continue


# Function to add tasks
def add_task():
    while True:
        try:
            is_existing = input(Fore.WHITE + "\nDo you have an existing task list file(.csv)? Y/N: ").strip().upper()

            if is_existing not in ["Y", "N"]:
                raise ValueError

            if is_existing == "Y":
                filepath = input(Fore.WHITE + "\nPlease enter the file name (with .csv extension): ").strip()

                updated_task_list = update_time_left(filepath)

               
            else:
                return False
        except ValueError:
            print(Fore.RED + "\nInvalid input. Please enter Y or N.")
            continue


# Function to view tasks
def view_task(): ...


# Function to Mark task as done
def mark_task_as_done(): ...


# Function to Remove tasks
def remove_task(): ...


# Function to save tasks
def save_task(): ...


# Function to exit
def exit():
    sys.exit(Fore.GREEN + "\nThank you for using Task Manager!")


def get_due_date():
    while True:
        try:
            due_date_input= date(input("Enter the due date (YYYY-MM-DD): ").strip())

            return due_date_input
        except ValueError:
            print(Fore.RED + "\nInvalid date format. Please enter the date in YYYY-MM-DD format.")
            continue


def update_time_left(source):
    try:
        with open(source, 'r') as file:
            reader = csv.DictReader(file)
            task_list = list(reader)

        updated_time_left = []
        for task in task_list:
            date_entry = map(int, task["due_date"].split("-"))
            updated_time_left.append((date.__sub__((date(*date_entry)), date.today())).days)
            
        for task in task_list:
            task["time_left"] = updated_time_left[0]
            updated_time_left.pop(0)

        print(task_list)
        return task_list  
    except FileNotFoundError:
        print(Fore.RED + "\nFile not found. Please ensure the file exists.")
        return False


if __name__ == "__main__":
    main()
