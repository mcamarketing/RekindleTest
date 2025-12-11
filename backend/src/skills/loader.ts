/**
 * Skill Loader Library
 *
 * Dynamically loads and executes skills from the /skills directory.
 * Provides TypeScript backend with access to procedural expertise stored on disk.
 */

import * as fs from 'fs';
import * as path from 'path';

export interface SkillConfig {
  skill_name: string;
  version: string;
  description: string;
  owners: string[];
  tags: string[];
  dependencies: {
    required_data: string[];
    optional_data?: string[];
  };
  outputs: Record<string, any>;
  success_criteria: Record<string, string>;
  usage_frequency: 'low' | 'medium' | 'high';
  execution_mode: 'synchronous' | 'batch' | 'async';
  estimated_runtime_ms: number;
  cost_per_execution: number;
}

export interface SkillMetadata {
  name: string;
  version: string;
  description: string;
  configPath: string;
  instructionsPath: string;
  scriptsPath: string;
  examplesPath: string;
  testsPath: string;
}

export interface LoadedSkill {
  metadata: SkillMetadata;
  config: SkillConfig;
  instructions: string;
  hasScripts: boolean;
  hasExamples: boolean;
  hasTests: boolean;
}

export class SkillLoader {
  private skillsBasePath: string;
  private skillCache: Map<string, LoadedSkill> = new Map();

  constructor(skillsBasePath?: string) {
    // Default to /skills at project root
    this.skillsBasePath = skillsBasePath || path.join(__dirname, '../../../skills');
  }

  /**
   * Discover all available skills in the skills directory
   */
  discoverSkills(): SkillMetadata[] {
    try {
      const skillDirs = fs.readdirSync(this.skillsBasePath, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name);

      return skillDirs.map(skillName => this.getSkillMetadata(skillName)).filter(Boolean) as SkillMetadata[];
    } catch (error) {
      console.error('Error discovering skills:', error);
      return [];
    }
  }

