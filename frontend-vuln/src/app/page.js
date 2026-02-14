"use client";

import { useEffect, useState } from "react";
import { HOST, PORT, BASE_URL } from "./variables";
import { datadogRum } from "@datadog/browser-rum";


export default function Home() {
  console.log(HOST, PORT, "HOST AND PORT IMPORT FROM BUILD TIME");

  const [notes, setNotes] = useState([]);
  const [newContent, setNewContent] = useState("");

  datadogRum.setUser({
    id: "1234",
    name: "John Doe",
    email: "john@doe.com",
    plan: "premium",
  });

  const fetchNotes = async () => {
    datadogRum;
    // using NEXT_PUBLIC_HOST and NEXT_PUBLIC_PORT
    // non NEXT_PUBLIC_* environment variables are only available in the Node.js environment, meaning they aren't accessible to the browser (the client runs in a different environment.
    // const res = await fetch(`http://${HOST}:${PORT}/notes`);
    const res = await fetch(`${BASE_URL}/notes`);
    const data = await res.json();
    setNotes(data);
  };

  const addNote = async () => {
    if (!newContent.trim()) return;
    await fetch(`${BASE_URL}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: newContent }),
    });
    setNewContent("");
    fetchNotes();
  };

  const deleteNote = async (id) => {
    await fetch(`${BASE_URL}/notes/${id}`, { method: "DELETE" });
    fetchNotes();
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  return (
    <main className="max-w-xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">📝 Notes App</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          placeholder="Write a note..."
          className="flex-1 px-3 py-2 border rounded-md shadow-sm"
        />
        <button
          onClick={addNote}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add Note
        </button>
      </div>

      <ul className="space-y-3">
        {notes.map((note) => (
          <li
            key={note.id}
            className="flex justify-between items-center p-3 bg-white border rounded shadow-sm"
          >
            <p className="text-md text-black">{note.content}</p>
            <button
              onClick={() => deleteNote(note.id)}
              className="text-red-500 hover:text-red-700"
            >
              🗑️
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
