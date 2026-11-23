# 🎨 VISUAL WORKFLOW DIAGRAMS
## AI Career Discovery System - Architecture & Data Flow

---

## 1️⃣ COMPLETE APPLICATION WORKFLOW

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   USER JOURNEY FLOWCHART                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                        START APPLICATION
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Show Welcome Screen │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
              ┌────▶│ Personal Info Form  │◀────┐
              │     │ ├─ Name (Required)  │     │
              │     │ ├─ DOB (Optional)   │     │
              │     │ ├─ Place (Optional) │     │
              │     │ └─ Time (Optional)  │     │
              │     └─────────────────────┘     │
              │              │                  │
              │ [Invalid]    ▼                  │
              │         [Validation]            │
              │              │                  │
              │          [Valid]                │
              │              │                  │
              └──────────────[Error]────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Show Question 1/30  │
                    │ ┌─────────────────┐ │
                    │ │ Text Input Area │ │
                    │ │ Voice Button    │ │
                    │ │ Previous/Next   │ │
                    │ └─────────────────┘ │
                    └─────────────────────┘
                              │
                    ┌─────────────────────┐
                    │ Answer Question?    │
                    └─────────────────────┘
                         │       │       │
              ┌──────────┘       │       └──────────┐
              ▼                  ▼                   ▼
         [TYPING]          [VOICE INPUT]      [SELECT OPTION]
              │                  │                   │
              ▼                  ▼                   ▼
         ┌────────┐    ┌──────────────┐    ┌──────────────┐
         │ Manual │    │ Speak →      │    │ Click Option │
         │ Type   │    │ Recognize →  │    │              │
         │ Text   │    │ Save Text    │    │ Store Value  │
         └────────┘    └──────────────┘    └──────────────┘
              │                  │                   │
              └──────────────┬───┴───────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ Save Answer         │
                    │ Store in State      │
                    └─────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
    [PREVIOUS] ◀───────────────────────────── [NEXT]
         │                                       │
         ▼                                       ▼
    Back to Q-1                            Show Q+1 or
                                           Report Gen
                                           
                    ... (Questions 2-29) ...
                    
                             │
                             ▼
                    ┌──────────────────────┐
                    │ Question 30 Reached  │
                    │ "Final Thoughts?"    │
                    └──────────────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ [GENERATE REPORT]    │
                    │  Button Enabled ✓    │
                    └──────────────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ ⏳ PROCESSING...     │
                    │ AI Analyzing Data    │
                    │ Computing Metrics    │
                    │ Matching Careers     │
                    │ Generating Report    │
                    └──────────────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │ ✅ REPORT READY      │
                    │ ┌──────────────────┐ │
                    │ │ Beautiful Report │ │
                    │ │ Charts & Graphs  │ │
                    │ │ Recommendations  │ │
                    │ │ Download PDF     │ │
                    │ │ [New Interview]  │ │
                    │ └──────────────────┘ │
                    └──────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
    [DOWNLOAD]                            [NEW INTERVIEW]
         │                                       │
         ▼                                       ▼
    Get PDF File                         Clear All Data
                                              │
                                              ▼
                                         Return to Start
