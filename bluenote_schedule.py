from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager

# 待機時間
WAIT_SEC = 10

# 初期URL
INITIAL_URL = "https://reserve.bluenote.co.jp/reserve/schedule/move/202402/"

# 押下するリンク
LINK_PATH = "/reserve/schedule/exec/3493"

# リダイレクト先のURL
LINK_REDIRECT_URL = "https://reserve.bluenote.co.jp/reserve/plan"

# 確認用のCSSクラス
CONFIRM_CLASS_NAME = "times"
CONFIRM_CSS_PROPERTY = "background-color"
CONFIRM_CORRECT_COLOR = "#f4f1ea"
CONFIRM_INCORRECT_COLOR = "#eeeeee"

## Lambdaから呼び出される ##
def lambda_handler(event, context):

    # Chromeオプションの設定
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # WebDriverの設定
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(INITIAL_URL)

    try:
        # 2. リンクを開く
        link_element = WebDriverWait(driver, WAIT_SEC).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="{}"]'.format(LINK_PATH)))
        )
        link_element.click()

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
            css_property = div_element.value_of_css_property(CONFIRM_CSS_PROPERTY)
            if css_property.lower() in [CONFIRM_INCORRECT_COLOR, CONFIRM_CORRECT_COLOR]:
                print(f"Div with class 'times' has the correct background color: {css_property}")

    finally:
        # ブラウザを閉じる
        driver.quit()

# ローカル実行用
if __name__ == "__main__":
    lambda_handler(None, None)
