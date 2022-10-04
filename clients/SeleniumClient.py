from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


class SeleniumClient:
    def __init__(self, sleep_time=3, is_hide=True):
        """notion login까지 완료 된 후에 진행 """
        self.t = sleep_time

        print('[진행중] Selenium 준비중...')

        options = webdriver.ChromeOptions()
        if is_hide:
            options.add_argument("headless")  # 창 숨기기
            options.add_argument("no-sandbox")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")  # for google 로그인 화면

        options.add_argument("window-size=1920,1080")  # for notion 로그인 버튼

        # web driver 시작
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        print('[진행중] Selenium Chrome WebDriver 시작.. ')
        self.driver.implicitly_wait(self.t)

    def tistory_login(self, id, pw):
        # 티스토리 로그인이 카카오로 수정됨
        print('[진행중] Selenium으로 티스토리(카카오) 로그인중..')

        # 로그인창으로 이동 tistory로 redirection
        self.driver.get(
            'https://accounts.kakao.com/login?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fis_popup%3Dfalse%26ka%3Dsdk%252F1.39.10%2520os%252Fjavascript%2520sdk_type%252Fjavascript%2520lang%252Fko-kr%2520device%252FMacIntel%2520origin%252Fhttps%25253A%25252F%25252Fwww.tistory.com%26auth_tran_id%3Dfazrebo4cehb8aef3eeb03fa312b81795386484f051kjmiil9v%26response_type%3Dcode%26state%3DaHR0cHM6Ly93d3cudGlzdG9yeS5jb20v%26redirect_uri%3Dhttps%253A%252F%252Fwww.tistory.com%252Fauth%252Fkakao%252Fredirect%26client_id%3Db8aef3eeb03fa312b81795386484f051')
        sleep(self.t)

        try:
            # 아이디 입력
            self.driver.find_element(By.XPATH, '//*[@id="id_email_2"]').send_keys(id)
            sleep(self.t // 2)
            # 비밀번호 입력
            self.driver.find_element(By.XPATH, '//*[@id="id_password_3"]').send_keys(pw)
            sleep(self.t // 2)

            # 로그인 버튼 클릭
            self.driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[8]/button[1]').click()
            sleep(self.t)
            print('[진행중] Selenium으로 티스토리(카카오) 로그인 완료!')

        except:
            # 환경마다 로그인 페이지가 다른 경우를 대비하여 다른 XPATH 지정
            print('[진행중] 카카오 로그인 재시도..')

            self.driver.find_element(By.XPATH, '//*[@id="input-loginKey"]').send_keys(id)
            sleep(self.t // 2)
            # 비밀번호 입력
            self.driver.find_element(By.XPATH, '//*[@id="input-password"]').send_keys(pw)
            sleep(self.t // 2)

            # 로그인 버튼 클릭
            self.driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/form/div[4]/button[1]').click()
            sleep(self.t)
            print('[진행중] Selenium으로 티스토리(카카오) 로그인 완료!')

    def get_tistory_authorize_code(self, client_id, redirect_uri):
        # 인증 url로 이동 (선행으로 로그인이 되어있어야 함)
        authorize_url = f'https://www.tistory.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
        self.driver.get(authorize_url)

        resp = self.driver.page_source
        soup = BeautifulSoup(resp, 'html.parser')

        code = soup.script.text.split('code=')[1].split('&state')[0]

        return code

    def quit(self):
        self.driver.quit()
