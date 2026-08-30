from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message},
        )


class InvalidCredentialsException(AppException):
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            code="INVALID_CREDENTIALS",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class DocumentNotFoundException(AppException):
    def __init__(self, message: str = "The requested document was not found."):
        super().__init__(
            code="DOCUMENT_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConversationNotFoundException(AppException):
    def __init__(self, message: str = "The requested conversation was not found."):
        super().__init__(
            code="CONVERSATION_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class MessageNotFoundException(AppException):
    def __init__(self, message: str = "The requested assistant message was not found."):
        super().__init__(
            code="MESSAGE_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnsupportedFileTypeException(AppException):
    def __init__(self, message: str = "File type not supported. Supported: PDF, DOCX, TXT"):
        super().__init__(
            code="UNSUPPORTED_FILE_TYPE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileTooLargeException(AppException):
    def __init__(self, message: str = "File exceeds maximum allowed size"):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class StorageException(AppException):
    def __init__(self, message: str = "Document storage operation failed."):
        super().__init__(
            code="STORAGE_FAILURE",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class DocumentProcessingFailedException(AppException):
    def __init__(self, message: str = "Failed to process document"):
        super().__init__(
            code="DOCUMENT_PROCESSING_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class VectorSearchFailedException(AppException):
    def __init__(self, message: str = "Vector search operation failed"):
        super().__init__(
            code="VECTOR_SEARCH_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class EmbeddingFailedException(AppException):
    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(
            code="EMBEDDING_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class LLMFailedException(AppException):
    def __init__(self, message: str = "LLM generation failed"):
        super().__init__(
            code="LLM_FAILED",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class InsufficientContextException(AppException):
    def __init__(
        self,
        message: str = "I couldn't find reliable information about this in the college knowledge base. Please try rephrasing your question or contact the college administration.",
    ):
        super().__init__(
            code="INSUFFICIENT_CONTEXT",
            message=message,
            status_code=status.HTTP_200_OK,
        )
