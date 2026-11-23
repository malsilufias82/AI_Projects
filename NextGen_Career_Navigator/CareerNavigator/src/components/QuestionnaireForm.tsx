import React, { useState } from 'react';
import { QUESTIONS } from '../types';
import { Answer } from '../types';
import { VoiceRecorder } from './VoiceRecorder';

interface QuestionnairFormProps {
  onComplete: (answers: Answer[], personalInfo: any) => void;
  onReset: () => void;
}

export const QuestionnaireForm: React.FC<QuestionnairFormProps> = ({ onComplete, onReset }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [personalInfo, setPersonalInfo] = useState({
    name: '',
    dateOfBirth: '',
    placeOfBirth: '',
    birthTime: '',
  });
  const [showPersonalInfo, setShowPersonalInfo] = useState(true);
  const [showVoiceInput, setShowVoiceInput] = useState(false);

  const question = QUESTIONS[currentQuestion];
  const progress = ((currentQuestion + 1) / QUESTIONS.length) * 100;

  const handlePersonalInfoChange = (field: string, value: string) => {
    setPersonalInfo({ ...personalInfo, [field]: value });
  };

  const handleStartQuestionnaire = () => {
    if (personalInfo.name.trim()) {
      setShowPersonalInfo(false);
    }
  };

  const handleAnswerChange = (answer: string) => {
    const newAnswers = answers.filter(a => a.questionId !== question.id);
    newAnswers.push({
      questionId: question.id,
      text: answer,
      section: question.section,
    });
    setAnswers(newAnswers);
  };

  const handleMultiSelectChange = (selectedOption: string) => {
    const existingAnswer = answers.find(a => a.questionId === question.id);
    let currentAnswers = existingAnswer ? existingAnswer.text.split('|||').filter(a => a) : [];

    if (currentAnswers.includes(selectedOption)) {
      currentAnswers = currentAnswers.filter(a => a !== selectedOption);
    } else {
      currentAnswers.push(selectedOption);
    }

    const newAnswers = answers.filter(a => a.questionId !== question.id);
    newAnswers.push({
      questionId: question.id,
      text: currentAnswers.join('|||'),
      section: question.section,
    });
    setAnswers(newAnswers);
  };

  const handleVoiceText = (text: string) => {
    const existingText = answers.find(a => a.questionId === question.id)?.text || '';
    handleAnswerChange(existingText ? existingText + text : text);
  };

  const handleVoiceClear = () => {
    // When voice is cleared, remove the current answer
    const newAnswers = answers.filter(a => a.questionId !== question.id);
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setShowVoiceInput(false);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
      setShowVoiceInput(false);
    }
  };

  const handleSubmit = () => {
    onComplete(answers, personalInfo);
  };

  const handleReset = () => {
    setCurrentQuestion(0);
    setAnswers([]);
    setPersonalInfo({
      name: '',
      dateOfBirth: '',
      placeOfBirth: '',
      birthTime: '',
    });
    setShowPersonalInfo(true);
    setShowVoiceInput(false);
    onReset();
  };

  const currentAnswer = answers.find(a => a.questionId === question.id)?.text || '';
  const currentAnswersArray = currentAnswer ? currentAnswer.split('|||').filter(a => a) : [];

  if (showPersonalInfo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Career Discovery
          </h1>
          <p className="text-gray-600 text-center mb-6">
            AI-Powered Career Roundtable Interview
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Your Full Name *
              </label>
              <input
                type="text"
                value={personalInfo.name}
                onChange={(e) => handlePersonalInfoChange('name', e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                placeholder="Enter your name"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Date of Birth (Optional)
              </label>
              <input
                type="date"
                value={personalInfo.dateOfBirth}
                onChange={(e) => handlePersonalInfoChange('dateOfBirth', e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Place of Birth (Optional)
              </label>
              <input
                type="text"
                value={personalInfo.placeOfBirth}
                onChange={(e) => handlePersonalInfoChange('placeOfBirth', e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
                placeholder="Enter place of birth"
              />
            </div>

            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Time of Birth (Optional - for Astrology)
              </label>
              <input
                type="time"
                value={personalInfo.birthTime}
                onChange={(e) => handlePersonalInfoChange('birthTime', e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          <button
            onClick={handleStartQuestionnaire}
            disabled={!personalInfo.name.trim()}
            className="w-full mt-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Start Interview
          </button>

          <p className="text-gray-500 text-xs text-center mt-4">
            30 questions • ~15 minutes • Comprehensive analysis
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-white mb-6 text-center">
          <h1 className="text-3xl font-bold mb-2">Career Discovery Interview</h1>
          <p className="text-blue-100">{personalInfo.name}</p>
        </div>

        {/* Progress Bar */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <p className="text-gray-600 font-semibold">
                Question {currentQuestion + 1} of {QUESTIONS.length}
              </p>
              <p className="text-gray-500 text-sm">{question.section}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-purple-600">{Math.round(progress)}%</p>
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">{question.text}</h2>

          {question.type === 'textarea' ? (
            <>
              <textarea
                value={currentAnswer}
                onChange={(e) => handleAnswerChange(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 resize-none"
                placeholder="Enter your answer here..."
                rows={5}
              />
              
              {question.voiceEnabled && (
                <div className="mt-4">
                  <button
                    onClick={() => setShowVoiceInput(!showVoiceInput)}
                    className="w-full mb-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-bold py-2 rounded-lg hover:opacity-90 transition flex items-center justify-center gap-2"
                  >
                    <span className="text-lg">🎤</span>
                    {showVoiceInput ? 'Hide Voice Input' : 'Add Voice Input'}
                  </button>
                  
                  {showVoiceInput && (
                    <VoiceRecorder onTextReceived={handleVoiceText} onClear={handleVoiceClear} />
                  )}
                </div>
              )}
            </>
          ) : question.multiSelect ? (
            <div className="space-y-3">
              <p className="text-gray-600 text-sm font-semibold mb-4">Select one or more options:</p>
              {question.options?.map((option) => (
                <button
                  key={option}
                  onClick={() => handleMultiSelectChange(option)}
                  className={`w-full p-4 rounded-lg font-semibold transition flex items-center gap-3 ${
                    currentAnswersArray.includes(option)
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white border-2 border-purple-700'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-2 border-transparent'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={currentAnswersArray.includes(option)}
                    onChange={() => {}}
                    className="w-5 h-5 cursor-pointer"
                  />
                  {option}
                </button>
              ))}
              {currentAnswersArray.length > 0 && (
                <p className="text-blue-600 text-sm font-semibold mt-3">
                  ✓ {currentAnswersArray.length} option(s) selected
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {question.options?.map((option) => (
                <button
                  key={option}
                  onClick={() => handleAnswerChange(option)}
                  className={`w-full p-4 rounded-lg font-semibold transition ${
                    currentAnswer === option
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex gap-4 justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className="flex-1 bg-white text-purple-600 font-bold py-3 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Previous
          </button>

          {currentQuestion === QUESTIONS.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={answers.length === 0}
              className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold py-3 rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Generate Report
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 rounded-lg hover:opacity-90 transition"
            >
              Next
            </button>
          )}

          <button
            onClick={handleReset}
            className="px-6 bg-red-500 text-white font-bold py-3 rounded-lg hover:bg-red-600 transition"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
};
