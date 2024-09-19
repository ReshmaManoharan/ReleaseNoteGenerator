import subprocess
import os
import shutil
import pytest
from release_notes_generator import ReleaseNotesGenerator
from confluence_handler import ConfluenceHandler  # Adjust import as needed

@pytest.fixture
def setup_repos():
    """
    Fixture to set up test environment.
    """
    repos = { "request-promise": {
            "url": "https://github.com/request/request-promise.git",
            "from_tag": "v4.2.5",
            "to_tag": "v4.2.6"
        }
    }
    generator = ReleaseNotesGenerator(repos)
    clone_dir = "test_repo"
    yield generator, clone_dir
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)

@pytest.fixture
def confluence_handler():
    """Fixture to create a ConfluenceHandler instance."""
    return ConfluenceHandler()

def test_clone_repo(setup_repos):
    """
    Test if cloning of a repository is successful
    """
    generator, clone_dir = setup_repos
    repo_url = generator.repos["request-promise"]["url"]
    generator.clone_repo(repo_url, clone_dir)
    assert os.path.exists(clone_dir)

def test_parse_git_log(setup_repos):
    """
    Test parsing git log between two tags to verify if there is atleast one commit between tags.
    """
    generator, clone_dir = setup_repos
    repo_url = generator.repos["request-promise"]["url"]
    generator.clone_repo(repo_url, clone_dir)
    os.chdir(clone_dir)
    commits = generator.parse_git_log(generator.repos["request-promise"]["from_tag"], generator.repos["request-promise"]["to_tag"], "request-promise")
    os.chdir("..")
    assert len(commits) > 0
    assert "hash" in commits[0]
    assert "author" in commits[0]
    assert "message" in commits[0]
    assert "date" in commits[0]
    assert "repo" in commits[0]

def test_empty_repos():
    """
    Test handling of empty repositories list
    """
    empty_generator = ReleaseNotesGenerator({})
    commits = empty_generator.generate_release_notes()
    assert len(commits) == 0

def test_invalid_repo_url():
    """
    Test handling of invalid repository URL
    """
    invalid_repos = {
        "invalid-repo": {
            "url": "https://github.com/invalid/invalid-repo.git",
            "from_tag": "v0.0.1",
            "to_tag": "v0.0.2"
        }
    }
    invalid_generator = ReleaseNotesGenerator(invalid_repos)
    commits = invalid_generator.generate_release_notes()
    assert len(commits) == 0

def test_get_parent_page_id(confluence_handler):
    """
    Test getting the parent page ID.
    """
    page_id = confluence_handler.get_parent_page_id()
    assert isinstance(page_id, str)

def test_create_page(confluence_handler):
    """
    Test creating a page successfully.
    """
    commits = [{'author': 'Me', 'repo': 'check', 'message': 'Initial commit', 'date': '2024-09-18'}]
    repos = {'check': {'from_tag': 'v0.0.1', 'to_tag': 'v0.0.2'}}
    confluence_handler.create_page(commits, repos)
    page_title = "check v0.0.2 Released !!"
    page_id = confluence_handler.confluence.get_page_id("Softwarere", page_title)
    assert page_id is not None

def test_create_page_already_exists(confluence_handler):
    """
    Test handling of page already existing error.
    """
    commits = [{'author': 'Me', 'repo': 'check', 'message': 'Initial commit', 'date': '2024-09-18'}]
    repos = {'check': {'from_tag': 'v0.0.1', 'to_tag': 'v0.0.2'}}
    confluence_handler.create_page(commits, repos)
    #This should log an error for existing page
    confluence_handler.create_page(commits, repos)
    # Verify it still exists
    page_title = "check v0.0.2 Released !!"
    page_id = confluence_handler.confluence.get_page_id("Softwarere", page_title)
    assert page_id is not None
