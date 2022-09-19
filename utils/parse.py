from bs4 import BeautifulSoup
import base64
from io import BytesIO
import os
from urllib import parse
from typing import List


def array2str(array):
    """ ['1','2','3'] -> '1, 2, 3' """
    return ', '.join(array)


def encode_b64(filepath):
    """이미지 파일 경로로부터 불러와서 base64로 encoding"""
    with open(filepath, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read())

    # b' 제거
    encoded_string = str(encoded_string)[2:][:-1]
    return 'data:image/jpeg;base64,' + encoded_string


def decode_b64(img_bs64):
    """base64 encoding된 값으로부터 bytes의 형식으로 반환(for attach)"""
    if ',' in img_bs64:
        img_bs64 = img_bs64.split(',')[1]
    img_decoded = base64.b64decode(img_bs64)

    return BytesIO(img_decoded)


def get_notion_html(html_fp,
                    code_languages: List = None,
                    code_theme: str = None,
                    from_zip=False,
                    is_save=False):
    """
        CSS선택자를 위해
        최상단 article 태그에 NOTION class 추가
        page-body클래스를 가진 최상단 div 태그에 TISTORY class추가
    """

    # html 로드하기 (압축파일로 진행하면 BeautifulSoup 타입, html 파일경로는 string)
    if from_zip:
        soup = html_fp
    else:
        with open(html_fp, encoding='UTF-8') as fp:
            soup = BeautifulSoup(fp, 'lxml')

    # 기존 head 정보(meta, title, style) 제거
    soup.find('meta').extract()
    soup.find('title').extract()
    soup.find('style').extract()

    # 코드 블럭이 존재하면 코드 블럭 type에 맞게 지정
    pre_tags = soup.find_all('pre')
    for i, pre_tag in enumerate(pre_tags):
        if code_languages is not None:
            pre_tag['class'].append(code_languages[i])
        else:
            pre_tag['class'].append('python')

    # 본문 내용 가져오기, class 추가
    article = soup.find('article')
    article['class'].append('Notion')

    # page-body 태그 가져오기, class 추가(선택자 우선순위를 두기 위해서)
    page_body_tag = soup.find('div', class_='page-body')
    page_body_tag['class'].append('Tistory')

    # 테이블(notion property 표 제거), 제목 제거
    article.select('table')[0].extract()

    # 제목 제거
    title = article.find('h1', class_='page-title')
    title.extract()

    # zip파일이 아닌 html 파일로부터 parsing하는 경우만 이미지 태그 수정
    if not from_zip:
        img_dir = os.path.dirname(html_fp)
        img_folder_name = os.path.basename(html_fp).split('.')[0]
        img_tags = article.find_all('img')
        for img_tag in img_tags:
            # 외부의 url 이미지이거나 이미 bases64인코딩된 이미지는 skip
            # 이미지 경로로 되어있는 경우는 직접 bases64 인코딩된 값으로 img 태그의 src 수정
            if img_tag['src'].startswith('http') or img_tag['src'].startswith('data:image/'):
                continue
            else:
                # src에 file path 입력
                file_basename = img_tag['src'].split('/')[-1]
                filepath = os.path.join(img_dir, img_folder_name,
                                        parse.unquote(file_basename))  # basename은 url 인코딩

                # 이미지 태그의 src를 base64로 대체
                encoded_string = encode_b64(filepath)
                img_tag['src'] = encoded_string

    # body태그에 notion style css link 추가
    style_tag = soup.new_tag('link', rel='stylesheet',
                             href="https://rawcdn.githack.com/ppuep94/n2t/5ef4dc01e9d6336341e9ab95bb71672f9d3a3dc9/assets/css/style2.css")
    body = soup.find('body')
    body.insert(0, style_tag)

    # body태그에 code style css 적용
    if code_theme is None:
        code_theme = 'atom-one-dark'
    code_css = BeautifulSoup(
        f"""<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.2/styles/{code_theme}.min.css">
                <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.2/highlight.min.js"></script>
                <script>hljs.initHighlightingOnLoad();</script>""",
        'lxml')
    body.insert(0, code_css)

    # N2T 워터마크 추가
    watermark = BeautifulSoup('<br><p class="">Uploaded by <mark class="highlight-orange"><a href="https://github.com/jmjeon94/N2T">N2T</a></mark></p>', 'lxml')
    page_body_tag.append(watermark)

    if is_save:
        # html 파일로 재 저장
        save_fp = html_fp.replace('.html', '_output.html')
        with open(save_fp, "w") as fp:
            fp.write(str(soup))
        print(f'output 파일 저장완료. [{save_fp}]')

    return soup


if __name__ == '__main__':
    contents = get_notion_html(html_fp='exported html file path', is_save=True)
