# Learning Notes — Project 03

Complete this during implementation; do not invent reflections before encountering real issues.

## Mistakes and fixes

1. **Mistake:** [What failed? Include test/command.]  
   **Root cause:** [...]  
   **Fix:** [...]  
   **Regression test:** [...]

2. **Mistake:** [...]  
   **Root cause:** [...]  
   **Fix:** [...]  
   **Regression test:** [...]

3. **Mistake:** [...]  
   **Root cause:** [...]  
   **Fix:** [...]  
   **Regression test:** [...]

## Design trade-offs

- Why does the baseline keep row outcomes in memory?
- What is the memory cost of the seen-order-ID set?
- How would deterministic output be preserved while streaming?
- Why do per-file atomic replacements not make the output set transactional?
