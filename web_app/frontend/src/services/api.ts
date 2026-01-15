import axios, { AxiosError } from "axios";
import type { Contact, ApiResponse,QueryResult,TableSchema,SqlQuery } from "../types";

// const API_BASE_URL = "http://localhost:5000/api";
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";


const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getAllContacts = async (): Promise<Contact[]> => {
  try {
    const response = await api.get<ApiResponse<Contact[]>>("/contacts");
    if (response.data.success && response.data.data) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || "Failed to fetch contacts");
    }
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to fetch contacts"
    );
  }
};

export const getContact = async (id: number): Promise<Contact> => {
  try {
    const response = await api.get<ApiResponse<Contact>>(`/contacts/${id}`);
    if (response.data.success && response.data.data) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || "Failed to fetch contact");
    }
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to fetch contact"
    );
  }
};

export const searchContacts = async (query: string): Promise<Contact[]> => {
  try {
    const response = await api.get<ApiResponse<Contact[]>>(
      `/contacts/search?q=${encodeURIComponent(query)}`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || "Failed to search contacts");
    }
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to search contacts"
    );
  }
};

export const createContact = async (
  contactData: Omit<Contact, "id" | "created_at">
): Promise<Contact> => {
  try {
    const response = await api.post<ApiResponse<Contact>>(
      "/contacts",
      contactData
    );
    if (response.data.success && response.data.data) {
      return response.data.data; 
    } else {
      throw new Error(response.data.error || "Failed to create contact");
    }
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to create contact"
    );
  }
};

export const updateContact = async (
  id: number,
  contactData: Partial<Contact>
): Promise<ApiResponse> => {
  try {
    const response = await api.put<ApiResponse>(`/contacts/${id}`, contactData);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to update contact"
    );
  }
};

export const deleteContact = async (id: number): Promise<ApiResponse> => {
  try {
    const response = await api.delete<ApiResponse>(`/contacts/${id}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to delete contact"
    );
  }
};

export const healthCheck = async (): Promise<ApiResponse> => {
  try {
    const response = await api.get<ApiResponse>("/health");
    return response.data;
  } catch (error) {
    throw new Error("API is not reachable");
  }
};


export const executeSqlQuery = async (query: string): Promise<QueryResult> => {
  try {
    console.log("Sending SQL query:", query);
    const response = await api.post<any>("/sql/execute", { query });
    console.log("SQL API Response:", response.data);

    const responseData = response.data;

    if (!responseData.success) {
      return {
        success: false,
        error: responseData.error || "Query execution failed",
      };
    }

    const result: QueryResult = {
      success: true,
    };

    if (responseData.data !== undefined) {
      result.data = responseData.data;
    }
    if (responseData.rows_affected !== undefined) {
      result.rows_affected = responseData.rows_affected;
    }
    if (responseData.message !== undefined) {
      result.message = responseData.message;
    }
    if (responseData.result !== undefined) {
      result.result = responseData.result;
    }

    console.log("Processed QueryResult:", result);
    return result;
  } catch (error) {
    console.error("SQL execution error:", error);
    const axiosError = error as AxiosError<any>;

    if (axiosError.response?.data) {
      const errorData = axiosError.response.data;
      return {
        success: false,
        error:
          errorData.error || errorData.message || "Failed to execute SQL query",
      };
    }

    return {
      success: false,
      error:
        "Failed to execute SQL query. Please check if the backend is running.",
    };
  }
};

export const getTableSchema = async (tableName?: string): Promise<TableSchema[]> => {
  try {
    const url = tableName ? `/sql/schema/${tableName}` : "/sql/schema";
    const response = await api.get<ApiResponse<TableSchema[]>>(url);
    if (response.data.success && response.data.data) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || "Failed to fetch schema");
    }
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to fetch schema"
    );
  }
};

export const createIndex = async (
  tableName: string,
  columnName: string,
  indexName?: string
): Promise<ApiResponse> => {
  try {
    const response = await api.post<ApiResponse>("/sql/index", {
      table_name: tableName,
      column_name: columnName,
      index_name: indexName
    });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to create index"
    );
  }
};

export const dropIndex = async (indexName: string, tableName: string): Promise<ApiResponse> => {
  try {
    const response = await api.delete<ApiResponse>(`/sql/index/${tableName}/${indexName}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiResponse>;
    throw new Error(
      axiosError.response?.data?.error || "Failed to drop index"
    );
  }
};

export const getQueryHistory = async (): Promise<SqlQuery[]> => {
  try {
    const response = await api.get<ApiResponse<SqlQuery[]>>("/sql/history");
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    return [];
  } catch (error) {
    console.error("Failed to fetch query history:", error);
    return [];
  }
};