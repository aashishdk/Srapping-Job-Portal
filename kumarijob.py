import requests
from bs4 import BeautifulSoup
import pandas as pd

job_data = []

# Function to extract job data from the listing page
def extract(job):
    divs = job.find_all('div', class_='left')

    if not divs:
        print("No divs found")
        return

    for item in divs:
        # Extract job title and link to the job details page
        title_tag = item.find('span', class_="title")
        job_title = title_tag.text.strip() if title_tag else "Job title not found"

        print(f"Job Title: {job_title}")

        # Extract company name
        company_tag = item.find('span', class_='meta')
        company_title = company_tag.text.strip() if company_tag else "Company not found"
        print(f"Company Name: {company_title}")

        # Extract job details link
        job_details_link = item.find('a', href=True)['href'] if item.find('a', href=True) else None
        if job_details_link:
            job_details_url = f'{job_details_link}'
            print(f"Job Details URL: {job_details_url}")

            # Scrape job details page and get the extracted data
            location, job_level, salary, job_description = scrape_job_details(job_details_url)

            # Append data to job_data list
            job_data.append({
                'Job Title': job_title,
                'Company': company_title,
                'Location': location,
                'Job Level': job_level,
                'Salary': salary,
                'Job Description': job_description
            })
        else:
            print('No link found')

# Function to scrape job level, salary, and description from the job details page
def scrape_job_details(job_details_url):
    response = requests.get(job_details_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize values
        location = "Not mentioned"
        job_level = "Not mentioned"
        salary = "Not Mentioned"

        # Extract job details dynamically based on label text
        details = soup.find_all('li', class_="row")
        
        for detail in details:
            label = detail.find('span', class_="basic-item__left")
            value = detail.find('span', class_="basic-item__right col-7")

            if label and value:
                label_text = label.text.strip()
                value_text = value.text.strip()

                if "Location" in label_text:
                    location = value_text
                elif "Job Level" in label_text:
                    job_level = value_text
                elif "Salary" in label_text:
                    salary = value_text

        # Extract Job Description
        description_tag = soup.find("div", class_='job-description-wrap')
        if description_tag:
            job_descriptions_tag = description_tag.find('ul') or description_tag.find('p') or description_tag.find('li')
            job_description = job_descriptions_tag.text.strip() if job_descriptions_tag else "Not Mentioned"
        else:
            job_description = "Not Found"

        # Print job details
        print(f"Location: {location}")
        print(f"Job Level: {job_level}")
        print(f"Salary: {salary}")
        print(f"Job Description: {job_description}")
        print("-" * 50)

        return location, job_level, salary, job_description 
    else:
        print(f"Failed to fetch job details for {job_details_url}")
        return "Not Found", "Not Found", "Not Found", "Not Found"

# Base URL with pagination parameter
base_url = 'https://www.kumarijob.com/search?page='
max_pages = 18

for page in range(1, max_pages + 1):
    print(f"\nScraping Page {page}...\n")
    url = base_url + str(page)
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        extract(soup)
    else:
        print(f"Failed to fetch page {page}")

print("\nScraping Complete!")

# Convert the job data list to a DataFrame and save to CSV
df = pd.DataFrame(job_data)
df.to_csv('Kumari_job_listings.csv', index=False)
print("\nScraping Complete and Data Saved to CSV!")
