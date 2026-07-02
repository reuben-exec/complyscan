# ComplyScan Frontend Development Plan

## Project Overview
Building a professional frontend for ComplyScan (NABH Compliance Dashboard) following superhuman-inspired design patterns. The interface should be clean, professional, and tester-friendly while maintaining medical/clinical credibility.

## Current State
- Frontend at `backend/static/` with chapter/requirement analysis views, file upload, and LLM-enhanced analysis
- Existing UI has functional navigation with tag-based indicators for LLM evaluation, manual overrides, and LLM disagreement flags
- Disagreement badges (red) alert reviewers when LLM overrides strong keyword-based Pass 1 results

## Design Principles

### Superhuman-Inspired Elements
1. **Performance-focused**: Fast load times, responsive interactions
2. **Premium visual hierarchy**: Clear information architecture for medical data
3. **Keyboard-first**: Efficient navigation for power users (testers, reviewers)
4. **Subtle animations**: Professional micro-interactions without distraction
5. **Color psychology**: Medical whites/grays with accent colors for compliance status

### Medical/Clincial Credibility
1. **Clean whitespace**: Reduces cognitive load for review
2. **Structured data presentation**: Table-based evidence review
3. **Clear status indicators**: Color-coded compliance (green/yellow/red)
4. **Professional typography**: Sans-serif, readable at clinical distances

### Tester/Reviewer UX
1. **Progress indicators**: Clear feedback on analysis stage
2. **Disagreement flags**: Red badges highlight LLM overrides of strong Pass 1 findings
3. **Batch operations**: Efficient handling of multiple requirements
4. **Search and filter**: Fast navigation through 24 requirements
5. **Export capabilities**: PDF reports for documentation

## Design System Specifications

### Color Palette
- **Primary**: Medical blue (#1a365d) - clinical, trustworthy
- **Secondary**: Dark charcoal (#2d3748) - premium text
- **Background**: Off-white (#f7fafc) - reduces eye strain
- **Surface**: White (#ffffff) - clean contrast
- **Status colors**:
  - Compliant: Teal (#2d7a55)
  - Partial: Gold (#d69e2e) 
  - Non-compliant: Coral (#e53e3e)
  - Not found: Steel gray (#718096)

### Typography
- **Headings**: Inter, 20px+, weight 600
- **Body**: Inter, 14px, line-height 1.5
- **Code/Monospace**: SF Mono, 12px for evidence extraction

### Component Library
1. **Cards**: Soft shadows, rounded corners (8px radius)
2. **Buttons**: Minimum 44px height, subtle hover states
3. **Tables**: Striped rows for evidence review
4. **Forms**: Focus states with accessible color contrast
5. **Modals**: Backdrop blur, smooth fade/scale
6. **Tags**: Small uppercase badges for LLM (purple), Manual (amber/gold), Disagreement (red) indicators

## UI Animations & Micro-interactions

### Subtle Enhancements
1. **Card hover lift**: 2px elevation on hover
2. **Button press**: Scale down feedback
3. **Status badge transitions**: Smooth color changes
4. **Loading spinner**: Pulse animation
5. **Score bar fill**: Animated width on update

### Feedback Mechanisms
1. **Success states**: Checkmark + color update
2. **Error handling**: Inline validation with clear messages
3. **Override workflow**: Visual distinction of modified items
4. **LLM Disagreement**: Red badge (`⚠ Override`) when LLM overturns a strong Pass 1 finding
5. **Analysis progress**: Step indicator visual

## Page Structure & Information Architecture

### Main Navigation
- **Header**: Brand + status indicator
- **Sidebar**: Quick access to commonly used requirements
- **Breadcrumb**: Context tracking (Chapters > Requirements > Analysis)

### Chapter Selection
1. **Grid layout**: 2-3 cards per row
2. **Hover expansion**: Slight card elevation and icon shift
3. **Clear descriptions**: Medical terminology with plain language explanation

### Requirement List
1. **Search/filter bar**: Requirement ID + title search
2. **Batch actions**: Select multiple for report generation
3. **Quick view**: Requirement preview on hover

### Analysis View
1. **Side-by-side layout**: Text input + results panel
2. **Split view**: 60/40 or 50/50 based on screen width
3. **Context preservation**: Previous analysis state maintained

## Interactive Features

### Keyboard Shortcuts
- `q`/`e` - Navigate chapters
- `/` - Focus text search
- `Enter` - Run analysis
- `Escape` - Close modals
- `m` - Toggle override mode

### Progress Tracking
1. **Analysis stages**: Pass 1 (keyword) → Pass 2 (LLM semantic)
2. **Progress bar**: Shows completion within requirement set
3. **Timing indicator**: Shows response time metrics

### Data Visualization
1. **Compliance radar**: Multi-dimensional score display
2. **Evidence breakdown**: Pie chart of status distribution
3. **Trend indicators**: Comparison with previous analyses (if stored)

## Technical Implementation Plan

### Phase 1: Foundation
1. **Enhance CSS**: Refactor to use CSS custom properties
2. **Component library**: Extract reusable components
3. **Responsive design**: Mobile-first approach with desktop enhancements
4. **Accessibility**: WCAG 2.1 AA compliance audit

### Phase 2: Interactions
1. **Animation framework**: Add gsap or Framer Motion integration
2. **Micro-interactions**: Haptic feedback simulation
3. **Transition effects**: Smooth page navigation
4. **Visual feedback**: Loading states and error recovery

### Phase 3: Advanced Features
1. **Smart search**: Client-side filtering for 24 requirements
2. **Analysis comparison**: Side-by-side requirement analysis
3. **Saved presets**: User-defined text templates
4. **Export improvements**: Multi-format report generation

## Testing & Validation

### User Testing (Testers & Reviewers)
1. **Task scenarios**:
   - "Find HIC-R01 compliance in the uploaded document"
   - "Override incorrect compliance status"
   - "Generate PDF report for audit trail"
2. **Performance testing**: Target <1s analysis load time for 20-page PDFs
3. **Usability testing**: Reduce clicks from document to result by 30%

### Acceptance Criteria
- All existing functionality preserved and enhanced
- Visual polish adds to medical professionalism
- Response times remain <30s for 20-page documents
- New features don't break existing workflows
- Mobile responsive with progressive enhancement

## Implementation Timeline

- **Week 1**: Design system upgrade and component library
- **Week 2**: Interactive animations and micro-interactions
- **Week 3**: Advanced features and optimization
- **Week 4**: Testing, QA, and deployment preparation

## Files to Modify
1. `backend/static/styles.css` - Complete redesign
2. `backend/static/index.html` - New component structure
3. `backend/static/index.js` - Enhanced interaction logic
4. `AGENTS.md` - Document design decisions and patterns

## Success Metrics
- User satisfaction score >=85%
- Analysis completion time <=30 seconds
- Mobile responsiveness score >=90%
- Visual polish rating >=4/5 (professional appearance)
- Performance score >=95%