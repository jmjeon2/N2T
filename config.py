from utils.dotdict import dotdict

cfg = dotdict(
    TISTORY=dotdict(
        ID='',
        PW='',
        BLOG_NAME='',
        SECRET_KEY='',
        CLIENT_ID='',
        REDIRECT_URI='',
    ),

    NOTION=dotdict(
        TOKEN_V2='',
        TABLE_PAGE_URL='',
        DOWNLOAD_DIR='',
        CODE_BLOCK_THEME='',

        COLUMN=dotdict(
            TITLE='',
            CATEGORY='',
            TAG='',
            STATUS='',
            URL=''
        ),

        POST=dotdict(
            UPLOAD_VALUE='',
            MODIFY_VALUE='',
            COMPLETE_VALUE='',
        ),

    ),

    MAIL=dotdict(
        ID='',
        KEY='',
    )
)
