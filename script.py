import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import asyncio
from concurrent.futures import ThreadPoolExecutor


num_threads = 24

def check_xFanTV(addresses, results, start):
    options = Options()
    options.add_argument('--headless')
    options.headless = True
    service = Service(executable_path='msedgedriver.exe')
    driver = webdriver.Edge(options=options, service=service)

    for i, address in enumerate(addresses):
        driver.get(f"https://suivision.xyz/account/{address}?tab=Assets")
        try:
            element = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'xFanTV')]"))
            )
            print(f"{i}: {address} - xFanTV: True")
            results[start + i] = True
        except:
            print(f"{i}: {address} - xFanTV: False")
            results[start + i] = False
    driver.quit()

def task(df, start, end, results):
    addresses = df.loc[start:end, 'address'].tolist()
    check_xFanTV(addresses, results, start)


async def checkfile(fileName):
    df = pd.read_excel(fileName, names=['name', 'address'])
    chunk_size = len(df) // num_threads
    results = [None] * len(df)

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        tasks = []
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < num_threads - 1 else len(df) - 1
            tasks.append(loop.run_in_executor(executor, task, df, start, end, results))
        await asyncio.gather(*tasks)

    df['xFanTV'] = results
    df.to_excel(f"{fileName}_lan2.xlsx", index=False)

file_list = [
    'updated_data.xlsx'
]

for file in file_list:
    asyncio.run(checkfile(file))

print("All done")