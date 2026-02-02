import project
import csv
import os
import pytest


def test_taskfile_initialization():
    taskfile = project.Taskfile("sample.csv")
    assert taskfile.filename == "sample.csv"
    
    taskfile = project.Taskfile("sample")
    assert taskfile.filename == "sample.csv"

    with pytest.raises(ValueError):
        project.Taskfile("")

    with pytest.raises(ValueError):
        project.Taskfile("sample.txt")
    
    with pytest.raises(ValueError):
        project.Taskfile(".sample.csv")
                 
    with pytest.raises(ValueError):
        project.Taskfile("sample..csv")

    with pytest.raises(ValueError):
        project.Taskfile("sam/ple.csv")


def test_file_creation(tmp_path):
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
    with pytest.raises(ValueError):
        project.answer_is_valid("123")
    
    with pytest.raises(ValueError):
        project.answer_is_valid("test")
    
    with pytest.raises(ValueError):
        project.answer_is_valid("a1")
    
    with pytest.raises(ValueError):
        project.answer_is_valid("!!!")

    with pytest.raises(ValueError):
        project.answer_is_valid("")
    
    assert project.answer_is_valid("Y") == "Y"
    assert project.answer_is_valid("N") == "N"
    assert project.answer_is_valid("EXIT") == "EXIT"
