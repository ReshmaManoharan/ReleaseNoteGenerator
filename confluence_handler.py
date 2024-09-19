from atlassian import Confluence
import logging
import os
from summarizecommits import SummarizeCommits

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfluenceHandler:
    """
    Handles methods like create/update with confluence
    """
    def __init__(self):
        """
        Initializes the confluence client
        """
        #For now, the arguments are hardcoded, but it can be passed
        self.confluence = Confluence(url='https://confluence-use.atlassian.net', username="reshmams395@gmail.com", password=os.getenv("CONFLUENCE_TOKEN"),
                        cloud=True)
        self.prompt = "Generate release notes summary strictly based on the following commits. provide response in markdown format\n"


    def get_parent_page_id(self):
        """
        Get Page Id of the Space in Confluence

        Returns:
            Str: Page Id of the Space in Confluence
        """
        return self.confluence.get_page_id("Softwarere", "Software_release")

    def create_page(self, commits, repos):
        """
        Create a page in Confluence

        Args:
            repos (dict): Nested Dictionary of Repositories
            commits (str): The commits(release notes) that has to be update to the page
        """
        try:
            summaryobj = SummarizeCommits()
            summary = summaryobj.generate_release_notes(commits, self.prompt)
        except Exception as err:
            summary = ""
        try:
            package_info = "The Release notes for " 
            page_title = ""
            for repo, value in repos.items():
                package_info += f"{repo} : From Tag {value['from_tag']} - To Tag {value['to_tag']}</br>"
                page_title += f"{repo} {value['to_tag']} "
            logging.debug(package_info)
            #html template for the confluence page
            front_page = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f9f9f9;
                        margin: 20px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }
                    th {
                        background-color: #4CAF50;
                        color: white;
                        font-weight: bold;
                    }
                    tr:hover {
                        background-color: #ddd;
                    }
                </style>
            </head>
            <body>
            <p>Please test the latest software version reflecting recent changes from the Git repository. Ensure all new features and bug fixes are thoroughly verified. Refer to the commit history for specific test cases related to these changes. Report any issues encountered during testing back to the development team.</p>
            </br>
            <h3> Package Details: <h3>
            <p>""" +  package_info \
            + """</p>
            <h3> AI Summary: <h3>
            <p>""" +  summary \
            + """</p>
            <h3>Commit History: </h3>
            <table>
                <thead>
                    <tr>
                        <th>Author</th>
                        <th>Repository Name</th>
                        <th>Commit Message</th>
                        <th>Commit Date</th>
                    </tr>
                </thead>
                <tbody>"""
            table_row = ""
            for commit in commits:
                table_row += f"<tr><td>{commit['author']}</td><td>{commit['repo']}</td><td>{commit['message']}</td><td>{commit['date']}</td></tr>"
            page_end = """</tbody></table></body></html>"""
            body = front_page + table_row + page_end
            page_title = page_title + "Released !!"
            resp = self.confluence.create_page("Softwarere", page_title, body, parent_id=self.get_parent_page_id(), type='page', representation='storage', editor='v2', full_width=False)
            assert resp and resp["id"]
            logging.info(f"Page with {page_title} created successfully !!")
        except AssertionError as err:
            logging.error(err)
        except Exception as err:
            if "A page with this title already exists" in str(err):
                logging.error("Page already exists !!. Please delete and recreate the page")
            logging.error(err)

if __name__ == '__main__':
    c = ConfluenceHandler()
    print(c.get_parent_page_id())
    create_page("Release_notes_3")
