// Types and interfaces for the career discovery system
export interface Answer {
  questionId: string;
  text: string;
  section: string;
}

export interface CandidateData {
  personalInfo: {
    name: string;
    dateOfBirth?: string;
    placeOfBirth?: string;
    birthTime?: string;
  };
  answers: Answer[];
  timestamp: string;
}

export interface AnalysisMetrics {
  personalityType: string;
  personalityScore: number;
  aptitudeProfile: {
    logical: number;
    creative: number;
    communication: number;
    leadership: number;
  };
  learningStyle: string;
  leadershipPotential: number;
  communicationSkills: number;
  entrepreneurialPotential: number;
  creativityScore: number;
  technicalInclination: number;
  employability: number;
  aiDisruptionRisk: number;
}

export interface CareerRecommendation {
  rank: number;
  title: string;
  description: string;
  whyItFits: string;
  salary: {
    year3: string;
    year5: string;
    year10: string;
  };
  demand: string;
  aiRisk: string;
  skillsRequired: string[];
  certifications: string[];
  confidence: number;
}

export interface Report {
  candidateName: string;
  generatedAt: string;
  metrics: AnalysisMetrics;
  topStrengths: string[];
  hiddenStrengths: string[];
  growthAreas: string[];
  recommendations: CareerRecommendation[];
  wealthPlan: WealthPlan;
  careerRoadmap: CareerRoadmap;
}

export interface WealthPlan {
  careers: {
    careerTitle: string;
    primaryIncome: string;
    secondaryIncome: string[];
    businessOpportunities: string[];
    personalBranding: string;
    investmentStrategy: string;
  }[];
}

export interface CareerRoadmap {
  year1: {
    skills: string[];
    certifications: string[];
    projects: string[];
  };
  year3: {
    milestones: string[];
    salaryTarget: string;
  };
  year5: {
    milestones: string[];
    wealthTarget: string;
  };
}

export const QUESTIONS = [
  // Section 1: Self-Awareness & Personality
  {
    id: 'q1',
    section: 'Self-Awareness & Personality',
    text: 'What activities make you lose track of time?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q2',
    section: 'Self-Awareness & Personality',
    text: 'If money was not a concern, what would you spend your life doing?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q3',
    section: 'Self-Awareness & Personality',
    text: 'Do you prefer working with people, technology, ideas, or data?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['People', 'Technology', 'Ideas', 'Data', 'Mix of all']
  },
  {
    id: 'q4',
    section: 'Self-Awareness & Personality',
    text: 'Are you more introverted, extroverted, or ambivert?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Introverted', 'Extroverted', 'Ambivert']
  },
  {
    id: 'q5',
    section: 'Self-Awareness & Personality',
    text: 'What are the three qualities people appreciate most about you?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q6',
    section: 'Self-Awareness & Personality',
    text: 'What kind of problems do you enjoy solving?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q7',
    section: 'Self-Awareness & Personality',
    text: 'Do you prefer structured environments or flexible environments?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Structured', 'Flexible', 'Mix of both']
  },
  {
    id: 'q8',
    section: 'Self-Awareness & Personality',
    text: 'What achievement are you most proud of and why?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  // Section 2: Interests & Passion
  {
    id: 'q9',
    section: 'Interests & Passion',
    text: 'Which school or college subjects excite you the most?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q10',
    section: 'Interests & Passion',
    text: 'Which topics do you watch videos, read articles, or research about voluntarily?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q11',
    section: 'Interests & Passion',
    text: 'If you could master one skill instantly, what would it be?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q12',
    section: 'Interests & Passion',
    text: 'Which industries fascinate you most?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q13',
    section: 'Interests & Passion',
    text: 'What type of work sounds most exciting to you?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q14',
    section: 'Interests & Passion',
    text: 'What would your dream workday look like?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  // Section 3: Aptitude & Strengths
  {
    id: 'q15',
    section: 'Aptitude & Strengths',
    text: 'Are you stronger in logical reasoning, creativity, communication, or leadership?',
    type: 'select',
    multiSelect: true,
    voiceEnabled: false,
    options: ['Logical Reasoning', 'Creativity', 'Communication', 'Leadership']
  },
  {
    id: 'q16',
    section: 'Aptitude & Strengths',
    text: 'Do you enjoy analytical tasks or creative tasks more?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Analytical', 'Creative', 'Equal']
  },
  {
    id: 'q17',
    section: 'Aptitude & Strengths',
    text: 'How comfortable are you with mathematics and numbers?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Very Comfortable', 'Comfortable', 'Moderate', 'Uncomfortable']
  },
  {
    id: 'q18',
    section: 'Aptitude & Strengths',
    text: 'How quickly do you learn new concepts?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Very Quick', 'Quick', 'Average', 'Slow but Thorough']
  },
  {
    id: 'q19',
    section: 'Aptitude & Strengths',
    text: 'Do you enjoy building things, solving problems, teaching others, or leading teams?',
    type: 'select',
    multiSelect: true,
    voiceEnabled: false,
    options: ['Building', 'Problem Solving', 'Teaching', 'Leadership']
  },
  {
    id: 'q20',
    section: 'Aptitude & Strengths',
    text: 'What skills do you believe come naturally to you?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  // Section 4: Work Style & Lifestyle
  {
    id: 'q21',
    section: 'Work Style & Lifestyle',
    text: 'Do you want job security or high earning potential?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Job Security', 'High Earning', 'Balance']
  },
  {
    id: 'q22',
    section: 'Work Style & Lifestyle',
    text: 'Would you rather work for a company, start a business, or freelance?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Company', 'Business', 'Freelance', 'Hybrid']
  },
  {
    id: 'q23',
    section: 'Work Style & Lifestyle',
    text: 'How much risk are you comfortable taking?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Low Risk', 'Moderate Risk', 'High Risk']
  },
  {
    id: 'q24',
    section: 'Work Style & Lifestyle',
    text: 'Do you prefer remote work, hybrid work, or office work?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['Remote', 'Hybrid', 'Office']
  },
  {
    id: 'q25',
    section: 'Work Style & Lifestyle',
    text: 'What kind of lifestyle do you want at age 35?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  // Section 5: Future Goals
  {
    id: 'q26',
    section: 'Future Goals',
    text: 'What annual income would make you financially satisfied?',
    type: 'select',
    multiSelect: false,
    voiceEnabled: false,
    options: ['$30,000-$50,000', '$50,000-$75,000', '$75,000-$100,000', '$100,000-$150,000', '$150,000+']
  },
  {
    id: 'q27',
    section: 'Future Goals',
    text: 'What impact would you like to create in society?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q28',
    section: 'Future Goals',
    text: 'Which successful people do you admire and why?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q29',
    section: 'Future Goals',
    text: 'Where do you see yourself in the next 10 years?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  },
  {
    id: 'q30',
    section: 'Future Goals',
    text: 'If you had to choose today, what career options are you already considering?',
    type: 'textarea',
    multiSelect: false,
    voiceEnabled: true
  }
];
