from ninja import Query


class PaginationParams(Query):
    page: int = 1
    page_size: int = 20
