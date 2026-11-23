# AI Career Discovery Roundtable Interview

A comprehensive web application that conducts an AI-powered career discovery interview based on a panel of expert professionals and generates a detailed, personalized career recommendation report.

## Features

✨ **30 Comprehensive Questions**
- Section 1: Self-Awareness & Personality (8 questions)
- Section 2: Interests & Passion (6 questions)
- Section 3: Aptitude & Strengths (6 questions)
- Section 4: Work Style & Lifestyle (5 questions)
- Section 5: Future Goals (5 questions)

🎤 **Voice-to-Text Input** (Optional)
- For text questions, candidates can click "Add Voice Input" to speak their answers
- Browser-based speech recognition using Web Speech API
- Real-time transcription as you speak
- Perfect for hands-free input or long responses
- Supported on Chrome, Edge, Firefox, and Safari

☑️ **Multi-Select Answers** (Where Applicable)
- Select one or more options for certain questions
- Visual checkboxes for easy selection
- Option counter showing how many items are selected
- Perfect for questions with multiple valid answers

📊 **Advanced Analysis Engine**
- Personality Type Analysis
- Aptitude Profile Assessment (Logic, Creativity, Communication, Leadership)
- Learning Style Evaluation
- Leadership Potential Scoring
- Communication Skills Assessment
- Entrepreneurial Potential Analysis
- Creativity Score Calculation
- Technical Inclination Measurement
- Employability Index
- AI Disruption Risk Assessment

🎯 **Career Recommendations**
- Top 3 personalized career options
- Confidence scores for each recommendation
- Why each career fits your profile
- Salary projections (Year 3, 5, and 10)
- Market demand outlook
- AI disruption risk analysis
- Required skills and certifications
- Global employment opportunities

💼 **Wealth Acceleration Plan**
- Primary income strategies
- Secondary income opportunities
- Business venture recommendations
- Personal branding roadmap
- Investment strategies

🗺️ **5-Year Career Roadmap**
- Year 1: Foundation building
  - Skills to acquire
  - Certifications to pursue
  - Projects to complete
- Year 3: Growth phase
  - Career milestones
  - Salary targets
- Year 5: Excellence phase
  - Leadership milestones
  - Wealth targets

📈 **Beautiful Visualizations**
- Interactive radar charts for aptitude profiles
- Bar charts for skills assessment
- Progress tracking dashboards
- Metric cards with visual indicators
- Risk assessment gauges
- Career comparison analytics

📄 **PDF Report Generation**
- Download comprehensive career report as PDF
- Professional formatting
- All metrics and recommendations included

🔄 **Multi-Candidate Support**
- Reset button for multiple candidates
- Session-based data management
- Clean workflow between interviews

## Tech Stack

- **Frontend Framework**: React 18.2
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.3
- **Charts & Visualization**: Recharts
- **PDF Generation**: jsPDF
- **Screenshot Capture**: html2canvas
- **Build Tool**: Vite 5.0
- **Development Server**: Built-in Vite server

## Installation

1. Clone or extract the project
2. Navigate to the project directory:
```bash
cd hackthon
```

3. Install dependencies:
```bash
npm install
```

## Running the Application

**Development Mode:**
```bash
npm run dev
```

The application will automatically open in your browser at `http://localhost:5173`

**Build for Production:**
```bash
npm run build
```

**Preview Production Build:**
```bash
npm run preview
```

## Project Structure

```
hackthon/
├── src/
│   ├── components/
│   │   ├── QuestionnaireForm.tsx    # Interactive question form with voice & multi-select
│   │   ├── VoiceRecorder.tsx         # Speech-to-text component
│   │   └── ReportDisplay.tsx         # Beautiful report visualization
│   ├── services/
│   │   └── analysisEngine.ts        # AI analysis and recommendations
│   ├── types.ts                      # TypeScript interfaces
│   ├── App.tsx                       # Main application component
│   ├── App.css                       # Application styles
│   ├── index.css                     # Tailwind CSS imports
│   └── main.tsx                      # Application entry point
├── index.html                        # HTML template
├── vite.config.ts                    # Vite configuration
├── tailwind.config.js                # Tailwind CSS configuration
├── postcss.config.js                 # PostCSS configuration
├── tsconfig.json                     # TypeScript configuration
├── package.json                      # Project dependencies
└── README.md                         # This file
```

## How to Use

1. **Start Interview**: Click "Start Interview" button
2. **Enter Personal Information**: Provide your name and optional birth details
3. **Answer Questions**: Go through all 30 questions, one by one
   - **Text questions**: Type your response or click "Add Voice Input" to speak
   - **Multiple choice questions**: Click to select a single option
   - **Multi-select questions**: Click checkboxes to select one or more options
   - **Voice input**: When enabled, click the 🎤 button, start speaking, and your words will be transcribed
4. **Review Progress**: Monitor your progress with the progress bar
5. **Generate Report**: Submit your answers to generate your personalized report
6. **Review Analysis**: Explore your personality profile, strengths, and recommendations
7. **Download Report**: Save your comprehensive career report as PDF
8. **New Interview**: Click "New Interview" to help another candidate

### Voice Input Instructions
- Click "Add Voice Input" button on text questions (marked with 🎤)
- Click "Start Voice Input" or the microphone button
- Speak clearly - the app will transcribe your words in real-time
- Click "Stop Recording" when you're done speaking
- Your transcript appears in the preview box below
- You can continue typing or speaking to add more text
- Click "Clear" to remove the voice transcript if needed

