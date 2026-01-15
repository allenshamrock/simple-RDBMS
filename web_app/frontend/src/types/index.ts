export interface Contact {
  id: number;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  company?: string;
  created_at?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ContactFormProps {
  contact: Contact | null;
  onClose: () => void;
  onSuccess: () => void;
  onContactCreated?: (contact: Contact) => void;
}

export interface ContactListProps {
  contacts: Contact[];
  onEdit: (contact: Contact) => void;
  onDeleteSuccess: () => void;
}

export interface SearchBarProps {
  onSearch: (query: string) => void;
}

export interface TableSchema {
  name: string;
  columns: ColumnSchema[];
  indexes: IndexSchema[];
}

export interface ColumnSchema {
  name: string;
  data_type: string;
  is_primary: boolean;
  is_unique: boolean;
  nullable: boolean;
}

export interface IndexSchema {
  name: string;
  table_name: string;
  column_name: string;
}

export interface QueryResult {
  success: boolean;
  data?: any[];
  rows_affected?: number;
  message?: string;
  error?: string;
}

export interface SqlQuery {
  id?: number;
  query: string;
  result?: QueryResult;
  timestamp: string;
}