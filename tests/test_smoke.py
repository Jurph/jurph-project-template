"""Basic smoke tests for the template project."""

from your_project.main import main


def test_main_runs(capsys) -> None:
    """The starter CLI should print a placeholder message."""
    main()
    captured = capsys.readouterr()
    assert "Replace this with your real entry point." in captured.out
