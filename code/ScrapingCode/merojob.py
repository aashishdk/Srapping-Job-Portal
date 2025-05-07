import requests
from bs4 import BeautifulSoup
import pandas as pd

# List to store job data
job_data = []

# Function to extract job data from the listing page
def extract(job):
    divs = job.find_all('div', class_='col-8 col-lg-9 col-md-9 pl-3 pl-md-0 text-left')

    for item in divs:
        # Extract job title and link to the job details page
        title_tag = item.find('h1', class_="text-primary font-weight-bold media-heading h4") or item.select_one('.text-primary')
        job_title = title_tag.text.strip() if title_tag else "Job title not found"

        # Extract company name
        company_tag = item.find('h3', class_='h6') or item.select_one('.h6')
        company_title = company_tag.text.strip() if company_tag else "Company not found"

        # Extract location
        location_tag = item.find("div", class_='media-body') or item.select_one('.text-muted')
        location_title = location_tag.text.strip() if location_tag else "Location not found"

        # Extract the link to the job details page
        job_details_link = item.find('a', href=True)['href'] if item.find('a', href=True) else None
        if job_details_link:
            # Complete the URL by joining it with the base URL
            job_details_url = f'https://merojob.com{job_details_link}'
            #print(f"Job Title: {job_title}, \n Company: {company_title}, \n Location: {location_title}")
            #print(f"Job Details URL: {job_details_url}")

            # Scrape job details page and store the data
            job_level, no_of_openings, salary,experience, job_description = scrape_job_details(job_details_url)

            # Print the extracted data
            print(f"Job Title: {job_title}")
            print(f"Location: {location_title}")
            print(f"No. of Openings: {no_of_openings}")
            print(f"Company: {company_title}")
            print(f"Job Level: {job_level}")
            print(f"Salary: {salary}")
            print(f"Experience: {experience}")
            print(f"Job URL: {job_details_url}")
            print(f"Job Description: {job_description}\n")
            print(f"******" * 20)

            # Append job data to the list
            job_data.append({
                'Job Title': job_title,
                'Company': company_title,
                'Location': location_title,
                'No. of Openings': no_of_openings,
                'Job Level': job_level,
                'Salary': salary,
                'Experience': experience,
                'Job URL': job_details_url,
                'Job Description': job_description
            })

# Function to scrape job level, salary, and description from the job details page
def scrape_job_details(job_details_url):
    response = requests.get(job_details_url)
    job_level = no_of_openings = salary = experience = job_description = "Not found"

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract job level (if available)
        job_level_tag = soup.find('table', class_="table table-hover m-0")
        if job_level_tag:
            job_level_row = job_level_tag.find_all('tr')
            specific_job_level = job_level_row[1].find_all('td')[2]
            job_level = specific_job_level.text.strip() if specific_job_level else "Job level not found"

        
        #Extract No. of Openings
        no_of_openings_tag = soup.find('table', class_='table table-hover m-0')
        if no_of_openings_tag:
            no_of_openings_tag_row = no_of_openings_tag.find_all('tr')
            if no_of_openings_tag_row:
                specific_openings = no_of_openings_tag_row[2].find_all('td')[2]
                no_of_openings = specific_openings.text.strip() if specific_openings else "Not found"
            else:
                print("Not found")

        # Extract salary (if available)
        salary_tag = soup.find('table', class_='table table-hover m-0')
        if salary_tag:
            salary_row = salary_tag.find_all('tr')
            if salary_row:
                specific_salary = salary_row[5].find_all('td')[2]
                salary = specific_salary.text.strip() if specific_salary else "Not found"
            else:
                print("Not found")
        
        #Extract Experience 
        tables = soup.find_all('table', class_="table table-hover m-0")
        if len(tables) > 1:  # Check if the second table exists
            experience_tag = tables[1]  # Access the second table
            experience_row = experience_tag.find_all('tr')
            if experience_row:
                specific_experience = experience_row[1].find_all('td')[2]
                experience = specific_experience.text.strip() if specific_experience else "Not found"

        # Extract job description (if available)
        description_tag = soup.find("div", class_='card-text p-2', itemprop="description")
        if description_tag:
            description_para = description_tag.find('ul') or description_tag.find('p')
            job_description = description_para.text.strip() if description_para else "Not found"

    return job_level, no_of_openings, salary, experience, job_description

# Base URL with pagination parameter
base_url = 'https://merojob.com/search/?q=&page='

max_pages = 50  # Change this to limit the number of pages you want to scrape

for page in range(1, max_pages + 1):
    print(f"\nScraping Page {page}...\n")
    url = base_url + str(page)
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        if not soup.find_all('div', class_='col-8 col-lg-9 col-md-9 pl-3 pl-md-0 text-left'):
            print(f"Only {page} job listing pages are available in the website.Stopping Scrapping")
            break
        else:
            extract(soup)
    else:
        print(f"Failed to fetch page {page}")

# Convert the job data list to a DataFrame
df = pd.DataFrame(job_data)

# Save the DataFrame to a CSV file
df.to_csv('merojob_listings.csv', index=False)

print("\nScraping Complete and Data Saved to CSV!")