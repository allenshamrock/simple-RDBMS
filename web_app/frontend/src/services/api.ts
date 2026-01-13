import axios, { AxiosError } from "axios";
import type { Contact, ApiResponse } from "../types";

const API_BASE_URL = "http://localhost:5000/api";

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
