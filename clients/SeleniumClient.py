from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

KAKAO_LOGIN_PAGE = 'https://accounts.kakao.com/login?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fis_popup%3Dfalse%26ka%3Dsdk%252F1.43.0%2520os%252Fjavascript%2520sdk_type%252Fjavascript%2520lang%252Fen-US%2520device%252FMacIntel%2520origin%252Fhttps%25253A%25252F%25252Fwww.tistory.com%26auth_tran_id%3Dn11fn9p740o3e6ddd834b023f24221217e370daed18l9ms8up0%26response_type%3Dcode%26state%3DaHR0cHM6Ly93d3cudGlzdG9yeS5jb20v%26redirect_uri%3Dhttps%253A%252F%252Fwww.tistory.com%252Fauth%252Fkakao%252Fredirect%26through_account%3Dtrue%26client_id%3D3e6ddd834b023f24221217e370daed18&talk_login=hidden'


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
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=options
            )
        except:
            self.driver = webdriver.Chrome(options=options)

        print('[진행중] Selenium Chrome WebDriver 시작.. ')
        self.driver.implicitly_wait(self.t)

    def _input_email(self, id):

        # 환경마다 로그인 페이지가 다른 경우를 대비하여 다른 XPATH 지정
        identifiers = [
            (By.XPATH, '//*[@id="id_email_2"]'),
            (By.XPATH, '//*[@id="loginKey--1"]'),
            (By.XPATH, '//*[@id="loginId--1"]')
        ]

        # 아이디 입력
        for i, identifier in enumerate(identifiers):
            try:
                self.driver.find_element(*identifier).send_keys(id)
                print('[진행중] Tistory(with KAKAO) 아이디 입력 완료!')
                break
            except:
                sleep(self.t // 2)
                print('[진행중] Selenium으로 아이디 입력중...', i + 1)
                continue
        else:
            print(f'카카오 페이지 URL: {KAKAO_LOGIN_PAGE}')
            raise ValueError('[Error] Selenium으로 아이디 입력 실패. 카카오 로그인 페이지에서 아이디 XPATH 값을 확인해주세요.')

    def _input_password(self, pw):

        # 환경마다 로그인 페이지가 다른 경우를 대비하여 다른 XPATH 지정
        identifiers = [
            (By.XPATH, '//*[@id="id_password_3"]'),
            (By.XPATH, '//*[@id="password--2"]')
        ]

        # 비밀번호 입력
        for i, identifier in enumerate(identifiers):
            try:
                self.driver.find_element(*identifier).send_keys(pw)
                print('[진행중] Tistory(with KAKAO) 비밀번호 입력 완료!')
                break
            except:
                sleep(self.t // 2)
                print('[진행중] Selenium으로 패스워드 입력중...', i + 1)
                continue
        else:
            print(f'카카오 페이지 URL: {KAKAO_LOGIN_PAGE}')
            raise ValueError('[Error] Selenium으로 비밀번호 입력 실패. 카카오 로그인 페이지에서 비밀번호 XPATH 값을 확인해주세요.')

    def tistory_login(self, id, pw):
        # 티스토리 로그인이 카카오로 수정됨
        print('[진행중] Selenium으로 티스토리(카카오) 로그인중..')

        # tistory의 카카오 로그인 창으로 이동
        self.driver.get(KAKAO_LOGIN_PAGE)
        sleep(self.t)

        # 아이디 입력
        self._input_email(id)

        # 비밀번호 입력
        self._input_password(pw)

        # 로그인 버튼 클릭
        self.driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/form/div[4]/button[1]').click()
        sleep(self.t + 5)  # 로그인 완료까지 시간이 걸림

        print('[진행중] Selenium으로 티스토리(카카오) 로그인 완료!')

    def get_tistory_authorize_code(self, client_id, redirect_uri):
        # 인증 url로 이동 (선행으로 로그인이 되어있어야 함)
        authorize_url = f'https://www.tistory.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
        self.driver.get(authorize_url)

        resp = self.driver.page_source
        soup = BeautifulSoup(resp, 'html.parser')

        try:
            code = soup.script.text.split('code=')[1].split('&state')[0]
        except:
            print(soup.prettify())
            raise ValueError(f'[Error] Tistory 인증 코드 발급 실패. 위의 출력 메시지를 보고 로그인이 되어있는지 확인해주세요.')

        return code

    def quit(self):
        self.driver.quit()
