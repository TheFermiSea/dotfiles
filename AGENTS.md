# Global AI Agent Guidelines

This file provides guidelines for AI agents working across all projects for user: **squires.b@gmail.com**

## ByteRover Shared Memory System

**All projects should use ByteRover for persistent memory and cross-agent coordination.**

### Standard Workflow

```bash
# 1. Start session - retrieve context
brv retrieve -q "topic or feature"

# 2. Work - code, test, verify
# ... your work here ...

# 3. Record - add learnings
brv add -s "Section" -c "file:line - Specific finding"

# 4. Share - push to shared space (with user approval)
brv push -y
```

### Best Practices

**Always:**
- Retrieve context before starting work
- Include file:line references in learnings
- Use standard sections (Lessons Learned, Best Practices, Common Errors, Architecture, Testing)
- Reference related issues (bd-XXX, GitHub issues, etc.)
- Share knowledge after completing work

**Never:**
- Skip context retrieval
- Write vague memories without file references
- Use non-standard sections without good reason
- Push without user approval

### Writing Effective Memories

**Template:**
```
src/path/file.rs:line - [Problem/Pattern]. [Solution]. [Rationale]. Related: issue-XXX
```

**Good Examples:**

✅ Specific and actionable:
```bash
brv add -s "Common Errors" -c "src/api/auth.rs:89 - Token expiration not checked before API calls. Add if token.is_expired() check. Prevents 401 errors. Related: issue-456"
```

✅ Includes context and rationale:
```bash
brv add -s "Best Practices" -c "Use async/await for all I/O operations in Node.js services. Prevents blocking event loop. See server.js:123 for pattern. 10x throughput improvement measured"
```

❌ Too vague:
```bash
brv add -s "Notes" -c "Fixed auth bug"
```

### Standard Sections

Use these across all projects for consistency:

- **Lessons Learned** - Discoveries and new insights
- **Best Practices** - Proven patterns and approaches
- **Common Errors** - Bugs and their solutions
- **Architecture** - Design decisions and trade-offs
- **Testing** - Test strategies and patterns
- **Project Structure and Dependencies** - Organization and setup
- **Code Style and Quality** - Conventions and standards

### Project-Specific Configuration

Each project may have additional ByteRover configuration:

- Check for `.byterover-quick-ref.md` in project root
- Review project-specific `AGENTS.md` for workflows
- Follow project conventions (issue trackers, code standards)

### Cross-Project Learning

ByteRover enables learning across projects:

```bash
# Retrieve patterns from other projects
brv retrieve -q "authentication JWT patterns"

# May find memories from multiple projects
# Apply learnings to current project
# Record new insights specific to this project
```

### Troubleshooting

**Authentication issues:**
```bash
brv logout
brv login  # Use squires.b@gmail.com
```

**Can't find project:**
```bash
cd /path/to/project
brv status  # Should show project connection
```

**No memories found:**
```bash
# Try broader search
brv retrieve -q "general topic"

# Or initialize new project
brv init
```

### Resources

- **ByteRover Dashboard**: https://app.byterover.com
- **CLI Documentation**: Run `brv --help`
- **Project-specific guides**: Check project's `docs/` directory

## Multi-Agent Coordination

When multiple AI agents work on the same project:

1. **Always retrieve first**: Get latest shared context
2. **Claim work**: Use issue tracker to avoid conflicts
3. **Record immediately**: Add learnings right after discoveries
4. **Push regularly**: Share knowledge frequently
5. **Cross-reference**: Mention other agents' findings when relevant

### Agent Types

Different agents for different tasks:

- **Claude Code**: Primary development, comprehensive tasks
- **Codex**: Code generation, quick implementations
- **Gemini**: Analysis, research, planning
- **Specialized agents**: Domain-specific work

All agents should follow the same ByteRover workflow regardless of specialty.

## Project Standards

### Issue Tracking

Projects may use different systems:
- **beads (bd)**: Rust projects, AI-friendly
- **GitHub Issues**: Open source projects
- **Linear/Jira**: Team projects

Always use the project's chosen system and reference IDs in memories.

### Code Quality

Tools vary by project:
- **Rust**: clippy, rustfmt, ast-grep, recurse.ml
- **TypeScript**: eslint, prettier, tsc
- **Python**: ruff, black, mypy

Run project-specific quality checks before pushing.

### Testing

Follow project testing conventions:
- Unit tests in same file/directory
- Integration tests in dedicated directory
- End-to-end tests when applicable
- Always run tests before committing

### Documentation

Keep documentation updated:
- Code comments for complex logic
- README for setup and usage
- Architecture docs for design decisions
- Changelog for significant changes

Record documentation updates in ByteRover for cross-agent awareness.

## Communication

### With User

- Ask for clarification when requirements unclear
- Report blockers immediately
- Suggest improvements when appropriate
- Document decisions in ByteRover

### With Other Agents

- Via ByteRover shared memory (primary)
- Via issue tracker comments (secondary)
- Via code comments (for implementation details)

### Cross-Session Context

ByteRover maintains context across sessions:

```bash
# Session 1: Agent A works
brv add -s "In Progress" -c "src/auth.rs - Implementing OAuth flow, 60% complete"
brv push -y

# Session 2: Agent B or same agent continues
brv retrieve -q "OAuth implementation progress"
# Finds Agent A's status, continues work
```

## Security and Privacy

**Never commit:**
- API keys, tokens, credentials
- Personal information
- Proprietary code without permission

**Always:**
- Use environment variables for secrets
- Review code before pushing
- Follow security best practices
- Document security considerations in ByteRover

## Success Criteria

An effective agent:

✅ Retrieves context before starting work
✅ Writes specific, actionable memories
✅ Uses standard sections consistently
✅ References files/lines in learnings
✅ Shares knowledge regularly
✅ Follows project conventions
✅ Produces working, tested code
✅ Documents design decisions

## Getting Help

**ByteRover Issues:**
- Check project's `.byterover-quick-ref.md`
- Review `docs/BYTEROVER_MULTI_AGENT_SETUP.md`
- Run `brv --help`

**Project Issues:**
- Check project's `CLAUDE.md` or `README.md`
- Review `AGENTS.md` in project root
- Ask user for clarification

**General Questions:**
- Search ByteRover memories across projects
- Review similar projects' learnings
- Consult official documentation

---

**Remember**: ByteRover is your persistent memory system. Use it consistently to improve over time and coordinate with other agents effectively.
