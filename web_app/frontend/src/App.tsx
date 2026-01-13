import { useState, useEffect } from "react";
import ContactList from "./components/contact-list";
import ContactForm from "./components/contact-form";
import SearchBar from "./components/search-bar";
import { getAllContacts, searchContacts } from "./services/api";
import type { Contact } from "./types";
import { FaPlus } from "react-icons/fa";

function App() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshCounter, setRefreshCounter] = useState(0);

  useEffect(() => {
    console.log("App mounted, loading contacts...");
    loadContacts();
  }, []);

  useEffect(() => {
    console.log("Contacts updated:", contacts);
  }, [contacts]);

  const loadContacts = async () => {
    try {
      console.log("Calling loadContacts()");
      setLoading(true);
      const data = await getAllContacts();
      console.log("Received contacts:", data);
      setContacts(data);
    } catch (error) {
      console.error("Error loading contacts:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    console.log("Searching for:", query);
    setSearchQuery(query);
    if (query.trim() === "") {
      loadContacts();
    } else {
      try {
        const data = await searchContacts(query);
        setContacts(data);
      } catch (error) {
        console.error("Error searching contacts:", error);
      }
    }
  };

  const handleEdit = (contact: Contact) => {
    console.log("Editing contact:", contact);
    setSelectedContact(contact);
    setShowForm(true);
  };

  const handleAdd = () => {
    console.log("Adding new contact");
    setSelectedContact(null);
    setShowForm(true);
  };

  const handleFormClose = () => {
    console.log("Closing form, refreshing contacts...");
    setShowForm(false);
    setSelectedContact(null);

    // Force refresh in multiple ways
    loadContacts();
    setRefreshCounter((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold mb-2">Contact Manager</h1>
          <p className="text-primary-100">Built with Custom RDBMS</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Debug info */}
        <div className="mb-4 p-2 bg-yellow-50 text-sm text-gray-700 rounded">
          Contacts: {contacts.length} | Refresh: {refreshCounter}
        </div>

        {/* Search and Add Section */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex-1">
            <SearchBar onSearch={handleSearch} />
          </div>
          <button
            onClick={handleAdd}
            className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            <FaPlus />
            Add Contact
          </button>
        </div>

        {/* Contacts List */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <span className="ml-3">Loading contacts...</span>
            </div>
          ) : (
            <ContactList
              key={refreshCounter}
              contacts={contacts}
              onEdit={handleEdit}
              onDeleteSuccess={loadContacts}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="container mx-auto px-4 py-6 text-center text-gray-600">
          <p>Powered by Custom RDBM - Built with Flask & React</p>
        </div>
      </footer>

      {/* Contact Form Modal */}
      {showForm && (
        <ContactForm
          contact={selectedContact}
          onClose={handleFormClose}
          onSuccess={handleFormClose}
        />
      )}
    </div>
  );
}

export default App;
