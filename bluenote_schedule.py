from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

# 待機時間
WAIT_SEC = 10

# 初期URL
INITIAL_URL = "https://reserve.bluenote.co.jp/reserve/schedule/move/202402/"

# 押下するリンク
LINK_PATH = "https://reserve.bluenote.co.jp/reserve/schedule/exec/3493"

# リダイレクト先のURL
LINK_REDIRECT_URL = "https://reserve.bluenote.co.jp/reserve/plan"

# 確認用のCSSクラス
CONFIRM_CLASS_NAME = "times"
CONFIRM_CSS_PROPERTY = "background-image"
CONFIRM_STR = "sellout"

## Lambdaから呼び出される ##
def lambda_handler(event, context):

    options = webdriver.ChromeOptions()
    # headless-chromiumのパスを指定
    options.binary_location = "/opt/headless/headless-chromium"
    options.add_argument("--headless")
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        # chromedriverのパスを指定
        executable_path="/opt/headless/chromedriver",
        options=options
    )

    driver.get(INITIAL_URL)

    try:
        # 2. リンクを開く
        driver.get(LINK_PATH)

        # 3. URLが正しいか確認
        WebDriverWait(driver, WAIT_SEC).until(
            EC.url_to_be(LINK_REDIRECT_URL)
        )
        current_url = driver.current_url
        if current_url == LINK_REDIRECT_URL:
            print(f"Successfully navigated to {LINK_REDIRECT_URL}")
        else:
            print(f"Unexpected URL: {current_url}")

        # 4. 特定のDivタグのCSS取得
        div_elements = driver.find_elements(By.CLASS_NAME, CONFIRM_CLASS_NAME)
        
        for div_element in div_elements:
            
            # WebElementを復元
            element_id = div_element.get("ELEMENT")
            web_element = WebElement(driver, element_id)
    
            # CSSプロパティを取得
            background_image_path = web_element.value_of_css_property("background-image")

            if background_image_path is not None and CONFIRM_STR in background_image_path:
                print(f"Div with class 'times' has the correct background image: {background_image_path}")

    finally:
        # ブラウザを閉じる
        driver.quit()

# ローカル実行用
if __name__ == "__main__":
    lambda_handler(None, None)
