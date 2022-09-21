import requests
from bs4 import BeautifulSoup
from utils.parse import decode_b64


class TistoryClient:
    def __init__(self, authorize_code, secret_key, client_id, redirect_uri, blog_name, token=None):
        # get tistory token using authorize code
        if token is None:
            self.token = self.get_tistory_token(client_id, secret_key, redirect_uri, authorize_code)
        else:
            self.token = token

        # get blog name (한 계정에 블로그가 여러 개인 경우 직접 입력 필요)
        self.blog_name = blog_name

        print('[진행중] Tistory Authorize code, Access Token 발급 완료!')

    def get_tistory_token(self, client_id, client_sercret_key, redirect_uri, code):
        """code를 통해 token값 얻기"""
        url = 'https://www.tistory.com/oauth/access_token'
        params = {
            'client_id': client_id,
            'client_secret': client_sercret_key,
            'redirect_uri': redirect_uri,
            'code': code,
            'grant_type': 'authorization_code'
        }
        resp = requests.get(url, params=params)
        access_token = resp.text.split('=')[1]

        return access_token

    def get_tistory_code(self, id, pw, client_id, redirect_uri):
        """login 하고 code 얻기(deprecated)"""
        url = 'https://www.tistory.com/auth/login'
        data = {
            'fp': '2b3b3ed59715ed70a510de6b31444276',
            'keepLogin': 'on',
            'loginId': id,
            'password': pw,
            'redirectUrl': f'https://www.tistory.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
        }
        resp = requests.post(url, params=data)
        soup = BeautifulSoup(resp.text, 'html.parser')

        try:
            code = soup.script.text.split('code=')[1].split('&state')[0]
        except:
            print(soup.prettify())
            raise ValueError(f'[Error] Tistory 로그인 실패(아이디, 비밀번호, client_id, uri 재확인), ID=[{id}]')

        return code

    def get_blogName(self):
        """blog 이름 가져오기"""
        resp = self.get_blog_info()
        soup = BeautifulSoup(resp.text, 'lxml')
        blogName = soup.find('name').text
        return blogName

    def get_blog_info(self):
        """개인 api token으로 블로그 정보 가져오기"""
        url = 'https://www.tistory.com/apis/blog/info'
        params = {
            'access_token': self.token,
            'output': 'xml'
        }
        resp = requests.get(url, params=params)

        return resp

    def get_post(self, postID):
        """postID로 게시글 정보 가져오기"""
        url = 'https://www.tistory.com/apis/post/read'
        params = {
            'access_token': self.token,
            'blogName': self.blog_name,
            'postId': postID
        }
        resp = requests.get(url, params=params)
        return resp

    def get_category_id_from_name(self, target_name, output_type='xml'):
        """이름으로 category id 찾기"""

        # 모든 카테고리 항목 가져오기
        resp = self.get_category_ids(output_type)
        soup = BeautifulSoup(resp.text, 'lxml')
        category_list = soup.find_all('category')

        for item in category_list:
            label = item.find('label').text
            if label.strip() == target_name.replace('\b', '').strip():
                return item.find('id').text

        raise ValueError(
            f'[Error] 티스토리에 해당 카테고리가 없습니다. target:[{target_name}], categories:{[item.find("label").text for item in category_list]}')

    def get_category_ids(self, output_type='xml'):
        """내 블로그에 있는 모든 카테고리 리스트 가져오기"""
        url = 'https://www.tistory.com/apis/category/list'
        params = {
            'access_token': self.token,
            'blogName': self.blog_name,
            'output': output_type
        }
        resp = requests.get(url, params=params)
        return resp

    def posting(self, title, content, visibility, category, tag, output_type='xml', modify_id=None):

        """
        blogName: Blog Name (필수)
        title: 글 제목 (필수)
        content: 글 내용
        visibility: 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
        category: 카테고리 아이디 (기본값: 0)
        published: 발행시간 (TIMESTAMP 이며 미래의 시간을 넣을 경우 예약. 기본값: 현재시간)
        tag: 태그 (',' 로 구분)
        """
        data = {
            'access_token': self.token,
            'blogName': self.blog_name,
            'output': output_type,
            'title': title,
            'content': content,
            'visibility': visibility,
            'category': category,
            'tag': tag
        }
        if modify_id is None:
            url = 'https://www.tistory.com/apis/post/write'
        else:
            url = f'https://www.tistory.com/apis/post/modify'
            data['postId'] = modify_id

        resp = requests.post(url, data=data)

        return resp

    def attach(self, img_bs64):
        """
        https://www.tistory.com/apis/post/attach?
          access_token={access-token}
          &blogName={blog-name}
        """
        f = decode_b64(img_bs64)
        files = {'uploadedfile': f}

        url = 'https://www.tistory.com/apis/post/attach'
        data = {
            'access_token': self.token,
            'blogName': self.blog_name
        }

        resp = requests.post(url, data=data, files=files)
        soup = BeautifulSoup(resp.text, 'html.parser')
        url = soup.url.text
        replacer = soup.replacer.text

        return url, replacer
