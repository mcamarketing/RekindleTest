# Gemini CLI Quick Reference Guide

## Installation Status
✅ **Installed**: `@google/gemini-cli@preview` (global installation)

---

## Authentication

### Option 1: Google Account (Free Tier)
- **Limits**: 1,000 requests/day, 60 requests/minute
- **Steps**:
  1. Run `gemini` in terminal
  2. Type `/auth` and press Enter
  3. Select Google login option
  4. Complete OAuth flow in browser

### Option 2: API Key (Paid)
- **Benefits**: Faster performance, use preferred models (e.g., Gemini 2.5 Pro)
- **Setup**: Create `.env` file with `GEMINI_API_KEY=your_key_here`

---

## Basic Commands

### Launch Gemini CLI
```bash
gemini
```

### Authentication
```bash
gemini /auth
```

### Check Version
```bash
gemini --version
```

### Get Help
```bash
gemini --help
```

---

## Common Workflows

### 1. Code Generation & Refactoring
```bash
# Generate code from description
gemini "Create a React component for user profile"

# Refactor existing code
gemini "Refactor this function to use async/await" < file.ts

# Explain code
gemini "Explain what this code does" < file.ts
```

### 2. Project Context Awareness
Gemini CLI can understand your project structure when run from the project root:
```bash
cd C:\Users\Hello\OneDrive\Documents\REKINDLE
gemini "Add error handling to the authentication flow"
```

### 3. File Operations
```bash
# Work with specific files
gemini "Optimize this component" --file src/components/App.tsx

# Batch operations
gemini "Add TypeScript types to all functions" --file src/**/*.ts
```

---

## Cursor IDE Integration

### Features Available in Cursor:
- ✅ **Context-aware suggestions**: Gemini understands your codebase
- ✅ **In-editor diffing**: See changes before applying
- ✅ **Intelligent code completion**: AI-powered suggestions
- ✅ **Real-time feedback**: Get suggestions as you type

### Using in Cursor:
1. **Terminal Integration**: Open Cursor's integrated terminal and run `gemini` commands
2. **Command Palette**: Use Cursor's command palette to access Gemini CLI features
3. **Inline Suggestions**: Gemini CLI provides suggestions directly in your editor

---

## Best Practices

### 1. Start with Context
Always run Gemini CLI from your project root to maintain context:
```bash
cd C:\Users\Hello\OneDrive\Documents\REKINDLE
gemini "your command here"
```

### 2. Use Specific Prompts
- ❌ Bad: "Fix the bug"
- ✅ Good: "Fix the authentication error in App.tsx that occurs when user logs in"

### 3. Review Diffs Before Applying
Gemini CLI shows diffs in Cursor - always review before accepting changes.

### 4. Iterative Refinement
Break large tasks into smaller prompts:
```bash
# Step 1: Understand the problem
gemini "Analyze the performance issues in the dashboard"

# Step 2: Implement solution
gemini "Optimize the dashboard rendering using React.memo"

# Step 3: Test and verify
gemini "Add unit tests for the optimized dashboard component"
```

---

## Advanced Usage

### Using with Environment Variables
```bash
# Set API key for session
$env:GEMINI_API_KEY="your_key_here"
gemini "your command"
```

### Piping Files
```bash
# Process file content
Get-Content src/App.tsx | gemini "Add error boundaries"
```

### Batch Processing
```bash
# Process multiple files
gemini "Add JSDoc comments" --file src/**/*.{ts,tsx}
```

---

## Troubleshooting

### Issue: Command not found
**Solution**: Ensure npm global bin is in your PATH
```powershell
npm config get prefix
# Add the output path to your system PATH
```

### Issue: Authentication fails
**Solution**: 
1. Clear cache: `gemini /logout`
2. Re-authenticate: `gemini /auth`

### Issue: Rate limit exceeded
**Solution**: 
- Wait for rate limit reset (60 requests/minute)
- Consider upgrading to paid API key for higher limits

---

## Project-Specific Tips

### For REKINDLE Project:
- **Backend**: Use Gemini CLI for API endpoint optimization
- **Frontend**: Leverage for React component generation and refactoring
- **Database**: Generate SQL queries and migrations
- **Documentation**: Auto-generate docs from code comments

### Example Commands for This Project:
```bash
# Backend optimization
gemini "Optimize the database queries in backend/routes"

# Frontend enhancement
gemini "Add loading states to all async operations in src/components"

# Documentation
gemini "Generate API documentation from the backend routes"
```

---

## Quick Command Cheat Sheet

| Task | Command |
|------|---------|
| Generate component | `gemini "Create React component for X"` |
| Refactor code | `gemini "Refactor X to use Y pattern" --file path/to/file` |
| Add tests | `gemini "Add unit tests for X component"` |
| Fix bugs | `gemini "Fix the bug in X that causes Y"` |
| Optimize performance | `gemini "Optimize X for better performance"` |
| Add documentation | `gemini "Add JSDoc comments to X"` |
| Explain code | `gemini "Explain how X works" --file path/to/file` |

---

## Resources

- **Official Docs**: [Google Gemini CLI Documentation](https://ai.google.dev/gemini-api/docs)
- **GitHub**: Check for latest updates and examples
- **Community**: Join discussions for tips and tricks

---

**Last Updated**: $(Get-Date -Format "yyyy-MM-dd")
**Status**: ✅ Ready to use

