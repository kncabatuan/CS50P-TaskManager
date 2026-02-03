# PERSONAL TASK MANAGER 
#### Video Demo: ...
#### Description:

**Personal Task Manager** is a command-line interface (CLI) python program that was made to keep track of your everyday responsibilities in an easier and user-friendly way. 

With this program, the user is able to load up or create a CSV file that contains all the information about the task/s that the user has taken up. These will automatically update everytime they load up their CSV file and,
if the user so chooses, be viewed in the terminal, color-coded for quick recognition of the tasks' status. The user also has the power to mark a task as "Done" or remove a task entirely from their file.

The user can also export the contents of their CSV file to MS Excel for more advanced purposes.

---

##### Features

- **View Tasks**: Display all tasks (color-coded) in a formatted table with id, status, due date, and time left.
- **Add Task**: Add a new task with a due date.
- **Mark Task as Done**: Update the status of a task to "Done".
- **Remove Task**: Delete tasks from the task list.
- **Export to Excel**: Save tasks from CSV to an XLSX file.
- **Load or Create CSV**: Open an existing CSV or create a new one.
- **Exit Program**: Close the application safely.

---

##### How to Use

1. Run the program using `python project.py`.

2. Indicate whether you have an existing task list or want to create a new one by answering the question with `y` or `n`. The user can also enter `exit` to close the program (*This applies on any prompt including file naming*).

3. Use the main menu by entering values [1-8]
    1. View all tasks
        - This wil print all of the tasks in a colored table on the terminal
            - WHITE: Pending task
            - RED: Overdue task
            - GREEN: Done task
    2. Add a new task
        - This will prompt user for a **description of task** and **due date** (YYYY-MM-DD) and add that task to the currently loaded CSV file
    3. Mark tasks as done
        - This will prompt the user for **ID/s of task/s** (comma-separated) that the user want to mark as done and updates the loaded CSV file accordingly
    4. Remove tasks
        - This will prompt the user for **ID/s of task/s** (comma-separated) that the user want to remove and updates the loaded CSV file accordingly
    5. Export the task list to Excel
        - This will prompt the user for a **name of XLSX file** and exports the contents of the loaded CSV file into
        the newly created XLSX file
    6. Create new file
        - This will prompt the user for a **name of CSV file** and creates the file with appropriate task manager headers
    7. Load new file
        - This will prompt the user for the **name of CSV file** (with .csv extension) that they want to load up.
    8. Exit the program
        - This will close the program

4. Follow on-screen prompts for entering required information.
5. The program validates input and provides guidance at each step.

---

##### Technical Details

- **Programming Language**: Python 3.13.2
- **Libraries Used**: `colorama`, `prettytable`, `pandas`, `csv`, `datetime`, `re`, `os`, `sys`, `time`
- **Data Storage**: CSV files for tasks, optional Excel export
- **Validation**: Ensures filenames, task IDs, and dates are valid; prevents invalid operations

##### Limitations/Future Improvements

- This is program is limited to the creators' knowledge in python post CS50P, Introduction to Python Programming and a little bit of self study on other python libraries and OOP
- Here are a few features for improvement of this program:
    - Add feature to sort through the task list by time left, by due_date, or by status
    - Change time left to include hours and minutes to be a bit more accurate
    - Include functionality in add task to add urgency of task (moderately urgent, non-urgent, extremely urgent) and change the urgency of tasks
    - Add feature to sort through the task list by urgency of task
    - Add feature to include person responsible for task and to sort through task list by person
    - Add feature in view task to view only by level of urgency or by status
