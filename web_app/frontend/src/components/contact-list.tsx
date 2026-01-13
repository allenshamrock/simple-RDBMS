import React from "react";
import type { Contact, ContactListProps } from "../types";
import { deleteContact } from "../services/api";
import { FaEdit, FaTrash } from "react-icons/fa";

const ContactList: React.FC<ContactListProps> = ({
  contacts,
  onEdit,
  onDeleteSuccess,
}) => {
  const handleDelete = async (id: number) => {
    if (window.confirm("Are you sure you want to delete this contact?")) {
      try {
        await deleteContact(id);
        onDeleteSuccess();
      } catch (error) {
        alert(
          "Error deleting contact: " +
            (error instanceof Error ? error.message : "Unknown error")
        );
      }
    }
  };

  if (contacts.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg
            className="w-16 h-16 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
        </div>
        <h3 className="text-xl font-medium text-gray-600 mb-2">
          No contacts found
        </h3>
        <p className="text-gray-500">Add your first contact to get started</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contact
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contact Info
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Company
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {contacts.map((contact) => (
            <tr key={contact.id} className="hover:bg-gray-50 transition-colors">
              {/* Name Column */}
              <td className="px-6 py-4">
                <div>
                  <div className="font-medium text-gray-900">
                    {contact.name}
                  </div>
                  {contact.address && (
                    <div className="text-sm text-gray-500 mt-1">
                      {contact.address}
                    </div>
                  )}
                </div>
              </td>

              {/* Contact Info Column */}
              <td className="px-6 py-4">
                <div className="space-y-1">
                  <div className="text-sm text-gray-900">{contact.email}</div>
                  <div className="text-sm text-gray-500">
                    {contact.phone || (
                      <span className="text-gray-400">No phone</span>
                    )}
                  </div>
                </div>
              </td>

              {/* Company Column */}
              <td className="px-6 py-4">
                <div className="text-sm text-gray-900">
                  {contact.company || <span className="text-gray-400">-</span>}
                </div>
              </td>

              {/* Actions Column */}
              <td className="px-6 py-4">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => onEdit(contact)}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors"
                  >
                    <FaEdit />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(contact.id)}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    <FaTrash />
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ContactList;
