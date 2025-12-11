# Rekindle Pro Skills Architecture

A reusable skills architecture allowing all agents (CrewAI, REX, backend services) to load procedural expertise from disk instead of cramming it into prompts.

## Overview

Skills are self-contained expertise modules that provide:
- **Instructions**: Step-by-step procedural knowledge (Markdown)
- **Configuration**: Metadata, dependencies, success criteria (JSON)
- **Scripts**: Executable logic (TypeScript)
- **Examples**: Real-world use cases (JSON/Markdown)
- **Tests**: Validation and quality assurance (TypeScript)

## Available Skills

### 1. **pipeline_revival_messaging**
Generate warm, human, trigger-aware revival messages for dormant leads.

- **Owners**: rex_team, revenue_intelligence
- **Tags**: messaging, revival, copywriting, engagement, sales
- **Key Features**: Industry-specific tone, trigger-based context, DO/DON'T rules

### 2. **dormant_lead_analysis**
Score and segment dormant leads using RFV+S framework (Recency, Frequency, Value, Source).

- **Owners**: revenue_intelligence, data_team
- **Tags**: scoring, segmentation, prioritization, lead-analysis
- **Key Features**: 12-point scoring system, High/Medium/Low segmentation

### 3. **roi_estimation**
Calculate revenue upside from revival campaigns across low/base/strong scenarios.

- **Owners**: revenue_intelligence, finance_team
- **Tags**: roi, revenue, forecasting, conversion, scenarios
- **Key Features**: Industry-specific conversion rates, 3 scenario modeling

### 4. **crm_normalization**
Transform lead data from various CRMs into canonical Rekindle format.

- **Owners**: data_team, platform_team
- **Tags**: normalization, crm, data-quality, etl, transformation
- **Key Features**: Salesforce/HubSpot/Pipedrive support, quality scoring

### 5. **objection_handling**
Provide tactical, empathetic responses to common objections during outreach.

- **Owners**: sales_enablement, rex_team
- **Tags**: objections, sales, responses, enablement
- **Key Features**: 7 objection types, acknowledge-reframe-reduce framework

## Directory Structure

```
skills/
├── README.md                          # This file
├── pipeline_revival_messaging/
│   ├── README.md                      # Skill-specific documentation
│   ├── instructions.md                # Procedural expertise
│   ├── config.json                    # Metadata and configuration
│   ├── scripts/
│   │   └── generate_message.ts        # Executable logic
│   ├── examples/
│   │   ├── saas-hot-funding.md
│   │   ├── agency-warm-hiring.md
│   │   └── ...
│   └── tests/
│       └── test_message_generation.ts
├── dormant_lead_analysis/
│   ├── ...
├── roi_estimation/
│   ├── ...
├── crm_normalization/
│   ├── ...
└── objection_handling/
    ├── ...
```

## Usage

### Backend (TypeScript)

```typescript
import { skillLoader, loadInstructions } from './backend/src/skills/loader';

// Discover all skills
const skills = skillLoader.discoverSkills();
console.log(`Found ${skills.length} skills`);

// Load instructions for an agent
const instructions = loadInstructions('pipeline_revival_messaging');
console.log(instructions);

// Load full skill with config and examples
const skill = skillLoader.loadSkill('roi_estimation');
console.log(skill.config.success_criteria);
```

### CrewAI Agents (Python)

```python
import requests

# Get skill instructions
response = requests.get('http://localhost:3000/api/skills/dormant_lead_analysis/instructions')
instructions = response.text

# Use in agent prompt
agent = Agent(
    role='Lead Scoring Specialist',
    goal='Score and segment dormant leads',
    backstory=instructions,  # Load skill instructions dynamically
    tools=[...]
)
```

### REX System (Python)

```python
# Load skill as JSON payload
response = requests.get('http://localhost:3000/api/skills/objection_handling/agent-payload')
skill = response.json()

# Access structured data
print(skill['instructions'])
print(skill['required_inputs'])
print(skill['examples'])
```

## API Endpoints

The skills system exposes HTTP endpoints for agent consumption:

- `GET /api/skills` - List all skills
- `GET /api/skills/:name` - Get full skill details
- `GET /api/skills/:name/instructions` - Get instructions (Markdown)
- `GET /api/skills/:name/config` - Get configuration (JSON)
- `GET /api/skills/:name/examples` - Get examples
- `GET /api/skills/:name/agent-payload` - Optimized for LLM consumption
- `GET /api/skills/search/by-tag/:tag` - Find skills by tag
- `GET /api/skills/search/by-owner/:owner` - Find skills by owner

