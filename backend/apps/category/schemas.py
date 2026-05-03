from ninja import Schema, Field


class CategoryOut(Schema):
    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    icon: str = Field(default="", description="分类图标")
    type: str = Field(..., description="分类类型（activity/time/group）")
    sort: int = Field(default=0, description="排序值")