```

---

## 2️⃣ AI PROCESSING ARCHITECTURE

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            AI ANALYSIS ENGINE ARCHITECTURE                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

        ┌────────────────────────────────────────┐
        │     30 User Answers (Input)            │
        │  ├─ Text Answers (Q1, Q2, etc)        │
        │  ├─ Voice Transcriptions (16 Q)       │
        │  ├─ Single Selections (17 Q)          │
        │  └─ Multi-Selections (Q15, Q19)       │
        └────────────────────────────────────────┘
                          │
                          ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃    ANALYSIS ENGINE (analysisEngine.ts)┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │Validate  │   │ Extract  │   │ Normalize│
    │Answers   │   │ Features │   │ Data     │
    └──────────┘   └──────────┘   └──────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
        ┌────────────────────────────────────┐
        │  AI METRICS CALCULATION (11 Total) │
        └────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │PERSONALITY  │  │ APTITUDE    │  │ EMPLOYABLE  │
    │ASSESSMENT   │  │ PROFILE     │  │ SKILLS      │
    │             │  │             │  │             │
    │✓ Intro/Ext  │  │✓ Logical    │  │✓ Learning   │
    │✓ Work Style │  │✓ Creative   │  │✓ Skills     │
    │✓ Flexible   │  │✓ Comm.      │  │✓ Teamwork   │
    │✓ Type       │  │✓ Leadership │  │✓ Index      │
    └─────────────┘  └─────────────┘  └─────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │LEADERSHIP  │   │COMMUNIC.   │   │TECHNICAL   │
    │POTENTIAL   │   │SKILLS      │   │INCLINATION│
    │            │   │            │   │            │
    │Score: 0-100│   │Score: 0-100│   │Score: 0-100│
    └────────────┘   └────────────┘   └────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │CREATIV.    │   │ENTREPRENEUR│   │AI RISK     │
    │SCORE       │   │POTENTIAL   │   │ASSESSMENT  │
    │            │   │            │   │            │
    │Score: 0-100│   │Score: 0-100│   │Risk: 5-95% │
    └────────────┘   └────────────┘   └────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  AI INSIGHTS GENERATION         │
        │  ├─ Pattern Recognition         │
        │  ├─ Strength Identification     │
        │  ├─ Hidden Talent Detection     │
        │  ├─ Growth Area Analysis        │
        │  └─ Recommendation Ranking      │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  CAREER MATCHING ENGINE         │
        │  ├─ Profile Analysis            │
        │  ├─ Career Database Query       │
        │  ├─ Compatibility Scoring       │
        │  ├─ Top 3-5 Matches             │
        │  └─ Detailed Recommendations    │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  REPORT GENERATION              │
        │  ├─ Metrics Dashboard           │
        │  ├─ Chart Generation            │
        │  ├─ Career Options              │
        │  ├─ Wealth Plan                 │
        │  ├─ 5-Year Roadmap              │
        │  └─ PDF Creation                │
        └─────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  BEAUTIFUL REPORT (Output)      │
        │  ┌───────────────────────────┐  │
        │  │ Career Recommendations    │  │
        │  │ Metrics & Visuals         │  │
        │  │ Wealth Acceleration Plan  │  │
        │  │ 5-Year Roadmap            │  │
        │  │ PDF Download Option       │  │
        │  └───────────────────────────┘  │
        └─────────────────────────────────┘
```

---

## 3️⃣ QUESTION FLOW TO METRICS MAPPING

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃         HOW EACH METRIC IS CALCULATED FROM QUESTIONS         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

PERSONALITY TYPE
├─ Q4 (Introvert/Extrovert) ──┐
├─ Q3 (Work Style)            ├─► PERSONALITY TYPE
└─ Q7 (Flexibility)           │   "Visionary", "Analyst",
                              │   "Creator", "Professional"

LOGICAL REASONING (0-100)
├─ Q1 (Coding activities) ────────┐
├─ Q15 select "Logical" ──────────┼─► LOGICAL SCORE
├─ Q16 (Analytical preference) ───┤   Weighted Average
└─ Q17 (Math comfort) ────────────┘

CREATIVE THINKING (0-100)
├─ Q1 (Creative activities) ──────┐
├─ Q16 (Creative preference) ─────┼─► CREATIVE SCORE
├─ Q11 (Learning preference) ─────┤   Weighted Average
└─ Q14 (Innovation comfort) ──────┘

COMMUNICATION SKILLS (0-100)
├─ Q4 (Team preference) ──────────┐
├─ Q5 (Communication type) ───────┼─► COMMUNICATION SCORE
├─ Q15 select "Communication" ────┤   Weighted Average
└─ Q19 select "Communication" ────┘

