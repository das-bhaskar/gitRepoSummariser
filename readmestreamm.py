import streamlit as st
import os
import git
import shutil
import requests
import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

def clone_repository(repo_url):
    """
    Clone a Git repository from the given URL.
    
    Args:
        repo_url (str): The URL of the Git repository.
        
    Returns:
        git.Repo: The cloned repository object.
    """
    destination = "cloned_repo"
    if os.path.exists(destination):
        shutil.rmtree(destination)  # Delete the existing directory
    try:
        repo = git.Repo.clone_from(repo_url, destination)
        return repo
    except git.exc.GitCommandError as e:
        raise RuntimeError(f"Failed to clone repository: {e}")

def traverse_repository(repo):
    """
    Traverse the cloned repository and collect information about all files.
    
    Args:
        repo (git.Repo): The cloned repository object.
        
    Returns:
        dict: A dictionary with file paths as keys and file contents as values.
    """
    file_contents = {}
    for file_path in repo.git.ls_files().split('\n'):
        try:
            content = repo.git.show(f"HEAD:{file_path}")
            file_contents[file_path] = content
        except git.exc.GitCommandError:
            file_contents[file_path] = None  # Handle non-text or inaccessible files
    return file_contents

def analyze_with_gemini(content):
    """
    Analyze content using Gemini AI.

    Args:
        content (str): The content to analyze.

    Returns:
        str: The analysis result.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        content = content + " analyse everything thoroughly then summarize and explain. guide how to use this GitHub repo and show all resources listed and categorise everything. present in great detail"
        response = model.generate_content(content)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def extract_readme(repo_files):
    """
    Extract the README file contents if present.
    
    Args:
        repo_files (dict): A dictionary with file paths as keys and file contents as values.
        
    Returns:
        str: The contents of the README file, or None if not found.
    """
    for file_path, content in repo_files.items():
        if 'README' in os.path.basename(file_path).upper():
            return content
    return None

def main():
    st.title("GitHub Repository Summary")

    # Get GitHub repository URL from user
    repo_url = st.text_input("Enter GitHub repository URL:")
    if st.button("Submit"):
        if repo_url:
            try:
                repo = clone_repository(repo_url)
                st.success("Repository cloned successfully.")
                repo_files = traverse_repository(repo)
                readme_content = extract_readme(repo_files)
                if readme_content:
                    st.info("README Content Summary:")
                    st.write(analyze_with_gemini(readme_content))
                    # Add conversation logic here based on context
                else:
                    st.warning("No README file found.")
            except RuntimeError as e:
                st.error(str(e))
        else:
            st.warning("Please enter a valid GitHub repository URL.")

if __name__ == "__main__":
    main()
