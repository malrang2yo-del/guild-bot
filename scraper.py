import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# 설정
GUILD_NAME = "비글" # 길드명
URL = f"https://meaegi.com/g/{GUILD_NAME}"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    driver.implicitly_wait(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # UI 변경에 대비하여 화면 내 모든 텍스트 중 '가입', '탈퇴' 단어가 포함된 문장만 추출
    history_list = [text for text in soup.body.stripped_strings if "가입" in text or "탈퇴" in text]
    
    if not history_list:
        raise Exception("사이트 접속 실패 또는 길드 히스토리 내역이 없습니다.")

    latest_record = history_list[0] # 가장 최신 기록

    # 중복 알림 방지 로직 (이전 데이터와 비교)
    last_saved = ""
    if os.path.exists("last_data.txt"):
        with open("last_data.txt", "r", encoding="utf-8") as f:
            last_saved = f.read().strip()

    if latest_record != last_saved:
        # 디스코드로 전송
        requests.post(WEBHOOK_URL, json={"content": f"🚨 **[길드 히스토리 업데이트]**\n> {latest_record}", "username": "길드 알림봇"})
        
        # 갱신된 기록 저장
        with open("last_data.txt", "w", encoding="utf-8") as f:
            f.write(latest_record)

except Exception as e:
    requests.post(WEBHOOK_URL, json={"content": f"⚠️ **크롤러 오류:** {e}", "username": "길드 알림봇"})
finally:
    driver.quit()
