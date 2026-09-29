import React, { useState } from "react";

/** Download a filtered session or course export using the signed-in user's token. */
export default function ExportButton() {
  const [resourceType, setResourceType] = useState("sessions");
  const [resourceId, setResourceId] = useState("");
  const [format, setFormat] = useState("csv");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [studentId, setStudentId] = useState("");
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  async function downloadExport(event) {
    event.preventDefault();
    setError("");
    if (!resourceId || Number(resourceId) < 1) {
      setError("Enter a valid session or course ID.");
      return;
    }

    const query = new URLSearchParams({ format });
    if (start) query.set("start", start);
    if (end) query.set("end", end);
    if (studentId) query.set("student_id", studentId);
    const token = localStorage.getItem("token");

    setDownloading(true);
    try {
      const response = await fetch(
        `/api/export/${resourceType}/${encodeURIComponent(resourceId)}?${query}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} },
      );
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(
          body.detail || "Export failed. Please check your access and filters.",
        );
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `engagement-${resourceType.slice(0, -1)}-${resourceId}.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (downloadError) {
      setError(downloadError.message);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <form
      onSubmit={downloadExport}
      style={{ display: "grid", gap: "0.75rem", maxWidth: 420 }}
    >
      <h2>Export engagement data</h2>
      <label>
        Data
        <select
          value={resourceType}
          onChange={(event) => setResourceType(event.target.value)}
        >
          <option value="sessions">Session</option>
          <option value="courses">Course</option>
        </select>
      </label>
      <label>
        {resourceType === "sessions" ? "Session ID" : "Course ID"}
        <input
          type="number"
          min="1"
          required
          value={resourceId}
          onChange={(event) => setResourceId(event.target.value)}
        />
      </label>
      <label>
        Format
        <select value={format} onChange={(event) => setFormat(event.target.value)}>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
        </select>
      </label>
      <label>
        Start date
        <input
          type="date"
          value={start}
          onChange={(event) => setStart(event.target.value)}
        />
      </label>
      <label>
        End date
        <input
          type="date"
          value={end}
          onChange={(event) => setEnd(event.target.value)}
        />
      </label>
      <label>
        Student ID filter (optional)
        <input
          type="number"
          min="1"
          value={studentId}
          onChange={(event) => setStudentId(event.target.value)}
        />
      </label>
      <button type="submit" disabled={downloading}>
        {downloading ? "Preparing download…" : "Download export"}
      </button>
      {error && <p role="alert" style={{ color: "#b42318" }}>{error}</p>}
    </form>
  );
}
