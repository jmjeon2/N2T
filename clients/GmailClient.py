import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GMailClient:
    def __init__(self, email, key):
        self.email = email
        self.key = key

        # 세션생성, 로그인
        self.s = smtplib.SMTP('smtp.gmail.com', 587)
        self.s.starttls()
        self.s.login(self.email, self.key)

    def send_mail(self, to_email, title, content):
        # 제목, 본문 작성
        msg = MIMEMultipart()
        msg['Subject'] = title
        msg.attach(MIMEText(content, 'plain'))

        # 메일 전송
        self.s.sendmail(self.email, to_email, msg.as_string())

    def close(self):
        self.s.quit()

if __name__=='__main__':

    from config_private import cfg

    gclient = GMailClient(cfg.MAIL.ID, cfg.MAIL.KEY)
    gclient.send_mail(cfg.MAIL.ID, 'title', 'content')
    gclient.close()