import requests
from bs4 import BeautifulSoup as bs
import json

def get_content_value(row_data):
    if row_data.find("li"):
        return [li.get_text(" ", strip=True).replace("\xa0", " ") for li in row_data.find_all("li")]
    elif row_data.find("br"):
        return [text for text in row_data.stripped_strings]
    else:
        return row_data.get_text(" ", strip=True).replace("\xa0", " ")

def clean_tags(soup):
    for tag in soup.find_all(["sup", "span"]):
        tag.decompose()

def get_info_box(url):
    try:
        r = requests.get(url, timeout=15)
        soup = bs(r.content, 'html.parser')
        info_box = soup.find(class_="infobox vevent")
        info_rows = info_box.find_all("tr")

        clean_tags(soup)

        movie_info = {}
        for index, row in enumerate(info_rows):
            if index == 0:
                movie_info['title'] = row.find("th").get_text(" ", strip=True)
            else:
                header = row.find('th')
                if header:
                    content_key = row.find("th").get_text(" ", strip=True)
                    content_value = get_content_value(row.find("td"))
                    movie_info[content_key] = content_value

        return movie_info
    except Exception as e:
        print(f"An error occurred while scraping {url}: {str(e)}")
        return None

base_path = "https://en.wikipedia.org/"
movie_info_list = []

for i in range(0, 20):
    for j in range(1900, 2000):
        url = f"https://en.wikipedia.org/wiki/List_of_American_films_of_{j}"
        try:
            r = requests.get(url, timeout=30)
            soup = bs(r.content, 'html.parser')
            movies = soup.select(".wikitable.sortable i a")

            for index, movie in enumerate(movies):
                if index % 10 == 0:
                    print(index)
                try:
                    relative_path = movie['href']
                    full_path = base_path + relative_path
                    title = movie['title']

                    movie_info_list.append(get_info_box(full_path))
                except Exception as e:
                    print(movie.get_text())
                    print(e)
        except requests.exceptions.Timeout:
            print(f"Timeout occurred while scraping {url}")
        except Exception as e:
            print(f"An error occurred while scraping {url}: {str(e)}")

with open('movie_info_list.json', 'w') as f:
    json.dump(movie_info_list, f)