LEADERSHIP POTENTIAL (0-100)
├─ Q19 select "Leadership" ───────┐
├─ Q4 (Team preference) ──────────┼─► LEADERSHIP SCORE
├─ Q6 (Success motivation) ───────┤   Weighted Average
└─ Q10 (Feedback response) ───────┘

ENTREPRENEURIAL POTENTIAL (0-100)
├─ Q22 (Work style) ──────────────┐
├─ Q23 (Risk appetite) ───────────┼─► ENTREPRENEUR SCORE
└─ Q6 (Independence) ─────────────┘   Weighted Average

TECHNICAL INCLINATION (0-100)
├─ Q3 (Technology focus) ─────────┐
├─ Q12 (Technology industries) ───┼─► TECHNICAL SCORE
└─ Q17 (Math comfort) ────────────┘   Weighted Average

EMPLOYABILITY INDEX (0-100)
├─ Q18 (Learning speed) ──────────┐
├─ Q20 (Professional skills count)─┼─► EMPLOYABILITY SCORE
├─ Q21 (Teamwork style) ──────────┤   Weighted Average
└─ Communication Score ───────────┘

AI DISRUPTION RISK (5-95%)
├─ Q3 (Work type) ────────────────┐
└─ Q12 (Industry) ────────────────┼─► AI RISK %
   (Data=High, People=Low,        │   (0% very safe,
    Creative=Medium)               │    100% high risk)
```

---

## 4️⃣ CAREER RECOMMENDATION ENGINE

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            CAREER MATCHING & RECOMMENDATION FLOW              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

        CANDIDATE PROFILE CREATED
                │
                ▼
        ┌─────────────────────────┐
        │ Profile Summary:        │
        │ ├─ Leadership: 75/100   │
        │ ├─ Communication: 82/100│
        │ ├─ Technical: 65/100    │
        │ ├─ Creativity: 70/100   │
        │ ├─ Entrepreneurial: 60% │
        │ └─ AI Risk: 45%         │
        └─────────────────────────┘
                │
                ▼
        ┌─────────────────────────┐
        │ CAREER DATABASE         │
        │ ├─ Product Manager      │
        │ ├─ Tech Lead            │
        │ ├─ Entrepreneur         │
        │ ├─ Manager              │
        │ ├─ Data Analyst         │
        │ ├─ Software Engineer    │
        │ ├─ UX Designer          │
        │ ├─ Consultant           │
        │ └─ ... (180+ careers)   │
        └─────────────────────────┘
                │
                ▼
        ┌─────────────────────────────────┐
        │ COMPATIBILITY ALGORITHM         │
        │                                 │
        │ For Each Career:                │
        │ ├─ Match Traits                 │
        │ ├─ Weight by Importance         │
        │ ├─ Calculate Score (0-100)      │
        │ └─ Rank by Score                │
        └─────────────────────────────────┘
                │
                ▼
        ┌─────────────────────────────────┐
        │ SCORED CAREERS (Top 10)         │
        │                                 │
        │ Product Manager    95% ⭐⭐⭐   │
        │ Tech Lead          88% ⭐⭐    │
        │ Engineering Mgr    82% ⭐⭐    │
        │ Consultant         75% ⭐      │
        │ Data Analyst       70% ⭐      │
        │ ... (5 more)       ...         │
        └─────────────────────────────────┘
                │
                ▼
        ┌─────────────────────────────────┐
        │ SELECT TOP 3-5                  │
        │                                 │
        │ ✓ Product Manager (95%)         │
        │ ✓ Tech Lead (88%)               │
        │ ✓ Engineering Manager (82%)     │
        └─────────────────────────────────┘
                │
                ▼
        ┌─────────────────────────────────┐
        │ DETAILED RECOMMENDATIONS        │
        │                                 │
        │ For Each Top Career:            │
        │ ├─ Why It Fits                  │
        │ ├─ Salary Projection            │
        │ ├─ Market Demand                │
        │ ├─ AI Risk Assessment           │
        │ ├─ Required Skills              │
        │ ├─ Certifications               │
        │ └─ Growth Potential             │
        └─────────────────────────────────┘
                │
                ▼
        FINAL RECOMMENDATIONS
        (Displayed in Report)
```

