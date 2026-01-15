import React, { useState, useEffect } from "react";
import { executeSqlQuery, getQueryHistory } from "../services/api";
import {
  FaPlay,
  FaHistory,
  FaCopy,
  FaTrash,
  FaCheck,
  FaTimes,
} from "react-icons/fa";
import type { QueryResult, SqlQuery } from "../types";

interface SqlQueryEditorProps {
  onQueryExecuted?: (result: QueryResult) => void;
}

const SqlQueryEditor: React.FC<SqlQueryEditorProps> = ({ onQueryExecuted }) => {
  const [query, setQuery] = useState<string>("SELECT * FROM contacts LIMIT 10");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<SqlQuery[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const loadHistory = async () => {
    const historyData = await getQueryHistory();
    setHistory(historyData);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const executeQuery = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      const result = await executeSqlQuery(query);
      setResult(result);
      if (onQueryExecuted) {
        onQueryExecuted(result);
      }
      await loadHistory(); 
    } catch (error: any) {
      setResult({
        success: false,
        error: error.message || "Failed to execute query",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const loadFromHistory = (historyQuery: SqlQuery) => {
    setQuery(historyQuery.query);
    setShowHistory(false);
  };

  const clearResult = () => {
    setResult(null);
  };

  const sampleQueries = [
    "SELECT * FROM contacts",
    "SELECT name, email FROM contacts WHERE name LIKE '%john%'",
    "SELECT COUNT(*) as total_contacts FROM contacts",
    "SELECT * FROM contacts ORDER BY created_at DESC",
    "SELECT company, COUNT(*) as count FROM contacts GROUP BY company",
    "INSERT INTO contacts (name, email, phone) VALUES ('John Doe', 'john@example.com', '1234567890')",
    "UPDATE contacts SET phone = '0987654321' WHERE email = 'john@example.com'",
    "DELETE FROM contacts WHERE id = 1",
    "CREATE INDEX idx_contacts_email ON contacts (email)",
    "DROP INDEX idx_contacts_email ON contacts",
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">SQL Query Editor</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            <FaHistory />
            History
          </button>
          <button
            onClick={clearResult}
            disabled={!result}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <FaTrash />
            Clear
          </button>
        </div>
      </div>

      {/* Query History Panel */}
      {showHistory && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-semibold">Query History</h3>
            <button
              onClick={() => setShowHistory(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <FaTimes />
            </button>
          </div>
          <div className="max-h-60 overflow-y-auto">
            {history.length === 0 ? (
              <p className="text-gray-500 italic">No query history</p>
            ) : (
              history.map((item) => (
                <div
                  key={item.id}
                  className="p-3 mb-2 bg-white border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => loadFromHistory(item)}
                >
                  <div className="flex justify-between items-start">
                    <code className="text-sm text-gray-700 flex-1 mr-2">
                      {item.query.length > 80
                        ? `${item.query.substring(0, 80)}...`
                        : item.query}
                    </code>
                    <span className="text-xs text-gray-500">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    {item.result?.success ? (
                      <span className="inline-flex items-center gap-1 text-xs text-green-600">
                        <FaCheck /> Success
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs text-red-600">
                        <FaTimes /> Error
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Query Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enter SQL Query:
        </label>
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={6}
            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
            placeholder="Enter your SQL query here..."
          />
          <button
            onClick={() => copyToClipboard(query)}
            className="absolute top-2 right-2 p-2 text-gray-500 hover:text-gray-700"
            title="Copy to clipboard"
          >
            <FaCopy />
          </button>
        </div>
      </div>

      {/* Sample Queries */}
      <div className="mb-6">
        <p className="text-sm text-gray-600 mb-2">Sample Queries:</p>
        <div className="flex flex-wrap gap-2">
          {sampleQueries.map((sample, index) => (
            <button
              key={index}
              onClick={() => setQuery(sample)}
              className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full"
            >
              {sample.split(" ").slice(0, 3).join(" ")}...
            </button>
          ))}
        </div>
      </div>

      {/* Execute Button */}
      <div className="mb-6">
        <button
          onClick={executeQuery}
          disabled={loading || !query.trim()}
          className="flex items-center justify-center gap-2 w-full max-w-md py-3 bg-green-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FaPlay />
          {loading ? "Executing..." : "Execute Query"}
        </button>
      </div>

      {/* Result Display */}
      {result && (
        <div className="mt-6 border-t pt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">
              {result.success ? "✅ Query Results" : "❌ Query Error"}
            </h3>
            {result.rows_affected !== undefined && (
              <span className="text-sm text-gray-600">
                Rows affected: {result.rows_affected}
              </span>
            )}
          </div>

          {result.error ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 font-mono text-sm">{result.error}</p>
            </div>
          ) : result.data && result.data.length > 0 ? (
            <div className="overflow-x-auto border rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {Object.keys(result.data[0]).map((column) => (
                      <th
                        key={column}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {result.data.slice(0, 100).map((row, rowIndex) => (
                    <tr key={rowIndex} className="hover:bg-gray-50">
                      {Object.values(row).map((value: any, colIndex) => (
                        <td
                          key={colIndex}
                          className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                        >
                          {value === null ? (
                            <span className="text-gray-400 italic">NULL</span>
                          ) : typeof value === "object" ? (
                            JSON.stringify(value)
                          ) : (
                            String(value)
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {result.data.length > 100 && (
                <div className="p-4 bg-gray-50 text-center text-sm text-gray-600">
                  Showing first 100 of {result.data.length} rows
                </div>
              )}
            </div>
          ) : (
            <div className="p-4 bg-gray-50 text-center text-gray-600 rounded-lg border">
              {result.message || "No data returned"}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SqlQueryEditor;
