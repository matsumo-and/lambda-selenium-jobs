from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import boto3
import os

# 待機時間
WAIT_SEC = 5

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

# SNS Arn
SNS_ARN = os.environ.get('SNS_ARN')

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

        send_flag = False
        days_count = 0
        seat_count = 0
        for i in range(len(div_elements) - 1):
            
            div_element = div_elements[i]
            
            # WebElementを復元
            element_id = div_element.get("ELEMENT")
            web_element = WebElement(driver, element_id)
    
            # CSSプロパティを取得
            background_image_path = web_element.value_of_css_property("background-image")

            if background_image_path is not None and background_image_path != "none" and CONFIRM_STR not in background_image_path:
                print(f"Div with class 'times' has the correct background image: {background_image_path}")
                days_count += 1

                # 日程が空いているので詳細な席数をしらべる
                # 該当日にちをクリック
                web_element.click()
                # 待機する
                WebDriverWait(driver, WAIT_SEC).until(
                    EC.url_to_be("https://reserve.bluenote.co.jp/reserve/plan/change/")
                )
                
                # クリック後再度復元
                div_elements = driver.find_elements(By.CLASS_NAME, CONFIRM_CLASS_NAME)
                div_element = div_elements[i]
                
                # 席数を確認
                try:
                    seats = driver.find_elements_by_xpath('//div[contains(@class, "active") and contains(@id, "seatingArea_")]')
                    
                    if seats is not None and len(seats) != 0:
                        send_flag = True
                        seat_count += len(seats)
                except:
                    print("空きがありません")

        # 1件でも予約可能であれば通知
        if send_flag:
            message = f"Yussef Dayesのコンサートに{days_count}日程で{seat_count}シートの空きが出ています"
            send_to_sns(message)

    finally:
        # ブラウザを閉じる
        driver.quit()


## SNSで通知する ##
def send_to_sns(message):

    #SNS Clientの作成
    sns_agent = boto3.client('sns')

    # SNSにメッセージを発行
    sns_agent.publish(
        TopicArn=SNS_ARN,
        Message=message,
        Subject="キャンセル待ちが発生しています"
    )

# ローカル実行用
if __name__ == "__main__":
    lambda_handler(None, None)
