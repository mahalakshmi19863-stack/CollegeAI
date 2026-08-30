export type UserRole = "STUDENT" | "ADMIN";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
  last_login?: string | null;
}

export type DocumentStatus = "UPLOADED" | "PROCESSING" | "PROCESSED" | "FAILED";

export interface CollegeDocument {
  id: string;
  name: string;
  original_filename: string;
  file_type: "PDF" | "DOCX" | "TXT";
  file_size: number;
  category: string;
  department?: string;
  description?: string;
  version: number;
  status: DocumentStatus;
  uploaded_by: string;
  uploaded_at: string;
  updated_at: string;
  is_active: boolean;
  processing_error?: string | null;
  chunk_count: number;
  total_pages?: number | null;
}

export interface SourceItem {
  document_id: string;
  document_name: string;
  page_number?: number | null;
  relevance_score: number;
  category?: string;
  department?: string;
  snippet?: string;
}

export interface RetrievalStats {
  chunks_retrieved: number;
  chunks_used: number;
  processing_time_ms?: number | null;
}

export type MessageRole = "USER" | "ASSISTANT";

export interface Message {
  id: string;
  conversation_id: string;
  user_id: string;
  role: MessageRole;
  content: string;
  sources?: SourceItem[] | null;
  retrieval_metadata?: RetrievalStats | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatResponseData {
  conversation_id: string;
  message_id: string;
  answer: string;
  sources: SourceItem[];
  retrieval: RetrievalStats;
}

export interface AdminDashboardData {
  total_documents: number;
  processed_documents: number;
  failed_documents: number;
  total_students: number;
  total_questions: number;
  feedback_stats: {
    total: number;
    helpful: number;
    not_helpful: number;
    satisfaction_rate_percent: number;
  };
  recent_uploads: CollegeDocument[];
}

export interface AdminAnalyticsData {
  categories: Record<string, number>;
  departments: Record<string, number>;
  overview: AdminDashboardData;
}
