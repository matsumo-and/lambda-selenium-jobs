from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 初期URL
initial_url = "https://reserve.bluenote.co.jp/reserve/schedule/move/202402/"

# WebDriverの設定
driver = webdriver.Chrome()  # Chromeドライバーを使用する場合
driver.get(initial_url)

try:
    # 2. リンクを開く
    link_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href="/reserve/schedule/exec/3493"]'))
    )
    link_element.click()

    # 3. URLが正しいか確認
    expected_url = "https://reserve.bluenote.co.jp/reserve/plan"
    WebDriverWait(driver, 10).until(
        EC.url_to_be(expected_url)
    )
    current_url = driver.current_url
    if current_url == expected_url:
        print(f"Successfully navigated to {expected_url}")
    else:
        print(f"Unexpected URL: {current_url}")

    # 4. 特定のDivタグのCSS取得
    div_elements = driver.find_elements(By.CLASS_NAME, "times")
    for div_element in div_elements:
        background_color = div_element.value_of_css_property("background-color")
        if background_color.lower() in ["#eeeeee", "#f4f1ea"]:
            print(f"Div with class 'times' has the correct background color: {background_color}")

finally:
    # セッション維持のためにブラウザを閉じない
    pass
