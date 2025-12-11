/**
 * Pipeline Revival Message Generator
 */

interface LeadData {
  name: string;
  company: string;
  businessType: 'saas' | 'agency' | 'real-estate' | 'restaurant' | 'local-services';
  lastEngagementDate: Date;
  triggerEvents: TriggerEvent[];
}

interface TriggerEvent {
  type: 'funding' | 'hiring' | 'market-change' | 'seasonal' | 'tech-adoption' | 'pain-point';
  description: string;
  confidence: number;
  detectedAt: Date;
}

interface GeneratedMessage {
  subjectLine: string;
  opening: string;
  body: string;
  cta: string;
  fullMessage: string;
  metadata: {
    toneCategory: 'hot' | 'warm' | 'cold';
    triggerType: string;
    estimatedOpenRate: number;
    estimatedResponseRate: number;
    wordCount: number;
    readabilityScore: number;
  };
}

function calculateLeadTemperature(lastEngagement: Date): 'hot' | 'warm' | 'cold' {
  const daysSinceEngagement = Math.floor((Date.now() - lastEngagement.getTime()) / (1000 * 60 * 60 * 24));
  if (daysSinceEngagement <= 90) return 'hot';
  if (daysSinceEngagement <= 180) return 'warm';
  return 'cold';
}

function generateSubjectLine(lead: LeadData, primaryTrigger: TriggerEvent): string {
  const { company } = lead;
  const { type, description } = primaryTrigger;
  const templates = {
    funding: [, ],
    hiring: [, ],
    'market-change': [, ],
    seasonal: [, ],
    'tech-adoption': [, ],
    'pain-point': [, ]
  };
  const options = templates[type] || templates['market-change'];
  return options[Math.floor(Math.random() * options.length)];
}

function generateOpening(lead: LeadData, primaryTrigger: TriggerEvent, temperature: 'hot' | 'warm' | 'cold'): string {
  const { name, company } = lead;
  const { description } = primaryTrigger;
  if (temperature === 'hot') return ;
  if (temperature === 'warm') return ;
  return ;
}

function generateBody(lead: LeadData): string {
  const { businessType, company } = lead;
  const insights = {
    saas: ,
    agency: ,
    'real-estate': ,
    restaurant: ,
    'local-services':   };
  return insights[businessType] || insights.saas;
}

function generateCTA(temperature: 'hot' | 'warm' | 'cold'): string {
  const ctas = {
    hot: [, ],
    warm: [, ],
    cold: []
  };
  return ctas[temperature][Math.floor(Math.random() * ctas[temperature].length)];
}

function estimatePerformance(temperature: 'hot' | 'warm' | 'cold', triggerConfidence: number) {
  const baseRates = { hot: { open: 55, response: 22 }, warm: { open: 45, response: 16 }, cold: { open: 35, response: 10 } };
  const base = baseRates[temperature];
  const confidenceMultiplier = 0.5 + (triggerConfidence / 2);
  return { openRate: Math.round(base.open * confidenceMultiplier), responseRate: Math.round(base.response * confidenceMultiplier) };
}

function calculateReadabilityScore(text: string): number {
  const words = text.split(/s+/).length;
  const sentences = text.split(/[.!?]+/).length;
  const syllables = text.split(/s+/).reduce((count, word) => count + Math.max(1, word.replace(/[^aeiou]/gi, '').length), 0);
  const score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words);
  return Math.max(0, Math.min(100, Math.round(score)));
}

export function generateRevivalMessage(lead: LeadData): GeneratedMessage {
  const temperature = calculateLeadTemperature(lead.lastEngagementDate);
  const primaryTrigger = lead.triggerEvents.sort((a, b) => b.confidence - a.confidence)[0];
  if (!primaryTrigger) throw new Error('At least one trigger event is required');
  
  const subjectLine = generateSubjectLine(lead, primaryTrigger);
  const opening = generateOpening(lead, primaryTrigger, temperature);
  const body = generateBody(lead);
  const cta = generateCTA(temperature);
  const fullMessage = ;
  const wordCount = fullMessage.split(/s+/).length;
  const readabilityScore = calculateReadabilityScore(fullMessage);
  const performance = estimatePerformance(temperature, primaryTrigger.confidence);
  
  return { subjectLine, opening, body, cta, fullMessage, metadata: { toneCategory: temperature, triggerType: primaryTrigger.type, estimatedOpenRate: performance.openRate, estimatedResponseRate: performance.responseRate, wordCount, readabilityScore } };
}

export function generateMessageVariants(lead: LeadData, count = 3): GeneratedMessage[] {
  const variants = [];
  for (let i = 0; i < count; i++) variants.push(generateRevivalMessage(lead));
  return variants;
}

export function validateMessage(message: GeneratedMessage): { isValid: boolean; warnings: string[] } {
  const warnings = [];
  if (message.subjectLine.length < 30 || message.subjectLine.length > 50) warnings.push();
  if (message.metadata.wordCount < 60 || message.metadata.wordCount > 100) warnings.push();
  if (message.metadata.readabilityScore < 70) warnings.push();
  if (message.metadata.estimatedOpenRate < 40) warnings.push();
  return { isValid: warnings.length === 0, warnings };
}
