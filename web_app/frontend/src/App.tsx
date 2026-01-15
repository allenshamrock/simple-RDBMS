import { useState, useEffect } from "react";
import ContactList from "./components/contact-list";
import ContactForm from "./components/contact-form";
import SearchBar from "./components/search-bar";
import SqlQueryEditor from "./components/sql-query-editor";
import DatabaseSchema from "./components/database-schema";
import { getAllContacts, searchContacts, healthCheck } from "./services/api";
import type { Contact } from "./types";
import { FaPlus, FaDatabase, FaTerminal } from "react-icons/fa";

function App() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshCounter, setRefreshCounter] = useState(0);
  const [activeTab, setActiveTab] = useState<"contacts" | "sql" | "schema">(
    "contacts"
  );
  const [dbStatus, setDbStatus] = useState<
    "healthy" | "unhealthy" | "checking"
  >("checking");

  useEffect(() => {
    console.log("App mounted, loading contacts...");
    loadContacts();
    checkDbHealth();
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

  const checkDbHealth = async () => {
    try {
      setDbStatus("checking");
      await healthCheck();
      setDbStatus("healthy");
    } catch (error) {
      setDbStatus("unhealthy");
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
    loadContacts();
    setRefreshCounter((prev) => prev + 1);
  };

  const handleQueryExecuted = () => {
    // Refresh contacts when SQL queries affect the contacts table
    if (activeTab === "contacts") {
      loadContacts();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Contact Manager</h1>
              <p className="text-primary-100">Built with Custom RDBMS</p>
            </div>
            <div className="mt-4 md:mt-0 flex items-center gap-4">
              <div
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  dbStatus === "healthy"
                    ? "bg-green-500"
                    : dbStatus === "unhealthy"
                    ? "bg-red-500"
                    : "bg-yellow-500"
                }`}
              >
                {dbStatus === "healthy"
                  ? "● Database Connected"
                  : dbStatus === "unhealthy"
                  ? "● Database Error"
                  : "● Checking..."}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab("contacts")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "contacts"
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Contacts
              </button>
              <button
                onClick={() => setActiveTab("sql")}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === "sql"
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <FaTerminal />
                SQL Query Editor
              </button>
              <button
                onClick={() => setActiveTab("schema")}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === "schema"
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <FaDatabase />
                Database Schema
              </button>
            </nav>
          </div>
        </div>

        {/* Contacts Tab */}
        {activeTab === "contacts" && (
          <>
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
          </>
        )}

        {/* SQL Query Editor Tab */}
        {activeTab === "sql" && (
          <SqlQueryEditor onQueryExecuted={handleQueryExecuted} />
        )}

        {/* Database Schema Tab */}
        {activeTab === "schema" && <DatabaseSchema />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between text-gray-600">
            <p>Powered by Custom RDBMS - Built with Flask & React</p>
            <div className="mt-2 md:mt-0 flex gap-4">
              <button
                onClick={() => setActiveTab("contacts")}
                className="text-primary-600 hover:text-primary-800"
              >
                Contacts
              </button>
              <button
                onClick={() => setActiveTab("sql")}
                className="text-primary-600 hover:text-primary-800"
              >
                SQL Editor
              </button>
              <button
                onClick={() => setActiveTab("schema")}
                className="text-primary-600 hover:text-primary-800"
              >
                Schema
              </button>
            </div>
          </div>
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
