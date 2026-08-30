# Project 2 — RAG-Based College Chatbot

## Project Specification — `spec.md`

---

# 1. Project Overview

Build a full-stack AI-powered college information assistant called **CollegeAI**.

CollegeAI allows students to ask questions about college-related information and receive answers grounded in an administrator-managed knowledge base containing official college documents such as PDFs, notices, FAQs, academic calendars, regulations, admission documents, department information, hostel information, scholarship documents, placement information, and other official resources.

The application must use a genuine **Retrieval-Augmented Generation (RAG)** pipeline.

The system must NOT be implemented as a simple chatbot that directly sends questions to an LLM.

The mandatory pipeline is:

```text
College Documents
       ↓
Document Upload
       ↓
Text Extraction / OCR
       ↓
Text Cleaning
       ↓
Chunking
       ↓
Embedding Generation
       ↓
MongoDB Atlas Vector Search
       ↓
Semantic Retrieval
       ↓
Relevant Context
       ↓
LLM
       ↓
Grounded Answer
       ↓
Sources / References
```

The final application must be fully functional locally and deployable using:

```text
Source Code → GitHub
Frontend → Vercel
Backend → Render
Database → MongoDB Atlas
```

---

# 2. Project Objective

Create a production-style college knowledge assistant that enables:

### Students

* Register
* Login
* Ask college-related questions
* Receive AI-generated grounded answers
* See the documents used to answer the question
* See page numbers where available
* Continue conversations
* View chat history
* Delete conversations
* Give answer feedback
* Use suggested questions

### Administrators

* Login
* Access an admin dashboard
* Upload college documents
* View uploaded documents
* Search and filter documents
* Categorize documents
* Process documents
* Monitor processing status
* Replace documents
* Manage document versions
* Delete documents
* View basic usage and feedback analytics

---

# 3. Core Principle

The uploaded college knowledge base is the source of truth for college-specific information.

The LLM must not invent information that is not supported by retrieved college documents.

If relevant information cannot be found in the knowledge base, the system must clearly state that the information is unavailable.

Example:

```text
Student:
What is the hostel fee?

System:
The annual hostel fee is ₹50,000.

Source:
Hostel Information 2026
Page 8
```

If the information does not exist:

```text
Student:
What is the principal's monthly salary?

System:
I couldn't find reliable information about this in the college knowledge base.
Please try rephrasing your question or contact the college administration.
```

The system must never fabricate a salary, fee, date, policy, faculty name, deadline, or other college-specific information.

---

# 4. Supported Knowledge Topics

The knowledge base must support documents covering:

* Admissions
* Departments
* Courses
* Curriculum
* Fees
* Examinations
* Academic calendar
* Hostel
* Library
* Scholarships
* Placements
* Clubs
* Events
* Faculty
* Campus facilities
* Rules
* Regulations
* Policies
* Student services
* General college information

The category system must be extensible.

---

# 5. Technology Stack

## Frontend

Use:

* Next.js
* React
* TypeScript
* Tailwind CSS
* Axios or Fetch
* Zustand or equivalent lightweight state management
* Lucide React icons

The frontend must be responsive and production-ready.

---

## Backend

Use:

* Python
* FastAPI
* Pydantic
* Uvicorn
* PyMongo or Motor
* JWT authentication
* bcrypt/passlib for password hashing

The backend must contain the complete RAG pipeline.

---

## Database

Use:

**MongoDB Atlas**

MongoDB Atlas must store:

* Users
* Documents
* Document chunks
* Embeddings
* Conversations
* Messages
* Feedback
* Categories
* Document versions

---

## Vector Database

Use:

**MongoDB Atlas Vector Search**

Do NOT replace vector search with:

* keyword-only search
* array scanning
* string matching
* fake similarity scores
* hardcoded search results

The application must perform actual vector similarity search.

---

## Embeddings

Use a reliable semantic embedding model.

The embedding service must be modular so that the embedding model can be replaced later.

The same embedding space must be used for:

```text
Document chunks
+
User queries
```

---

## LLM

Use a server-side LLM API.

The implementation should support configurable providers.

Preferred architecture:

```text
Primary LLM
     ↓
Fallback LLM
     ↓
Graceful error handling
```

The exact provider may be selected according to available API credentials.

API keys must remain server-side.

---

# 6. Deployment Architecture

The final system must use:

```text
                         STUDENT / ADMIN
                               |
                               v
                      +----------------+
                      |     VERCEL     |
                      |    FRONTEND    |
                      |    Next.js     |
                      +-------+--------+
                              |
                           HTTPS
                              |
                              v
                      +----------------+
                      |     RENDER     |
                      |    BACKEND     |
                      |    FastAPI     |
                      +-------+--------+
                              |
                +-------------+-------------+
                |                           |
                v                           v
        +---------------+            +---------------+
        | MongoDB Atlas |            |   LLM API     |
        |               |            |               |
        | Application DB|            | Answer        |
        | Vector Search |            | Generation    |
        +---------------+            +---------------+
```

