import uuid
from typing import List, Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from ..auth.dependencies import get_current_user, require_admin
from ..config import settings
from ..models.document import (
    DocumentCategory,
    DocumentResponse,
    DocumentStatus,
    DocumentUpdate,
)
from ..models.user import UserResponse
from ..utils.errors import AppException, FileTooLargeException, UnsupportedFileTypeException
from ..utils.responses import ApiResponse, success_response
from .processor import process_document_background
from .service import document_service
from .storage import storage

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {"PDF", "DOCX", "TXT"}


@router.post("", response_model=ApiResponse[DocumentResponse])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    category: str = Form("General"),
    department: Optional[str] = Form("General"),
    description: Optional[str] = Form(None),
    version: int = Form(1, ge=1),
    current_user: UserResponse = Depends(require_admin),
):
    """Upload a new college document (Admin only)."""
    # 1. Validate file extension
    filename = file.filename or "uploaded_file"
    ext = filename.split(".")[-1].upper() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeException(
            f"File format .{ext} is not supported. Allowed formats: PDF, DOCX, TXT."
        )

    # 2. Read content and validate size
    content = await file.read()
    file_size = len(content)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise FileTooLargeException(
            f"File size exceeds maximum allowed {settings.MAX_FILE_SIZE_MB}MB."
        )

    doc_name = name.strip() if name and name.strip() else filename
    if len(doc_name) > 255:
        raise AppException(
            code="INVALID_DOCUMENT_NAME",
            message="Document name must be 255 characters or fewer.",
        )

    # 3. Save through the configured storage provider
    storage_reference = await storage.save_document(filename, content)

    # 4. Create document record
    try:
        doc = await document_service.create_document(
            name=doc_name,
            original_filename=filename,
            file_type=ext,
            file_size=file_size,
            storage_path=storage_reference,
            uploaded_by=current_user.name,
            category=category,
            department=department,
            description=description,
            version=version,
        )
    except Exception:
        await storage.delete_document(storage_reference)
        raise

    # 5. Launch asynchronous background processing / ingestion
    background_tasks.add_task(
        process_document_background,
        document_id=doc.id,
        file_path=None,
        file_type=ext,
        document_name=doc.name,
        category=category,
        department=department or "General",
        version=version,
        source_reference=doc.storage_reference,
    )

    return success_response(doc)


@router.get("", response_model=ApiResponse[List[DocumentResponse]])
async def list_documents(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """List knowledge base documents with search and filter capabilities."""
    docs = await document_service.list_documents(
        search=search,
        category=category,
        department=department,
        status=status,
        is_active=is_active,
    )
    return success_response(docs)


@router.get("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def get_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Get single document details by ID."""
    doc = await document_service.get_document_by_id(document_id)
    return success_response(doc)


@router.patch("/{document_id}", response_model=ApiResponse[DocumentResponse])
async def update_document(
    document_id: str,
    updates: DocumentUpdate,
    current_user: UserResponse = Depends(require_admin),
):
    """Update document metadata or toggle active version status (Admin only)."""
    doc = await document_service.update_document(document_id, updates)
    return success_response(doc)


@router.delete("/{document_id}", response_model=ApiResponse[dict])
async def delete_document(
    document_id: str,
    current_user: UserResponse = Depends(require_admin),
):
    """Delete a document and all its indexed chunks (Admin only)."""
    await document_service.delete_document(document_id)
    return success_response({"message": "Document successfully deleted."})


@router.post("/{document_id}/reprocess", response_model=ApiResponse[DocumentResponse])
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(require_admin),
):
    """Trigger manual re-extraction, chunking, and re-indexing (Admin only)."""
    doc = await document_service.get_document_by_id(document_id)
    background_tasks.add_task(
        process_document_background,
        document_id=doc.id,
        file_path=None,
        file_type=doc.file_type,
        document_name=doc.name,
        category=doc.category,
        department=doc.department or "General",
        version=doc.version,
        source_reference=doc.storage_reference,
    )

    return success_response(doc)


@router.post("/{document_id}/replace", response_model=ApiResponse[DocumentResponse])
async def replace_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(require_admin),
):
    """Upload a replacement as the next active document version (Admin only)."""
    existing = await document_service.get_document_by_id(document_id)
    filename = file.filename or "replacement_file"
    ext = filename.split(".")[-1].upper() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeException(
            f"File format .{ext} is not supported. Allowed formats: PDF, DOCX, TXT."
        )

    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise FileTooLargeException(
            f"File size exceeds maximum allowed {settings.MAX_FILE_SIZE_MB}MB."
        )

    storage_reference = await storage.save_document(filename, content)

    try:
        replacement = await document_service.create_document(
            name=existing.name,
            original_filename=filename,
            file_type=ext,
            file_size=len(content),
            storage_path=storage_reference,
            uploaded_by=current_user.name,
            category=existing.category,
            department=existing.department,
            description=existing.description,
            version=existing.version + 1,
        )
    except Exception:
        await storage.delete_document(storage_reference)
        raise
    background_tasks.add_task(
        process_document_background,
        document_id=replacement.id,
        file_path=None,
        file_type=ext,
        document_name=replacement.name,
        category=replacement.category,
        department=replacement.department or "General",
        version=replacement.version,
        source_reference=replacement.storage_reference,
    )
    return success_response(replacement)
