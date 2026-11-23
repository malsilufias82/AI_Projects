import React, { useRef } from 'react';
import {
  BarChart, Bar, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Cell,
  ScatterChart, Scatter, ReferenceLine
} from 'recharts';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { Report, CareerRecommendation } from '../types';

interface ReportDisplayProps {
  report: Report;
  onBackToForm: () => void;
}

export const ReportDisplay: React.FC<ReportDisplayProps> = ({ report, onBackToForm }) => {
  const reportRef = useRef<HTMLDivElement>(null);

  const downloadReport = async () => {
    if (!reportRef.current) return;

    try {
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgWidth = 210;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= 297;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= 297;
      }

      pdf.save(`Career_Report_${report.candidateName}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF. Please try again.');
    }
  };

  const aptitudeData = [
    { name: 'Logic', value: report.metrics.aptitudeProfile.logical },
    { name: 'Creative', value: report.metrics.aptitudeProfile.creative },
    { name: 'Communication', value: report.metrics.aptitudeProfile.communication },
    { name: 'Leadership', value: report.metrics.aptitudeProfile.leadership },
  ];

  const metricsData = [
    { name: 'Leadership', value: report.metrics.leadershipPotential },
    { name: 'Communication', value: report.metrics.communicationSkills },
    { name: 'Entrepreneurial', value: report.metrics.entrepreneurialPotential },
    { name: 'Creativity', value: report.metrics.creativityScore },
    { name: 'Technical', value: report.metrics.technicalInclination },
    { name: 'Employability', value: report.metrics.employability },
  ];

  const careerComparisonData = report.recommendations.map(rec => ({
    name: rec.title,
    demand: rec.confidence,
    aiRisk: 100 - parseInt(rec.aiRisk.match(/\d+/)?.[0] || '50'),
  }));

  const colors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6'];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div ref={reportRef} className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 rounded-2xl shadow-xl p-8 mb-8 text-white">
          <h1 className="text-4xl font-bold mb-2">Career Discovery Report</h1>
          <p className="text-xl text-gray-100">AI Roundtable Interview Analysis</p>
          <div className="flex justify-between items-start mt-6">
            <div>
              <p className="text-gray-100">Candidate Name</p>
              <p className="text-2xl font-bold">{report.candidateName}</p>
            </div>
            <div className="text-right">
              <p className="text-gray-100">Report Generated</p>
              <p className="text-lg">{new Date(report.generatedAt).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        {/* Personality Profile */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="w-1 h-8 bg-purple-600 mr-3 rounded"></span>
            Personality & Profile
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6 border-2 border-purple-200">
              <p className="text-gray-600 font-semibold mb-2">Personality Type</p>
              <p className="text-2xl font-bold text-purple-600">{report.metrics.personalityType}</p>
              <p className="text-gray-600 text-sm mt-2">Personality Score: {report.metrics.personalityScore}%</p>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border-2 border-blue-200">
              <p className="text-gray-600 font-semibold mb-2">Learning Style</p>
              <p className="text-2xl font-bold text-blue-600">{report.metrics.learningStyle}</p>
              <p className="text-gray-600 text-sm mt-2">Adaptability Score: {report.metrics.employability}%</p>
            </div>
          </div>

          {/* Aptitude Profile Radar */}
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Aptitude Profile</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={aptitudeData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="name" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Key Metrics Dashboard */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="w-1 h-8 bg-pink-600 mr-3 rounded"></span>
            Key Metrics Dashboard
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
            {metricsData.map((metric, idx) => (
              <div key={metric.name} className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 border-l-4" style={{ borderColor: colors[idx % colors.length] }}>
                <p className="text-gray-600 text-sm font-semibold mb-2">{metric.name}</p>
                <p className="text-3xl font-bold" style={{ color: colors[idx % colors.length] }}>
                  {metric.value}%
                </p>
                <div className="w-full bg-gray-300 rounded-full h-2 mt-3">
                  <div
                    className="h-2 rounded-full transition-all duration-500"
                    style={{
                      width: `${metric.value}%`,
                      backgroundColor: colors[idx % colors.length],
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          {/* Risk Assessment */}
          <div className="bg-red-50 rounded-lg p-6 border-2 border-red-200">
            <p className="text-gray-700 font-semibold mb-2">AI Disruption Risk</p>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="w-full bg-gray-300 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-orange-500 to-red-600 h-3 rounded-full"
                    style={{ width: `${report.metrics.aiDisruptionRisk}%` }}
                  ></div>
                </div>
              </div>
              <p className="text-2xl font-bold text-red-600 min-w-fit">{report.metrics.aiDisruptionRisk}%</p>
            </div>
            <p className="text-gray-600 text-sm mt-2">
              {report.metrics.aiDisruptionRisk < 30 ? '✓ Low risk - Your skills are AI-proof' : report.metrics.aiDisruptionRisk < 60 ? '⚠ Moderate risk - Consider upskilling' : '⚠ High risk - Focus on uniquely human skills'}
            </p>
          </div>
        </div>

        {/* Strengths */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="w-1 h-6 bg-green-600 mr-3 rounded"></span>
              Top Strengths
            </h2>
            <ul className="space-y-3">
              {report.topStrengths.map((strength, idx) => (
                <li key={idx} className="flex items-start gap-3 bg-green-50 p-3 rounded-lg">
                  <span className="text-green-600 font-bold text-lg flex-shrink-0">✓</span>
                  <span className="text-gray-700">{strength}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="w-1 h-6 bg-yellow-600 mr-3 rounded"></span>
              Growth Areas
            </h2>
            <ul className="space-y-3">
              {report.growthAreas.map((area, idx) => (
                <li key={idx} className="flex items-start gap-3 bg-yellow-50 p-3 rounded-lg">
                  <span className="text-yellow-600 font-bold text-lg flex-shrink-0">→</span>
                  <span className="text-gray-700">{area}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Hidden Strengths */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-lg p-8 mb-8 border-2 border-blue-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="w-1 h-6 bg-blue-600 mr-3 rounded"></span>
            Hidden Strengths & Opportunities
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {report.hiddenStrengths.map((strength, idx) => (
              <div key={idx} className="bg-white p-4 rounded-lg border-l-4 border-blue-600">
                <p className="text-gray-700">{strength}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Career Recommendations */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="w-1 h-8 bg-indigo-600 mr-3 rounded"></span>
            Top Career Recommendations
          </h2>

          <div className="space-y-6">
            {report.recommendations.map((rec, idx) => (
              <div key={idx} className="border-2 border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition">
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-semibold text-indigo-100">Career Option {rec.rank}</p>
                      <h3 className="text-2xl font-bold mt-1">{rec.title}</h3>
                      <p className="text-indigo-100 mt-2">{rec.description}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-indigo-100">Confidence</p>
                      <p className="text-3xl font-bold">{rec.confidence}%</p>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-gray-50">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg border-l-4 border-green-500">
                      <p className="text-gray-600 text-sm font-semibold">Year 3 Salary</p>
                      <p className="text-lg font-bold text-green-600 mt-1">{rec.salary.year3}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border-l-4 border-blue-500">
                      <p className="text-gray-600 text-sm font-semibold">Year 5 Salary</p>
                      <p className="text-lg font-bold text-blue-600 mt-1">{rec.salary.year5}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border-l-4 border-purple-500">
                      <p className="text-gray-600 text-sm font-semibold">Year 10 Salary</p>
                      <p className="text-lg font-bold text-purple-600 mt-1">{rec.salary.year10}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <p className="text-gray-700 font-semibold mb-3">Why It Fits</p>
                      <p className="text-gray-600 text-sm mb-4">{rec.whyItFits}</p>

                      <div className="flex gap-2 mb-4">
                        <div className="flex-1 bg-gradient-to-r from-green-100 to-green-200 p-3 rounded-lg">
                          <p className="text-green-700 font-semibold text-sm">Market Demand</p>
                          <p className="text-green-900 font-bold">{rec.demand}</p>
                        </div>
                        <div className="flex-1 bg-gradient-to-r from-red-100 to-red-200 p-3 rounded-lg">
                          <p className="text-red-700 font-semibold text-sm">AI Risk</p>
                          <p className="text-red-900 font-bold">{rec.aiRisk}</p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="mb-4">
                        <p className="text-gray-700 font-semibold mb-2">Required Skills</p>
                        <div className="flex flex-wrap gap-2">
                          {rec.skillsRequired.map((skill, sidx) => (
                            <span key={sidx} className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-sm font-semibold">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-gray-700 font-semibold mb-2">Certifications</p>
                        <div className="flex flex-wrap gap-2">
                          {rec.certifications.map((cert, cidx) => (
                            <span key={cidx} className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm font-semibold">
                              {cert}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Wealth Plan */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="w-1 h-8 bg-yellow-600 mr-3 rounded"></span>
            Wealth Acceleration Plan
          </h2>

          {report.wealthPlan.careers.map((career, idx) => (
            <div key={idx} className="mb-8 p-6 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg border-2 border-yellow-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4">{career.careerTitle}</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="font-semibold text-gray-700 mb-2">Income Streams</p>
                  <ul className="space-y-2">
                    <li className="text-gray-600"><span className="font-semibold">Primary:</span> {career.primaryIncome}</li>
                    {career.secondaryIncome.map((income, sidx) => (
                      <li key={sidx} className="text-gray-600"><span className="font-semibold">Secondary:</span> {income}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <p className="font-semibold text-gray-700 mb-2">Business Opportunities</p>
                  <ul className="space-y-1">
                    {career.businessOpportunities.map((opp, oidx) => (
                      <li key={oidx} className="text-gray-600">• {opp}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-4 rounded-lg">
                  <p className="font-semibold text-gray-700 mb-2">Personal Branding Strategy</p>
                  <p className="text-gray-600 text-sm">{career.personalBranding}</p>
                </div>

                <div className="bg-white p-4 rounded-lg">
                  <p className="font-semibold text-gray-700 mb-2">Investment Strategy</p>
                  <p className="text-gray-600 text-sm">{career.investmentStrategy}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Career Roadmap */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="w-1 h-8 bg-green-600 mr-3 rounded"></span>
            5-Year Career Roadmap
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Year 1 */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border-2 border-blue-300">
              <h3 className="text-lg font-bold text-blue-900 mb-4">Year 1: Foundation</h3>
              <div className="space-y-4">
                <div>
                  <p className="font-semibold text-blue-900 mb-2">Skills to Learn</p>
                  <ul className="space-y-1">
                    {report.careerRoadmap.year1.skills.map((skill, idx) => (
                      <li key={idx} className="text-blue-800 text-sm">• {skill}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-semibold text-blue-900 mb-2">Certifications</p>
                  <ul className="space-y-1">
                    {report.careerRoadmap.year1.certifications.map((cert, idx) => (
                      <li key={idx} className="text-blue-800 text-sm">• {cert}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Year 3 */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border-2 border-purple-300">
              <h3 className="text-lg font-bold text-purple-900 mb-4">Year 3: Growth</h3>
              <div className="space-y-4">
                <div>
                  <p className="font-semibold text-purple-900 mb-2">Milestones</p>
                  <ul className="space-y-1">
                    {report.careerRoadmap.year3.milestones.map((milestone, idx) => (
                      <li key={idx} className="text-purple-800 text-sm">• {milestone}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-semibold text-purple-900 mb-2">Salary Target</p>
                  <p className="text-purple-800 font-bold">{report.careerRoadmap.year3.salaryTarget}</p>
                </div>
              </div>
            </div>

            {/* Year 5 */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border-2 border-green-300">
              <h3 className="text-lg font-bold text-green-900 mb-4">Year 5: Excellence</h3>
              <div className="space-y-4">
                <div>
                  <p className="font-semibold text-green-900 mb-2">Milestones</p>
                  <ul className="space-y-1">
                    {report.careerRoadmap.year5.milestones.map((milestone, idx) => (
                      <li key={idx} className="text-green-800 text-sm">• {milestone}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="font-semibold text-green-900 mb-2">Wealth Target</p>
                  <p className="text-green-800 font-bold">{report.careerRoadmap.year5.wealthTarget}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center mb-8 no-print">
          <button
            onClick={downloadReport}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 px-8 rounded-lg hover:opacity-90 transition"
          >
            Download PDF Report
          </button>
          <button
            onClick={onBackToForm}
            className="bg-white text-gray-800 font-bold py-3 px-8 rounded-lg border-2 border-gray-300 hover:bg-gray-50 transition"
          >
            New Interview
          </button>
        </div>

        <div className="text-center text-gray-600 text-sm">
          <p>© 2024 AI Career Discovery Roundtable | Powered by Advanced Analytics Engine</p>
        </div>
      </div>
    </div>
  );
};
