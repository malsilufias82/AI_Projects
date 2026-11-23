import { Answer, AnalysisMetrics, CareerRecommendation, Report, WealthPlan, CareerRoadmap } from './types';

export class AnalysisEngine {
  private answers: Answer[];

  constructor(answers: Answer[]) {
    this.answers = answers;
  }

  analyze(): AnalysisMetrics {
    return {
      personalityType: this.analyzePersonalityType(),
      personalityScore: this.calculatePersonalityScore(),
      aptitudeProfile: this.analyzeAptitudeProfile(),
      learningStyle: this.analyzeLearningStyle(),
      leadershipPotential: this.calculateLeadershipPotential(),
      communicationSkills: this.calculateCommunicationSkills(),
      entrepreneurialPotential: this.calculateEntrepreneurialPotential(),
      creativityScore: this.calculateCreativityScore(),
      technicalInclination: this.calculateTechnicalInclination(),
      employability: this.calculateEmployability(),
      aiDisruptionRisk: this.calculateAIDisruptionRisk(),
    };
  }

  private analyzePersonalityType(): string {
    const q4 = this.getAnswerText('q4');
    const q3 = this.getAnswerText('q3');
    const q7 = this.getAnswerText('q7');

    let type = '';
    if (q4) type = q4;
    if (q3) type += ` (${q3} focused)`;
    if (q7) type += ` - ${q7} preference`;

    return type || 'Analytical Professional';
  }

  private calculatePersonalityScore(): number {
    const keyAnswers = ['q2', 'q5', 'q6', 'q8'];
    const answeredCount = keyAnswers.filter(id => this.findAnswer(id)).length;
    return Math.round((answeredCount / keyAnswers.length) * 100);
  }

  private analyzeAptitudeProfile() {
    const profile = {
      logical: 50,
      creative: 50,
      communication: 50,
      leadership: 50,
    };

    const q15Array = this.getAnswerArray('q15');
    const q16 = this.getAnswerText('q16');
    const q19Array = this.getAnswerArray('q19');
    const q6 = this.getAnswerText('q6');

    // Handle multi-select q15
    if (q15Array.includes('Logical Reasoning')) profile.logical = 80;
    if (q15Array.includes('Creativity')) profile.creative = 80;
    if (q15Array.includes('Communication')) profile.communication = 80;
    if (q15Array.includes('Leadership')) profile.leadership = 80;

    if (q16.includes('Analytical')) profile.logical = Math.max(profile.logical, 75);
    if (q16.includes('Creative')) profile.creative = Math.max(profile.creative, 75);

    // Handle multi-select q19
    if (q19Array.includes('Leadership')) profile.leadership = 85;
    if (q19Array.includes('Teaching')) profile.communication = 85;
    if (q19Array.includes('Building')) profile.logical = 80;
    if (q19Array.includes('Problem Solving')) profile.logical = 80;

    const q1 = this.getAnswerText('q1');
    if (q1.toLowerCase().includes('creative')) profile.creative = 85;
    if (q1.toLowerCase().includes('code')) profile.logical = 85;
    if (q1.toLowerCase().includes('people')) profile.communication = 80;

    return profile;
  }

  private analyzeLearningStyle(): string {
    const q18 = this.getAnswerText('q18');
    const q16 = this.getAnswerText('q16');

    let style = 'Balanced Learner';

    if (q18.includes('Very Quick')) style = 'Quick Adaptive Learner';
    if (q18.includes('Slow but Thorough')) style = 'Deep Learning Focused';

    if (q16.includes('Analytical')) style = 'Logical & Structured';
    if (q16.includes('Creative')) style = 'Intuitive & Experimental';

    return style;
  }

  private calculateLeadershipPotential(): number {
    const leadershopAnswers = ['q5', 'q8', 'q19', 'q28'];
    let score = 50;

    const q19Array = this.getAnswerArray('q19');
    if (q19Array.includes('Leadership')) score = 85;

    const q25 = this.getAnswerText('q25');
    if (q25.toLowerCase().includes('lead')) score = Math.max(score, 80);

    const answeredCount = leadershopAnswers.filter(id => this.findAnswer(id)).length;
    score = Math.round(score * (answeredCount / leadershopAnswers.length));

    return Math.min(score, 100);
  }