### Multi-Select Instructions
- Some questions allow selecting multiple options
- Look for the text "Select one or more options:"
- Click checkboxes next to each option you want to select
- The counter shows how many options you've selected (e.g., "✓ 2 option(s) selected")
- Continue to the next question or click Previous

## Multi-Select Questions

The following questions support selecting multiple options:

- **Q15**: "Are you stronger in logical reasoning, creativity, communication, or leadership?"
  - You can select multiple strengths (e.g., both Communication and Leadership)

- **Q19**: "Do you enjoy building things, solving problems, teaching others, or leading teams?"
  - Select all activities you enjoy (e.g., Teaching and Leadership)

This allows for more nuanced responses that reflect multiple interests and strengths.

## Voice-Enabled Questions

The following questions support voice-to-text input:

- Q1, Q2, Q5, Q6, Q8 (Section 1)
- Q9, Q10, Q11, Q12, Q13, Q14 (Section 2)
- Q20 (Section 3)
- Q25 (Section 4)
- Q27, Q28, Q29, Q30 (Section 5)

All other text fields have voice input disabled for faster selection-based questions.

## Key Components

### QuestionnaireForm Component
- Interactive question flow (1 question per screen)
- Personal information collection
- Progress tracking
- Previous/Next navigation
- Answer persistence
- Reset functionality
- Voice input toggle for text questions
- Multi-select checkbox support

### VoiceRecorder Component
- Real-time speech-to-text conversion
- Browser-based Web Speech API
- Visual recording status indicator
- Transcript preview
- Clear button to reset transcript
- Error handling for unsupported browsers
- Support for continuous speech input

### ReportDisplay Component
- Multi-section report layout
- Personality & profile section
- Key metrics dashboard
- Strengths & growth areas
- Career recommendations (Top 3)
- Wealth acceleration plan
- 5-year career roadmap
- PDF download capability
- Responsive design for all devices

### AnalysisEngine Service
- Personality type analysis
- Aptitude profile calculation
- Learning style assessment
- Leadership potential scoring
- Career recommendation generation
- Strengths identification
- Growth area analysis

## Analysis Methodology

The application analyzes responses using a sophisticated algorithm that considers:

1. **Personality Indicators**: Introversion/Extroversion, work preferences, environmental fit
2. **Aptitude Assessment**: Logical reasoning, creativity, communication, leadership abilities
3. **Learning Patterns**: Speed of learning, learning style preferences
4. **Career Motivation**: Intrinsic interests, passion areas, problem-solving preferences
5. **Risk Profile**: Risk appetite, security vs. growth preference
6. **Market Trends**: AI disruption risks, industry demand projections
7. **Salary Expectations**: Income goals and financial aspirations
8. **Leadership Potential**: Team management abilities and influence capacity

## Career Recommendations

The system recommends careers based on matching:
- Your personality profile with career requirements
- Your aptitudes with skill demands
- Your interests with industry opportunities
- Your learning style with training requirements
- Your risk appetite with career paths
- Your financial goals with earning potential

## Report Metrics Explained

- **Leadership Potential (0-100%)**: Ability to lead teams and manage people
- **Communication Skills (0-100%)**: Effectiveness in conveying ideas
- **Entrepreneurial Potential (0-100%)**: Likelihood of success as a business owner
- **Creativity Score (0-100%)**: Innovation and creative problem-solving ability
- **Technical Inclination (0-100%)**: Comfort with technology and technical roles
- **Employability (0-100%)**: Overall market demand for your skills
- **AI Disruption Risk (0-100%)**: Risk that AI will replace your role (lower is better)

## Features in Detail

### Adaptive Career Recommendations
The system generates 3-5 career recommendations based on your unique profile. Each recommendation includes:
- Why the career fits you
- Realistic salary projections
- Required skills and certifications
- Market demand outlook
- AI disruption risk level

### Wealth Acceleration Plan
Customized strategies to maximize income including:
- Multiple income streams
- Business opportunities
- Consulting and freelancing options
- Personal branding strategies
- Investment recommendations

### Career Roadmap
Step-by-step 5-year plan including:
- Year 1: Building foundational skills
- Year 3: Growth and advancement milestones
- Year 5: Leadership and wealth targets

## Browser Support

- Chrome (latest) - Full voice support
- Firefox (latest) - Full voice support
- Safari (latest) - Full voice support
- Edge (latest) - Full voice support
- Mobile browsers - Works on iOS Safari and Android Chrome with voice support

### Voice Input Availability
- Desktop browsers with microphone access
- Mobile devices with microphone (Android and iOS)
- May require HTTPS in production (HTTP OK for localhost)

## Performance

- Optimized for fast loading (< 2 seconds)
- Responsive design for mobile and desktop
- Smooth animations and transitions
- Efficient data processing

## Future Enhancements

- Integration with industry databases for real-time salary data
- Machine learning model for improved recommendations
- Numerology and astrology analysis integration
- Video testimonials from recommended careers
- Skill gap analysis with learning resources
- Networking with professionals in recommended careers
- Real-time job market data integration

## License

This project is proprietary and confidential.

## Support

For issues or questions, please contact the development team.

---

**Made with ❤️ for career discovery and professional growth**