---

## 5️⃣ VOICE INPUT WORKFLOW

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          VOICE-TO-TEXT FEATURE (16 Questions)                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

USER CLICKS "ADD VOICE INPUT"
            │
            ▼
    ┌──────────────────────┐
    │ Browser Requests     │
    │ Microphone Permission│
    └──────────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
[ALLOW]        [DENY]
    │               │
    ▼               ▼
✓ Ready      Error: Permission
             Denied
    │
    ▼
USER CLICKS "START VOICE INPUT"
    │
    ▼
┌──────────────────────────┐
│ Recording Starts         │
│ 🎤 Listening...         │
│ (Pulsing red button)     │
└──────────────────────────┘
    │
    ▼
┌──────────────────────────┐
│ USER SPEAKS              │
│ "I enjoy problem solving"│
│                          │
│ REAL-TIME TRANSCRIPT:    │
│ "I enjoy problem..."     │
│ (showing interim)        │
└──────────────────────────┘
    │
    ▼
┌──────────────────────────┐
│ WEB SPEECH API           │
│ Recognizes Speech        │
│ (Local browser feature)  │
└──────────────────────────┘
    │
    ├─────┬─────┬─────┐
    ▼     ▼     ▼     ▼
[Final] [Interim] [Error] [End]
    │       │        │      │
    ▼       ▼        ▼      ▼
Save  Show Live Error Show Final
Text  Preview Message Text
    │       │        │      │
    └───────┴────────┘      │
        │                   │
        ▼                   ▼
    Updated          Stopped
    Transcript       (Ready)
    │               │
    └───────┬───────┘
            │
            ▼
    ┌──────────────────────┐
    │ TRANSCRIPT READY     │
    │ ✓ "I enjoy solving   │
    │   complex problems"  │
    │                      │
    │ [CLEAR] Button       │
    └──────────────────────┘
            │
    ┌───────┴────────┐
    ▼                ▼
[CLEAR]          [NEXT]
    │                │
    ▼                ▼
Clear All        Save to
& Retry          Answer
    │                │
    └────────┬───────┘
             │
             ▼
      ANSWER SAVED
```

---

## 6️⃣ MULTI-SELECT FEATURE (Q15 & Q19)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        MULTI-SELECT QUESTIONS (Q15 & Q19)                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Q15: "Select your key strengths"
┌─────────────────────────────────┐
│ ☐ Logical Reasoning             │
│ ☐ Creative Thinking             │
│ ☐ Communication Skills          │
│ ☐ Leadership Abilities          │
│                                 │
│ ✓ 0 option(s) selected          │
└─────────────────────────────────┘

USER CLICKS CHECKBOX:
        │
        ▼
    [☑ Logical]   ◀─── Checked
        │
        ▼
    Store: "Logical"
        │
        ▼
    Counter: "✓ 1 option(s) selected"

USER CLICKS ANOTHER:
        │
        ▼
    [☑ Leadership]   ◀─── Checked
        │
        ▼
    Append: "Logical|||Leadership"
    (Triple pipe delimiter)
        │
        ▼
    Counter: "✓ 2 option(s) selected"

USER CAN DESELECT:
        │
        ▼
    [☐ Logical]   ◀─── Unchecked
        │
        ▼
    Remove: "Leadership"
        │
        ▼
    Counter: "✓ 1 option(s) selected"

WHEN SUBMITTED:
        │
        ▼
    ┌────────────────────────────┐
    │ Data Format:               │
    │ "Logical|||Leadership"     │
    │                            │
    │ AI Processing:             │
    │ Split by "|||"             │
    │ ["Logical", "Leadership"]  │
    │                            │
    │ Used in:                   │
    │ ├─ Aptitude calculation    │
    │ ├─ Leadership scoring      │
    │ └─ Recommendations         │
    └────────────────────────────┘
```

