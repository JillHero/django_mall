from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    # 每页条数 如果前端没有指明每页条数的关键词的话就用这条
    page_size = 2
    # 前端指明每页数量的关键词
    page_size_query_param = 'page_size'
    # 最大条数
    max_page_size = 20