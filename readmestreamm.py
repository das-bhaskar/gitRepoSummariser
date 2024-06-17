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
    try:
        repo = git.Repo.clone_from(repo_url, "cloned_repo")
        return repo
    except git.exc.GitCommandError as e:
        st.error("Error:", e)
        return None

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

# Other functions remain the same...

def main():
    st.title("GitHub Repository Summary")

    # Get GitHub repository URL from user
    repo_url = st.text_input("Enter GitHub repository URL:")
    if st.button("Submit"):
        if repo_url:
            repo = clone_repository(repo_url)
            if repo:
                st.success("Repository cloned successfully.")
                repo_files = traverse_repository(repo)
                readme_content = extract_readme(repo_files)
                if readme_content:
                    st.info("README Content Summary:")
                    st.write(analyze_with_gemini(readme_content))
                    # Add conversation logic here based on context
                else:
                    st.warning("No README file found.")
            else:
                st.error("Failed to clone repository.")
        else:
            st.warning("Please enter a valid GitHub repository URL.")

if __name__ == "__main__":
    main()
