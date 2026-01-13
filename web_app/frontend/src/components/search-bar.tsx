import React, { useState } from "react";
import type { SearchBarProps } from "../types";
import { FaSearch, FaTimes } from "react-icons/fa";

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleClear = () => {
    setQuery("");
    onSearch("");
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          className="w-full px-4 py-3 pl-12 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
          placeholder="Search contacts by name, email, or phone..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        {/* Search Icon */}
        <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
          <FaSearch />
        </div>

        {/* Clear Button */}
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <FaTimes />
          </button>
        )}

        {/* Search Button */}
        <button
          type="submit"
          className="absolute right-12 top-1/2 transform -translate-y-1/2 text-primary-600 hover:text-primary-700 transition-colors"
        >
          Search
        </button>
      </div>
    </form>
  );
};

export default SearchBar;
