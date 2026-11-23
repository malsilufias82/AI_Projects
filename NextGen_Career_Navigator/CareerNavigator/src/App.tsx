import React, { useState } from 'react';
import { QuestionnaireForm } from './components/QuestionnaireForm';
import { ReportDisplay } from './components/ReportDisplay';
import { Answer, Report, CandidateData } from './types';
import { AnalysisEngine, generateWealthPlan, generateCareerRoadmap } from './services/analysisEngine';
import './App.css';

type AppState = 'form' | 'report';

function App() {
  const [appState, setAppState] = useState<AppState>('form');
  const [currentReport, setCurrentReport] = useState<Report | null>(null);

  const handleQuestionnairesComplete = (answers: Answer[], personalInfo: any) => {
    // Create analysis
    const analysisEngine = new AnalysisEngine(answers);
    const metrics = analysisEngine.analyze();
    const recommendations = analysisEngine.generateRecommendations(metrics);
    const topStrengths = analysisEngine.getTopStrengths(metrics);
    const hiddenStrengths = analysisEngine.getHiddenStrengths(metrics);
    const growthAreas = analysisEngine.getGrowthAreas(metrics);
    const wealthPlan = generateWealthPlan(recommendations);
    const careerRoadmap = generateCareerRoadmap(recommendations);

    // Generate report
    const report: Report = {
      candidateName: personalInfo.name,
      generatedAt: new Date().toISOString(),
      metrics,
      topStrengths,
      hiddenStrengths,
      growthAreas,
      recommendations,
      wealthPlan,
      careerRoadmap,
    };

    setCurrentReport(report);
    setAppState('report');
  };

  const handleBackToForm = () => {
    setCurrentReport(null);
    setAppState('form');
  };

  const handleReset = () => {
    setCurrentReport(null);
    setAppState('form');
  };

  return (
    <div className="min-h-screen">
      {appState === 'form' ? (
        <QuestionnaireForm
          onComplete={handleQuestionnairesComplete}
          onReset={handleReset}
        />
      ) : currentReport ? (
        <ReportDisplay report={currentReport} onBackToForm={handleBackToForm} />
      ) : null}
    </div>
  );
}

export default App;
