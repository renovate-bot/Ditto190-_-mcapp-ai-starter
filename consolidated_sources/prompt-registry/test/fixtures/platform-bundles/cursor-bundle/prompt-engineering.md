# Cursor Prompt Engineering

## Effective Prompt Strategies

### Code Generation Prompts

```
Generate a TypeScript function that:
- Takes an array of objects with 'name' and 'age' properties
- Filters adults (age >= 18)
- Sorts by age in descending order
- Returns the top N results
Include proper TypeScript types and JSDoc comments.
```

### Code Explanation Prompts

```
Explain this code snippet:
- What does it do?
- What are the potential edge cases?
- How could it be optimized?
- Are there any security concerns?
```

### Refactoring Prompts

```
Refactor this code to:
- Use modern ES6+ features
- Improve readability and maintainability
- Add proper error handling
- Follow clean code principles
```

## Advanced Techniques

### Context Building

- Provide relevant code context before asking questions
- Include error messages and stack traces when debugging
- Specify the framework/library versions you're using

### Iterative Development

- Start with high-level architecture questions
- Gradually dive into implementation details
- Ask for alternative approaches to compare solutions

### Code Review Assistance

- Ask AI to review your code for bugs and improvements
- Request specific feedback on performance or security
- Get suggestions for better naming and structure

## Best Practices

- Be specific about requirements and constraints
- Ask for explanations of AI suggestions
- Verify generated code through testing
- Use AI to learn new concepts and patterns
