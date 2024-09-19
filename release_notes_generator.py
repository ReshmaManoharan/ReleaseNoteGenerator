import subprocess
import re
import os
import shutil
import logging
from confluence_handler import ConfluenceHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReleaseNotesGenerator:
    def __init__(self, repos):
        """
        Initializes the ReleaseNotesGenerator with a list of repositories and confluence handler

        Args:
            repos (dict): A dictionary containing repository information.
        """
        self.repos = repos

    def clone_repo(self, repo_url, clone_dir):
        """
        Clones a Git repository into a specified directory.

        Args:
            repo_url (str): The URL of the Git repository to clone.
            clone_dir (str): The directory to clone the repository into.
        """
        logging.info(f"Cloning repository {repo_url} into {clone_dir}")
        try:
            subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
            logging.info(f"Successfully cloned {repo_url}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone {repo_url}: {e}")

    def parse_git_log(self, from_tag, to_tag, reponame):
        """
        Parses the git log between two tags for a given repository.
        Args:
            from_tag (str): The starting tag from where you want to get the list of commits.
            to_tag (str): The ending tag until where you want to get the list of commits.
            reponame (str): The name of the repository.
        Returns:
            list: A list of dictionaries, each containing commit information.
        """
        logging.info(f"Parsing git log for {reponame} from {from_tag} to {to_tag}")
        commits = []
        try:
            # Run the git log command and capture the output
            git_log_output = subprocess.check_output(
                ["git", "log", f"{from_tag}..{to_tag}", 
                 "--pretty=format:%h - %an: %s (%ad)", "--date=format:%Y-%m-%d"],
                text=True
            ).strip()
            logging.info(f"Successfully retrieved git log for {reponame}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to retrieve git log for {reponame}: {e}")
        # Regex pattern to match the format of each line
        pattern = r"(?P<hash>[a-f0-9]+) - (?P<author>[^:]+): (?P<message>.*?) \((?P<date>\d{4}-\d{2}-\d{2})\)"
        # Iterate over each line of the git log output
        for line in git_log_output.split("\n"):
            match = re.match(pattern, line)
            if match:
                # Create a dictionary for each commit
                commit = match.groupdict()
                commit["repo"] = reponame
                commits.append(commit)
        logging.info(f"Parsed {len(commits)} commits for {reponame}")
        return commits

    def generate_release_notes(self):
        """
        Generates release notes by cloning repositories and parsing git logs.

        Returns:
            list: A list of dictionaries, each containing commit information.
        """
        logging.info("Starting the release notes generation process")
        # Initialize an empty list to hold parsed commits
        commits = []
        for repo_name, repo_info in self.repos.items():
            clone_dir = repo_name
            repo_url = repo_info["url"]
            from_tag = repo_info["from_tag"]
            to_tag = repo_info["to_tag"]  
            try:
                # Clone the repository
                self.clone_repo(repo_url, clone_dir)
                # Change the working directory to the cloned repository
                os.chdir(clone_dir) 
                # Parse the git log between the two tags
                repo_commits = self.parse_git_log(from_tag, to_tag, repo_name)
                commits.extend(repo_commits)
                # Change back to the parent directory
                os.chdir("..")
                # Remove the cloned repository directory
                shutil.rmtree(clone_dir)
            except Exception as e:
                logging.error(f"Error processing repository {repo_url}: {e}")
            finally:
                if os.path.exists(clone_dir):
                    shutil.rmtree(clone_dir)
        logging.info("Finished processing all repositories")
        logging.debug(f"Commits: {commits}")
        logging.info(f"Total number of commits: {len(commits)}")
        return commits

if __name__ == "__main__":
    # Variable to store the repositories and their tags
    repos = {
    "request-promise": {
        "url": "https://github.com/request/request-promise.git",
        "from_tag": "v4.2.5",
        "to_tag": "v4.2.6"
    }
    # Add more repositories here
    }
    generator = ReleaseNotesGenerator(repos)
    commits = generator.generate_release_notes()
    #Write to confluence
    confluence = ConfluenceHandler()
    #Provide an unique name
    confluence.create_page(commits, repos)
