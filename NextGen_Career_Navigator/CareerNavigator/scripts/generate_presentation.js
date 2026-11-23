const fs = require('fs');
const path = require('path');
const PPTX = require('pptxgenjs');

function readFileSafe(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch (e) {
    return '';
  }
}

function extractSummary(readme) {
  const lines = readme.split('\n');
  const title = lines[0] ? lines[0].replace(/^#\s*/, '') : 'Project Presentation';

  const featuresIndex = readme.indexOf('## Features');
  const techIndex = readme.indexOf('## Tech Stack');
  const features = featuresIndex !== -1 && techIndex !== -1 ? readme.slice(featuresIndex, techIndex) : '';

  return { title, features };
}

function main() {
  const root = path.resolve(__dirname, '..');
  const readmePath = path.join(root, 'README.md');
  const readme = readFileSafe(readmePath);
  const pkg = JSON.parse(readFileSafe(path.join(root, 'package.json')) || '{}');

  const srcFiles = [
    path.join(root, 'src', 'App.tsx'),
    path.join(root, 'src', 'components', 'QuestionnaireForm.tsx'),
    path.join(root, 'src', 'components', 'ReportDisplay.tsx'),
    path.join(root, 'src', 'services', 'analysisEngine.ts'),
  ];

  const srcContents = srcFiles.map(p => ({ file: path.basename(p), content: readFileSafe(p) }));

  const summary = extractSummary(readme);

  const pptx = new PPTX();
  pptx.author = pkg.author || 'AI Career Discovery Team';
  pptx.company = pkg.name || 'Career Discovery Roundtable';

  // Title slide
  let slide = pptx.addSlide();
  slide.addText(summary.title, { x: 0.5, y: 1.0, fontSize: 36, bold: true });
  slide.addText('AI-Powered Career Discovery', { x: 0.5, y: 2.0, fontSize: 20, color: '666666' });
  slide.addText(`Generated: ${new Date().toLocaleDateString()}`, { x: 0.5, y: 3.2, fontSize: 12, color: '999999' });

  // Features slide
  slide = pptx.addSlide();
  slide.addText('Key Features', { x: 0.5, y: 0.3, fontSize: 28, bold: true });

  const featuresLines = summary.features.split('\n').filter(l => l.trim().length > 0).slice(0, 14).map(l => l.replace(/^[-#\s]*/g, ''));
  slide.addText(featuresLines, { x: 0.5, y: 1.0, fontSize: 18, bullet: true, color: '333333' });

  // Architecture & Components
  slide = pptx.addSlide();
  slide.addText('Architecture & Key Components', { x: 0.5, y: 0.3, fontSize: 26, bold: true });
  slide.addText([
    'Frontend: React + TypeScript + Tailwind',
    'Visualization: Recharts',
    'PDF: jsPDF + html2canvas',
    'Core: QuestionnaireForm, VoiceRecorder, ReportDisplay, AnalysisEngine'
  ], { x: 0.5, y: 1.0, fontSize: 18, bullet: true });

  // Analysis Engine
  slide = pptx.addSlide();
  slide.addText('Analysis Engine', { x: 0.5, y: 0.3, fontSize: 26, bold: true });
  slide.addText([
    'Personality & Aptitude analysis',
    'Leadership, Communication, Creativity scoring',
    'Career recommendation generation',
    'Wealth plan & 5-year roadmap generation'
  ], { x: 0.5, y: 1.0, fontSize: 18, bullet: true });

  // Sample Code Snippets
  slide = pptx.addSlide();
  slide.addText('Sample Snippets', { x: 0.5, y: 0.3, fontSize: 26, bold: true });
  const snippets = srcContents.map(s => `// ${s.file}\n${s.content.split('\n').slice(0, 12).join('\n')}`);
  slide.addText(snippets.slice(0,3), { x: 0.5, y: 1.0, fontSize: 12 });

  // How to run
  slide = pptx.addSlide();
  slide.addText('How to Run', { x: 0.5, y: 0.3, fontSize: 26, bold: true });
  slide.addText([
    'npm install',
    'npm run dev',
    'Open http://localhost:5173'
  ], { x: 0.5, y: 1.0, fontSize: 18, bullet: true });

  // Contact / Next Steps
  slide = pptx.addSlide();
  slide.addText('Next Steps', { x: 0.5, y: 0.3, fontSize: 26, bold: true });
  slide.addText([
    'Add ML model for improved recommendations',
    'Integrate real-time salary data',
    'Add user accounts and persistence',
    'Improve accessibility and mobile UX'
  ], { x: 0.5, y: 1.0, fontSize: 18, bullet: true });

  const outPath = path.join(root, 'presentation_generated.pptx');
  pptx.writeFile(outPath).then(() => {
    console.log('Presentation generated at', outPath);
  }).catch(err => {
    console.error('Error writing PPTX:', err);
    process.exit(1);
  });
}

main();
