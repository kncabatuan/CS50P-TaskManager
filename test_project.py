import project
import csv
import os
import pytest


def test_taskfile_initialization():
    taskfile = project.Taskfile("sample.csv")
    assert taskfile.filename == "sample.csv"
    
    taskfile = project.Taskfile("sample")
    assert taskfile.filename == "sample.csv"

    test_invalid_names = ["", "sample.txt", ".sample.csv", "sample..csv", "sam/ple.csv"]

    for name in test_invalid_names:
        with pytest.raises(ValueError):
            project.Taskfile(name)


def test_file_creation():
    with pytest.raises(FileExistsError):
        project.Taskfile.create_file("sample.csv")

    try:
        taskfile = project.Taskfile.create_file("test_file.csv")
        with open(taskfile.filename, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert rows[0][0] == "id"
    finally:
        if os.path.exists("test_file.csv"):
            os.remove("test_file.csv")


def test_file_loading(tmp_path):
    with pytest.raises(FileNotFoundError):
        project.Taskfile.load_file("nonexistent.csv")

    temp_folder = tmp_path / "sample_folder"
    temp_folder.mkdir()
    with pytest.raises(PermissionError):
        project.Taskfile.load_file(temp_folder)


def test_valid_answer():

    test_invalid_values = ["123", "test", "a1", "!!!", ""]
    test_valid_values = ["Y", "N", "EXIT"]

    for value in test_invalid_values:
        with pytest.raises(ValueError):
            project.answer_is_valid(value)
    
    for value in test_valid_values:
        assert project.answer_is_valid(value) == value


def test_valid_choice():

    test_invalid_values = ["0", "9", "-1", "a", "1.5", "---", ""]
    test_valid_values = ["exit"]
    for i in range(1, 9):
        test_valid_values.append(str(i))

    for value in test_invalid_values:
        with pytest.raises(ValueError):
            project.choice_is_valid(value)
    
    for value in test_valid_values:
        assert project.choice_is_valid(value) == value



