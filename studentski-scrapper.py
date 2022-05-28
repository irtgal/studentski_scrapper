from curses.ascii import isdigit
import requests
from bs4 import BeautifulSoup
import json
import statistics
from datetime import date

jobs = []

today = date.today().strftime("%Y-%m-%d")
jobs_file = 'podatki-' + today + '.json'
stats_file = 'statistika-' + today + '.txt'


def extract_job_info(job_div):
    foh = job_div.find('h3').getText()
    tip_element = job_div.find('h5')
    tip = tip_element.getText() if tip_element else None
    atributi = job_div.find_all("ul", {'class': 'job-attributes'})[0]
    lokacija = atributi.find("li").getText().strip()
    neto = atributi.find("li", {'class': 'job-payment'}).find('strong').getText().replace("€/h neto", '').strip()
    job = {'foh': foh, 'tip': tip, 'lokacija': lokacija, 'neto': neto}
    return job
    
def scrape_studentski():
    print('Scrappam studentski-servis.com')
    URL = f"https://www.studentski-servis.com/studenti/prosta-dela?page=1"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    page_number = 1
    max_page = int(soup.find_all('a', {'class': 'page-link'})[-2].getText())

    while page_number <= max_page:
        URL = f"https://www.studentski-servis.com/studenti/prosta-dela?page={page_number}"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")
        job_divs = soup.find_all("article", {"class": "job-item"})
        for job_div in job_divs:
            jobs.append(extract_job_info(job_div))
        print(f'Stran: {page_number}/{max_page}')
        page_number += 1

    with open(jobs_file, 'w') as file:
        file.write(json.dumps(jobs))
        

def get_all_jobs():
    f = open(jobs_file, "r")
    return json.loads(f.read())
    
def get_fohs():
    fohs = set()
    jobs = get_all_jobs()
    for job in jobs:
        fohs.add(job["foh"])
    return fohs
   

def get_stats(foh=None):
    neto_list = []
    neto_not_specified = 0
    foh_name = 'VSA'
    if (foh):
        jobs_list = [job for job in get_all_jobs() if job["foh"] == foh]
        foh_name = foh
    else:
        jobs_list =  get_all_jobs()
        
    for job in jobs_list:
        neto = job["neto"]
        try:
            neto_float = float(neto)
            neto_list.append(neto_float)
        except ValueError:
            neto_not_specified += 1

    if len(neto_list) == 0:
        print('NAPAKA: Ni informacij o placah za: ', foh)
        return ''
            
    count = len(neto_list)
    average = sum(neto_list)/len(neto_list)
    median = statistics.median(neto_list)
    max_neto = max(neto_list)
    return (f'''
Vrsta dela: {foh_name}
Stevilo plac: {count}
Povprecna placa: {average}
Mediana: {median}
Najvisja placa: {max_neto}
Placa ni podana: {neto_not_specified}
          ''')
    
def generate_stat_file():
    scrape_studentski()
    stats = [get_stats()] # prvo naredi statistiko za vse vrste del
    for foh in get_fohs():
        stats.append(get_stats(foh))
        with open(stats_file, 'w', encoding="utf-8") as file:
            for stat in stats:
                file.write(stat)
    
        
        
    
    
generate_stat_file()