  /**
   * Get metadata for a specific skill
   */
  private getSkillMetadata(skillName: string): SkillMetadata | null {
    const skillPath = path.join(this.skillsBasePath, skillName);
    const configPath = path.join(skillPath, 'config.json');

    if (!fs.existsSync(configPath)) {
      console.warn(`Skill ${skillName} missing config.json`);
      return null;
    }

    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf-8')) as SkillConfig;

      return {
        name: skillName,
        version: config.version,
        description: config.description,
        configPath,
        instructionsPath: path.join(skillPath, 'instructions.md'),
        scriptsPath: path.join(skillPath, 'scripts'),
        examplesPath: path.join(skillPath, 'examples'),
        testsPath: path.join(skillPath, 'tests')
      };
    } catch (error) {
      console.error(`Error loading metadata for skill ${skillName}:`, error);
      return null;
    }
  }

  /**
   * Load a skill with all its components
   */
  loadSkill(skillName: string, useCache: boolean = true): LoadedSkill | null {
    // Check cache first
    if (useCache && this.skillCache.has(skillName)) {
      return this.skillCache.get(skillName)!;
    }

    const metadata = this.getSkillMetadata(skillName);
    if (!metadata) {
      console.error(`Skill ${skillName} not found`);
      return null;
    }

    try {
      // Load config
      const config = JSON.parse(fs.readFileSync(metadata.configPath, 'utf-8')) as SkillConfig;

      // Load instructions
      let instructions = '';
      if (fs.existsSync(metadata.instructionsPath)) {
        instructions = fs.readFileSync(metadata.instructionsPath, 'utf-8');
      }

      // Check for optional components
      const hasScripts = fs.existsSync(metadata.scriptsPath);
      const hasExamples = fs.existsSync(metadata.examplesPath);
      const hasTests = fs.existsSync(metadata.testsPath);

      const loadedSkill: LoadedSkill = {
        metadata,
        config,
        instructions,
        hasScripts,
        hasExamples,
        hasTests
      };

      // Cache the loaded skill
      this.skillCache.set(skillName, loadedSkill);

      return loadedSkill;
    } catch (error) {
      console.error(`Error loading skill ${skillName}:`, error);
      return null;
    }
  }

  /**
   * Load instructions for a skill (most common use case for LLM agents)
   */
  loadInstructions(skillName: string): string | null {
    const skill = this.loadSkill(skillName);
    return skill ? skill.instructions : null;
  }

  /**
   * Load config for a skill
   */
  loadConfig(skillName: string): SkillConfig | null {
    const skill = this.loadSkill(skillName);
    return skill ? skill.config : null;
  }

  /**
   * Load examples for a skill
   */
  loadExamples(skillName: string): Record<string, any>[] {
    const skill = this.loadSkill(skillName);
    if (!skill || !skill.hasExamples) {
      return [];
    }

    try {
      const exampleFiles = fs.readdirSync(skill.metadata.examplesPath)
        .filter(file => file.endsWith('.json') || file.endsWith('.md'));

      return exampleFiles.map(file => {
        const filePath = path.join(skill.metadata.examplesPath, file);
        const content = fs.readFileSync(filePath, 'utf-8');

        if (file.endsWith('.json')) {
          return JSON.parse(content);
        } else {
          return { filename: file, content };
        }
      });
    } catch (error) {
      console.error(`Error loading examples for skill ${skillName}:`, error);
      return [];
    }
  }

  /**
   * Get skill by tags (for discovery)
   */
  findSkillsByTag(tag: string): LoadedSkill[] {
    const allSkills = this.discoverSkills();
    return allSkills
      .map(metadata => this.loadSkill(metadata.name))
      .filter(skill => skill && skill.config.tags.includes(tag)) as LoadedSkill[];
  }

  /**
   * Get skills by owner
   */
  findSkillsByOwner(owner: string): LoadedSkill[] {
    const allSkills = this.discoverSkills();
    return allSkills
      .map(metadata => this.loadSkill(metadata.name))
      .filter(skill => skill && skill.config.owners.includes(owner)) as LoadedSkill[];
  }

  /**
   * Validate skill structure
   */
  validateSkill(skillName: string): { valid: boolean; errors: string[] } {
    const skill = this.loadSkill(skillName);
    const errors: string[] = [];

    if (!skill) {
      return { valid: false, errors: ['Skill not found or failed to load'] };
    }

    // Check required fields in config
    if (!skill.config.skill_name) errors.push('Missing skill_name in config');
    if (!skill.config.version) errors.push('Missing version in config');
    if (!skill.config.description) errors.push('Missing description in config');

    // Check required files
    if (!skill.instructions || skill.instructions.length === 0) {
      errors.push('Missing or empty instructions.md');
    }

    if (!fs.existsSync(skill.metadata.configPath)) {
      errors.push('Missing config.json');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Clear cache (useful for development/testing)
   */
  clearCache(): void {
    this.skillCache.clear();
  }

  /**
   * Get all skills grouped by category/owner
   */
  getSkillsCatalog(): Record<string, LoadedSkill[]> {
    const allSkills = this.discoverSkills();
    const catalog: Record<string, LoadedSkill[]> = {};

    allSkills.forEach(metadata => {
      const skill = this.loadSkill(metadata.name);
      if (!skill) return;

      skill.config.owners.forEach(owner => {
        if (!catalog[owner]) {
          catalog[owner] = [];
        }
        catalog[owner].push(skill);
      });
    });

    return catalog;
  }

  /**
   * Export skill as JSON for agent consumption
   */
  exportSkillForAgent(skillName: string): string | null {
    const skill = this.loadSkill(skillName);
    if (!skill) return null;

    const agentPayload = {
      name: skill.metadata.name,
      version: skill.config.version,
      description: skill.config.description,
      instructions: skill.instructions,
      required_inputs: skill.config.dependencies.required_data,
      optional_inputs: skill.config.dependencies.optional_data || [],
      expected_outputs: skill.config.outputs,
      examples: this.loadExamples(skillName)
    };

    return JSON.stringify(agentPayload, null, 2);
  }
}

// Export singleton instance
export const skillLoader = new SkillLoader();

// Convenience functions
export function loadSkill(skillName: string): LoadedSkill | null {
  return skillLoader.loadSkill(skillName);
}

export function loadInstructions(skillName: string): string | null {
  return skillLoader.loadInstructions(skillName);
}

export function discoverSkills(): SkillMetadata[] {
  return skillLoader.discoverSkills();
}

export function findSkillsByTag(tag: string): LoadedSkill[] {
  return skillLoader.findSkillsByTag(tag);
}
