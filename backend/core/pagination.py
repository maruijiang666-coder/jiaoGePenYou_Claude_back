from ninja import Schema


class PaginationParams(Schema):
    page: int = 1
    page_size: int = 20
