import streamlit as st
import os
import git
import shutil
import requests
import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

def clear_directory(directory):
    """
    Clear the contents of a directory.
    
    Args:
        directory (str): The directory to clear.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            st.warning(f"Failed to delete {file_path}. Reason: {e}")

def clone_repository(repo_url, destination):
    """
    Clone a Git repository from the given URL to the specified destination.
    
    Args:
        repo_url (str): The URL of the Git repository.
        destination (str): The directory where the repository should be cloned.
        
    Returns:
        str: The path to the cloned repository.
    """
    clear_directory(destination)  # Clear the directory before cloning
    try:
        repo = git.Repo.clone_from(repo_url, destination)
        return repo.working_dir
    except git.exc.GitCommandError as e:
        st.error("Error:", e)
        return None

def traverse_repository(repo_path):
    """
    Traverse the cloned repository and collect information about all files.
    
    Args:
        repo_path (str): The path to the cloned repository.
        
    Returns:
        dict: A dictionary with file paths as keys and file contents as values.
    """
    file_contents = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents[file_path] = f.read()
            except (UnicodeDecodeError, FileNotFoundError):
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

def extract_readme(file_contents):
    """
    Extract the README file contents if present.
    
    Args:
        file_contents (dict): A dictionary with file paths as keys and file contents as values.
        
    Returns:
        str: The contents of the README file, or None if not found.
    """
    for file_path, content in file_contents.items():
        if 'README' in os.path.basename(file_path).upper():
            return content
    return None

def main():
    st.title("GitHub Repository Summary")

    # Get GitHub repository URL from user
    repo_url = st.text_input("Enter GitHub repository URL:")
    if st.button("Submit"):
        if repo_url:
            destination = os.path.join(os.getcwd(), "repoload")  # Specify destination directory for cloning
            cloned_repo_path = clone_repository(repo_url, destination)
            if cloned_repo_path:
                st.success("Repository cloned successfully.")
                repo_files = traverse_repository(cloned_repo_path)
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