  private calculateCommunicationSkills(): number {
    const q4 = this.getAnswerText('q4');
    const q15Array = this.getAnswerArray('q15');
    const q19Array = this.getAnswerArray('q19');

    let score = 50;

    if (q4.includes('Extroverted')) score = 75;
    if (q4.includes('Ambivert')) score = 70;

    if (q15Array.includes('Communication')) score = 85;
    if (q19Array.includes('Teaching')) score = Math.max(score, 80);

    const q5 = this.getAnswerText('q5');
    if (q5) score = Math.min(Math.round(score * 1.1), 95);

    return Math.min(score, 100);
  }

  private calculateEntrepreneurialPotential(): number {
    const q22 = this.getAnswerText('q22');
    const q23 = this.getAnswerText('q23');
    const q2 = this.getAnswerText('q2');

    let score = 50;

    if (q22.includes('Business')) score = 80;
    if (q22.includes('Freelance')) score = 70;

    if (q23.includes('High Risk')) score = Math.max(score, 75);
    if (q23.includes('Moderate Risk')) score = Math.max(score, 65);

    if (q2.toLowerCase().includes('business')) score = Math.max(score, 80);
    if (q2.toLowerCase().includes('startup')) score = Math.max(score, 85);

    return Math.min(score, 100);
  }

  private calculateCreativityScore(): number {
    const q1 = this.getAnswerText('q1');
    const q16 = this.getAnswerText('q16');
    const q11 = this.getAnswerText('q11');

    let score = 50;

    if (q16.includes('Creative')) score = 80;
    if (q16.includes('Equal')) score = 65;

    if (q1.toLowerCase().includes('creative')) score = Math.max(score, 75);
    if (q1.toLowerCase().includes('art')) score = Math.max(score, 85);

    if (q11.toLowerCase().includes('creative')) score = Math.max(score, 80);

    return Math.min(score, 100);
  }

  private calculateTechnicalInclination(): number {
    const q3 = this.getAnswerText('q3');
    const q17 = this.getAnswerText('q17');
    const q12 = this.getAnswerText('q12');

    let score = 50;

    if (q3.includes('Technology')) score = 85;
    if (q3.includes('Data')) score = 80;

    if (q17.includes('Very Comfortable')) score = Math.max(score, 80);
    if (q17.includes('Comfortable')) score = Math.max(score, 70);

    if (q12.toLowerCase().includes('tech')) score = Math.max(score, 85);
    if (q12.toLowerCase().includes('it')) score = Math.max(score, 80);

    return Math.min(score, 100);
  }

  private calculateEmployability(): number {
    const q18 = this.getAnswerText('q18');
    const q20 = this.getAnswerText('q20');
    const q30 = this.getAnswerText('q30');

    let score = 60;

    if (q18.includes('Very Quick')) score = Math.max(score, 80);
    if (q18.includes('Quick')) score = Math.max(score, 75);

    if (q30) score = Math.max(score, 70);

    const skillsAnswer = this.getAnswerText('q20');
    if (skillsAnswer) {
      const skillCount = skillsAnswer.split(',').length;
      score = Math.min(score + skillCount * 5, 95);
    }

    return Math.min(score, 100);
  }

  private calculateAIDisruptionRisk(): number {
    const q3 = this.getAnswerText('q3');
    const q30 = this.getAnswerText('q30');
    const q16 = this.getAnswerText('q16');

    let risk = 40;

    if (q3.includes('Data')) risk = 75;
    if (q3.includes('Technology')) risk = 60;
    if (q3.includes('People')) risk = 20;

    if (q16.includes('Creative')) risk = Math.max(risk - 20, 10);

    const careersAnswer = this.getAnswerText('q30');
    if (careersAnswer.toLowerCase().includes('creative')) risk = Math.max(risk - 25, 10);
    if (careersAnswer.toLowerCase().includes('leadership')) risk = Math.max(risk - 30, 5);

    return Math.max(Math.min(risk, 95), 5);
  }

  private findAnswer(questionId: string): Answer | undefined {
    return this.answers.find(a => a.questionId === questionId);
  }

  private getAnswerText(questionId: string): string {
    const answer = this.findAnswer(questionId);
    return answer ? answer.text.split('|||')[0].trim() : '';
  }

  private getAnswerArray(questionId: string): string[] {
    const answer = this.findAnswer(questionId);
    return answer ? answer.text.split('|||').filter(a => a.trim()) : [];
  }

