from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from backend.dependencies import get_current_active_user
from rag.vector_store import VectorStoreService
from utils.file_handler import get_file_md5_hex
import os

router = APIRouter()

vector_store = VectorStoreService()


@router.get("/", response_model=list[schemas.DocumentResponse])
async def get_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    documents = db.query(models.Document).all()
    return documents


@router.get("/{document_id}", response_model=schemas.DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    allowed_types = ("txt", "pdf")
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型，仅支持: {', '.join(allowed_types)}")
    
    file_content = await file.read()
    file_hash = get_file_md5_hex(file.filename)
    
    existing_doc = db.query(models.Document).filter(models.Document.file_hash == file_hash).first()
    if existing_doc:
        raise HTTPException(status_code=400, detail="文档已存在")
    
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name
    
    try:
        vector_store.load_document()
        
        new_doc = models.Document(
            filename=file.filename,
            file_path=temp_path,
            file_hash=file_hash,
            is_processed=True
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        return {"message": "文档上传并处理成功", "document_id": new_doc.id}
    except Exception as e:
        os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if os.path.exists(document.file_path):
        os.unlink(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return {"message": "文档删除成功"}