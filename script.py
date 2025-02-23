import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from threading import Thread

# reading csv file 
df = pd.read_excel("data.xlsx", names=['name', 'address'])

def check_xFanTV(addresses, results, start):
    options = Options()
    options.add_argument('--headless')
    options.headless = True
    driver = webdriver.Edge(options=options)
    
    for i, address in enumerate(addresses):
        driver.get(f"https://suivision.xyz/account/{address}?tab=Assets")
        try:
            # Đợi phần tử chứa chữ "xFanTV" xuất hiện
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'xFanTV')]"))
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

# Chia DataFrame thành 6 phần và chạy 6 luồng song song
threads = []
num_threads = 8
chunk_size = len(df) // num_threads
results = [None] * len(df)

for i in range(num_threads):
    start = i * chunk_size
    end = start + chunk_size - 1 if i < num_threads - 1 else len(df) - 1
    t = Thread(target=task, args=(df, start, end, results))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Cập nhật DataFrame với kết quả
df['xFanTV'] = results

# Save the updated DataFrame to a new Excel file
df.to_excel("updated_data.xlsx", index=False)