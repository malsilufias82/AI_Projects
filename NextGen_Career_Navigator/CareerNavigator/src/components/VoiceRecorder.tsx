import React, { useState, useRef, useEffect } from 'react';

interface VoiceRecorderProps {
  onTextReceived: (text: string) => void;
  onClear?: () => void;
  placeholder?: string;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onTextReceived, onClear, placeholder = 'Click mic to start speaking...' }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string>('');
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef<string>('');

  useEffect(() => {
    // Check if browser supports Web Speech API
    const SpeechRecognition = window.webkitSpeechRecognition || (window as any).SpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSupported(true);
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError('');
        finalTranscriptRef.current = '';
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptSegment = event.results[i][0].transcript;

          if (event.results[i].isFinal) {
            finalTranscriptRef.current += transcriptSegment + ' ';
            // Only call onTextReceived once with accumulated final transcript
            onTextReceived(transcriptSegment + ' ');
          } else {
            interimTranscript += transcriptSegment;
          }
        }

        // Show final + interim in display
        setTranscript(finalTranscriptRef.current + interimTranscript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        let errorMessage = 'Microphone error occurred';
        
        if (event.error === 'no-speech') {
          errorMessage = 'No speech detected. Please try again.';
        } else if (event.error === 'network') {
          errorMessage = 'Network error. Please check connection.';
        } else if (event.error === 'not-allowed') {
          errorMessage = 'Microphone permission denied. Check browser settings.';
        }
        
        setError(errorMessage);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
    // Empty dependency array - initialize once on mount
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setTranscript('');
      setError('');
      finalTranscriptRef.current = '';
      recognitionRef.current.start();
    }
  };

  const clearTranscript = () => {
    setTranscript('');
    setError('');
    finalTranscriptRef.current = '';
    if (onClear) {
      onClear();
    }
  };

  if (!isSupported) {
    return (
      <div className="text-center text-gray-500 py-4 bg-gray-50 p-4 rounded-lg border-2 border-gray-200">
        <p className="text-sm">🎤 Voice input not supported in this browser</p>
        <p className="text-xs mt-1">Try Chrome, Firefox, Safari or Edge</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border-2 border-blue-200">
      {error && (
        <div className="mb-3 bg-red-50 border-l-4 border-red-500 p-3 rounded">
          <p className="text-red-700 text-sm font-semibold">⚠ {error}</p>
        </div>
      )}

      <div className="flex gap-3 mb-3">
        <button
          onClick={toggleListening}
          className={`flex-1 flex items-center justify-center gap-2 font-semibold py-3 rounded-lg transition ${
            isListening
              ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          <span className="text-xl">🎤</span>
          {isListening ? 'Stop Recording' : 'Start Voice Input'}
        </button>

        {transcript && (
          <button
            onClick={clearTranscript}
            className="px-4 bg-gray-400 text-white font-semibold rounded-lg hover:bg-gray-500 transition"
          >
            Clear
          </button>
        )}
      </div>

      {transcript && (
        <div className="bg-white p-3 rounded-lg border-l-4 border-blue-500">
          <p className="text-gray-700 text-sm">{transcript}</p>
          <p className="text-gray-500 text-xs mt-2">✓ Ready to save</p>
        </div>
      )}

      {isListening && !transcript && (
        <div className="text-center py-3">
          <p className="text-blue-600 font-semibold">Listening... 👂</p>
          <p className="text-gray-600 text-sm mt-1">Speak clearly to convert to text</p>
        </div>
      )}
    </div>
  );
};
