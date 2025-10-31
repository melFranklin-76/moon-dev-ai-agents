# Claude Skills for Moon Dev Trading Agents

## What Are Claude Skills?

Claude Skills are **modular capabilities** that extend Claude's functionality through instructions, scripts, and resources. They're automatically loaded when needed - no manual invocation required.

Think of them as **expert knowledge packs** that make Claude instantly proficient in specific areas of your codebase.

## How Skills Work

### 3-Level Progressive Loading

**Level 1: Metadata (Always Loaded)**
- Skill name + description
- Claude knows when to activate this skill

**Level 2: Main Instructions (Loaded When Triggered)**
- `skill.md` file with core guidance
- Quick start commands
- Common workflows

**Level 3: Detailed Resources (Loaded As Needed)**
- Additional `.md` files for deep dives
- Loaded progressively to avoid context bloat
- Examples: strategies.md, setup.md, workflows.md

### Auto-Discovery

When you open this project in Claude Code or Claude Desktop:
1. Claude automatically scans `.claude/skills/` directory
2. Loads all skill metadata (Level 1)
3. Knows when to use each skill based on your questions
4. Loads deeper content only when needed

**No installation required!** Skills work immediately when you clone this repo.

## Available Skills

### 1. Small Account Dashboard

**Location:** `.claude/skills/small_account_dashboard/`

**What It Does:**
Gives instant expertise on the $250 Options Scalper Dashboard - a Streamlit trading dashboard with 20 battle-tested strategies, live scanner, and 10-day challenge tracker.

**When Claude Uses It:**
- Questions about the dashboard
- Setup and installation help
- Strategy explanations
- Troubleshooting issues
- Trading workflow guidance

**Files:**
- `skill.md` - Main instructions and quick reference
- `strategies.md` - Detailed breakdown of all 20 strategies (159-178)
- `setup.md` - Complete installation and configuration guide
- `workflows.md` - Step-by-step common tasks and trading routines

**Ask Questions Like:**
- "How do I run the small account dashboard?"
- "What is strategy #177 and how do I trade it?"
- "How do I set up Alpaca API?"
- "Walk me through the daily trading workflow"
- "How does the 10-day challenge work?"

---

## Using Skills

### In Claude Code / Claude Desktop

Just ask questions naturally:

```
"How do I run the small account dashboard?"
"What's the difference between strategy 163 and 164?"
"Show me how to execute a VWAP reclaim trade"
"What should I do if I hit my daily loss limit?"
```

Claude will automatically:
1. Recognize you're asking about the dashboard
2. Load the `small_account_dashboard` skill
3. Reference the appropriate files
4. Give you expert answers

### You'll Know It's Working When:

Claude will reference specific files like:
- "According to the dashboard skill..."
- "Based on strategies.md..."
- "The setup guide indicates..."

### Testing Skills

**Quick Test:**
Ask Claude: "What agents are available in this repo?"

If skills are working, Claude will give a detailed answer using the skill content.

---

## Creating Your Own Skills

### Basic Structure

```
.claude/skills/
  your_skill_name/
    skill.md          # Main file (required)
    resource_1.md     # Additional resource (optional)
    resource_2.md     # Additional resource (optional)
```

### skill.md Format

```markdown
---
name: Your Skill Name
description: Brief description (max 1024 chars) of what this skill covers
---

# Your Skill Name - Expert Knowledge

## What This Skill Covers
- Topic 1
- Topic 2
- Topic 3

## Quick Start Commands
\`\`\`bash
command_1
command_2
\`\`\`

## Core Concepts
(Your main content here)

## File References
For deeper information:
- **resource_1.md** - Details about X
- **resource_2.md** - Details about Y
```

### Best Practices

**1. Start Simple**
- Clear, concise instructions in `skill.md`
- Add complexity as needed

**2. Split Large Content**
- Main instructions in `skill.md`
- Deep dives in separate resource files
- Prevents context bloat

**3. Use Progressive Disclosure**
- Level 1: "This skill handles X, Y, Z"
- Level 2: "Here's how to do X"
- Level 3: "Here's every detail about X" (separate file)

**4. Test Iteratively**
- Ask Claude questions
- Refine based on answers
- Add missing information

---

## Skill Development Workflow

### 1. Plan Your Skill

**What expertise should it provide?**
- Topic/area coverage
- Common questions it should answer
- Resources it should reference

**Example:**
```
Skill: Trading Strategies
Answers:
- What strategies are available?
- How do I execute strategy X?
- What are the risk parameters?
Resources:
- Full strategy list
- Risk management rules
- Execution workflows
```

### 2. Create Skill Directory

```bash
mkdir -p .claude/skills/your_skill_name
```

### 3. Write skill.md

**Required YAML frontmatter:**
```yaml
---
name: Your Skill Name  # Max 64 characters
description: What this skill does and when to use it  # Max 1024 characters
---
```

**Content sections:**
- What this skill covers
- Quick start commands
- Core concepts
- Common workflows
- File references (for Level 3 resources)

### 4. Add Resource Files (Optional)

**When to use resource files:**
- Content too large for skill.md
- Deep technical details
- Step-by-step tutorials
- Reference documentation

**Example:**
```
strategies.md - All 20 strategies with examples
setup.md - Complete installation guide
workflows.md - Daily routines and common tasks
```

### 5. Test Your Skill

**Open Claude Code/Desktop and ask:**
```
"Tell me about [your topic]"
"How do I [perform task]?"
"Show me [specific detail]"
```

**Check if:**
- Claude recognizes when to use the skill
- Answers are accurate and helpful
- References correct files
- Loads resources progressively

### 6. Refine

