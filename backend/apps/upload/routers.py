from ninja import Router, UploadedFile, File, Schema, Field
from core.auth import BearerAuth
from .services import upload_file, delete_file

router = Router(auth=BearerAuth())


class DeleteRequest(Schema):
    object_name: str = Field(..., description="要删除的文件对象名")


@router.post("", response=dict, summary="上传文件", description="上传单个文件到 MinIO 存储")
def upload_single(request, file: UploadedFile = File(...), category: str = "general"):
    url = upload_file(file, file.name, category)
    return {"success": True, "data": {"url": url}}


@router.post("/batch", response=dict, summary="批量上传", description="批量上传多个文件到 MinIO 存储")
def upload_batch(request, files: list[UploadedFile] = File(...), category: str = "general"):
    urls = [upload_file(f, f.name, category) for f in files]
    return {"success": True, "data": {"urls": urls}}


@router.delete("", response=dict, summary="删除文件", description="从 MinIO 存储中删除指定文件")
def remove_file(request, body: DeleteRequest):
    delete_file(body.object_name)
    return {"success": True, "data": None}
