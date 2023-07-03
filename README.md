## Coding Challenge-3: Natural Language Queries Against a Structural Database

### Tasks:
**1. Handle single step queries**
e.g. "What are the targets of vorinostat?", "Find drugs that are used for treating ulcerative colitis." etc.

- Drug and disease queries appear to be working fine
- Querying for drug targets appears to use a completely different GraphQL syntax than the others. I'm not sure why. GPT is having issues returning the correct syntax most of the time.

**2. 2-step queries**
e.g. "Which diseases are associated with the genes targetted by fasudil?", "Show all the diseases that have at least 5 pathways associated with Alzheimer"

### Expectations:
- You can build the solution on Jupyter notebook, but we prefer to see as a CLI functionality
- The response should list the queried entities, no extra paragraphs or text.
   - I left the debug message prints in, such as `Querying Open Targets genetics database...`. Hopefully that's ok.
- We will test the solution on a set of held out instructions and questions (10 cases for each task). 
- You may need an OpenAI account for OpenAI api or a similar LLM API access. 

### Potential Enhancements:

- Current prompt is low accuracy because we only provide an example query for two use cases.
  - Rather than using a single prompt to generate the GraphQL query, we could improve both efficiency/cost and accuracy by first classifying the use case, and including only that example in the prompt.
  - Another alternative, which at least improves accuracy, is simply providing an example of every query type (assuming they can all fit within a single prompt).
- Should retry transient OpenAI and Open Targets API errors, while providing an explanation and gracefully exiting for permanent errors. I wrote a error retrying blurb with `tenacity` but left it commented out to avoid dependencies.
- Can use vector cache to store semantically similar user queries
