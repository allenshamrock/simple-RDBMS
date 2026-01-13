import { useState, useEffect } from "react";
import { createContact, updateContact } from "../services/api";
import type { Contact, ContactFormProps } from "../types";
import { FaTimes } from "react-icons/fa";

interface FormData {
  name: string;
  email: string;
  phone: string;
  address: string;
  company: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  [key: string]: string | undefined;
}

const ContactForm: React.FC<ContactFormProps> = ({
  contact,
  onClose,
  onSuccess,
  onContactCreated
}) => {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    phone: "",
    address: "",
    company: "",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (contact) {
      setFormData({
        name: contact.name || "",
        email: contact.email || "",
        phone: contact.phone || "",
        address: contact.address || "",
        company: contact.company || "",
      });
    }
  }, [contact]);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!validateForm()) {
    return;
  }

  setIsSubmitting(true);

  try {
    if (contact) {
      await updateContact(contact.id, formData);
    } else {
      const newContact = await createContact(formData);

      if (onContactCreated) {
        onContactCreated(newContact);
      }
    }
    onSuccess(); 
  } catch (error) {
    alert(
      `Error saving contact: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  } finally {
    setIsSubmitting(false);
  }
};

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>

      {/* Modal */}
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-800">
              {contact ? "Edit Contact" : "Add New Contact"}
            </h2>
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
            >
              <FaTimes size={24} />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Name Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name *
                  </label>
                  <input
                    type="text"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition ${
                      errors.name
                        ? "border-red-500 focus:ring-red-500"
                        : "border-gray-300"
                    }`}
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    disabled={isSubmitting}
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                  )}
                </div>

                {/* Email Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition ${
                      errors.email
                        ? "border-red-500 focus:ring-red-500"
                        : "border-gray-300"
                    }`}
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={isSubmitting}
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                  )}
                </div>

                {/* Phone Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    disabled={isSubmitting}
                  />
                </div>

                {/* Company Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                    name="company"
                    value={formData.company}
                    onChange={handleChange}
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              {/* Address Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address
                </label>
                <textarea
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  rows={3}
                  disabled={isSubmitting}
                />
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Saving...
                  </span>
                ) : (
                  "Save Contact"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ContactForm;
