import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_image_urls(url: str):
    driver.get(url)
    time.sleep(1)
    img_tags = driver.find_elements(By.TAG_NAME, "img")
    return {img.get_attribute("src") for img in img_tags if img.get_attribute("src") and "https://a0.muscache.com/im/pictures/" in img.get_attribute("src")}
