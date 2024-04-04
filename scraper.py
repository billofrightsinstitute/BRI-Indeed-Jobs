import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Define the missing scrape_indeed_jobs function
def scrape_indeed_jobs(job_search_url):
    # Retrieve API key from environment variables
    api_key = os.getenv("SOME_SECRET")
    if api_key is None:
        print("API_KEY not found in .env file.")
        return None

    # Construct the URL for the ScrapingDog API
    url = f"https://api.scrapingdog.com/scrape?api_key={api_key}&url={job_search_url}&dynamic=false"

    # Make the HTTP GET request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def scrape_job_description(job_url):
    # Retrieve API key from environment variables
    api_key = os.getenv("SOME_SECRET")
    if api_key is None:
        print("API_KEY not found in .env file.")
        return "API_KEY not found in .env file."

    # Construct the URL for the ScrapingDog API
    url = f"https://api.scrapingdog.com/scrape?api_key={api_key}&url={job_url}&dynamic=false"

    # Make the HTTP GET request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        description_div = soup.find('div', id='jobDescriptionText')
        
        if description_div:
            description_text = description_div.get_text(separator=' ', strip=True)
            # Remove instances of [email\u00a0protected]
            cleaned_description = description_text.replace("[email\u00a0protected]", "")
            return cleaned_description
        else:
            return "Job description section not found"
    else:
        return "Failed to retrieve job description page"

def extract_job_information(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    job_titles = []
    job_urls = []
    
    for title_tag in soup.find_all('h2', class_='jobTitle'):
        title = title_tag.text.strip()
        job_titles.append(title)
        
        # Find the 'a' tag with the 'data-jk' attribute
        a_tag = title_tag.find('a', attrs={'data-jk': True})
        if a_tag:
            job_id = a_tag['data-jk']
            url = f"https://www.indeed.com/viewjob?jk={job_id}"
            job_urls.append(url)
        else:
            job_urls.append("URL not available")

    # Extracting company names and locations as before
    company_names = []
    company_locations = []
    for location in soup.find_all(class_='company_location'):
        css_1p0sjhy_div = location.find('div', class_='css-1p0sjhy eu4oa1w0')
        if css_1p0sjhy_div:
            company_locations.append(css_1p0sjhy_div.text.strip())
            company_name_span = location.find('span', class_='css-92r8pb eu4oa1w0')
            if company_name_span:
                company_names.append(company_name_span.text.strip())
            else:
                company_names.append("N/A")

    # Extracting job metadata as before
    job_metadata = []
    for meta_group in soup.find_all(class_='jobMetaDataGroup'):
        metadata_texts = []
        for meta in meta_group.find_all('div', class_='metadata'):
            meta_text = meta.get_text(strip=True)
            if meta_text:
                metadata_texts.append(meta_text)
        formatted_metadata = '. '.join(metadata_texts) + '.' if metadata_texts else ''
        job_metadata.append(formatted_metadata)

    # Extracting job dates as before
    job_dates = [date.text.replace('Posted', '').strip() for date in soup.find_all(class_='underShelfFooter')]

    # Scraping job descriptions
    job_descriptions = []
    for url in job_urls:
        if url != "URL not available":
            job_description = scrape_job_description(url)
            job_descriptions.append(job_description)
        else:
            job_descriptions.append("Job description not available")

    return job_titles, job_urls, company_names, company_locations, job_metadata, job_dates, job_descriptions


if __name__ == "__main__":
    job_search_url = "https://www.indeed.com/cmp/Bill-of-Rights-Institute/jobs"

    html_content = scrape_indeed_jobs(job_search_url)
    if html_content:
        job_titles, job_urls, company_names, company_locations, job_metadata, job_dates, job_descriptions = extract_job_information(html_content)

        # Store job information in a list of dictionaries
        jobs = []
        for title, url, name, location, metadata, date, description in zip(job_titles, job_urls, company_names, company_locations, job_metadata, job_dates, job_descriptions):
            job_info = {
                "Job Title": title,
                "Job URL": url,
                "Company Name": name,
                "Company Location": location,
                "Salary": metadata,
                "Date Posted": date,
                "Job Description": description
            }
            jobs.append(job_info)

        # Write job information to JSON file
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        with open(os.path.join(results_dir, "results.json"), "w") as f:
            json.dump(jobs, f, indent=4)

        # Print job information
        for job in jobs:
            print("Job Title:", job["Job Title"])
            print("Job URL:", job["Job URL"])
            print("Company Name:", job["Company Name"])
            print("Company Location:", job["Company Location"])
            print("Salary:", job["Salary"])
            print("Date Posted:", job["Date Posted"])
            print("Job Description:", job["Job Description"])
            print()
