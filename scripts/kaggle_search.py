from kaggle.api.kaggle_api_extended import KaggleApi
import os

api = KaggleApi()
api.authenticate()

try:
    results = api.dataset_list(search='ielts', page=1)
    print(f'Found {len(results)} items')
    for d in results:
        print(f"{d.ref}: {d.title} | url={d.url}")
except Exception as e:
    print('Kaggle search failed:', e)
