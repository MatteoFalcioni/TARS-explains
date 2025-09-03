import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

function ChatBubble({ role, children }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={[
          "max-w-[80%] rounded-xl p-4 shadow",
          isUser ? "bg-sky-800/60" : "bg-gray-800/80",
        ].join(" ")}
      >
        <div
          className={[
            "mb-2 font-semibold",
            isUser ? "text-sky-300" : "text-green-300",
          ].join(" ")}
        >
          {isUser ? "User:" : "TARS:"}
        </div>
        <div className="whitespace-pre-wrap leading-relaxed">{children}</div>
      </div>
    </div>
  );
}

export default function App() {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([]); // ← chat history
  const [eqCount, setEqCount] = useState(0); // global equation numbering
  const chunksRef = useRef([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleToggleRecord = async () => {
    if (!recording) {
      if (!("MediaRecorder" in window)) {
        setError("MediaRecorder not supported in this browser.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        try {
          // release mic light
          stream.getTracks().forEach((t) => t.stop());
          if (!chunksRef.current.length) {
            setError("No audio captured. Try again.");
            return;
          }

          const blob = new Blob(chunksRef.current, { type: "audio/webm" });
          chunksRef.current = [];

          const formData = new FormData();
          formData.append("audio", blob, "recording.webm");

          setLoading(true);
          setError("");

          const res = await fetch("http://localhost:8000/api/ask", {
            method: "POST",
            body: formData,
          });

          if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Request failed with ${res.status}`);
          }

          const data = await res.json();

          // Assign progressive numbers to this turn's equations
          const numberedEquations = (data.equations || []).map((eq, i) => ({
            ...eq,
            n: eqCount + i + 1, // 1-based, continues from previous turns
          }));

          setMessages((prev) => [
            ...prev,
            { role: "user", text: data.transcript },
            {
              role: "tars",
              text: data.text,
              audioUrl: `http://localhost:8000${data.audio_url}`,
              equations: numberedEquations,
            },
          ]);
          setEqCount(eqCount + numberedEquations.length);
          
        } catch (e) {
          console.error(e);
          setError(e.message || "Unknown error");
        } finally {
          setLoading(false);
        }
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
    } else {
      mediaRecorder?.stop();
      setRecording(false);
      setMediaRecorder(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-8 space-y-6">
      <h1 className="text-3xl sm:text-4xl font-extrabold text-blue-400 tracking-wide">
        TARS-explains
      </h1>

      {/* Record Button */}
      <button
        onClick={handleToggleRecord}
        className={[
          "w-24 h-24 rounded-full flex items-center justify-center text-lg font-bold",
          "shadow-lg transition ring-2 ring-white/10",
          recording
            ? "bg-red-600 animate-pulse"
            : "bg-gray-700 hover:bg-gray-600",
        ].join(" ")}
        title={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? "Stop" : "Record"}
      </button>

      {/* Status */}
      <div className="h-6">
        {loading && <div className="text-sm text-blue-300">TARS is thinking…</div>}
        {error && <div className="text-sm text-red-400">Error: {error}</div>}
      </div>

      {/* Chat log */}
      <div className="w-full max-w-3xl flex-1 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className="space-y-2">
            <ChatBubble role={msg.role}>{msg.text}</ChatBubble>

            {/* If this is a TARS message, show audio + equations */}
            {msg.role === "tars" && (
              <div className="pl-2">
                {msg.audioUrl && (
                  <audio
                    className="mt-2"
                    src={msg.audioUrl}
                    controls
                    autoPlay={idx === messages.length - 1}
                  />
                )}

                {msg.equations?.length > 0 && (
                  <div className="mt-3 ml-8 rounded-lg bg-gray-800/60 p-3 border border-gray-700">
                    <div className="text-sm font-semibold text-yellow-300 mb-2">
                      Equations
                    </div>
                    <div className="space-y-3">
                      {msg.equations.map((eq, i) => {
                        const clean = (eq.content || "").replace(/^#.*\n/, ""); // remove a leading '# Equation ...' line if present
                        return (
                          <div key={i} className="relative rounded-md border border-gray-700/60 bg-gray-900/40 p-3">
                            <div className="absolute right-3 top-2 text-gray-400 text-sm">
                              (eq. {eq.n})
                            </div>
                            <ReactMarkdown
                              children={clean}
                              remarkPlugins={[remarkMath]}
                              rehypePlugins={[rehypeKatex]}
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
