from ninja import Schema, Field


class ConfigPublicOut(Schema):
    contact_phone: str = Field(default="", description="联系电话")
    service_time: str = Field(default="", description="服务时间")
    app_version: str = Field(default="", description="客户端版本号")
