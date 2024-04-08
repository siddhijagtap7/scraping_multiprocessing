import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import dateparser
from multiprocessing import Pool
import time
from datetime import datetime

with open('config.json') as config_file:
    config = json.load(config_file)

import logger       #Import Logger File


def scrape_news_google(page, company_key):
    url = f"https://www.google.com/search?q={company_key}&tbm=nws&page={page}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all('div', {'class': 'BNeawe vvjwJb AP7Wnd'})
        links = soup.find_all(attrs={'class':'Gx5Zad fP1Qef xpd EtOod pkphOe'})
        times = soup.find_all('span', {'class': 'r0bn4c rQMQod'})
        medianame = soup.find_all('div', {'class': ['BNeawe UPmit AP7Wnd lRVwie']})
        results = []
        for i in range(len(headlines)):
            link=links[i].find('a')['href']
            result = {
                "Search String": company_key.replace('+',' '),
                "Search Engine": "Google",
                "Link": link.split('/url?q=')[1].split('&sa=U&')[0],
                "Heading": headlines[i].text,
                "TimeFrame": times[i].text,
                "Media Name": medianame[i].text
            }
            results.append(result)
        return results
    except Exception as e:
        logging.error(f"Error scraping Google page {page}: {e}")
        return []


def scrape_news_yahoo(page, company_key):
    url = f"https://news.search.yahoo.com/search?p={company_key}&b{((page-1)*10)+1}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all('h4', {'class': 's-title fz-16 lh-20'})
        links = soup.find_all('a', {'href': True})
        times = soup.find_all('span', {'class': 'fc-2nd s-time mr-8'})
        medianame = soup.find_all('span', {'class': 's-source mr-5 cite-co'})
        results = []
        for i in range(len(headlines)):
            result = {
                "Search String": company_key.replace('+',' '),
                "Search Engine": "Yahoo",
                "Link": links[i]['href'],
                "Heading": headlines[i].text,
                "TimeFrame": times[i].text,
                "Media Name": medianame[i].text
            }
            results.append(result)
        return results
    except Exception as e:
        logging.error(f"Error scraping Yahoo page {page}: {e}")
        return []


def scrape_news_bing(page, company_key):
    a = ((page - 1) * 10) + 1
    url = f"https://www.bing.com/news/search?q={company_key}&first={a}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.select('div.t_t a.title')
        links = soup.select('div.t_t a.title')
        times = soup.find_all('span', attrs={'tabindex': '0'})
        medianame = soup.find_all('div', attrs={'class': 'news-card newsitem cardcommon'})
        results = []
        for i in range(len(headlines)):
            result = {
                "Search String": company_key.replace('+',' '),
                "Search Engine": "Bing",
                "Link": links[i]['href'],
                "Heading": headlines[i].text,
                "TimeFrame": times[i].text,
                "Media Name": medianame[i]["data-author"]
            }
            results.append(result)
        return results
    except Exception as e:
        logging.error(f"Error scraping Bing page {page}: {e}")
        return []


def scrape_news_multiprocess(args):
    company_key, no_of_pages = args
    results = []

    #if search_engine == "Google":
    scrape_page_function = scrape_news_google
    #elif search_engine == "Yahoo":
    scrape_page_function1 = scrape_news_yahoo
    #else:
    scrape_page_function2 = scrape_news_bing

    with Pool() as pool:        #Pool() can executes multiple processes simultaneously and run asynchronously and store multiple lists
        results.extend(pool.starmap(scrape_page_function, [(page, company_key) for page in range(1, no_of_pages + 1)]))      #starmap() is used to pass multiple arguments
        results.extend(pool.starmap(scrape_page_function1, [(page, company_key) for page in range(1, no_of_pages + 1)]))      #starmap() is used to pass multiple arguments
        results.extend(pool.starmap(scrape_page_function2, [(page, company_key) for page in range(1, no_of_pages + 1)]))      #starmap() is used to pass multiple arguments
        
    return [item for sublist in results for item in sublist]

def convert_timeframe_format(all_results):
    results=[]
    for result in all_results:
        set_date=result["TimeFrame"]
        parse_date=dateparser.parse(set_date,settings={'TIMEZONE':'UTC'})   #UTC is the date format when we not set then takes default

        if(parse_date):
            formatted_date=parse_date.strftime('%d-%m-%Y')
            result['TimeFrame']=formatted_date
        results.append(result)

    return results

def main():
    all_results = []
    cross_company_key=[]
    try:
        if(not config["search_company"] or not config["search_keyword"] or config["no_of_pages"]<=0):
            print("Enter valid input...")
        else:
            for company in config["search_company"]:
                for key in config["search_keyword"]:
                    cross_company_key.append(f'{company}+{key}')
                    #for search_engine in config["search_engines"]:
            for company_key in cross_company_key:
                results = scrape_news_multiprocess(( company_key, config["no_of_pages"]))
                all_results.extend(results)
            
    except Exception as e:
        logging.error(f"Error scraping in main() function: {e}")

    except ValueError as e:
        logging.error("Enter valid input...")

    convert_date = convert_timeframe_format(all_results)
    all_results.extend(convert_date)
    timestamp=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_file=f"output_{timestamp}.csv"

    df = pd.DataFrame(all_results)
    print(df)
    with open(output_file,'w',newline='',encoding='utf-8') as csv_file:
                    #Store all_results in CSV file
        df.to_csv(csv_file,index=False)    
        print(f"Scraping Completed successfully. Data stored in {output_file}")
        logging.info(f"Scraping Completed successfully. Data stored in {output_file}")


if __name__ == "__main__":
    #start_time=time.time()
    main()
    #print(time.time()-start_time)
