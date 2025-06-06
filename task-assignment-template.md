# Task Assignment Best Practices

## File Ownership Strategy

### Example Task Breakdown:

**Task 1: Project Setup & Configuration**
- Owns: package.json, tsconfig.json, next.config.js, tailwind.config.ts, postcss.config.js
- Creates: .npmrc, .nvmrc, .gitignore

**Task 2: Layout & Structure**
- Owns: src/app/layout.tsx, src/app/globals.css
- Creates: src/components/layout/, src/styles/

**Task 3: Homepage Components**
- Owns: src/app/page.tsx
- Creates: src/components/home/

**Task 4: Shared UI Components**
- Owns: src/components/ui/
- Creates: All shared components

**Task 5: Feature Page A**
- Owns: src/app/features/page.tsx
- Creates: src/components/features/

## Task Description Template

```markdown
## Task: [Task Name]

### Owned Files (DO NOT let other agents modify):
- src/components/[component-name]/
- src/app/[page-name]/page.tsx

### Shared Files (coordinate changes):
- package.json (only add new dependencies)
- src/lib/utils.ts (only add new utilities)

### Creates New:
- src/components/[component-name]/index.tsx
- src/components/[component-name]/styles.css

### Dependencies:
- Wait for: Task 1 (Project Setup)
- Blocks: Task 8 (Integration)
```