from ninja import Router, UploadedFile, File, Schema
from core.auth import BearerAuth
from .services import upload_file, delete_file

router = Router(auth=BearerAuth())


class DeleteRequest(Schema):
    object_name: str


@router.post("", response=dict)
def upload_single(request, file: UploadedFile = File(...), category: str = "general"):
    url = upload_file(file, file.name, category)
    return {"success": True, "data": {"url": url}}


@router.post("/batch", response=dict)
def upload_batch(request, files: list[UploadedFile] = File(...), category: str = "general"):
    urls = [upload_file(f, f.name, category) for f in files]
    return {"success": True, "data": {"urls": urls}}


@router.delete("", response=dict)
def remove_file(request, body: DeleteRequest):
    delete_file(body.object_name)
    return {"success": True, "data": None}