Source control:

```text
GitHub
```

Deployment:

```text
Frontend → Vercel
Backend  → Render
Database → MongoDB Atlas
```

---

# 7. Project Structure

Use a clean monorepo structure.

```text
college-ai/
│
├── frontend/
│   ├── components/
│   │   ├── layout/
│   │   ├── chat/
│   │   ├── sources/
│   │   ├── admin/
│   │   └── common/
│   │
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── index.tsx
│   │   ├── login.tsx
│   │   ├── register.tsx
│   │   ├── dashboard.tsx
│   │   ├── chat/
│   │   │   └── [id].tsx
│   │   ├── conversations.tsx
│   │   ├── admin/
│   │   │   ├── index.tsx
│   │   │   ├── documents.tsx
│   │   │   └── analytics.tsx
│   │   └── settings.tsx
│   │
│   ├── store/
│   │   ├── authStore.ts
│   │   └── chatStore.ts
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   ├── types/
│   ├── hooks/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── auth/
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   │
│   │   ├── documents/
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── processor.py
│   │   │
│   │   ├── rag/
│   │   │   ├── ingestion.py
│   │   │   ├── extraction.py
│   │   │   ├── chunking.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_search.py
│   │   │   ├── retrieval.py
│   │   │   ├── reranking.py
│   │   │   ├── prompting.py
│   │   │   └── pipeline.py
│   │   │
│   │   ├── chat/
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   │
│   │   ├── admin/
│   │   │   ├── routes.py
│   │   │   └── service.py
│   │   │
│   │   ├── feedback/
│   │   │   └── routes.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── feedback.py
│   │   │
│   │   ├── database/
│   │   │   └── mongodb.py
│   │   │
│   │   └── utils/
│   │
│   ├── requirements.txt
│   └── ...
│
├── docs/
│   ├── architecture.md
│   ├── rag.md
│   ├── api.md
│   ├── database.md
│   ├── deployment.md
│   └── testing.md
│
├── .env.example
├── .gitignore
├── README.md
└── spec.md
```

The implementation agent may improve the internal structure when necessary, but the architectural separation must remain clear.

---

# 8. Authentication

Implement:

* Registration
* Login
* Logout
* JWT authentication
* Current-user endpoint
* Password hashing
* Protected routes
* Role-based authorization

Roles:

```text
STUDENT
ADMIN
```

Passwords must never be stored in plaintext.

Use a strong password hashing algorithm.

The backend must validate authorization independently of frontend state.

---

# 9. Authentication API

Implement:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

Registration should validate:

* Name
* Email
* Password

Login should return an authentication token/session mechanism.

The frontend must persist authentication state securely.

---

# 10. User Database

Users collection:

```text
users
```

Suggested fields:

```text
_id
name
email
password_hash
role
created_at
updated_at
last_login
```

Email must be unique.

---

# 11. Document Management

Administrators must be able to:

* Upload documents
* View documents
* Search documents
* Filter documents
* Categorize documents
* Update metadata
* Replace documents
* Delete documents
* View processing status
* View document versions

Supported formats:

```text
PDF
DOCX
TXT
```

The architecture should allow future support for additional formats.

---

# 12. Document Metadata

Each document should store:

```text
_id
name
original_filename
file_type
file_size
category
department
description
version
status
storage_reference
uploaded_by
uploaded_at
updated_at
is_active
processing_error
```

Status:

```text
UPLOADED
PROCESSING
PROCESSED
FAILED
```

---

# 13. Document Ingestion Pipeline

The ingestion system must implement:

```text
Upload
   ↓
Validation
   ↓
Text Extraction
   ↓
Cleaning
   ↓
Page / Metadata Preservation
   ↓
Chunking
   ↓
Embedding Generation
   ↓
MongoDB Storage
   ↓
Vector Search Index
   ↓
PROCESSED
```

If any stage fails:

```text
FAILED
```

The error must be visible to the administrator.

---

# 14. PDF Processing

For PDFs:

* Extract text page-by-page where possible.
* Preserve page numbers.
* Preserve document metadata.
* Handle multi-page documents.
* Detect empty extraction.
* Gracefully handle corrupted PDFs.

If a PDF contains no extractable text, mark it appropriately and allow OCR if OCR support is implemented.

---

# 15. DOCX Processing

For DOCX:

* Extract paragraphs.
* Preserve document order.
* Remove irrelevant formatting.
* Preserve useful headings where possible.

---

# 16. TXT Processing

For TXT:

* Read safely.
* Normalize encoding.
* Clean excessive whitespace.
* Preserve meaningful structure.

---

# 17. OCR

OCR is an optional advanced feature.

If implemented:

```text
Scanned PDF
     ↓
OCR
     ↓
Extracted Text
     ↓
Chunking
     ↓
Embeddings
```

