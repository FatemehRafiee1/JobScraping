import json
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

from key_extractor import ner

with open("proxy.txt", 'r') as f:
    proxies = f.read().split('\n')

with open("user_agents.txt", 'r') as f:
    user_agents = f.read().split('\n')

def find_nearest_punctuation_index(text, index):
    punctuations = {'.', ',', ';', ':', '!', '?'}
    
    # Search left for the nearest punctuation
    for i in range(index, -1, -1):
        if text[i] in punctuations:
            return i
    
    # Search right for the nearest punctuation
    for i in range(index, len(text)):
        if text[i] in punctuations:
            return i
    
    # If no punctuation found, return the original index
    return index

def split_at_punctuation(long_string):
    length = len(long_string)
    part_length = length // 3
    
    # Find the index to split each part
    split_points = [part_length, 2 * part_length]
    for i in range(len(split_points)):
        split_points[i] = find_nearest_punctuation_index(long_string, split_points[i])
    
    # Split the string at the found indices
    part1 = long_string[:split_points[0]]
    part2 = long_string[split_points[0]:split_points[1]]
    part3 = long_string[split_points[1]:]
    
    return part1, part2, part3

# get raw data from website
def get_data(url, proxies, headers):
    while True:
        proxy = random.choice(proxies)
        try:
            print(f"Using proxy: {proxy}")
            res = requests.get(url, proxies={'http': proxy}, headers=headers)
            if res.status_code == 200:
                print("Success")
                return res
        except Exception as e:
            print(f"Failed to fetch data from {url}: {e}")

# get job title, company, date published, location, and url link
def extract_job_details(url, proxies, headers, n_jobs):
    while True:
        response = get_data(url, proxies, headers)
        page_text = BeautifulSoup(response.text, 'html.parser')
        section = page_text.find('section', class_='two-pane-serp-page__results-list')
        if n_jobs>jobs_per_page:
            jobs = section.find_all('li')  
        elif n_jobs==jobs_per_page:
            jobs = page_text.find_all('li')
        if len(jobs) == n_jobs:
            break
        print("Index out of range...")

    titles = [jobs[i].find('h3', class_='base-search-card__title').text.strip() for i in range(n_jobs)]
    subtitles = [jobs[i].find('h4', class_='base-search-card__subtitle').text.strip() for i in range(n_jobs)]
    locations = [jobs[i].find('span', class_='job-search-card__location').text.strip() for i in range(n_jobs)]
    dates = [jobs[i].find('time', class_='job-search-card__listdate--new').get('datetime') if jobs[i].find('time', class_='job-search-card__listdate--new') else jobs[i].find('time', class_='job-search-card__listdate').get('datetime') for i in range(n_jobs)]
    links = [jobs[i].find('a').get('href') for i in range(n_jobs)]

    if len(titles) == len(subtitles) == len(locations) == len(dates) == len(links):
        print('Lengths OK.')
    else:
        print("Length Mismatch!")
        print(len(titles), len(subtitles), len(locations), len(dates), len(links))
        return None, None, None, None, None
    
    return titles, subtitles, locations, dates, links

# extract job keywords from the thorough description
def extract_job_keywords(url, proxies, headers):
    knowledge = []
    response = get_data(url, proxies=proxies, headers=headers)
    if response:
        page_text = BeautifulSoup(response.text, 'html.parser')
        job_section = page_text.find('section', class_='core-section-container my-3 description')
        if job_section:
            description = job_section.find('div', class_='show-more-less-html__markup').text.strip()
            knowledge = [ner(text)[1] for text in split_at_punctuation(description)]

            result = []
            for j in range(len(knowledge)):
                for i in range(len(knowledge[j]['entities'])):
                    if knowledge[j]['entities'][i]['score'] > 0.99:
                        result.append(knowledge[j]['entities'][i]['word'])
            return result      
    return None


# parameters
iteration = 2
jobs_per_page = 25
proxy_file_path = "proxy.txt"
output_file_path = "sample_500.csv"
user_agents_file_path = "user_agents.txt"

url_base = 'https://www.linkedin.com/jobs/search?keywords=Python&location=United%20States&geoId=103644278&f_E=2&f_TPR=&f_WT=2&position=1&pageNum=0'
url_rest = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python&location=United%2BStates&geoId=103644278&f_E=2&f_TPR=&f_WT=2'

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}           

def fetch_job_data(url_base, url_rest, proxies, headers):
    start = True
    titles_total, subtitles_total, locations_total, dates_total, links_total = [], [], [], [], []
    for idx in range(0, iteration * jobs_per_page + 1, jobs_per_page):
        if start:
            current_url = url_base
        else:
            current_url = f'{url_rest}&start={idx-jobs_per_page}'
        titles, subtitles, locations, dates, links = extract_job_details(current_url, proxies, headers, 60 if start else jobs_per_page)
        start = False
        print(idx-jobs_per_page)
        if titles and subtitles and locations and dates and links:
            titles_total.extend(titles)
            subtitles_total.extend(subtitles)
            locations_total.extend(locations)
            dates_total.extend(dates)
            links_total.extend(links)
            print(len(titles), len(subtitles), len(locations), len(dates), len(links))

    return titles_total, subtitles_total, locations_total, dates_total, links_total

titles_total, subtitles_total, locations_total, dates_total, links_total = fetch_job_data(url_base, url_rest, proxies, headers)


# Extract job descriptions and keywords
skills_list = []
for link in links_total:
    detected_keywords = extract_job_keywords(link, proxies, headers)
    if detected_keywords:
        skills_list.append(detected_keywords)


# Create DataFrame
df = pd.DataFrame({'title': titles_total, 'company': subtitles_total, 'location': locations_total, 'date': dates_total, 'link': links_total})
df['skills'] = skills_list

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"Data saved to {output_file_path}")
