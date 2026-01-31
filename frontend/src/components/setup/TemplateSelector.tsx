import { useState } from 'react';
import { Sparkles } from 'lucide-react';

const TEMPLATES = [
  {
    id: 'family_traditional',
    name: 'Family Traditional',
    icon: '👨‍👩‍👧‍👦',
    description: 'Multi-generational family business with authentic recipes',
    context: {
      historyContext: 'Our family has been serving authentic [cuisine] for [X] generations. We use my grandmother\'s original recipes passed down since [year].',
      valuesContext: 'We prioritize authenticity, quality ingredients, and family atmosphere. Every dish is made with the same care we\'d serve our own family.',
      uspsContext: 'Family recipes you can\'t find anywhere else, traditional preparation methods, warm family atmosphere',
      targetAudienceContext: 'Families looking for authentic cuisine, food enthusiasts who value tradition, people seeking comfort food',
      challengesContext: 'Competing with faster modern restaurants, attracting younger customers while maintaining tradition',
      goalsContext: 'Preserve our legacy while growing sustainably, pass the business to next generation'
    }
  },
  {
    id: 'modern_fusion',
    name: 'Modern Fusion',
    icon: '✨',
    description: 'Contemporary restaurant with innovative cuisine',
    context: {
      historyContext: 'We launched in [year] with a vision to reimagine [cuisine] for modern palates. Our chef trained at [restaurant/school].',
      valuesContext: 'Innovation, sustainability, locally-sourced ingredients, creating Instagram-worthy experiences',
      uspsContext: 'Unique flavor combinations, beautiful plating, trendy atmosphere, craft cocktails',
      targetAudienceContext: 'Millennials and Gen Z who love trying new things, foodies, social media influencers, date night crowds',
      challengesContext: 'High competition in the trendy segment, maintaining consistency while innovating',
      goalsContext: 'Become the go-to spot for special occasions, expand to second location, gain media recognition'
    }
  },
  {
    id: 'fast_casual',
    name: 'Fast Casual',
    icon: '⚡',
    description: 'Quick service with quality food',
    context: {
      historyContext: 'Started as a food truck in [year], now with [X] locations. Built on the principle that fast food doesn\'t have to be unhealthy.',
      valuesContext: 'Speed without compromising quality, affordable healthy options, transparency in ingredients',
      uspsContext: 'Fresh ingredients, made-to-order, under 10 minutes, affordable prices, customizable menu',
      targetAudienceContext: 'Busy professionals, students, health-conscious quick lunch crowd, families on-the-go',
      challengesContext: 'Maintaining speed during rush, food cost management, competing with chains',
      goalsContext: 'Scale to [X] locations, develop franchise model, introduce app ordering'
    }
  },
  {
    id: 'upscale_dining',
    name: 'Upscale Dining',
    icon: '🍷',
    description: 'Fine dining experience',
    context: {
      historyContext: 'Opened by chef [name] in [year] after [X] years in Michelin-starred kitchens. Focus on elevated [cuisine].',
      valuesContext: 'Culinary artistry, exceptional service, curated wine program, memorable experiences',
      uspsContext: 'Michelin-quality dishes, sommelier on staff, tasting menu experiences, seasonal ingredients',
      targetAudienceContext: 'Affluent diners, special occasion celebrators, food critics, corporate dinners',
      challengesContext: 'High labor costs, maintaining consistency, managing reservations/no-shows',
      goalsContext: 'Earn Michelin star, increase average check, private dining revenue'
    }
  },
  {
    id: 'neighborhood_cafe',
    name: 'Neighborhood Café',
    icon: '☕',
    description: 'Community gathering spot',
    context: {
      historyContext: 'A neighborhood staple since [year]. We know our regulars by name and their usual orders.',
      valuesContext: 'Community, consistency, comfort, being a third place between home and work',
      uspsContext: 'Loyal customer base, cozy atmosphere, reliable favorites, good WiFi, meeting space',
      targetAudienceContext: 'Local residents, remote workers, retirees, students studying, morning regulars',
      challengesContext: 'Rent increases, competing with chains, expanding beyond regulars',
      goalsContext: 'Become community hub, host events, maintain profitability with rising costs'
    }
  },
  {
    id: 'custom',
    name: 'Start Fresh',
    icon: '✏️',
    description: 'Write your own unique story',
    context: {}
  }
];

interface TemplateSelectorProps {
  onSelect: (template: any) => void;
}

export function TemplateSelector({ onSelect }: TemplateSelectorProps) {
  const [selected, setSelected] = useState<string | null>(null);
  
  const handleSelect = (template: typeof TEMPLATES[0]) => {
    setSelected(template.id);
    // Only pass the context part, not the whole template object structure used for UI
    onSelect(template.context);
  };
  
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-5 h-5 text-purple-600" />
        <h4 className="font-semibold text-gray-900">Quick Start Templates</h4>
        <span className="text-xs text-gray-500">(optional - saves time)</span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {TEMPLATES.map(template => (
          <button
            key={template.id}
            onClick={() => handleSelect(template)}
            className={`p-4 rounded-lg border-2 transition-all text-left ${
              selected === template.id
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50/50'
            }`}
          >
            <div className="text-3xl mb-2">{template.icon}</div>
            <div className="font-semibold text-gray-900 text-sm mb-1">
              {template.name}
            </div>
            <div className="text-xs text-gray-600 line-clamp-2">
              {template.description}
            </div>
          </button>
        ))}
      </div>
      
      {selected && selected !== 'custom' && (
        <div className="mt-3 p-3 bg-purple-50 rounded-lg text-sm text-purple-800">
          ✨ Template applied! You can edit the pre-filled text below to match your exact situation.
        </div>
      )}
    </div>
  );
}
