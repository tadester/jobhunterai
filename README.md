# Smart JobHunter

Smart JobHunter is an AI-powered job application tool that processes a candidate's resume to identify their target job category and location, retrieves matching job listings via the Adzuna API, and automatically submits applications using Selenium automation.


## Features

- **Resume Processing:**  
  Extracts text from a PDF resume using PyPDF2.
  
- **Job Category Determination:**  
  Determines the candidate's target field (e.g., Software Engineering, Data Science, Healthcare) by matching keywords in the resume.

- **Location Extraction:**  
  Reads a list of cities from an external file (`cities.txt`) and extracts the candidate's location from the resume text. If no match is found, it uses a default location ("New York").

- **Job Listing Retrieval:**  
  Retrieves live job listings from the Adzuna API based on the extracted job category and location.  
  *Note: You must set up your Adzuna API credentials.*

- **Job Matching:**  
  Uses TF-IDF vectorization and cosine similarity to rank job listings based on how closely each description matches the candidate’s resume.

- **Application Submission:**  
  Automatically submits applications using Selenium.  
  The tool supports different submission flows for Indeed, LinkedIn Easy Apply, and a generic web form.  
  A progress bar shows the submission status, and results are updated with messages indicating success, failure, or any errors.

## Installation

1. **Clone or Download the Repository**

   ```bash
   git clone <repository-url>
   cd smart-jobhunter
2. **Set Up a Virtual Environment (Optional but Recommended)**
python -m venv venv
# On Unix/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
3. **Install Required Dependencies**
pip install streamlit PyPDF2 pandas scikit-learn requests selenium webdriver_manager
OR use requirements file 
4. **Create the Cities File**
Create a file named cities.txt in the project directory. List one city per line. For example:
Edmonton
Toronto
New York
5.**Set Up API Credentials**
Update the retrieve_jobs_from_api function in the code with your Adzuna API credentials:
Replace the placeholders for app_id and app_key with your actual Adzuna API ID and key.

## Usage
**Run the App**
In the project directory, run:
streamlit run your_script.py
**Using the Interface**

Upload Resume:
Click the file uploader widget to select your PDF resume.

Resume Processing:
The app will extract the text from your resume, determine your job category, and extract your location using the provided list of cities.

Job Listings:
The app retrieves matching job listings from the Adzuna API.
You can choose to load jobs from a local CSV file if desired.

Job Matching:
Click the "Match Jobs" button to see the top matching job listings based on your resume's similarity.

Application Submission:
Click "Submit Applications for These Jobs" to automatically submit applications using Selenium.
A progress bar will indicate submission progress, and a table will display the final submission status for each job.