---

## 7️⃣ REPORT GENERATION TIMELINE

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              REPORT GENERATION TIMELINE                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

T=0ms   User Clicks "Generate Report"
        │
        ├─► Show Loading Screen
        └─► "⏳ Processing your data..."
        
T=100ms All 30 Answers Validated
        │
        └─► Passed: 30 ✓
        
T=200ms Feature Extraction
        │
        ├─► Extract 40+ features
        ├─► Normalize values
        └─► Check patterns
        
T=300ms AI Metrics Calculation
        │
        ├─► Logical: 80/100
        ├─► Creative: 75/100
        ├─► Leadership: 70/100
        ├─► Communication: 82/100
        ├─► Technical: 85/100
        ├─► Entrepreneurial: 65/100
        ├─► AI Risk: 55%
        └─► ... (14 more)
        
T=500ms Career Matching
        │
        ├─► Match to careers
        ├─► Score each: 0-100
        ├─► Rank top 200
        ├─► Select top 3-5
        └─► Calculate details
        
T=1000ms Generate Insights
        │
        ├─► Identify strengths
        ├─► Find hidden talents
        ├─► Assess growth areas
        ├─► Create recommendations
        └─► Generate descriptions
        
T=1500ms Report HTML Creation
        │
        ├─► Build React components
        ├─► Apply styling
        ├─► Add animations
        └─► Render to DOM
        
T=2000ms Chart Generation
        │
        ├─► Recharts rendering
        ├─► Radar chart
        ├─► Bar charts
        ├─► Scatter plots
        └─► Animations
        
T=3000ms PDF Preparation
        │
        ├─► Convert DOM to Canvas
        ├─► Generate PDF
        ├─► Embed fonts
        └─► Prepare download
        
T=4500ms Display Report & PDF Ready
        │
        └─► Beautiful Report Shown ✓
            PDF Ready for Download ✓
            
TOTAL TIME: ~4.5 seconds ⚡
```

---

## 8️⃣ DATA FLOW: FROM INPUT TO OUTPUT

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           COMPLETE DATA TRANSFORMATION FLOW                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

RAW DATA INPUT
├─ Typed Text: "I love coding and designing products"
├─ Voice Transcription: "I prefer working in teams"
├─ Single Select: "Technology"
├─ Multi-Select: "Logical|||Leadership"
└─ Personal Info: Name, DOB, etc.

                      │
                      ▼
         ┌────────────────────────┐
         │ PARSE & NORMALIZE      │
         ├────────────────────────┤
         │ ├─ Extract answers     │
         │ ├─ Split multi-select  │
         │ ├─ Trim whitespace     │
         │ └─ Validate format     │
         └────────────────────────┘

                      │
                      ▼
         ┌────────────────────────┐
         │ FEATURE EXTRACTION     │
         ├────────────────────────┤
         │ ├─ Identify keywords   │
         │ ├─ Extract traits      │
         │ ├─ Recognize patterns  │
         │ └─ Count occurrences   │
         └────────────────────────┘

                      │
                      ▼
         ┌────────────────────────┐
         │ SCORING ALGORITHMS     │
         ├────────────────────────┤
         │ ├─ Apply weights       │
         │ ├─ Calculate scores    │
         │ ├─ Normalize 0-100     │
         │ └─ Create matrices     │
         └────────────────────────┘

                      │
                      ▼
         ┌────────────────────────┐
         │ INSIGHTS GENERATION    │
         ├────────────────────────┤
         │ ├─ Find patterns       │
         │ ├─ Identify strengths  │
         │ ├─ Detect weaknesses   │
         │ └─ Predict outcomes    │
         └────────────────────────┘

                      │
                      ▼
         ┌────────────────────────┐
         │ CAREER MATCHING        │
         ├────────────────────────┤
         │ ├─ Query career DB     │
         │ ├─ Calculate fit %     │
         │ ├─ Rank matches        │
         │ └─ Get details         │
         └────────────────────────┘

                      │
                      ▼
         ┌────────────────────────┐
         │ REPORT COMPOSITION     │
         ├────────────────────────┤
         │ ├─ Metrics dashboard   │
         │ ├─ Generate charts     │
         │ ├─ Write descriptions  │
         │ ├─ Create roadmap      │
         │ └─ Format PDF          │
         └────────────────────────┘

                      │
                      ▼
OUTPUT: BEAUTIFUL REPORT
├─ Visual Dashboard (Charts, Graphs)
├─ Career Recommendations (Top 3-5)
├─ Wealth Acceleration Plan
├─ 5-Year Career Roadmap
├─ Personalized Insights
└─ PDF Download Ready
```