## Creating a New Skill

1. **Create directory**: `skills/your_skill_name/`

2. **Add instructions.md**:
```markdown
# Your Skill Name

## Purpose
What this skill does...

## Core Principles
1. ...
2. ...

## Procedures
Step-by-step instructions...
```

3. **Add config.json**:
```json
{
  "skill_name": "your_skill_name",
  "version": "1.0.0",
  "description": "Brief description",
  "owners": ["team_name"],
  "tags": ["tag1", "tag2"],
  "dependencies": {
    "required_data": ["field1", "field2"]
  }
}
```

4. **Add scripts/** (optional):
```typescript
// scripts/your_logic.ts
export function executeSkill(input: any): any {
  // Implementation
}
```

5. **Add examples/** (optional):
```json
// examples/example1.json
{
  "input": {...},
  "output": {...}
}
```

6. **Add tests/** (optional):
```typescript
// tests/test_skill.ts
describe('Your Skill', () => {
  it('should...', () => {
    // Tests
  });
});
```

7. **Add README.md** with usage examples

## Integration Points

### Backend Services
- Revival Priority Engine (`backend/src/services/revival-priority-engine.ts`)
- Lead Segmentation (`backend/src/services/lead-segmentation.ts`)

### Agent Systems
- CrewAI Agents (`backend/crewai_agents/`)
- REX System (`backend/rex/`)

### Example Integration

Replace hardcoded ROI logic:

```typescript
// Before (hardcoded)
private calculateEstimatedROI(opportunity: PrioritizedOpportunity): number {
  const expectedRevenue = opportunity.potentialValue * 0.5;
  const totalCost = 5000;
  return (expectedRevenue - totalCost) / totalCost;
}

// After (skill-based)
import { skillLoader } from '../skills/loader';

private calculateEstimatedROI(opportunity: PrioritizedOpportunity): number {
  const instructions = skillLoader.loadInstructions('roi_estimation');
  // Use instructions to guide ROI calculation with industry-specific rates
  // ...
}
```

## Design Principles

1. **Git-friendly**: Plain text files (Markdown, JSON, TypeScript)
2. **Human-editable**: No complex binary formats
3. **Agent-readable**: Structured for LLM consumption
4. **Backend-usable**: TypeScript code can import and execute
5. **Self-contained**: Each skill is independent
6. **Version-controlled**: Track changes over time
7. **Testable**: Unit tests for critical logic

## Benefits

### Before (Prompt-Based)
❌ Knowledge baked into prompts
❌ Hard to update across agents
❌ No version control
❌ Duplicated across systems
❌ Context window bloat

### After (Skills-Based)
✅ Knowledge lives on disk
✅ Update once, all agents benefit
✅ Git tracks every change
✅ Single source of truth
✅ Load only what you need

## Performance

- **Discovery**: <10ms (scans file system)
- **Load**: <50ms per skill (with caching)
- **API Response**: <100ms (over HTTP)
- **Cache**: In-memory, clears on update

## Testing

Run skill tests:
```bash
# Test specific skill
npm test skills/pipeline_revival_messaging/tests

# Test all skills
npm test skills/*/tests

# Validate skill structure
curl http://localhost:3000/api/skills/roi_estimation/validate
```

## Maintenance

- **Adding Skills**: Follow creation guide above
- **Updating Skills**: Edit files, increment version in config.json
- **Deprecating Skills**: Move to `skills/archived/`
- **Ownership**: Contact owners listed in config.json

## Future Enhancements

- [ ] Skill versioning with semver
- [ ] Skill dependencies (skill A requires skill B)
- [ ] Dynamic skill composition
- [ ] Skill performance metrics
- [ ] Agent usage tracking
- [ ] Skill marketplace/catalog UI

## Support

- **Questions**: Contact `rex_team` or `revenue_intelligence`
- **Issues**: GitHub issues or Slack #rekindle-skills
- **Documentation**: This README + individual skill READMEs

---

**Version**: 1.0.0
**Last Updated**: 2025-01-15
**Maintained By**: REX Team, Revenue Intelligence
