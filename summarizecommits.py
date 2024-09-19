import os
import google.generativeai as genai

class SummarizeCommits:
    def __init__(self):
        try:
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("No API key found. Please set the GEMINI_API_KEY environment variable.")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as err:
            pass

    def generate_release_notes(self, commit_list, prompt):
        full_prompt = prompt + str(commit_list)
        response = self.model.generate_content(full_prompt)
        return response.text

# Example usage:
if __name__ == "__main__":
    prompt = "Generate release notes summary strictly based on the following commits. provide response in markdown format\n"
    generator = SummarizeCommits()
    release_notes = generator.generate_release_notes(commit_list, prompt)
    print(release_notes)
