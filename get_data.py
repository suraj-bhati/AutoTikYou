import asyncio
import csv
import json
from douyin_tiktok_scraper.scraper import Scraper

api = Scraper()

async def hybrid_parsing(url: str) -> dict:
    # Hybrid parsing(Douyin/TikTok URL)
    result = await api.hybrid_parsing(url)
    print(f"The hybrid parsing result:\n {result}")
    return result

def read_url_from_csv(filename: str) -> str:
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        # Assuming the URL is in the first column of the CSV
        for row in csv_reader:
            return row[0]
    return None

def save_data_to_json(filename: str, data: dict):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

url = read_url_from_csv("urls.csv")
if url:
    response = asyncio.run(hybrid_parsing(url))
    save_data_to_json("data.json", response)
else:
    print("No URL found in the CSV file.")