Do not claim OCR support unless it actually works.

---

# 18. Text Cleaning

Clean extracted content while preserving meaning.

Handle:

* Excessive whitespace
* Repeated blank lines
* Broken line wrapping
* Empty sections
* Unnecessary extraction artifacts

Do not remove meaningful information.

---

# 19. Chunking

Implement semantic document chunking.

Each chunk should contain:

```text
_id
document_id
document_name
document_version
content
chunk_index
page_number
category
department
created_at
embedding
```

Chunking must support configurable:

```text
CHUNK_SIZE
CHUNK_OVERLAP
```

Recommended starting configuration:

```text
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
```

These values may be tuned during testing.

---

# 20. Embedding Generation

Create a dedicated embedding service.

Document pipeline:

```text
Chunk
 ↓
Embedding Model
 ↓
Vector
 ↓
MongoDB Atlas
```

Query pipeline:

```text
User Question
 ↓
Same Embedding Model
 ↓
Query Vector
```

The same embedding model/version must be used for both document chunks and user queries.

---

# 21. Embedding Storage

Store embeddings alongside chunks.

Example:

```text
{
  content: "...",
  embedding: [0.012, -0.034, ...],
  document_id: "...",
  page_number: 12
}
```

Do not hardcode embeddings.

Do not create fake embeddings.

---

# 22. MongoDB Atlas Vector Search

Create a MongoDB Atlas Vector Search index for the embedding field.

The vector index must support semantic similarity search.

Conceptual structure:

```text
document_chunks
      |
      +-- content
      +-- embedding
      +-- document_id
      +-- page_number
      +-- category
      +-- department
```

Vector search must use the actual query embedding.

---

# 23. Retrieval Pipeline

For every user question:

```text
User Question
      ↓
Query Embedding
      ↓
MongoDB Atlas Vector Search
      ↓
Top-K Candidates
      ↓
Relevance Filtering
      ↓
Optional Reranking
      ↓
Final Context
```

Configurable:

```text
TOP_K
RELEVANCE_THRESHOLD
```

Initial values:

```text
TOP_K = 5
RELEVANCE_THRESHOLD = 0.70
```

These are starting values and must be evaluated using actual test queries.

---

# 24. Retrieval Metadata

Every retrieved chunk must retain:

* Document ID
* Document name
* Page number
* Category
* Department
* Version
* Similarity/relevance score
* Chunk content

This information is required for source attribution.

---

# 25. Source Attribution

Every grounded response must provide source information.

Example:

```text
Sources

Academic Handbook 2026
Page 24
Relevance: 0.91
```

If page number is unavailable:

```text
Academic Handbook 2026
```

Never fabricate page numbers.

Never fabricate document names.

---

# 26. Reranking

The architecture should support an optional reranking stage.

Pipeline:

```text
Vector Search
      ↓
Candidate Chunks
      ↓
Reranker
      ↓
Best Context
```

Reranking should only be enabled if it provides measurable retrieval improvement.

---

# 27. RAG Generation

The final RAG pipeline must be:

```text
QUESTION
   ↓
QUERY EMBEDDING
   ↓
VECTOR SEARCH
   ↓
RELEVANCE FILTER
   ↓
OPTIONAL RERANKING
   ↓
CONTEXT CONSTRUCTION
   ↓
GROUNDED LLM PROMPT
   ↓
LLM
   ↓
ANSWER
   ↓
SOURCE REFERENCES
```

This pipeline is mandatory.

---

# 28. Grounded Prompt Rules

The LLM system prompt must instruct the model to:

1. Use the supplied retrieved context as the source of truth.
2. Answer the student's question directly.
3. Never invent college-specific information.
4. Never invent dates.
5. Never invent fees.
6. Never invent rules.
7. Never invent faculty names.
8. Never invent policies.
9. Never invent sources.
10. If the retrieved context does not contain enough information, explicitly say that the information is unavailable.
11. Prefer concise answers.
12. Cite the supplied sources.

---

# 29. Unknown Question Handling

Before generation, evaluate whether the retrieved context is sufficiently relevant.

If the retrieval score is below the configured threshold:

Do not generate an answer based on weak context.

Return:

```text
I couldn't find reliable information about this in the college knowledge base. Please try rephrasing your question or contact the college administration.
```

This is mandatory.

---

# 30. Hallucination Prevention

The application must prioritize correctness over answering every question.

For example:

Knowledge base contains:

```text
Library hours are 8:00 AM to 8:00 PM on weekdays.
```

Question:

```text
What are the library hours?
```

Expected:

```text
The library is open from 8:00 AM to 8:00 PM on weekdays.
```

Question:

```text
What is the principal's monthly salary?
```

If salary information does not exist:

```text
I couldn't find reliable information about this in the college knowledge base.
```

Never generate a guessed salary.

---

# 31. Conversation System

Students must be able to:

