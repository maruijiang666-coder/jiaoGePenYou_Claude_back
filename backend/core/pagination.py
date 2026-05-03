from ninja import Schema, Field


class PaginationParams(Schema):
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")