  generateRecommendations(metrics: AnalysisMetrics): CareerRecommendation[] {
    const baseRecommendations: CareerRecommendation[] = [];

    // High Leadership & Communication
    if (metrics.leadershipPotential > 70 && metrics.communicationSkills > 70) {
      baseRecommendations.push({
        rank: 1,
        title: 'Executive Leadership / Management',
        description: 'Director, VP, or C-Level positions across industries',
        whyItFits: 'Strong leadership potential, excellent communication skills, and proven ability to influence others',
        salary: {
          year3: '$120,000 - $150,000',
          year5: '$180,000 - $250,000',
          year10: '$300,000 - $500,000+'
        },
        demand: 'High - Always in demand across sectors',
        aiRisk: 'Low (15-25%) - Leadership roles require human judgment',
        skillsRequired: ['Strategic Planning', 'Team Management', 'Financial Acumen', 'Decision Making'],
        certifications: ['MBA', 'Executive Coaching', 'Six Sigma'],
        confidence: Math.round((metrics.leadershipPotential + metrics.communicationSkills) / 2)
      });
    }

    // High Technical & Logical
    if (metrics.technicalInclination > 70 && metrics.aptitudeProfile.logical > 70) {
      baseRecommendations.push({
        rank: baseRecommendations.length + 1,
        title: 'Software Engineer / Tech Lead',
        description: 'Full-stack developer, architect, or technical leadership roles',
        whyItFits: 'Strong technical skills, logical thinking, and problem-solving abilities',
        salary: {
          year3: '$100,000 - $130,000',
          year5: '$150,000 - $200,000',
          year10: '$250,000 - $400,000+'
        },
        demand: 'Very High - Critical shortage globally',
        aiRisk: 'Medium (40-50%) - Some roles at risk, but creation roles growing',
        skillsRequired: ['Programming', 'System Design', 'Cloud Platforms', 'DevOps'],
        certifications: ['AWS', 'Azure', 'Advanced Programming Courses'],
        confidence: Math.round((metrics.technicalInclination + metrics.aptitudeProfile.logical) / 2)
      });
    }

    // High Creativity & Communication
    if (metrics.creativityScore > 70 && metrics.communicationSkills > 65) {
      baseRecommendations.push({
        rank: baseRecommendations.length + 1,
        title: 'Creative Professional / Content Leader',
        description: 'Marketing Director, Content Strategist, Creative Director, or Brand Manager',
        whyItFits: 'Strong creative vision combined with ability to communicate and lead teams',
        salary: {
          year3: '$80,000 - $110,000',
          year5: '$120,000 - $160,000',
          year10: '$200,000 - $350,000+'
        },
        demand: 'High - Growing in digital age',
        aiRisk: 'Medium (35-45%) - Creative jobs expanding despite AI',
        skillsRequired: ['Storytelling', 'Digital Marketing', 'Brand Strategy', 'Analytics'],
        certifications: ['Google Analytics', 'Content Strategy Courses', 'MBA'],
        confidence: Math.round((metrics.creativityScore + metrics.communicationSkills) / 2)
      });
    }

    // High Entrepreneurial Potential
    if (metrics.entrepreneurialPotential > 75) {
      baseRecommendations.push({
        rank: baseRecommendations.length + 1,
        title: 'Entrepreneur / Business Owner',
        description: 'Founder of startup, own business ventures, or franchise owner',
        whyItFits: 'Strong desire for independence, risk appetite, and drive to build',
        salary: {
          year3: '$50,000 - $150,000 (variable)',
          year5: '$100,000 - $500,000+ (variable)',
          year10: '$500,000 - $5,000,000+ (potential)'
        },
        demand: 'High - Entrepreneurship increasingly supported',
        aiRisk: 'Low (20%) - Entrepreneurs adapt quickly',
        skillsRequired: ['Business Planning', 'Sales', 'Finance', 'Marketing'],
        certifications: ['MBA', 'Business Courses', 'Lean Startup'],
        confidence: metrics.entrepreneurialPotential
      });
    }

    // Balanced profile - Consulting
    if (baseRecommendations.length === 0 || metrics.employability > 75) {
      baseRecommendations.push({
        rank: baseRecommendations.length + 1,
        title: 'Management Consultant / Strategy Professional',
        description: 'Work with top consulting firms or as independent consultant',
        whyItFits: 'Balanced skill set, strong learning ability, and adaptability',
        salary: {
          year3: '$90,000 - $130,000',
          year5: '$150,000 - $220,000',
          year10: '$250,000 - $400,000+'
        },
        demand: 'High - Companies always need external expertise',
        aiRisk: 'Low (25%) - Requires strategic thinking',
        skillsRequired: ['Analytical Thinking', 'Communication', 'Business Acumen', 'Project Management'],
        certifications: ['MBA', 'Consulting Courses', 'Project Management'],
        confidence: 70
      });
    }

    return baseRecommendations;
  }

