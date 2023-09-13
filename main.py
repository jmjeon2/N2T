from clients.TistoryClient import TistoryClient
from clients.SeleniumClient import SeleniumClient
from clients.NotionClient import Notion
from clients.ExportClient import NotionBackUpClient
from notion.block import CodeBlock
from utils.utils import *
from utils.parse import *
from clients.GmailClient import *
from datetime import datetime
import sys, os
import warnings
import traceback

warnings.filterwarnings('ignore')


class Notion2Tistory:
    def __init__(self, cfg, sleep_time=10, selenium_debug=False):

        # time log
        timestamp = datetime.now().strftime('%Y_%m%d_%H%M%S')
        print(f'\n[{timestamp}]')

        # notion 로그인
        self.n_client = Notion(cfg.NOTION.TOKEN_V2)

        # notion exporter 객체 생성
        self.export_client = NotionBackUpClient(cfg.NOTION.TOKEN_V2, cfg.NOTION.DOWNLOAD_DIR)

        # setting
        self.cfg = cfg

        # post, modify할 페이지 각각 가져오기
        self.pages = self.n_client.get_pages_readyToPost(table_url=cfg.NOTION.TABLE_PAGE_URL,
                                                         target_column=cfg.NOTION.COLUMN.STATUS,
                                                         target_upload_value=cfg.NOTION.POST.UPLOAD_VALUE,
                                                         target_modify_value=cfg.NOTION.POST.MODIFY_VALUE,
                                                         url_column=cfg.NOTION.COLUMN.URL
                                                         )

        # upload할 페이지 체크해서 없으면 프로그램 종료
        if len(self.pages) == 0:
            print('[완료] 발행할 할 페이지가 없습니다.')
            sys.exit(1)

        # selenium 시작
        self.s_client = SeleniumClient(sleep_time=sleep_time, is_hide=(not selenium_debug))

        # selenium으로 kakao(tistory) 로그인, authorize code 발급받기(for OAuth)
        try:
            self.s_client.tistory_login(cfg.TISTORY.ID, cfg.TISTORY.PW)
        except Exception as e:
            print(e)
            print('[오류] 카카오톡 로그인 실패')
            sys.exit(1)
        authorize_code = self.s_client.get_tistory_authorize_code(cfg.TISTORY.CLIENT_ID, cfg.TISTORY.REDIRECT_URI)

        # 위에서 발급받은 code로 tistory 로그인(access_token 발급받기)
        self.t_client = TistoryClient(authorize_code,
                                      cfg.TISTORY.SECRET_KEY,
                                      cfg.TISTORY.CLIENT_ID,
                                      cfg.TISTORY.REDIRECT_URI,
                                      cfg.TISTORY.BLOG_NAME)

        # selenium client 종료
        self.s_client.quit()

    def posts(self):
        for i, page in enumerate(self.pages):
            # download html page
            self.export_page(page)
            print(f'[진행중] {i + 1}번째 페이지 다운로드 완료...')

            # get downloaded file path
            download_dir = os.path.expanduser(self.cfg.NOTION.DOWNLOAD_DIR)
            page_path = get_html_path(download_dir)

            # parsing html to notion style page, post tistory
            self.parse_and_post(page, page_path)

            # 업로드한 페이지의 파일 삭제
            delete_file(page_path)
            print(f'\t[진행중] 페이지 파일 삭제완료! [{page_path}]')

        return self.pages

    def export_page(self, page):
        page_id = page[0].id
        self.export_client.export(page_id, 'html', self.n_client.file_token)

    def translate_img_url(self, contents):
        """
        html content내의 이미지(url)를 attach api의 url로 변경하기
        """
        figure_tags = contents.find_all('figure', class_='image')

        for i, figure_tag in enumerate(figure_tags):
            fp = figure_tag.img['src']

            # 외부 url의 경우 skip
            if fp.startswith('http'):
                continue

            url, replacer = self.t_client.attach(fp)

            # replacer 를 이용 하는 건 deprecated (-1로 동작하지 않도록 함)
            if i == -1:  # 첫번째 이미지는 썸네일로 replacer 사용
                # figure 태그 내에 replacer 추가
                figure_tag.append(replacer)
                # 이미지 태그 제거
                figure_tag.img.extract()

            else:  # url 사용
                figure_tag['style'] = "text-align: center;"  # 가운데 정렬
                figure_tag.a['href'] = url
                figure_tag.img['src'] = url
                figure_tag.img['srcset'] = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=" + url

        return contents

    def parse_and_post(self, page, filepath):
        """download한 html파일을 parsing해서 업로드"""

        # 테이블 속성값 가져오기
        try:
            if cfg.NOTION.COLUMN.TITLE:
                title = page[0].get_property(cfg.NOTION.COLUMN.TITLE)
            else:
                title = page[0].title
            tags = array2str(page[0].get_property(cfg.NOTION.COLUMN.TAG))
            category_str = page[0].get_property(cfg.NOTION.COLUMN.CATEGORY)
        except:
            raise ValueError(f'[Error] 테이블의 컬럼명을 다시 확인해주세요.')

        # get codeblock languages
        code_blocks = get_target_blocks(page[0], target_block_type=CodeBlock)
        code_langs = [code_block.language for code_block in code_blocks]

        # html 파일로부터 parsing
        content = get_notion_html(html_fp=filepath, code_languages=code_langs, code_theme=cfg.NOTION.CODE_BLOCK_THEME)
        content = self.translate_img_url(content)
        print(f'\t[진행중] parsing 완료... ', end='')

        # 카테고리 id를 얻고, posting 요청
        # 카테고리 미입력시 None
        if category_str:
            category_id = self.t_client.get_category_id_from_name(category_str)
        else:
            category_id = None

        resp_post = self.t_client.posting(title=title,
                                          content=content,
                                          visibility=3,
                                          category=category_id,
                                          tag=tags,
                                          modify_id=page[1])
        print(f'posting 완료... [{filepath.split("/")[-1]}]')

        # notion 속성값 반영
        page[0].set_property(cfg.NOTION.COLUMN.STATUS, cfg.NOTION.POST.COMPLETE_VALUE)
        page[0].set_property(cfg.NOTION.COLUMN.URL, BeautifulSoup(resp_post.text, 'lxml').find('url').text)


if __name__ == '__main__':
    from config import cfg

    try:
        # create Notion2Tistory client
        client = Notion2Tistory(cfg, sleep_time=5, selenium_debug=False)

        # post pages
        client.posts()

        # get mail info
        posted_page = [(page[0].title, page[0].get_property(cfg.NOTION.COLUMN.URL))
                       for page in client.pages]
        title, content = get_mail_content(posted_page)

    except Exception as e:
        error_msg = traceback.format_exc()
        print(error_msg)

        title, _ = get_mail_content(None)
        content = str(error_msg)

    # send alert mail
    if cfg.MAIL.ID:
        gmail_client = GMailClient(cfg.MAIL.ID, cfg.MAIL.KEY)
        try:
            gmail_client.send_mail(cfg.MAIL.ID, title, content)
            print('[진행중] 메일 전송 완료.')
        except Exception as e:
            print(e)
        finally:
            gmail_client.close()

    print('[완료] 프로그램 종료.')
