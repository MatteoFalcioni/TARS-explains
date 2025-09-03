import { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

function App() {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [tarsText, setTarsText] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [equations, setEquations] = useState([]);
  const chunksRef = useRef([]);

  const handleToggleRecord = async () => {
    if (!recording) {
      // Start recording
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);

      recorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = [];

        const formData = new FormData();
        formData.append("audio", blob, "recording.webm");

        const res = await fetch("http://localhost:8000/api/ask", {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        setTranscript(data.transcript);
        setTarsText(data.text);
        setAudioUrl(`http://localhost:8000${data.audio_url}`);
        setEquations(data.equations);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
    } else {
      // Stop recording
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center p-8 space-y-6">
      <h1 className="text-3xl font-bold text-blue-400">TARS Physics Explainer</h1>

      {/* Mic Button */}
      <button
        onClick={handleToggleRecord}
        className={`w-24 h-24 rounded-full flex items-center justify-center text-xl font-bold shadow-lg transition 
          ${recording ? "bg-red-600 animate-pulse" : "bg-gray-700 hover:bg-gray-600"}
        `}
      >
        {recording ? "Stop" : "Record"}
      </button>

      {/* Display transcript */}
      {transcript && (
        <div className="w-full max-w-2xl bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-blue-300">You said:</h2>
          <p className="mt-2">{transcript}</p>
        </div>
      )}

      {/* Display TARS answer */}
      {tarsText && (
        <div className="w-full max-w-2xl bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-green-300">TARS:</h2>
          <p className="mt-2">{tarsText}</p>
        </div>
      )}

      {/* Audio playback */}
      {audioUrl && (
        <audio src={audioUrl} controls autoPlay className="mt-4" />
      )}

      {/* Equations */}
      {equations.length > 0 && (
        <div className="w-full max-w-2xl bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-semibold text-yellow-300">Equations</h2>
          <div className="mt-2 space-y-4">
            {equations.map((eq, idx) => (
              <div key={idx} className="border-t border-gray-600 pt-2">
                <ReactMarkdown
                  children={eq.content}
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