* Start a conversation
* Ask multiple questions
* Continue context
* View previous conversations
* Rename conversations
* Delete conversations

Conversation context should be used carefully.

The retrieval system must still ground college-specific information in the knowledge base.

---

# 32. Conversations Collection

```text
conversations
```

Suggested fields:

```text
_id
user_id
title
created_at
updated_at
```

Students must only access their own conversations.

---

# 33. Messages Collection

```text
messages
```

Suggested fields:

```text
_id
conversation_id
user_id
role
content
sources
retrieval_metadata
created_at
```

Roles:

```text
USER
ASSISTANT
```

---

# 34. Chat API

Implement:

```text
POST   /api/chat
GET    /api/conversations
GET    /api/conversations/:id
PATCH  /api/conversations/:id
DELETE /api/conversations/:id
```

The chat endpoint must:

1. Validate authentication.
2. Validate the question.
3. Generate query embedding.
4. Search vector database.
5. Filter relevant chunks.
6. Construct context.
7. Call LLM.
8. Generate grounded response.
9. Attach sources.
10. Save conversation/message data.
11. Return the answer.

---

# 35. Chat Response

The API should return a structure similar to:

```json
{
  "success": true,
  "data": {
    "answer": "The library is open from 8:00 AM to 8:00 PM on weekdays.",
    "sources": [
      {
        "document_id": "...",
        "document_name": "Library Information 2026",
        "page_number": 8,
        "relevance_score": 0.91
      }
    ],
    "retrieval": {
      "chunks_retrieved": 5,
      "chunks_used": 2
    }
  }
}
```

The exact schema may be adjusted during implementation but source attribution must remain available.

---

# 36. Feedback System

Students should be able to rate answers:

```text
👍 Helpful
👎 Not Helpful
```

Optional comment:

```text
What could be improved?
```

Store feedback in MongoDB.

---

# 37. Feedback API

Implement:

```text
POST /api/feedback
```

Suggested fields:

```text
_id
message_id
user_id
rating
comment
created_at
```

---

# 38. Suggested Questions

Provide useful suggested questions.

Examples:

```text
What are the admission requirements?

When are the semester examinations?

What is the hostel fee?

What scholarships are available?

Tell me about the CSE department.

What are the library timings?

What clubs are available?
```

Suggested questions are UI helpers and must not bypass the RAG pipeline.

---

# 39. Student Dashboard

The student dashboard should include:

* Welcome section
* Ask AI section
* Suggested questions
* Recent conversations
* Knowledge categories
* User profile
* Navigation

---

# 40. Chat Interface

Build a professional AI assistant interface.

Required:

* Conversation sidebar
* New conversation button
* Message area
* User messages
* Assistant messages
* Source cards
* Input box
* Send button
* Loading indicator
* Error state
* Empty state
* Feedback controls
* Suggested questions

---

# 41. Admin Dashboard

Admin dashboard should show:

* Total documents
* Processed documents
* Failed documents
* Total students
* Total questions
* Recent uploads
* Processing status
* Feedback statistics

Use simple visualizations where useful.

---

# 42. Admin Document Page

Provide:

* Upload area
* Document table
* Search
* Filters
* Category selector
* Department selector
* Version information
* Processing status
* Replace button
* Delete button

Deleting a document must require confirmation.

---

# 43. Document Versioning

Support document versions.

Example:

```text
Academic_Calendar_2026_v1
Academic_Calendar_2026_v2
```

When a new version is uploaded:

```text
Old Version → inactive
New Version → active
```

Historical versions may remain stored.

Inactive versions must not incorrectly dominate retrieval.

---

# 44. Categories

Provide categories such as:

```text
Admissions
Academics
Examinations
Fees
Hostel
Library
Scholarships
Placements
Clubs
Events
Policies
General
```

Categories must be extensible.

---

# 45. Department Support

Documents may optionally contain:

```text
department
```

Examples:

```text
CSE
ECE
ISE
ME
CIVIL
General
```

The architecture should support department-specific filtering in future versions.

---

# 46. API Endpoints

## Health

```text
GET /api/health
```

---

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

---

## Chat

```text
POST   /api/chat
GET    /api/conversations
GET    /api/conversations/:id
PATCH  /api/conversations/:id
DELETE /api/conversations/:id
```

---

## Documents

```text
POST   /api/documents
GET    /api/documents
GET    /api/documents/:id
PATCH  /api/documents/:id
DELETE /api/documents/:id
POST   /api/documents/:id/reprocess
```

---

## Admin

```text
GET /api/admin/dashboard
GET /api/admin/analytics
```

---

## Feedback

```text
POST /api/feedback
```

---

# 47. API Error Format

Use a consistent error format.

Example:

```json
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The requested document was not found."
  }
}
```

Do not expose internal stack traces.

---

# 48. Error Codes

Use meaningful error codes such as:

