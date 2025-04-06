from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Set up Selenium with Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Path to the ChromeDriver
driver_path = r"E:\chromedriver-win64\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the URL
url = "https://www.vocalpanda.com/search?query=&address=Kathmandu,%20Nepal&location=null&lat=27.7103145&lng=85.3221634"
driver.get(url)

#storing scraped data into jobs
jobs = []

# Maximum number of pages to scrape
max_pages = 15

for page in range(1, max_pages + 1):
    print(f"\nScraping Page {page}....")

    try:
        # Wait for job listings to load
        job_listings = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.trendingJobCard"))
        )

        if not job_listings:
            print("No job listings found on this page.")
        else:
            for job in job_listings:
                try:
                    # Extract Job Title and link
                    job_title_element = job.find_element(By.CSS_SELECTOR, "div.company_name a.Desktop_H5_Bold")
                    job_title = job_title_element.text
                    job_link = job_title_element.get_attribute("href")

                    # Extract Location
                    location = job.find_element(By.CSS_SELECTOR, "div.Desktop_Small1_Regular").text

                    # Extract Company Name
                    company = job.find_element(By.CSS_SELECTOR, "div.Desktop_Body1_Medium a").text

                    # Open job details page in new tab
                    driver.execute_script("window.open(arguments[0]);", job_link)
                    driver.switch_to.window(driver.window_handles[1])  # Switch to new tab

                    try:
                        # Wait for job detail sections to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.bottomDetailRendererList"))
                        )
                        detail_blocks = driver.find_elements(By.CSS_SELECTOR, "div.bottomDetailRendererList")

                        job_level = "Not Found"
                        for block in detail_blocks:
                            spans = block.find_elements(By.TAG_NAME, "span")
                            if len(spans) >= 2:
                                label = spans[0].text.strip().lower()
                                value = spans[1].text.strip()
                                if label == "job level":
                                    job_level = value
                                    break

                    except Exception as e:
                        job_level = "Not Found"

                    try:
                        # Find all span elements with class Desktop_Body2_Medium
                        spans = driver.find_elements(By.CSS_SELECTOR, 'span.Desktop_Body2_Medium')

                        salary = "Not Found"
                        if len(spans) > 1:
                            salary = spans[1].text.strip()

                    except Exception as e:
                        salary = "Not Found"
                        print(f"Error extracting salary: {e}")

                    try:
                        description = "Not Found"
                        description_container = driver.find_element(By.CSS_SELECTOR, 'div.job_description')

                        # Try to extract from <ul> tags
                        ul_elements = description_container.find_elements(By.TAG_NAME, "ul")
                        if ul_elements:
                            description = "\n".join([ul.text.strip() for ul in ul_elements if ul.text.strip()])
                        else:
                            # If no <ul>, try extracting from <p> tags
                            p_elements = description_container.find_elements(By.TAG_NAME, "p")
                            if p_elements:
                                description = "\n".join([p.text.strip() for p in p_elements if p.text.strip()])

                    except Exception as e:
                        description = "Not Found"
                        print(f"Error fetching description: {e}")


                    # Close job tab and switch back to listings
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    jobs.append({
                        'Job_Title': job_title,
                        'Company': company,
                        'Location': location,
                        'Job Level': job_level,
                        'Salary': salary,
                        'Job Description': description
                    }) 

                    # Print Job Info
                    print(f"Job Title: {job_title}")
                    print(f"Location: {location}")
                    print(f"Company: {company}")
                    print(f"Job Level: {job_level}")
                    print(f"Salary: {salary}")
                    print(f"Description: {description}\n")
                    print('-------'*10)

                except Exception as e:
                    print(f"Error extracting job details: {e}")

        # Try to click "Next Page"
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.ant-pagination-next"))
            )
            if "ant-pagination-disabled" in next_button.get_attribute("class"):
                print("Pagination ended. No more pages.")
                break
            next_button.click()
            time.sleep(3)
        except Exception as e:
            print(f"Next button issue: {e}")
            break

    except Exception as e:
        print(f"Error: {e}")


# Close the driver after scraping
df = pd.DataFrame(jobs)
df.to_csv("Vocal_panda_listenings.csv",index=False)
print("Scrapping Completed......")
driver.quit()
