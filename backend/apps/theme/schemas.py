from ninja import Schema, Field


class ThemeOut(Schema):
    id: int = Field(..., description="主题ID")
    name: str = Field(..., description="主题名称")
    cover_image: str = Field(default="", description="封面图片")
    description: str = Field(default="", description="主题描述")
    sort: int = Field(default=0, description="排序值")
    status: str = Field(default="", description="状态（显示/隐藏）")