```text
INVALID_CREDENTIALS
UNAUTHORIZED
FORBIDDEN
DOCUMENT_NOT_FOUND
DOCUMENT_PROCESSING_FAILED
UNSUPPORTED_FILE_TYPE
FILE_TOO_LARGE
VECTOR_SEARCH_FAILED
EMBEDDING_FAILED
LLM_FAILED
INSUFFICIENT_CONTEXT
CONVERSATION_NOT_FOUND
```

---

# 49. Environment Variables

Create:

```text
.env.example
```

Backend variables:

```text
MONGODB_URI=
MONGODB_DATABASE=
JWT_SECRET=
LLM_API_KEY=
EMBEDDING_MODEL=
FRONTEND_URL=
TOP_K=5
RELEVANCE_THRESHOLD=0.70
CHUNK_SIZE=800
CHUNK_OVERLAP=120
MAX_FILE_SIZE_MB=20
```

Frontend:

```text
NEXT_PUBLIC_API_URL=
```

Never commit actual secrets.

---

# 50. Secret Management

Never commit:

* API keys
* MongoDB credentials
* JWT secrets
* Service credentials
* Private tokens

`.gitignore` must include:

```text
.env
.env.local
.env.*.local
node_modules/
.venv/
__pycache__/
*.pyc
.next/
dist/
```

---

# 51. CORS

Backend must allow only the configured frontend origin.

Use:

```text
FRONTEND_URL
```

Do not use unrestricted production CORS unless explicitly required.

---

# 52. Security

Implement:

* Password hashing
* JWT validation
* Protected APIs
* Role-based authorization
* Input validation
* File validation
* File-size limits
* CORS
* Secure environment variables
* Rate limiting where appropriate
* Safe error responses

Never trust role information supplied only by the frontend.

---

# 53. File Security

Validate:

* Extension
* MIME type
* File size
* File content where possible

Reject executable files and unsupported formats.

Never execute uploaded files.

---

# 54. Health Endpoint

Implement:

```text
GET /api/health
```

Response:

```json
{
  "status": "ok"
}
```

Optionally include:

```text
database
vector_search
llm
```

health indicators.

---

# 55. Local Development

The application must work locally before deployment.

Verify:

```text
Frontend starts
Backend starts
MongoDB connects
Authentication works
Document upload works
Document processing works
Embeddings work
Vector search works
RAG works
Sources appear
Unknown questions are rejected
Chat history works
Admin functions work
```

Do not deploy while the core RAG pipeline is broken.

---

# 56. Testing Strategy

Implement tests for:

## Authentication

* Registration
* Login
* Invalid credentials
* Protected endpoint
* Role authorization

## Documents

* Valid upload
* Invalid upload
* Text extraction
* Chunking
* Embedding generation
* Processing failure

## Retrieval

* Relevant retrieval
* Irrelevant retrieval
* Top-K
* Relevance threshold

## RAG

* Grounded answer
* Source attribution
* Unknown question
* Hallucination prevention

## Conversations

* Create
* Read
* Update
* Delete
* Access control

---

# 57. Mandatory RAG Acceptance Test 1

Create a test document containing:

```text
The college library is open from 8:00 AM to 8:00 PM on weekdays.
```

Upload it through the admin interface.

The system must:

```text
Extract
→ Chunk
→ Embed
→ Store
→ Index
```

Then ask:

```text
What are the library opening hours?
```

Expected answer:

```text
The college library is open from 8:00 AM to 8:00 PM on weekdays.
```

The response must display the uploaded document as a source.

---

# 58. Mandatory RAG Acceptance Test 2 — Unknown Question

Using the same knowledge base, ask:

```text
What is the monthly salary of the college principal?
```

If salary information does not exist:

Expected:

```text
I couldn't find reliable information about this in the college knowledge base.
```

The application must NOT invent an answer.

This test is mandatory.

---

# 59. Mandatory RAG Acceptance Test 3 — Retrieval Accuracy

Upload:

Document A:

```text
Hostel fee is ₹50,000 per year.
```

Document B:

```text
Library fee is ₹2,000 per year.
```

Ask:

```text
What is the hostel fee?
```

The hostel document must be retrieved as the relevant source.

Expected answer:

```text
The hostel fee is ₹50,000 per year.
```

---

# 60. Mandatory RAG Acceptance Test 4 — Versioning

Upload version 1:

```text
Hostel fee: ₹50,000
```

Upload version 2:

```text
Hostel fee: ₹55,000
```

Mark version 2 active.

Ask:

```text
What is the hostel fee?
```

Expected:

```text
₹55,000
```

The inactive old version must not override the active version.

---

# 61. UI / UX Requirements

The application must feel like a real AI product.

Use:

* Professional typography
* Consistent spacing
* Responsive layouts
* Clear hierarchy
* Clean cards
* Modern navigation
* Accessible buttons
* Source cards
* Good loading states
* Error states
* Empty states

