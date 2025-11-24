# Contributing to RekindlePro

## Code Steward/Repo Guardian Workflows

REX (Autonomous Orchestration System) serves as the Code Steward and Repo Guardian for the RekindlePro repository. Using GitHub MCP (Model Context Protocol), REX automates code quality maintenance, documentation updates, and repository health monitoring.

### GitHub MCP Integration

REX leverages GitHub MCP to interact with the repository through standardized protocols, enabling secure and efficient code stewardship operations.

## Workflow: Scanning TODOs/FIXMEs

REX performs automated scanning of the codebase for TODO and FIXME comments to identify areas requiring attention.

### Process
1. **Daily Automated Scan**: REX uses GitHub MCP to search across all source files for TODO/FIXME patterns
2. **Context Analysis**: Extracts surrounding code context and file metadata
3. **Priority Assessment**: Evaluates urgency based on code location, age, and impact
4. **Report Generation**: Creates structured reports with actionable items
5. **Assignment**: Routes findings to appropriate development workflows

### Implementation Details
- Search patterns: `TODO`, `FIXME`, `XXX`, `HACK`
- File types: `.py`, `.ts`, `.js`, `.tsx`, `.md`
- Exclusions: Generated files, test fixtures, documentation

## Workflow: Proposing Refactors

REX analyzes code patterns and proposes structural improvements to maintain code quality.

### Process
1. **Code Analysis**: Uses GitHub MCP to read source files and analyze patterns
2. **Quality Metrics**: Evaluates complexity, duplication, and maintainability
3. **Refactor Proposals**: Generates specific improvement suggestions
4. **Impact Assessment**: Estimates effort and risk of proposed changes
5. **PR Creation**: Implements approved refactors via branch and pull request

### Refactor Types
- Code duplication elimination
- Function/method extraction
- Class/interface restructuring
- Performance optimizations
- Security improvements

## Workflow: Updating Documentation

REX maintains comprehensive documentation automatically, ensuring accuracy and currency.

### Target Documents
- **REX_README.md**: System overview, architecture, and usage guides
- **REX_IMPLEMENTATION_COMPLETE.md**: Implementation status and completion tracking
- **Architecture Documentation**: System diagrams and component specifications

### Process
1. **Change Detection**: Monitors repository activity via GitHub MCP
2. **Content Analysis**: Reviews code changes and their documentation impact
3. **Update Generation**: Creates or modifies documentation content
4. **Review Integration**: Incorporates feedback from automated checks
5. **Publication**: Updates documentation via controlled PR process

## Workflow: Auto-Generating Documentation

REX generates technical documentation from code analysis and system metadata.

### Generated Content
- API documentation from FastAPI endpoints
- Component architecture diagrams
- Database schema documentation
- Integration guides
- Performance benchmarks

### Process
1. **Code Parsing**: Analyzes source code structure and annotations
2. **Metadata Extraction**: Gathers system configuration and runtime data
3. **Documentation Synthesis**: Combines analysis with existing templates
4. **Validation**: Ensures generated content accuracy and completeness
5. **Integration**: Merges with existing documentation repositories

## Write Operations and Branch Management

All write operations performed by REX follow strict version control practices to ensure traceability and review.

### Branch Strategy
- **Branch Naming**: `chore/mcp-{operation}-{timestamp}`
  - Examples: `chore/mcp-refactor-auth-20250124`, `chore/mcp-docs-update-20250124`
- **Base Branch**: `main` for production changes, `develop` for experimental features

### Pull Request Process
1. **Automated PR Creation**: REX creates PRs with descriptive titles
2. **Title Format**: `chore/mcp-{component}-{action}`
   - Examples: `chore/mcp-supabase-wiring`, `chore/mcp-docs-regeneration`
3. **Description**: Includes change rationale, impact assessment, and testing notes
4. **Review Requirements**: Requires approval from designated maintainers
5. **Merge Strategy**: Squash merge with automated commit messages

### Quality Gates
- Automated testing (unit, integration, linting)
- Security scanning
- Documentation validation
- Performance regression checks

## Maintenance Workflows

REX performs ongoing maintenance to ensure repository health and system reliability.

### Daily Maintenance
- Code quality scans
- Dependency vulnerability checks
- Test suite execution
- Documentation freshness validation

### Weekly Maintenance
- Comprehensive codebase analysis
- Performance benchmark updates
- Security audit reports
- Documentation completeness review

### Monthly Maintenance
- Architecture diagram regeneration
- Code coverage analysis
- Technical debt assessment
- Compliance documentation updates

### Emergency Maintenance
- Critical security patch application
- System outage response
- Data integrity restoration
- Incident postmortem documentation

## Instructions for Agents

### Agent Configuration
Agents interacting with GitHub MCP must be configured with appropriate permissions and rate limiting.

### Authentication
- Use GitHub Personal Access Tokens with minimal required scopes
- Implement token rotation for security
- Monitor API rate limits and implement backoff strategies

### Error Handling
- Implement retry logic for transient failures
- Log detailed error context for debugging
- Escalate critical failures to human operators

### Best Practices
- Batch operations to minimize API calls
- Cache results appropriately to reduce redundant requests
- Validate all inputs and outputs
- Maintain audit trails for all operations

### Monitoring and Alerting
- Track operation success rates
- Monitor API usage and limits
- Alert on failure patterns
- Generate performance reports

## Development Guidelines

### Code Standards
- Follow existing code style and conventions
- Maintain comprehensive test coverage
- Document all public APIs and interfaces
- Implement proper error handling

### Testing Requirements
- Unit tests for all new functionality
- Integration tests for system interactions
- Performance tests for critical paths
- Security tests for authentication and authorization

### Documentation Standards
- Update relevant documentation for all changes
- Include code examples and usage patterns
- Maintain changelog entries
- Update API documentation

### Security Considerations
- Never commit sensitive information
- Implement proper input validation
- Follow principle of least privilege
- Regularly update dependencies

## Getting Help

- **Documentation**: Refer to REX_README.md for system overview
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and feedback
- **Support**: Contact the development team for urgent issues