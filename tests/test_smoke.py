def test_project_structure():
    from pathlib import Path
    assert Path("app.py").exists()
    assert Path("models.py").exists()