Avoid:

* Excessive gradients
* Random colors
* Huge unnecessary text
* Fake statistics
* Placeholder buttons
* Broken layouts
* Non-functional controls

---

# 62. Responsive Design

Test at:

```text
1440px
1024px
768px
390px
```

The application must:

* Avoid horizontal overflow.
* Remain readable on mobile.
* Keep chat usable on mobile.
* Keep admin document management usable on smaller screens.

---

# 63. Accessibility

Implement:

* Semantic HTML
* Keyboard navigation
* Accessible labels
* Accessible buttons
* Focus states
* Proper contrast
* Meaningful error messages

---

# 64. Loading States

Provide loading indicators for:

* Login
* Registration
* Chat generation
* Document upload
* Document processing
* Dashboard loading
* Conversation loading
* Delete operations

Use skeleton loaders where appropriate.

---

# 65. Empty States

Provide useful empty states.

Examples:

```text
No conversations yet.

Ask your first question to start a conversation.
```

Admin:

```text
No documents uploaded yet.

Upload your first college document to build the knowledge base.
```

---

# 66. Student Pages

Implement:

```text
/
```

Landing page.

```text
/login
```

Login.

```text
/register
```

Registration.

```text
/dashboard
```

Student dashboard.

```text
/chat/[id]
```

Conversation page.

```text
/conversations
```

Conversation history.

```text
/settings
```

Profile/settings.

---

# 67. Admin Pages

Implement:

```text
/admin
```

Admin dashboard.

```text
/admin/documents
```

Document management.

```text
/admin/analytics
```

Analytics.

Admin pages must be inaccessible to normal students.

---

# 68. Root Routing

The root route should behave as follows:

```text
Authenticated user
       ↓
Dashboard

Unauthenticated user
       ↓
Landing/Login
```

---

# 69. Database Indexes

Create appropriate indexes for:

* User email
* Conversation user ID
* Message conversation ID
* Document category
* Document status
* Document active version
* Document chunk document ID

Create the required MongoDB Atlas Vector Search index.

---

# 70. Performance

Optimize:

* Database queries
* Vector retrieval
* Embedding generation
* Document processing
* API response times
* Frontend rendering

Avoid regenerating embeddings when a document has not changed.

Avoid unnecessary LLM calls.

---

# 71. Caching

Caching may be implemented for safe repeated operations.

Do not cache personalized responses incorrectly.

Do not allow one user's private conversation data to leak to another user.

---

# 72. Logging

Backend logs should help diagnose:

* Startup
* Database connection
* Document processing
* Embedding generation
* Vector search
* LLM errors
* API failures

Never log:

* Passwords
* JWT secrets
* API keys
* Raw credentials

---

# 73. Frontend API Configuration

Never hardcode production API URLs throughout the frontend.

Use:

```text
NEXT_PUBLIC_API_URL
```

Development:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Production:

