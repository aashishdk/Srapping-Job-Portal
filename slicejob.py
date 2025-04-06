import requests
from bs4 import BeautifulSoup
import pandas as pd

# List to store job data
job_data = []

# Function to extract job data from the listing page
def extract(job):
    divs = job.find_all('div', class_="col-xs-9 col-sm-7")
    if not divs:
        print("No div found")
        return  

    for item in divs:
        # Extract job title container
        title_tag = item.find('ul')
        if title_tag:
            title_find = title_tag.find('li', class_='job_tittle')
            job_title = title_find.text.strip() if title_find else "Not Found"
        else:
            job_title = "No title section found"

        # Extract location
        location_tag = item.find("li", class_='job_company')
        location_title = location_tag.text.strip() if location_tag else "Location not found"

        # Extract the link to the job details page
        job_details_link = item.find('a', href=True)['href'] if item.find('a', href=True) else None
        if job_details_link:
            job_details_url = f"{job_details_link}"

            # Scrape job details page and store the data
            company, job_level, salary, job_description = scrape_job_details(job_details_url)

            # Print the extracted data
            print(f"Job Title: {job_title}")
            print(f"Location: {location_title}")
            print(f"Job URL: {job_details_url}")
            print(f"Company: {company}")
            print(f"Job Level: {job_level}")
            print(f"Salary: {salary}")
            print(f"Job Description: {job_description}")
            print(f"******" * 20)

            # Append job data to the list (if you want to store the data)
            job_data.append({
                'Job Title': job_title,
                'Company': company,
                'Location': location_title,
                'Job Level': job_level,
                'Salary': salary,
                'Job Description': job_description
            })
        else:
            print("Job details link not found")

# Function to scrape job level, salary, and description from the job details page
def scrape_job_details(job_details_url):
    response = requests.get(job_details_url)
    job_level = salary = job_description = "Not found"
    company = "Not found"

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract Company name
        company_tag = soup.find('div', class_="company_desc")
        if company_tag:
            company_row = company_tag.find('h2')
            company = company_row.text.strip() if company_row else "Not Found"

        # Extract job level
        job_level_tag = soup.find('div', id="job_details_inner")  # Find the job details container
        if job_level_tag:
            for ul in job_level_tag.find_all('ul'):  # Loop through all <ul> tags
                list_items = ul.find_all('li')  # Get all <li> inside the current <ul>
                if list_items and "Career Level" in list_items[0].text:  # Check if 1st <li> contains "Career Level"
                    job_level = list_items[1].text.strip()  # Extract text from 2nd <li>

        # Extract Salary
        salary_tag = soup.find('div', id="job_details_inner")
        if salary_tag:
            for ul in salary_tag.find_all('ul'):
                salary_list = ul.find_all('li')
                if salary_list and "Salary" in salary_list[0].text:
                    salary = salary_list[1].text.strip()

        # Extract job description
        description_tag = soup.find("div", id="post_desc")  # Find the div containing job description
        if description_tag:
            # Check if the div contains a <ul> with <li> elements
            job_descriptions_tag = description_tag.find("ul") or description_tag.find('p')
            if job_descriptions_tag:
                job_description = job_descriptions_tag.text.strip()
        else:
            job_description = "Not Found"

    return company, job_level, salary, job_description

# Base URL with pagination parameter
base_url = 'https://www.slicejob.com/jobs/search/?job_category=&job_tittle=&submit=Search&page='

max_pages = 6  # Change this to limit the number of pages you want to scrape

# Loop through each page to scrape the data
for page in range(1, max_pages + 1):
    print(f"\nScraping Page {page}...\n")
    url = base_url + str(page)
    response = requests.get(url)

    # Check if the page exists
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Check if there is content on the page
        if not soup.find('div', class_="col-xs-9 col-sm-7"):  # No job listings found
            print(f"Only {page} pages are available on the website. Stopping scraping.")
            break
        else:
            extract(soup)
    else:
        print(f"Failed to fetch page {page}")
        break

# Convert the job data list to a DataFrame (if you want to save it as CSV)
df = pd.DataFrame(job_data)

# Save the DataFrame to a CSV file
df.to_csv('slicejob_listings.csv', index=False)

print("\nScraping Complete and Data Saved to CSV!")