  getTopStrengths(metrics: AnalysisMetrics): string[] {
    const strengths = [];

    const aptitudes = Object.entries(metrics.aptitudeProfile);
    aptitudes.sort((a, b) => b[1] - a[1]);

    if (aptitudes[0][1] > 70) {
      strengths.push(`Exceptional ${aptitudes[0][0]} skills (Score: ${aptitudes[0][1]})`);
    }

    if (metrics.leadershipPotential > 70) {
      strengths.push(`Strong leadership capabilities (Score: ${metrics.leadershipPotential})`);
    }

    if (metrics.employability > 75) {
      strengths.push(`High market employability (Score: ${metrics.employability})`);
    }

    if (metrics.technicalInclination > 70) {
      strengths.push(`Strong technical aptitude (Score: ${metrics.technicalInclination})`);
    }

    if (metrics.communicationSkills > 75) {
      strengths.push(`Excellent communication abilities (Score: ${metrics.communicationSkills})`);
    }

    return strengths.length > 0 ? strengths : ['Strong learner', 'Adaptable professional', 'Growth-oriented mindset'];
  }

  getHiddenStrengths(metrics: AnalysisMetrics): string[] {
    return [
      `Potential for ${metrics.entrepreneurialPotential > 60 ? 'entrepreneurship' : 'leadership'} roles`,
      `Cross-functional capability in multiple domains`,
      `Resilience and adaptability to changing markets`,
      `Emerging strengths in emerging technology sectors`,
      `Potential for rapid upskilling based on learning style: ${metrics.leadershipPotential > 60 ? 'mentorship qualities' : 'self-directed learning'}`
    ];
  }

  getGrowthAreas(metrics: AnalysisMetrics): string[] {
    const areas = [];

    const aptitudes = Object.entries(metrics.aptitudeProfile);
    aptitudes.sort((a, b) => a[1] - b[1]);

    if (aptitudes[0][1] < 50) {
      areas.push(`Develop ${aptitudes[0][0]} skills further`);
    }

    if (metrics.leadershipPotential < 60) {
      areas.push('Leadership and team management capabilities');
    }

    if (metrics.technicalInclination < 50) {
      areas.push('Technical skills and digital literacy');
    }

    if (metrics.aiDisruptionRisk > 70) {
      areas.push('AI-proof skills (creativity, emotional intelligence)');
    }

    if (areas.length === 0) {
      areas.push('Continue building on existing strengths', 'Explore new industry domains');
    }

    return areas;
  }
}

export function generateWealthPlan(recommendations: CareerRecommendation[]): WealthPlan {
  return {
    careers: recommendations.slice(0, 3).map(rec => ({
      careerTitle: rec.title,
      primaryIncome: rec.salary.year5,
      secondaryIncome: [
        'Consulting projects (20-30% additional)',
        'Content creation/speaking engagements',
        'Mentoring and coaching'
      ],
      businessOpportunities: [
        'Side business in industry expertise',
        'Digital product creation',
        'Training and certification programs'
      ],
      personalBranding: 'Build thought leadership through speaking, writing, and networking',
      investmentStrategy: 'Diversified portfolio: 40% stocks, 30% real estate, 20% bonds, 10% startup investments'
    }))
  };
}

export function generateCareerRoadmap(recommendations: CareerRecommendation[]): CareerRoadmap {
  return {
    year1: {
      skills: [
        'Deepen expertise in primary domain',
        'Develop communication and presentation skills',
        'Build professional network',
        'Start personal branding initiative'
      ],
      certifications: [
        'Industry-specific certifications',
        'Leadership fundamentals',
        'Project management basics'
      ],
      projects: [
        'Lead or contribute to 2-3 significant projects',
        'Publish research or articles in your field',
        'Complete capstone or certification project'
      ]
    },
    year3: {
      milestones: [
        'Advance to mid-level or senior position',
        'Lead team or major initiative',
        'Expand into adjacent skill areas',
        'Establish thought leadership'
      ],
      salaryTarget: recommendations[0]?.salary.year3 || '$100,000 - $150,000'
    },
    year5: {
      milestones: [
        'Senior leadership or specialist role',
        'Own significant business area',
        'Industry recognition or awards',
        'Mentor others in your field'
      ],
      wealthTarget: recommendations[0]?.salary.year5 || '$150,000 - $250,000'
    }
  };
}
