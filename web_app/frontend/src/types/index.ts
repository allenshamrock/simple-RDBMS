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