```text
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

# 74. Backend Production Configuration

The FastAPI application must use the deployment environment's port.

The application must be compatible with Render.

Example:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Do not permanently hardcode a production port.

---

# 75. MongoDB Atlas Deployment

Configure:

1. MongoDB Atlas cluster.
2. Database user.
3. Network access.
4. Database.
5. Collections.
6. Required indexes.
7. Vector Search index.

Connection string must be provided through:

```text
MONGODB_URI
```

Never hardcode credentials.

---

# 76. Render Deployment

Backend deployment must:

* Install Python dependencies.
* Start FastAPI.
* Use Render's `$PORT`.
* Connect to MongoDB Atlas.
* Read environment variables.
* Configure CORS.
* Expose `/api/health`.

Environment variables must be configured through Render.

---

# 77. Vercel Deployment

Frontend deployment must:

* Build successfully.
* Use `NEXT_PUBLIC_API_URL`.
* Connect to Render.
* Not depend on localhost.
* Handle API errors gracefully.

---

# 78. GitHub Requirements

Repository must contain:

```text
frontend/
backend/
docs/
README.md
spec.md
.env.example
.gitignore
```

Before pushing:

* Remove secrets.
* Verify `.gitignore`.
* Remove unnecessary build artifacts.
* Verify production URLs are environment-based.
* Verify README.

---

# 79. Documentation

Create:

```text
docs/architecture.md
docs/rag.md
docs/api.md
docs/database.md
docs/deployment.md
docs/testing.md
```

Documentation must describe the actual implementation.

Do not document features that do not exist.

---

# 80. README

README must contain:

1. Project name
2. Project overview
3. Problem statement
4. Solution
5. Core features
6. RAG architecture
7. System architecture
8. Technology stack
9. Project structure
10. Database design
11. API endpoints
12. Environment variables
13. Local setup
14. Running frontend
15. Running backend
16. Document ingestion process
17. RAG retrieval process
18. Deployment instructions
19. Testing
20. Screenshots
21. Live demo
22. Future scope
23. Known limitations

---

# 81. Development Phases

The AI coding agent must build the project incrementally.

---

## PHASE 1 — Project Foundation

Implement:

* Repository structure
* Next.js frontend
* FastAPI backend
* MongoDB connection
* Environment configuration
* Health endpoint
* Base UI
* Basic routing

Verify:

```text
Frontend starts
Backend starts
Database connects
Health endpoint works
```

---

## PHASE 2 — Authentication

Implement:

* Registration
* Login
* Logout
* JWT
* Password hashing
* Current-user endpoint
* Student/Admin roles
* Protected frontend routes
* Protected backend routes

Test authentication before proceeding.

---

## PHASE 3 — Document Management

Implement:

* Admin dashboard
* Document upload
* File validation
* Document metadata
* Document listing
* Search/filter
* Delete
* Update
* Processing status

---

## PHASE 4 — Document Processing

Implement:

* PDF extraction
* DOCX extraction
* TXT extraction
* Text cleaning
* Page metadata
* Chunking

Test document processing independently.

---

## PHASE 5 — Embeddings

Implement:

* Embedding service
* Batch embedding generation
* Embedding persistence
* Error handling

Verify that uploaded chunks receive real embeddings.

---

## PHASE 6 — MongoDB Vector Search

Implement:

* Atlas Vector Search index
* Query embedding
* Semantic search
* Top-K retrieval
* Similarity scores
* Relevance threshold

Verify retrieval independently before integrating the LLM.

---

## PHASE 7 — RAG Pipeline

Implement:

* Context selection
* Context formatting
* Grounded prompt
* LLM integration
* Source attribution
* Unknown question handling

Run all mandatory RAG acceptance tests.

---

## PHASE 8 — Chat System

Implement:

* Chat UI
* Conversations
* Messages
* Conversation history
* Suggested questions
* Feedback
* Source cards

---

## PHASE 9 — Admin Dashboard

Implement:

* Document analytics
* Processing statistics
* Feedback statistics
* Document versioning
* Management controls

---

## PHASE 10 — Advanced Features

Only after all mandatory functionality works.

Possible features:

* Hybrid search
* Reranking
* Multilingual queries
* OCR
* Streaming responses
* Conversation export
* Advanced analytics
* Department-specific knowledge bases

Do not sacrifice core reliability for bonus features.

---

## PHASE 11 — Testing

Run:

* Unit tests
* Integration tests
* Authentication tests
* API tests
* RAG tests
* Retrieval tests
* UI tests
* Responsive tests

Fix all critical failures.

---

## PHASE 12 — Deployment

Deploy in this order:

```text
MongoDB Atlas
      ↓
Backend → Render
      ↓
Test backend
      ↓
Frontend → Vercel
      ↓
Test complete application
```

---

# 82. Final Deployment Test

From the public Vercel URL verify:

```text
Landing page
↓
Registration
↓
Login
↓
Dashboard
↓
Admin login
↓
Upload document
↓
Document processing
↓
Embedding generation
↓
Vector search
↓
Student asks question
↓
RAG retrieval
↓
LLM answer
↓
Source display
↓
Chat history
↓
Feedback
```

Then test an unknown question.

The system must respond with an unavailable-information message rather than hallucinating.

---

# 83. Final Acceptance Criteria

The application is complete only when all mandatory items pass.

## Authentication

* [ ] Registration works
* [ ] Login works
* [ ] Logout works
* [ ] JWT/session works
* [ ] Student role works
* [ ] Admin role works
* [ ] Protected routes work
* [ ] Passwords are securely hashed

## Documents

* [ ] PDF upload works
* [ ] DOCX upload works
* [ ] TXT upload works
* [ ] Validation works
* [ ] Text extraction works
* [ ] Chunking works
* [ ] Metadata is preserved
* [ ] Processing status works
* [ ] Admin can delete
* [ ] Admin can update
* [ ] Versioning works

## Embeddings

* [ ] Real embedding model is used
* [ ] Chunks receive embeddings
* [ ] Query receives embedding
* [ ] Same embedding space is used

## Vector Search

* [ ] MongoDB Atlas Vector Search is configured
* [ ] Vector index exists
* [ ] Semantic retrieval works
* [ ] Top-K works
* [ ] Relevance filtering works
* [ ] Similarity scores are available

## RAG

* [ ] Retrieved chunks reach the LLM
* [ ] Grounded prompt is used
* [ ] Answers are based on retrieved context
* [ ] Sources are displayed
* [ ] Unknown questions are rejected
* [ ] Hallucination test passes

## Chat

* [ ] Student can ask questions
* [ ] Conversations are saved
* [ ] History works
* [ ] Conversation deletion works
* [ ] Feedback works
* [ ] Sources appear

## Admin

* [ ] Dashboard works
* [ ] Documents can be managed
* [ ] Processing status appears
* [ ] Analytics work
* [ ] Students cannot access admin functions

## Deployment

* [ ] GitHub repository works
* [ ] MongoDB Atlas works
* [ ] Render backend works
* [ ] Vercel frontend works
* [ ] Production API works
* [ ] CORS works
* [ ] Production authentication works
* [ ] No secrets are committed
* [ ] No production localhost references remain

---

# 84. AI CODING AGENT INSTRUCTIONS

The AI coding agent must treat this file as the primary source of truth.

Follow the specification exactly unless a technical limitation requires a documented change.

Do NOT:

* Build a fake chatbot.
* Hardcode answers.
* Fake vector search.
* Fake similarity scores.
* Hardcode source references.
* Pretend an uploaded document was indexed when it was not.
* Skip document processing.
* Skip embeddings.
* Skip MongoDB Atlas Vector Search.
* Expose API keys.
* Commit `.env`.
* Put database credentials in source code.
* Create non-functional buttons.
* Claim a feature works without testing it.

---

# 85. RAG Integrity Rule

This is the most important implementation rule:

```text
NO REAL RETRIEVAL
        =
