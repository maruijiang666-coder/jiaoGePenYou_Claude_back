from ninja import Router, UploadedFile, File
from core.auth import BearerAuth
from .services import upload_file, delete_file

router = Router(auth=BearerAuth())


@router.post("", response=dict)
def upload_single(request, file: UploadedFile = File(...), category: str = "general"):
    url = upload_file(file, file.name, category)
    return {"success": True, "data": {"url": url}}


@router.post("/batch", response=dict)
def upload_batch(request, files: list[UploadedFile] = File(...), category: str = "general"):
    urls = [upload_file(f, f.name, category) for f in files]
    return {"success": True, "data": {"urls": urls}}


@router.delete("/{object_name:path}", response=dict)
def remove_file(request, object_name: str):
    delete_file(object_name)
    return {"success": True, "data": None}
