from ninja import Schema


class CategoryOut(Schema):
    id: int
    name: str
    icon: str = ""
    type: str
    sort: int = 0