NOT A RAG PROJECT
```

The system must demonstrably perform:

```text
Document
 ↓
Extraction
 ↓
Chunking
 ↓
Embedding
 ↓
Vector Storage
 ↓
Vector Search
 ↓
Retrieved Context
 ↓
LLM
 ↓
Grounded Answer
```

The implementation must be testable at every stage.

---

# 86. Architecture Rules

The AI coding agent must:

* Keep authentication logic separate.
* Keep document processing separate.
* Keep RAG services modular.
* Keep database access centralized.
* Keep API routes thin.
* Keep business logic in services.
* Keep embedding logic separate from retrieval.
* Keep retrieval separate from generation.
* Keep source attribution separate from presentation.
* Keep frontend API calls centralized.
* Use environment variables for configuration.

---

# 87. AI Agent Development Workflow

The coding agent must follow:

```text
READ SPEC
    ↓
ANALYZE REQUIREMENTS
    ↓
CREATE IMPLEMENTATION PLAN
    ↓
IMPLEMENT ONE PHASE
    ↓
RUN APPLICATION
    ↓
RUN TESTS
    ↓
INSPECT ERRORS
    ↓
FIX ERRORS
    ↓
VERIFY PHASE
    ↓
DOCUMENT CHANGES
    ↓
NEXT PHASE
```

Do not generate the entire application blindly in one step.

---

# 88. Phase Completion Reporting

At the end of every development phase, report:

```text
PHASE:
STATUS:

FILES CREATED:
- ...

FILES MODIFIED:
- ...

FEATURES IMPLEMENTED:
- ...

TESTS RUN:
- ...

TEST RESULTS:
- ...

KNOWN ISSUES:
- ...

NEXT PHASE:
- ...
```

Do not mark a phase complete if its core requirements are failing.

---

# 89. Final Demonstration Flow

The final demonstration should show:

```text
ADMIN LOGIN
      ↓
UPLOAD OFFICIAL COLLEGE PDF
      ↓
DOCUMENT PROCESSING
      ↓
TEXT EXTRACTION
      ↓
CHUNKING
      ↓
EMBEDDINGS
      ↓
MONGODB ATLAS VECTOR SEARCH
      ↓
STUDENT LOGIN
      ↓
ASK COLLEGE QUESTION
      ↓
QUERY EMBEDDING
      ↓
SEMANTIC RETRIEVAL
      ↓
RELEVANT CONTEXT
      ↓
LLM
      ↓
GROUNDED ANSWER
      ↓
SOURCE DOCUMENT + PAGE
```

Then demonstrate:

```text
UNKNOWN QUESTION
      ↓
NO SUFFICIENT RETRIEVAL
      ↓
NO LLM HALLUCINATION
      ↓
INFORMATION UNAVAILABLE RESPONSE
```

This demonstration must prove that the project is a genuine RAG application.

---

# 90. Final Instruction

Build **CollegeAI** as a real, deployable, production-style RAG application.

The priority order is:

```text
1. Correctness
2. Genuine RAG implementation
3. Security
4. Reliability
5. Usability
6. Deployment
7. Visual polish
8. Advanced features
```

Do not sacrifice RAG correctness for visual features.

Do not sacrifice security for convenience.

Do not sacrifice reliability for unnecessary complexity.

Start with:

```text
PHASE 1 — PROJECT FOUNDATION
```

Before writing large amounts of code:

1. Read this entire `spec.md`.
2. Analyze the requirements.
3. Produce the implementation plan.
4. Confirm the proposed architecture.
5. Create the project foundation.
6. Run the application.
7. Verify Phase 1.
8. Continue phase-by-phase.

The final application must be genuinely functional, testable, explainable, secure, and deployable using:

```text
GitHub
   ↓
Vercel
   +
Render
   ↓
MongoDB Atlas
```

**End of Specification**
