from typing import List
from notion.client import NotionClient

NOTION_API_ROOT = "https://www.notion.so/api/v3"
BLOCK_SIZE = 1024  # download 1KB


class Notion:
    def __init__(self, notion_token):

        # access notion
        try:
            self.client = NotionClient(token_v2=notion_token)
            self.file_token = self.client.session.cookies.get('file_token')
            print('[진행중] Notion 로그인 완료')
        except:
            raise ValueError('[Error] notion token값이 올바르지 않습니다. 다시 확인 해 주세요. [{}]'.format(token_v2))

    def get_pages_readyToPost(self,
                              table_url: str,
                              target_column: str,
                              target_upload_value: str,
                              target_modify_value: str,
                              url_column: str):
        """
        table_url (str): Notion Table Page URL
        target_column (str): 테이블에서 발행 여부를 확인할 column 이름 e.g. '상태'
        target_values (str): 테이블에서 조회할 발행 리스트 e.g. '발행준비'
        target_values (str): 테이블에서 조회할 수정 리스트 e.g. '수정요청'
        url_column (str): 테이블에서 발행 후 기록할 url컬럼명 e.g. 'url'

        Return (List<cv.collection.CollectionRowBlock, post_id:str>): 발행할 게시물의 row, 기존에 발행된 경우라면 post id, 아니면 None을 담은 리스트
        """
        # get table
        cv = self.client.get_collection_view(table_url)

        # check query rows
        print('====== 업로드/수정 예정 목록 ======')

        pages = []
        for target_status in [target_upload_value, target_modify_value]:
            for row in cv.collection.get_rows(search=target_status):
                # target_column 테이블 컬럼이 upload, modify중에 있으면 추가
                if row.get_property(target_column) == target_upload_value:
                    modify_id = None
                elif row.get_property(target_column) == target_modify_value:
                    # url이 존재하면 수정 요청 게시물
                    modify_id = row.get_property(url_column).split('/')[-1]
                    assert modify_id, '[Error] 수정할 링크를 다시 확인해주세요.'
                else:
                    raise ValueError('[Error] 발행 컬럼을 다시 확인해주세요.')

                print(f'\t[{target_column}:{target_status}] 게시물: {row.title}')
                pages.append([row, modify_id])

        return pages


if __name__ == '__main__':

    from config_private import cfg

    client = Notion(notion_token=cfg.NOTION.TOKEN_V2)
    pages = client.get_pages_readyToPost(cfg.NOTION.TABLE_PAGE_URL,
                                         target_column=cfg.NOTION.COLUMN.STATUS,
                                         target_modify_value=cfg.NOTION.POST.MODIFY_VALUE,
                                         target_upload_value=cfg.NOTION.POST.UPLOAD_VALUE,
                                         url_column=cfg.NOTION.COLUMN.URL)

    for page in pages:
        print(page[0])
