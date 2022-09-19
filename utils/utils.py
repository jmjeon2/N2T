import os
from collections import deque
from glob import glob
from shutil import rmtree
import zipfile
from typing import Tuple, List

from bs4 import BeautifulSoup


def get_mail_content(page_info: List[Tuple[str, str]] = None):
    """post된 page 정보로부터 메일로 보낼 content 문자열 가져오기
    Args:
        page_info: 2차원 array [(page_title, post_url), ...]

    Returns:
        mail_title(str): 메일 제목
        mail_content(str): 메일 내용
    """

    # Error 발생한 경우
    if page_info is None:
        title = '[노션 알림] Notion2Tistory 에러 발생'
        content = ''
        return title, content

    # 업데이트 할 내용이 없는 경우
    elif len(page_info) == 0:
        title = '[노션 알림] 업데이트 할 항목이 없습니다.'
        content = ''
        return title, content

    else:
        # 메일 제목
        mail_title = f'[노션 알림] 총 {len(page_info)}개의 게시물이 업로드/수정 되었습니다.'

        # 메일 내용
        mail_content = f'총 {len(page_info)}개의 게시물이 업로드/수정 되었습니다.\n'
        for i, (page_title, page_url) in enumerate(page_info):
            mail_content += f' {i + 1}. {page_title} ({page_url})\n'

        return mail_title, mail_content


def get_url_from_pages(pages):
    """pages 객체 배열로부터 url 배열 가져오기
    pages: 2차원 array [[page, post_id], ...]
    """
    urls = []
    for page, _ in pages:
        url = get_url_from_id(page.title, page.id)
        urls.append(url)
    return urls


def get_url_from_id(title, id):
    """
    notion page의 title, id로 url 만들기
    영어가 아닌 문자(한글, 기호)가 포함된 경우에는 title이 링크에 들어가지 않음(get_titleUrl 규칙 따름)
    """
    title_url = get_titleUrl(title)
    if title_url == '':
        url = f'https://www.notion.so/{id.replace("-", "")}'
    else:
        url = f'https://www.notion.so/{title_url}-{id.replace("-", "")}'
    return url


def get_titleUrl(title):
    """
    notion에서 제목을 url로 바꾸는 규칙
    1. 영어, 숫자는 모두 포함
    2. 한글, 기호 등의 경우 - 로 대치
    """
    new_title = ''
    for ch in title:
        if ord('a') <= ord(ch.lower()) <= ord('z'):
            new_title += ch
        elif ord('0') <= ord(ch) <= ord('9'):
            new_title += ch
        else:
            # 첫 문자가 영어가 아닌 경우 continue
            if len(new_title) == 0: continue

            if new_title[-1] == '-':
                continue
            else:
                new_title += '-'

    if new_title == '':
        return new_title

    if new_title[-1] == '-':
        new_title = new_title[:-1]

    return new_title


def get_dir(path):
    """경로에 ~가 붙으면 expanduser 처리"""
    if path.startswith('~'):
        return os.path.expanduser(path)
    else:
        return path


def get_html_path(download_dir='~/'):
    """download_dir 폴더 내에 있는 모든 html 경로 반환"""

    # zip 파일로 다운로드 한 경우 압축해제
    pages_zip = glob(get_dir(os.path.join(download_dir, 'Export*.zip')))
    for zip_fp in pages_zip:
        zip = zipfile.ZipFile(zip_fp)
        # 압축할 폴더 생성
        zip_folder = get_dir(os.path.join(download_dir, zip_fp.replace('.zip', '')))
        os.makedirs(zip_folder, exist_ok=True)
        # 압축 풀기
        zip.extractall(zip_folder)
        zip.close()
        # zip 파일 제거
        os.remove(zip_fp)

    # 단일 html 파일
    pages_single = glob(get_dir(os.path.join(download_dir, '*.html')))
    # 이미지를 포함하여 폴더 형태의 html 파일
    pages_including_image = glob(get_dir(os.path.join(download_dir, 'Export*', '*.html')))

    html_pages = pages_single + pages_including_image

    # 파일은 한개여야함
    if len(html_pages) > 1:
        raise ValueError(f'[Error] 다운로드 폴더 경로를 비우고 다시 실행해주세요. Download Folder:[{download_dir}]')
    if len(html_pages) == 0:
        raise ValueError(f'[Error] 다운로드가 실패하였습니다. 경로를 다시 확인해주세요. Download Folder:[{download_dir}]')

    return html_pages[0]


def delete_file(filepath):
    if not os.path.exists(filepath):
        raise ValueError(f'[Error] 삭제할 파일이 존재하지 않습니다. [{filepath}]')

    # Export~/~.html 이미지를 포함한 폴더인 경우
    if 'Export' in filepath:
        dir_path = os.path.dirname(filepath)
        rmtree(dir_path)
    # ~.html 단일 파일인 경우
    else:
        os.remove(filepath)


def align_paths(paths, pages):
    """다운로드 폴더에서 가져온 page와 notion api로 가져온 page의 순서 맞추기(page id 이용)"""
    new_pages = []
    for path in paths:
        # html 파일을 열어 article안의 id값 가져오기
        with open(path) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        file_id = soup.find('article').get('id')
        # page의 id와 일치하면 append
        for page in pages:
            if file_id == page[0].id:
                new_pages.append(page)
    assert len(paths) == len(
        new_pages), f'[Error] Not matched number to align Pages with downloaded HTML{[len(paths)]}!={[len(new_pages)]}'
    return paths, new_pages


def get_target_blocks(page, target_block_type):
    target_blocks = []
    q = deque(page.children)

    while q:
        block = q.popleft()
        if isinstance(block, target_block_type):
            target_blocks.append(block)

        # add queue left if block has children
        for b in block.children[::-1]:
            q.appendleft(b)
    return target_blocks


if __name__ == '__main__':
    htmls = get_html_path('~/.n2t')
    print(htmls)
