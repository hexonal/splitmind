# Conflict Prevention Guide for Multi-Agent Development

## The Problem
When multiple AI agents work on the same codebase simultaneously, they often:
1. Modify the same files (package.json, layout.tsx, etc.)
2. Create overlapping functionality
3. Use different approaches for similar problems
4. Make incompatible architectural decisions

## Solution 1: Layer-Based Architecture

### Foundation Layer (Tasks 1-3)
**Purpose**: Set up project structure, configuration, and core systems
**Example Tasks**:
- Project initialization (owns: package.json, configs)
- Core layout system (owns: layout.tsx, global styles)
- Base component library (owns: components/ui/)

### Feature Layer (Tasks 4-10)
**Purpose**: Build independent features that don't overlap
**Example Tasks**:
- Homepage sections (owns: components/home/, app/page.tsx)
- About page (owns: app/about/, components/about/)
- Contact page (owns: app/contact/, components/contact/)

### Integration Layer (Tasks 11-15)
**Purpose**: Connect features, add polish, optimize
**Example Tasks**:
- Navigation system (reads all, modifies layout)
- Animations (adds to existing components)
- SEO/Performance (modifies configs, adds meta)

## Solution 2: Smart Task Descriptions

### Bad Task Description:
```
Task: Create homepage
Description: Build the homepage with hero section, features, and contact form
```

### Good Task Description:
```
Task: Homepage Hero Section ONLY
Description: 
- Create components/home/HeroSection.tsx
- DO NOT modify app/page.tsx (Task 8 will integrate)
- DO NOT modify layout.tsx
- DO NOT add to package.json
- Export component for later integration
```

## Solution 3: Explicit File Ownership

### In AI Task Master prompt:
```python
task_config = {
    "homepage_hero": {
        "owns": ["components/home/HeroSection.tsx", "components/home/HeroSection.css"],
        "creates": ["components/home/HeroSection.tsx", "components/home/HeroSection.css"],
        "reads": ["lib/utils.ts", "components/ui/button.tsx"],
        "never_modify": ["app/page.tsx", "app/layout.tsx", "package.json"]
    }
}
```

## Solution 4: Integration Tasks

Always include integration tasks that:
1. Come after feature tasks
2. Have permission to modify shared files
3. Resolve any integration issues
4. Ensure consistent styling/behavior

Example:
```
Task 12: Homepage Integration
Dependencies: [hero_section, feature_cards, contact_section]
Description: 
- Integrate all homepage components into app/page.tsx
- Ensure consistent spacing and styling
- Add smooth scroll navigation
- Resolve any conflicts between sections
```

## Solution 5: Architectural Rules in CLAUDE.md

Add clear rules to CLAUDE.md:

```markdown
## Architecture Rules

### Component Structure
- Each major section gets its own folder in components/
- Never modify another task's component folder
- Export all components through index.ts

### State Management
- Use React Context for global state
- Each feature manages its own local state
- Never add global state without coordination

### Styling Rules
- Use Tailwind classes only
- No inline styles
- No new CSS files without approval
- Reuse existing design tokens

### File Modification Rules
- NEVER modify package.json after Task 1
- NEVER modify layout.tsx after Task 2
- NEVER modify global styles after Task 2
- Create new files in your assigned folders only
```

## Solution 6: Dependency-Based Scheduling

Enhance the orchestrator to:
1. Check file ownership before spawning agents
2. Delay tasks if their required files are being modified
3. Queue tasks that need the same shared files

## Solution 7: Component Composition Pattern

Instead of modifying existing files, use composition:

```typescript
// Bad: Modifying existing page
// app/page.tsx
export default function Home() {
  return (
    <div>
      <Hero />
      <Features /> // Agent 2 adds this line - CONFLICT!
    </div>
  )
}

// Good: Component registry pattern
// lib/page-sections.ts
export const pageSections = {
  home: [] // Each agent adds their section here
}

// app/page.tsx (set up once)
import { pageSections } from '@/lib/page-sections'

export default function Home() {
  return (
    <div>
      {pageSections.home.map((Section, i) => (
        <Section key={i} />
      ))}
    </div>
  )
}
```

## Implementation Checklist

1. **Update Task Model** ✓ (partially done)
2. **Enhance AI Task Master** to assign file ownership
3. **Add Pre-Spawn Checks** in orchestrator
4. **Create Integration Task Templates**
5. **Update CLAUDE.md Template** with rules
6. **Add Conflict Detection** before merge
7. **Create Task Validation** system

## Example: Conflict-Free Website Project

```yaml
Wave 1 - Foundation:
  task_1:
    title: "Project Setup"
    owns: ["package.json", "*.config.*", ".npmrc", ".nvmrc"]
    
  task_2:
    title: "Layout System"
    owns: ["app/layout.tsx", "app/globals.css", "components/layout/"]
    
  task_3:
    title: "UI Component Library"
    owns: ["components/ui/", "lib/utils.ts"]

Wave 2 - Features:
  task_4:
    title: "Homepage Hero"
    creates: ["components/home/hero/"]
    never_touch: ["app/page.tsx"]
    
  task_5:
    title: "Homepage Features"  
    creates: ["components/home/features/"]
    never_touch: ["app/page.tsx"]

Wave 3 - Integration:
  task_10:
    title: "Homepage Assembly"
    owns: ["app/page.tsx"]
    integrates: ["components/home/*/"]
```

This approach would dramatically reduce conflicts!