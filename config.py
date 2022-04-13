from utils.dotdict import dotdict

cfg = dotdict(
    TISTORY=dotdict(
        ID='kakao email',
        PW='kakao password',
        BLOG_NAME='',
        SECRET_KEY='',
        CLIENT_ID='',
        REDIRECT_URI='',
    ),

    NOTION=dotdict(
        TOKEN_V2='',
        TABLE_PAGE_URL='',
        DOWNLOAD_DIR='~/.n2t',
        CODE_BLOCK_THEME='atom-one-dark',

        COLUMN=dotdict(
            TITLE='제목',
            CATEGORY='카테고리',
            TAG='태그',
            STATUS='상태',
            URL='링크'
        ),

        POST=dotdict(
            UPLOAD_VALUE='발행 요청',
            MODIFY_VALUE='수정 요청',
            COMPLETE_VALUE='발행 완료',
        ),
    ),

    MAIL=dotdict(
        ID='',
        KEY='',
    )
)
