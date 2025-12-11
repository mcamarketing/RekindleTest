/**
 * Skills Agent API
 *
 * Provides HTTP endpoints for LLM agents to discover and load skills.
 * Designed for easy consumption by CrewAI agents, REX, and other AI systems.
 */

import { Router, Request, Response } from 'express';
import { skillLoader, LoadedSkill } from './loader';

const router = Router();

/**
 * GET /skills
 * List all available skills with metadata
 */
router.get('/', (req: Request, res: Response) => {
  try {
    const skills = skillLoader.discoverSkills();

    res.json({
      success: true,
      count: skills.length,
      skills: skills.map(skill => ({
        name: skill.name,
        version: skill.version,
        description: skill.description
      }))
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to discover skills',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/:skillName
 * Get full skill details including instructions
 */
router.get('/:skillName', (req: Request, res: Response) => {
  try {
    const { skillName } = req.params;
    const skill = skillLoader.loadSkill(skillName);

    if (!skill) {
      return res.status(404).json({
        success: false,
        error: `Skill '${skillName}' not found`
      });
    }

    res.json({
      success: true,
      skill: {
        name: skill.metadata.name,
        version: skill.config.version,
        description: skill.config.description,
        instructions: skill.instructions,
        config: skill.config,
        metadata: {
          hasScripts: skill.hasScripts,
          hasExamples: skill.hasExamples,
          hasTests: skill.hasTests
        }
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to load skill',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/:skillName/instructions
 * Get only the instructions (most common agent use case)
 */
router.get('/:skillName/instructions', (req: Request, res: Response) => {
  try {
    const { skillName } = req.params;
    const instructions = skillLoader.loadInstructions(skillName);

    if (!instructions) {
      return res.status(404).json({
        success: false,
        error: `Instructions for skill '${skillName}' not found`
      });
    }

    // Return as plain text for easy LLM consumption
    res.type('text/markdown').send(instructions);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to load instructions',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/:skillName/config
 * Get skill configuration
 */
router.get('/:skillName/config', (req: Request, res: Response) => {
  try {
    const { skillName } = req.params;
    const config = skillLoader.loadConfig(skillName);

    if (!config) {
      return res.status(404).json({
        success: false,
        error: `Config for skill '${skillName}' not found`
      });
    }

    res.json({
      success: true,
      config
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to load config',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/:skillName/examples
 * Get skill examples
 */
router.get('/:skillName/examples', (req: Request, res: Response) => {
  try {
    const { skillName } = req.params;
    const examples = skillLoader.loadExamples(skillName);

    res.json({
      success: true,
      count: examples.length,
      examples
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to load examples',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/:skillName/agent-payload
 * Export skill in format optimized for agent consumption
 */
router.get('/:skillName/agent-payload', (req: Request, res: Response) => {
  try {
    const { skillName } = req.params;
    const payload = skillLoader.exportSkillForAgent(skillName);

    if (!payload) {
      return res.status(404).json({
        success: false,
        error: `Skill '${skillName}' not found`
      });
    }

    res.type('application/json').send(payload);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to export skill',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/search/by-tag/:tag
 * Find skills by tag
 */
router.get('/search/by-tag/:tag', (req: Request, res: Response) => {
  try {
    const { tag } = req.params;
    const skills = skillLoader.findSkillsByTag(tag);

    res.json({
      success: true,
      tag,
      count: skills.length,
      skills: skills.map(skill => ({
        name: skill.metadata.name,
        version: skill.config.version,
        description: skill.config.description,
        tags: skill.config.tags
      }))
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to search skills',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/search/by-owner/:owner
 * Find skills by owner
 */
router.get('/search/by-owner/:owner', (req: Request, res: Response) => {
  try {
    const { owner } = req.params;
    const skills = skillLoader.findSkillsByOwner(owner);

    res.json({
      success: true,
      owner,
      count: skills.length,
      skills: skills.map(skill => ({
        name: skill.metadata.name,
        version: skill.config.version,
        description: skill.config.description,
        owners: skill.config.owners
      }))
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to search skills',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /skills/catalog
 * Get skills grouped by owner/category
 */
router.get('/catalog', (req: Request, res: Response) => {
  try {
    const catalog = skillLoader.getSkillsCatalog();

    res.json({
      success: true,
      catalog
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get catalog',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /skills/:skillName/validate
 * Validate skill structure
 */
router.post('/:skillName/validate', (req: Request, res: Response) => {
  try {
    const { skillName } = req.params;
    const validation = skillLoader.validateSkill(skillName);

    res.json({
      success: validation.valid,
      skill: skillName,
      validation
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to validate skill',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
