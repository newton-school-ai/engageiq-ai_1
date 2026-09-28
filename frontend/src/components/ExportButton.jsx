import React, { useState } from "react";

export default function ExportButton({
  type = "session", // "session" or "course"
  id,
  startDate = "",
  endDate = "",
  studentId = "",
  baseUrl = "/api/export",
  className = "",
  style = {},
}) {
  const [format, setFormat] = useState("csv");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExport = async () => {
    if (!id) {
      setError("ID is required for export.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const endpointType = type === "course" ? "courses" : "sessions";
      const queryParams = new URLSearchParams();
      queryParams.append("format", format);

      if (startDate) queryParams.append("start", startDate);
      if (endDate) queryParams.append("end", endDate);
      if (studentId) queryParams.append("student_id", studentId);

      const url = `${baseUrl}/${endpointType}/${id}?${queryParams.toString()}`;

      const token = localStorage.getItem("token");
      const headers = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(url, { headers });

      if (!response.ok) {
        let errMessage = `Export failed with status ${response.status}`;
        try {
          const errData = await response.json();
          if (errData.detail) {
            errMessage =
              typeof errData.detail === "string"
                ? errData.detail
                : JSON.stringify(errData.detail);
          }
        } catch (_) {
          // Response was not JSON
        }
        throw new Error(errMessage);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;

      const contentDisposition = response.headers.get("Content-Disposition");
      let filename = `${type}_${id}_export.${format}`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=["']?([^"';]+)["']?/);
        if (match && match[1]) {
          filename = match[1];
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError(err.message || "An error occurred during export.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className={`export-button-container ${className}`}
      style={{
        display: "inline-flex",
        flexDirection: "column",
        gap: "4px",
        ...style,
      }}
    >
      <div style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value)}
          disabled={loading}
          aria-label="Export format"
          style={{
            padding: "6px 10px",
            borderRadius: "4px",
            border: "1px solid #ccc",
            fontSize: "14px",
            backgroundColor: "#fff",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
        </select>

        <button
          onClick={handleExport}
          disabled={loading || !id}
          style={{
            padding: "6px 14px",
            borderRadius: "4px",
            border: "none",
            backgroundColor: loading ? "#9ca3af" : "#2563eb",
            color: "#ffffff",
            fontSize: "14px",
            fontWeight: "500",
            cursor: loading || !id ? "not-allowed" : "pointer",
            transition: "background-color 0.2s",
          }}
        >
          {loading ? "Exporting..." : `Export ${format.toUpperCase()}`}
        </button>
      </div>

      {error && (
        <span
          style={{
            color: "#dc2626",
            fontSize: "12px",
            marginTop: "2px",
          }}
        >
          {error}
        </span>
      )}
    </div>
  );
}