---

## 9️⃣ KEY AI ALGORITHMS USED

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            AI ALGORITHMS & TECHNIQUES APPLIED                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

1. WEIGHTED SCORING ALGORITHM
   ├─ Formula: Score = Σ(Answer Value × Weight) / Σ(Weights)
   ├─ Used For: All 11 metrics
   ├─ Example: Leadership = (Q19×0.5 + Q4×0.3 + Q6×0.2)
   └─ Result: 0-100 normalized score

2. PATTERN RECOGNITION
   ├─ Analyze: 30 answers for consistency
   ├─ Identify: Personality type patterns
   ├─ Example: High Q1 + Q14 + Q16 = Creative
   └─ Result: Personality archetype label

3. CORRELATION ANALYSIS
   ├─ Correlate: Answers to outcomes
   ├─ Find: Relationships between questions
   ├─ Example: Q22 + Q23 ➜ Entrepreneurial score
   └─ Result: Composite metric calculation

4. DECISION TREE LOGIC
   ├─ IF Q22 = "Own projects" THEN +50 points
   ├─ IF Q23 = "High risk" THEN +20 points
   ├─ Nested conditions for complex scoring
   └─ Result: Multi-level decision rules

5. SIMILARITY MATCHING (Recommendation Engine)
   ├─ Algorithm: Cosine Similarity
   ├─ Compare: Candidate Profile vs Career Profiles
   ├─ Calculate: Dot product of feature vectors
   ├─ Formula: Similarity = (A·B) / (|A||B|)
   └─ Result: 0-100% match score per career

6. RANKING & SORTING
   ├─ Input: 180+ careers with match scores
   ├─ Sort: By match percentage (descending)
   ├─ Select: Top 3-5 recommendations
   └─ Result: Prioritized career suggestions

7. PREDICTION MODELING
   ├─ Input: Career choice + metrics
   ├─ Predict: Salary ranges (3, 5, 10 year)
   ├─ Model: Historical salary data
   └─ Result: Income projections

8. RISK ASSESSMENT ALGORITHM
   ├─ Input: Work type (Q3) + Industry (Q12)
   ├─ Calculate: AI automation risk
   ├─ Formula: Risk = Base(WorkType) + Adjustment(Industry)
   ├─ Range: 5% (very safe) to 95% (high risk)
   └─ Result: AI disruption percentage

9. TEXT NORMALIZATION
   ├─ Process: Lowercase all text
   ├─ Remove: Extra whitespace
   ├─ Split: Multi-select by "|||"
   ├─ Validate: Against allowed values
   └─ Result: Standardized data format

10. FEATURE ENGINEERING
    ├─ Extract: Keywords from text answers
    ├─ Convert: Categorical to numerical
    ├─ Combine: Multiple inputs into features
    ├─ Scale: To 0-100 or 0-1 range
    └─ Result: Machine-readable features
```

---

**For detailed code implementation, see:**
- [AI_WORKFLOW_GUIDE.md](AI_WORKFLOW_GUIDE.md) - Detailed explanation
- [analysisEngine.ts](c:\Users\rahul.mishra\Desktop\hackthon\src\services\analysisEngine.ts) - Source code
