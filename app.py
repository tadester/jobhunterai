import streamlit as st
import PyPDF2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import time

# Selenium and related helpers for form submission
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------------------------------------
# Resume and Job Processing Functions
# -------------------------------------------------------------

def get_resume_text(file_handle):
    """Extract plain text from a PDF resume."""
    pdf = PyPDF2.PdfReader(file_handle)
    content = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            content += page_text
    return content

def load_cities(filename="cities.txt"):
    """
    Load a list of cities from a text file.
    Each line in the file should contain one city.
    """
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        st.error("Error loading cities: " + str(e))
        return []

def extract_location_from_resume(resume_text, cities_file="cities.txt"):
    """
    Extract a location from the resume by checking against a list of cities loaded from a file.
    Returns the first matching city or a default value if no match is found.
    """
    cities = load_cities(cities_file)
    resume_lower = resume_text.lower()
    for city in cities:
        if city.lower() in resume_lower:
            return city
    return "New York"  # Default if none found

def determine_job_category(resume_text):
    """
    Determine the candidate's job field based on keywords.
    Compare against various common fields and choose the one with the highest match.
    """
    text = resume_text.lower()
    categories = {
        "Software Engineering": [
            "programming", "software", "developer", "coding", "engineer",
            "development", "fullstack", "backend", "frontend", "web", "app",
            "java", "python", "c++", "javascript"
        ],
        "Data Science": [
            "data science", "machine learning", "analytics", "data analysis",
            "deep learning", "neural network", "statistical", "python", "r",
            "tensorflow", "pytorch", "big data", "predictive modeling"
        ],
        "Healthcare": [
            "healthcare", "medical", "nursing", "clinic", "hospital",
            "patient care", "surgery", "diagnosis", "treatment", "clinical",
            "physician", "therapist"
        ],
        "Marketing": [
            "marketing", "advertising", "seo", "social media", "digital marketing",
            "content marketing", "branding", "campaign", "market research",
            "public relations", "pr"
        ],
        "Finance": [
            "finance", "accounting", "investment", "banking", "financial",
            "auditing", "audit", "risk management", "investment banking",
            "portfolio", "analyst"
        ],
        "Human Resources": [
            "human resources", "hr", "recruitment", "talent acquisition", "employee",
            "staffing", "personnel", "onboarding", "training", "benefits",
            "performance management"
        ],
        "Education": [
            "teacher", "education", "curriculum", "instruction", "tutor",
            "academic", "learning", "training", "professor", "educator",
            "lecturer", "school", "university"
        ],
        "Legal": [
            "law", "legal", "attorney", "lawyer", "litigation", "contract",
            "compliance", "paralegal", "regulation", "legal advisor",
            "jurisprudence"
        ]
    }
    best_field = None
    max_matches = 0
    for field, keywords in categories.items():
        count = sum(text.count(word) for word in keywords)
        if count > max_matches:
            max_matches = count
            best_field = field
    if best_field is None or max_matches == 0:
        best_field = "Software Engineering"
    return best_field

def find_matching_jobs(resume_text, jobs_df, top_n=50):
    """
    Rank job listings based on how closely each job description matches the resume.
    Returns the top 'top_n' matches.
    """
    combined_text = [resume_text] + jobs_df['description'].tolist()
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(combined_text)
    candidate_vector = tfidf_matrix[0]
    jobs_matrix = tfidf_matrix[1:]
    similarities = cosine_similarity(candidate_vector, jobs_matrix).flatten()
    jobs_df['similarity'] = similarities
    top_matches = jobs_df.sort_values(by='similarity', ascending=False).head(top_n)
    return top_matches

def retrieve_jobs_from_api(query="software engineer", location="New York", num_results=50):
    """
    Retrieve job listings from the Adzuna API.
    Extract the real application URL if available.
    """
    app_id = "3b9eab7e"
    app_key = "e659bb44909da59992faf8b5cc441c20"
    api_endpoint = "http://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": num_results,
        "what": query,
        "where": location,
        "content-type": "application/json"
    }
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        jobs = []
        for entry in data.get("results", []):
            region = entry.get("location", {}).get("area", [])
            region_str = ", ".join(region) if region else ""
            apply_link = entry.get("redirect_url")
            if not apply_link:
                apply_link = "https://example.com/apply?job=" + entry.get("title", "").replace(" ", "+")
            jobs.append({
                "job_title": entry.get("title"),
                "company": entry.get("company", {}).get("display_name", ""),
                "location": region_str,
                "description": entry.get("description", ""),
                "apply_url": apply_link
            })
        return pd.DataFrame(jobs)
    else:
        st.error("Failed to fetch jobs from the API.")
        return pd.DataFrame()

# -------------------------------------------------------------
# Selenium Application Submission Functions
# -------------------------------------------------------------

