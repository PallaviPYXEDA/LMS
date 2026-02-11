This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/pages/api-reference/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `pages/index.tsx`. The page auto-updates as you edit the file.

## AI code generation instructions.

### Core Principles:
1. **Simplicity First** - Always choose the simplest solution that works
2. **Minimum Changes** - Make only the necessary changes to achieve the goal
3. **No Over-Engineering** - Avoid unnecessary complexity or abstractions
4. **Production Ready** - All code should be production-level quality

### Best Practices:
1. **Follow React/Next.js Best Practices** - Use established patterns and conventions
2. **Code Organization** - Maintain clean folder structure (api/, components/, hooks/, utils/, types/, constants/)
3. **Reusability** - When possible write components and functions that can be reused across the project
4. **Type Safety** - Use TypeScript properly with clear interfaces and types

### Technical Guidelines:
1. **Folder Structure** - Keep related files grouped logically
2. **Component Design** - Small, focused components with single responsibilities
3. **API Integration** - Centralize API calls in dedicated service files
4. **State Management** - Use React hooks appropriately, avoid unnecessary state
5. **Styling** - Use Tailwind CSS consistently, maintain design system

### Quality Standards:
1. **Clean Code** - Write readable, maintainable code
2. **Documentation** - Add comments only when necessary for complex logic
3. **Testing Ready** - Structure code to be easily testable
4. **Scalability** - Consider how changes will scale with the project growth

### Other instuctions
1. Please show me the files you changed and explain the changes after you are done 
2. Api success response format

`response = {
        'status': 'success',
        'data': data,
        'errors': []
}
`
3. API failure response format

`response = {
        "status": "failure",
        "data": None,
        "errors": errors
}
`

## Suggested folder structure
📁 Frontend/
├── 📄 package.json
├── 📄 next.config.ts
├── 📄 tsconfig.json
├── 📄 aws-exports.ts
├── 📄 README.md
├── 📄 .gitignore
│
├── 📁 src/
│   ├── 📁 pages/
│   ├── 📁 components/
│   ├── 📁 api/
│   ├── 📁 types/
│   ├── 📁 styles/
│   └── 📁 constants/
│
├── 📁 scripts/
├── 📁 public/
└── 📁 node_modules/