# Automated Release Notes Generator and Smart Test Selection

## Overview

This project automates the creation of release notes in Confluence based on Git commits and can be extended for the application to recommend regression tests using machine learning.

## Purpose

- **Release Notes Generator**: Collects commit details from specified repositories based on tags and publishes formatted release notes in Confluence.
- **Smart Test Selection**: Analyzes commit history to determine which tests to run, ensuring critical areas are tested efficiently.

## Getting Started
- clone the repo
- export CONFLUENCE_TOKEN="YOUR TOKEN HERE, "
- export GEMINI_API_KEY="YOUR KEY"
- pip install -r requirements.txt
- python release_notes_generator.py
- Check the confluence for your new release notes.
- To re-run for another repo or list of repo. Update the variable **repos** in file release_notes_generator.py  

## Tech Stack

- **Confluence**: Cloud free version for documentation and release notes.
- **Git**: Source control for managing code repositories.
- **Python**: For writing the generator and machine learning model.
- **Libraries**:
  - `atlassian-python-api`: For interacting with Confluence.
  - `pytest`: For testing the application.
  - **Gemini AI**: Used for generating summaries for release notes in Confluence.
