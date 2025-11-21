import React from 'react';
import { motion } from 'framer-motion';
import { Check, Zap, TrendingUp, Award } from 'lucide-react';

interface PricingTier {
  name: string;
  originalPrice: number;
  foundingPrice: number;
  perMeetingFee: number | string;
  description: string;
  features: string[];
  highlighted?: boolean;
  badge?: string;
}

const pricingTiers: PricingTier[] = [
  {
    name: 'Starter',
    originalPrice: 29,
    foundingPrice: 14.99,
    perMeetingFee: 100,
    description: 'Perfect for growing teams testing AI-powered outreach',
    features: [
      '500 leads/month',
      'Email + SMS channels',
      'AI personalization',
      'Standard analytics',
      'Email support',
      'Basic CRM integration',
    ],
  },
  {
    name: 'Professional',
    originalPrice: 199,
    foundingPrice: 99.99,
    perMeetingFee: 250,
    description: 'For scaling teams serious about revenue growth',
    badge: 'Most Popular',
    highlighted: true,
    features: [
      '2,000 leads/month',
      'All channels (Email, SMS, WhatsApp, Voicemail)',
      'Advanced AI personalization',
      'Real-time analytics dashboard',
      'Priority support',
      'Full CRM integrations',
      'A/B testing',
      'Custom workflows',
    ],
  },
  {
    name: 'Enterprise',
    originalPrice: 799,
    foundingPrice: 399.99,
    perMeetingFee: '£500-£1,000',
    description: 'Maximum performance for enterprise sales teams',
    badge: 'Best Value',
    features: [
      'Unlimited leads',
      'All Professional features',
      'Dedicated success manager',
      'Custom AI model training',
      'White-glove onboarding',
      'SLA guarantees',
      'Full API access',
      'Custom integrations',
      'Advanced security features',
    ],
  },
];

const PricingCards: React.FC = () => {
  return (
    <div className="py-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm mb-6"
          >
            <Zap className="w-4 h-4" />
            Founding Rate - 50% Off Forever
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl font-bold text-white mb-4"
          >
            Lock In Your{' '}
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Founding Rate
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-xl text-slate-300 max-w-3xl mx-auto"
          >
            Join as a founding member and save 50% forever. Price locks in permanently after pilot.
          </motion.p>
        </div>

        {/* Pricing Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {pricingTiers.map((tier, index) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="relative"
            >
              {/* Badge */}
              {tier.badge && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                  <span className="inline-flex items-center gap-1 px-4 py-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full text-white text-sm font-medium shadow-lg">
                    <Award className="w-3 h-3" />
                    {tier.badge}
                  </span>
                </div>
              )}

              {/* Card */}
              <div
                className={`
                  relative h-full p-8 rounded-2xl backdrop-blur-sm
                  transition-all duration-300 hover:scale-105
                  ${
                    tier.highlighted
                      ? 'bg-gradient-to-br from-slate-800/90 to-slate-900/90 border-2 border-blue-500/50 shadow-2xl shadow-blue-500/20'
                      : 'bg-slate-800/50 border border-slate-700/50 hover:border-slate-600/50'
                  }
                `}
              >
                {/* Tier Name */}
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-white mb-2">{tier.name}</h3>
                  <p className="text-sm text-slate-400">{tier.description}</p>
                </div>

                {/* Pricing */}
                <div className="text-center mb-8">
                  {/* Original Price (Strikethrough) */}
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <span className="text-2xl text-slate-500 line-through">£{tier.originalPrice}</span>
                    <span className="text-xs text-slate-500">/month</span>
                  </div>

                  {/* Founding Price (Emphasized) */}
                  <div className="flex items-center justify-center gap-1">
                    <span className="text-5xl font-bold text-white">£{tier.foundingPrice}</span>
                    <span className="text-slate-400">/month</span>
                  </div>

                  {/* Founding Rate Badge */}
                  <div className="mt-3">
                    <span className="inline-block px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full text-green-400 text-xs font-medium">
                      Founding Rate - Save £{(tier.originalPrice - tier.foundingPrice).toFixed(2)}/mo
                    </span>
                  </div>

                  {/* Per Meeting Fee */}
                  <div className="mt-4 pt-4 border-t border-slate-700/50">
                    <div className="text-sm text-slate-400">Per qualified meeting</div>
                    <div className="text-2xl font-bold text-blue-400 mt-1">
                      {typeof tier.perMeetingFee === 'number' ? `£${tier.perMeetingFee}` : tier.perMeetingFee}
                    </div>
                  </div>
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-3">
                      <div
                        className={`
                          flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center
                          ${tier.highlighted ? 'bg-blue-500/20' : 'bg-slate-700/50'}
                        `}
                      >
                        <Check className="w-3 h-3 text-blue-400" />
                      </div>
                      <span className="text-sm text-slate-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <button
                  className={`
                    w-full py-4 px-6 rounded-xl font-semibold text-white
                    transition-all duration-300 transform hover:scale-105
                    ${
                      tier.highlighted
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 shadow-lg shadow-blue-500/25'
                        : 'bg-slate-700 hover:bg-slate-600'
                    }
                  `}
                >
                  Request Access
                </button>

                {/* Lock In Forever Note */}
                <p className="text-center text-xs text-slate-500 mt-4">
                  Price locked forever after pilot completion
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom Note */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="text-center mt-16"
        >
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 border border-slate-700/50 rounded-full">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-slate-300">
              <span className="font-semibold text-white">Founding members</span> save 50% forever and get priority support
            </span>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PricingCards;
