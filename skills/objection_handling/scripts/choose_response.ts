interface ObjectionInput {
  text: string;
}

interface ResponseOutput {
  type: string;
  template: string;
  keyPoints: string[];
}

const OBJECTION_PATTERNS = [
  {
    keywords: ['expensive', 'price', 'cost', 'budget', 'afford'],
    type: 'price',
    template: "I understand budget is a key consideration. Many of our clients find that the ROI from revived leads covers the investment within the first month. Would you be open to seeing a customized ROI projection for your business?",
    keyPoints: ['Focus on ROI', 'Offer projection', 'Ask for openness']
  },
  {
    keywords: ['tried', 'before', 'didn\'t work', 'failed', 'not successful'],
    type: 'tried_before',
    template: "I appreciate you sharing your previous experience. What specifically didn't work for you before? Our approach focuses on personalized messaging and timing, which often makes the difference. Could we explore how this might be different for you?",
    keyPoints: ['Ask for specifics', 'Differentiate approach', 'Explore differences']
  },
  {
    keywords: ['busy', 'time', 'priority', 'not now', 'later'],
    type: 'no_time',
    template: "I completely understand being busy. Rather than a full commitment, could we start with a 15-minute call to see if this aligns with your current priorities? Many teams find it saves them time in the long run.",
    keyPoints: ['Acknowledge busyness', 'Suggest low-commitment start', 'Highlight time savings']
  },
  {
    keywords: ['small', 'list', 'database', 'contacts', 'few leads'],
    type: 'small_list',
    template: "List size is important, but quality often matters more than quantity. We could start with a pilot using your best prospects to demonstrate results. Would that be a good first step?",
    keyPoints: ['Emphasize quality over quantity', 'Suggest pilot approach', 'Focus on best prospects']
  },
  {
    keywords: ['data', 'security', 'privacy', 'safe', 'protect'],
    type: 'data_concern',
    template: "Data security is absolutely critical. We use enterprise-grade encryption, SOC 2 compliance, and never sell or share your information. Would you like me to walk you through our security measures?",
    keyPoints: ['Highlight security features', 'Offer transparency', 'Address specific concerns']
  },
  {
    keywords: ['ai', 'artificial intelligence', 'automation', 'robots'],
    type: 'ai_concern',
    template: "AI is a tool that augments human intelligence, not replaces it. All our campaigns include human oversight and customization. In fact, our clients appreciate how it frees up their time for strategic work.",
    keyPoints: ['Explain AI as augmentation', 'Emphasize human oversight', 'Highlight benefits']
  }
];

function findMatchingObjection(text: string): { type: string; template: string; keyPoints: string[] } | null {
  const lowerText = text.toLowerCase();
  for (const pattern of OBJECTION_PATTERNS) {
    if (pattern.keywords.some(keyword => lowerText.includes(keyword))) {
      return {
        type: pattern.type,
        template: pattern.template,
        keyPoints: pattern.keyPoints
      };
    }
  }
  return null;
}

export function chooseResponse(input: ObjectionInput): ResponseOutput {
  const match = findMatchingObjection(input.text);
  if (match) {
    return match;
  }

  // Default response for unrecognized objections
  return {
    type: 'general',
    template: "Thank you for sharing that concern. Could you tell me more about what's on your mind? I'd like to understand better so I can address it properly.",
    keyPoints: ['Thank them', 'Ask for more details', 'Show willingness to understand']
  };
}