def submit_application_indeed(app_url):
    """Submit an application on an Indeed job page.
       Adjust the element IDs and selectors as needed.
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(app_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "indeed_apply_button"))
    )
    driver.find_element(By.ID, "applicant-name").clear()
    driver.find_element(By.ID, "applicant-name").send_keys("John Doe")
    driver.find_element(By.ID, "applicant-email").clear()
    driver.find_element(By.ID, "applicant-email").send_keys("john.doe@example.com")
    driver.find_element(By.ID, "applicant-phone").clear()
    driver.find_element(By.ID, "applicant-phone").send_keys("1234567890")
    driver.find_element(By.ID, "indeed_submit").click()
    time.sleep(3)
    driver.quit()
    return True

def submit_application_linkedin(app_url):
    """Submit an application using LinkedIn's Easy Apply.
       Adjust the selectors to match the current LinkedIn form.
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(app_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Easy Apply')]"))
    )
    driver.find_element(By.XPATH, "//button[contains(text(),'Easy Apply')]").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "fullName"))
    )
    driver.find_element(By.NAME, "fullName").clear()
    driver.find_element(By.NAME, "fullName").send_keys("John Doe")
    driver.find_element(By.NAME, "email").clear()
    driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
    driver.find_element(By.NAME, "phone").clear()
    driver.find_element(By.NAME, "phone").send_keys("1234567890")
    driver.find_element(By.XPATH, "//button[contains(text(),'Submit application')]").click()
    time.sleep(3)
    driver.quit()
    return True

def submit_application_generic(app_url):
    """Submit an application using a generic job form.
       Adjust field names and the submit button as needed.
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(app_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "fullName"))
    )
    driver.find_element(By.NAME, "fullName").clear()
    driver.find_element(By.NAME, "fullName").send_keys("John Doe")
    driver.find_element(By.NAME, "email").clear()
    driver.find_element(By.NAME, "email").send_keys("john.doe@example.com")
    driver.find_element(By.NAME, "phone").clear()
    driver.find_element(By.NAME, "phone").send_keys("1234567890")
    driver.find_element(By.ID, "submit").click()
    time.sleep(3)
    driver.quit()
    return True

def submit_applications_selenium(job_matches):
    """
    Iterate over matched jobs, determine the appropriate application submission method,
    and submit the applications one by one. A progress bar is displayed, and each job's status is updated.
    """
    results = job_matches.copy()
    results["application_status"] = "Not Applied"
    st.write("Submitting applications using Selenium...")
    
    total_jobs = len(results)
    progress_bar = st.progress(0)
    count = 0

    for idx, job in results.iterrows():
        url = job.get("apply_url")
        if not url:
            results.at[idx, "application_status"] = "No Apply Link"
        else:
            st.write(f"Processing: {job['job_title']} at {job['company']}")
            try:
                if "indeed.com" in url:
                    success = submit_application_indeed(url)
                elif "linkedin.com" in url:
                    success = submit_application_linkedin(url)
                else:
                    success = submit_application_generic(url)
                results.at[idx, "application_status"] = "Applied" if success else "Failed"
            except Exception as err:
                results.at[idx, "application_status"] = f"Error: {str(err)}"
        count += 1
        progress_bar.progress(count / total_jobs)
    
    st.success("All application submissions completed!")
    return results

# -------------------------------------------------------------
# Main Application (Streamlit Interface)
# -------------------------------------------------------------

def main():
    st.title("Smart JobHunter: Resume Processor, Job Matcher & Application Submitter")
    st.write(
        "Upload your resume (PDF) to identify your target job field and extract your location. "
        "Then, retrieve matching job listings and submit applications using Selenium."
    )
    
    resume_file = st.file_uploader("Select your resume (PDF)", type="pdf")
    resume_content = ""
    
    if resume_file is not None:
        with st.spinner("Processing resume..."):
            resume_content = get_resume_text(resume_file)
        if resume_content:
            st.subheader("Extracted Resume Text")
            st.text_area("Resume Content:", resume_content, height=300)
        else:
            st.error("Could not extract any text. Please try another file.")
    
    if resume_content:
        job_field = determine_job_category(resume_content)
        resume_location = extract_location_from_resume(resume_content)
        st.write(f"Identified Job Category: **{job_field}**")
        st.write(f"Identified Location: **{resume_location}**")
        
        st.subheader("Job Listings")
        load_local_jobs = st.checkbox("Load jobs from a local CSV file", value=False)
        
        if load_local_jobs:
            try:
                jobs_data = pd.read_csv("jobs.csv")
            except Exception as error:
                st.error("Error reading local job listings. Ensure 'jobs.csv' exists.")
                st.error(str(error))
                jobs_data = pd.DataFrame()
        else:
            st.write(f"Retrieving live job listings for **{job_field}** in **{resume_location}**...")
            jobs_data = retrieve_jobs_from_api(query=job_field, location=resume_location, num_results=50)
        
        if not jobs_data.empty:
            if st.button("Match Jobs"):
                matched_jobs = find_matching_jobs(resume_content, jobs_data, top_n=50)
                st.write("Matching Job Listings:")
                st.dataframe(matched_jobs[['job_title', 'company', 'location', 'similarity']])
                
                if st.button("Submit Applications for These Jobs"):
                    submission_status = submit_applications_selenium(matched_jobs)
                    st.write("Application Submission Status:")
                    st.dataframe(submission_status[['job_title', 'company', 'location', 'similarity', 'application_status']])
        else:
            st.error("No job listings were found.")

if __name__ == "__main__":
    main()
