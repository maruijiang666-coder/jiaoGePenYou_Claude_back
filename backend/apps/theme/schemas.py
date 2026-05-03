from ninja import Schema


class ThemeOut(Schema):
    id: int
    name: str
    cover_image: str = ""
    description: str = ""
    sort: int = 0
    status: str = ""
