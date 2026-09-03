from rest_framework import pagination


class SmallPagePagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size =20
    page_size_query_param = 'page_size'

class LargePagePagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100