Based on testing:
- Add missing information
- Clarify confusing sections
- Split large files if needed
- Update descriptions for better discovery

---

## Troubleshooting Skills

### Skill Not Loading

**Check:**
1. File location: `.claude/skills/skill_name/skill.md`
2. YAML frontmatter present and valid
3. File permissions readable
4. No syntax errors in markdown

**Restart Claude:**
- Close and reopen Claude Code/Desktop
- Skills are loaded at startup

### Skill Not Activating

**Improve description:**
```yaml
# Bad (too vague)
description: Trading stuff

# Good (specific)
description: Expert knowledge for $250 account dashboard with 20 strategies, live scanner, and 10-day challenge tracker
```

**Test activation:**
Ask directly: "Use the [skill name] skill to answer..."

### Wrong Information Provided

**Update skill.md:**
- Add missing details
- Clarify ambiguous sections
- Add examples

**Update resource files:**
- Fix incorrect information
- Add more context
- Include troubleshooting

---

## Security

### What NOT to Include

**Never put in skills:**
- ❌ API keys or secrets
- ❌ Passwords
- ❌ Private tokens
- ❌ Sensitive user data
- ❌ Proprietary algorithms (if confidential)

**These skills are in your repo:**
- Anyone who clones will see them
- Keep them educational and public-safe

### What's Safe

**Include:**
- ✅ Public documentation
- ✅ Setup instructions (without secrets)
- ✅ Code examples
- ✅ Workflows and best practices
- ✅ Architecture explanations

---

## Skill Maintenance

### When to Update Skills

**Add information when:**
- New features added to project
- Common questions arise
- Bugs fixed (update troubleshooting)
- Best practices change
- User feedback suggests missing info

### Versioning

Consider adding version to description:
```yaml
description: Dashboard v1.0 - Trading strategies and risk management
```

### Change Log

Maintain in skill.md if helpful:
```markdown
## Change Log

**v1.1 (2025-11-01)**
- Added strategy #177 BTC-Lead Sync details
- Updated Alpaca setup for new API

**v1.0 (2025-10-01)**
- Initial release
```

---

## Examples from This Repo

### Small Account Dashboard Skill

**Structure:**
```
.claude/skills/small_account_dashboard/
  skill.md (6KB)          - Quick start, overview, common workflows
  strategies.md (25KB)    - All 20 strategies with examples
  setup.md (15KB)         - Installation and configuration
  workflows.md (20KB)     - Daily routines, specific workflows
```

**Why This Works:**
- `skill.md` gives Claude instant context
- Resource files loaded only when needed
- Progressive detail (overview → specific → deep dive)
- Answers 95% of dashboard questions

**Usage Examples:**
```
User: "How do I run the dashboard?"
Claude: [Reads skill.md → gives commands]

User: "Explain strategy #177 in detail"
Claude: [Reads strategies.md → gives full breakdown]

User: "Walk me through the daily trading workflow"
Claude: [Reads workflows.md → gives step-by-step]
```

---

## Additional Resources

### Official Documentation
- [Anthropic Claude Skills Guide](https://docs.anthropic.com/en/docs/skills)
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)

### Community Examples
- [Anthropic Skills Cookbook](https://github.com/anthropics/skills-cookbook)

### Moon Dev Resources
- Main README: `../../README.md`
- Dashboard Guide: `../../SMALL_ACCOUNT_DASHBOARD_GUIDE.md`
- Trading Ideas: `../../trading_ideas.md` (if available)

---

## Contributing Skills

### Have an Idea for a Skill?

**Good skill candidates:**
- Common questions about part of codebase
- Complex setup procedures
- Domain-specific knowledge
- Workflow documentation

**Create it:**
1. Follow structure above
2. Test thoroughly
3. Submit PR or share

### Guidelines

**Skills should:**
- ✅ Be focused (one topic/area)
- ✅ Have clear use cases
- ✅ Use progressive disclosure
- ✅ Include examples
- ✅ Be well-tested

**Skills should NOT:**
- ❌ Duplicate existing documentation
- ❌ Be too broad (cover everything)
- ❌ Include sensitive information
- ❌ Require manual installation

---

## FAQ

**Q: Do skills work in the API?**
A: Skills are currently for Claude Code and Claude Desktop. API support may vary.

**Q: Can skills run code?**
A: Skills can include bash scripts that Claude can run. Output enters context, not the code itself.

**Q: How many skills can I have?**
A: No hard limit, but keep them focused. 5-10 well-designed skills better than 50 vague ones.

**Q: Do skills slow down Claude?**
A: No! Level 1 (metadata) is tiny. Deeper content only loads when needed.

**Q: Can I share skills?**
A: Yes! Bundle as `.zip` and share. Users extract to their `.claude/skills/` directory.

**Q: What if skills conflict?**
A: Claude is smart about using the right skill for the context. Keep descriptions specific.

**Q: Can I disable a skill?**
A: Rename the folder (add `.disabled` to name) or move it out of `.claude/skills/`.

**Q: Do skills work offline?**
A: Skill files are local, but Claude itself needs internet connection.

---

## Next Steps

**If you're new to skills:**
1. Try asking Claude questions about this project
2. See how it uses the dashboard skill
3. Explore the skill files to understand structure
4. Create your own skill for a part of your codebase

**If you're experienced:**
1. Review existing skills for improvements
2. Add skills for other parts of this repo
3. Share your skills with the community
4. Contribute to skills documentation

---

**Remember:** Skills are like having expert teammates who know your codebase inside out. They're always available, never forget details, and scale to help everyone on your team.

Build skills for the questions you answer repeatedly. Your future self (and teammates) will thank you. 🚀

