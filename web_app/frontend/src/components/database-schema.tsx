import React, { useState, useEffect } from "react";
import { getTableSchema, createIndex, dropIndex } from "../services/api";
import {
  FaTable,
  FaKey,
  FaDatabase,
  FaPlus,
  FaTrash,
  FaEye,
} from "react-icons/fa";
import type { TableSchema } from "../types";

const DatabaseSchema: React.FC = () => {
  const [schema, setSchema] = useState<TableSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [newIndexColumn, setNewIndexColumn] = useState("");
  const [newIndexName, setNewIndexName] = useState("");

  useEffect(() => {
    loadSchema();
  }, []);

  const loadSchema = async () => {
    try {
      setLoading(true);
      const data = await getTableSchema();
      setSchema(data);
      if (data.length > 0 && !selectedTable) {
        setSelectedTable(data[0].name);
      }
    } catch (error) {
      console.error("Error loading schema:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIndex = async (tableName: string) => {
    if (!newIndexColumn.trim()) {
      alert("Please enter a column name");
      return;
    }

    try {
      const indexName = newIndexName.trim() || undefined;
      await createIndex(tableName, newIndexColumn, indexName);
      alert("Index created successfully");
      await loadSchema();
      setNewIndexColumn("");
      setNewIndexName("");
    } catch (error: any) {
      alert(`Failed to create index: ${error.message}`);
    }
  };

  const handleDropIndex = async (tableName: string, indexName: string) => {
    if (confirm(`Are you sure you want to drop index ${indexName}?`)) {
      try {
        await dropIndex(indexName, tableName);
        alert("Index dropped successfully");
        await loadSchema();
      } catch (error: any) {
        alert(`Failed to drop index: ${error.message}`);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3">Loading database schema...</span>
      </div>
    );
  }

  const currentTable = schema.find((t) => t.name === selectedTable);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <FaDatabase className="text-2xl text-primary-600" />
        <h2 className="text-xl font-bold text-gray-800">Database Schema</h2>
      </div>

      {/* Table Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Table:
        </label>
        <div className="flex flex-wrap gap-2">
          {schema.map((table) => (
            <button
              key={table.name}
              onClick={() => setSelectedTable(table.name)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedTable === table.name
                  ? "bg-primary-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <div className="flex items-center gap-2">
                <FaTable />
                {table.name}
              </div>
            </button>
          ))}
        </div>
      </div>

      {currentTable && (
        <>
          {/* Columns Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FaEye />
              Columns in {currentTable.name}
            </h3>
            <div className="overflow-x-auto border rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Column
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Constraints
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {currentTable.columns.map((column) => (
                    <tr key={column.name} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center gap-2">
                          {column.name}
                          {column.is_primary && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              <FaKey className="mr-1" /> PK
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {column.data_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex flex-wrap gap-1">
                          {column.is_primary && (
                            <span className="px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-800">
                              PRIMARY KEY
                            </span>
                          )}
                          {column.is_unique && (
                            <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                              UNIQUE
                            </span>
                          )}
                          {!column.nullable && (
                            <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-800">
                              NOT NULL
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Indexes Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Indexes
            </h3>

            {currentTable.indexes.length > 0 ? (
              <div className="space-y-3">
                {currentTable.indexes.map((index) => (
                  <div
                    key={index.name}
                    className="flex items-center justify-between p-4 bg-gray-50 border rounded-lg"
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {index.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        Column: {index.column_name}
                      </div>
                    </div>
                    <button
                      onClick={() =>
                        handleDropIndex(currentTable.name, index.name)
                      }
                      className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                      title="Drop index"
                    >
                      <FaTrash />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">
                No indexes defined for this table
              </p>
            )}
          </div>

          {/* Create Index Form */}
          <div className="p-4 bg-gray-50 rounded-lg border">
            <h4 className="font-medium text-gray-800 mb-3 flex items-center gap-2">
              <FaPlus />
              Create New Index
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Column Name
                </label>
                <input
                  type="text"
                  value={newIndexColumn}
                  onChange={(e) => setNewIndexColumn(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter column name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Index Name (optional)
                </label>
                <input
                  type="text"
                  value={newIndexName}
                  onChange={(e) => setNewIndexName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Auto-generated if empty"
                />
              </div>
            </div>
            <button
              onClick={() => handleCreateIndex(currentTable.name)}
              disabled={!newIndexColumn.trim()}
              className="mt-4 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              Create Index
            </button>
          </div>
        </>
      )}

      {/* Refresh Button */}
      <div className="mt-6 pt-6 border-t">
        <button
          onClick={loadSchema}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          Refresh Schema
        </button>
      </div>
    </div>
  );
};

export default DatabaseSchema;
