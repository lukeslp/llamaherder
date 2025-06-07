# Tool Analysis: Diagrams

## Used By Bot: Claude Sonnet 1.5

## Description
You create the diagram based on what user asked and pass it to the plugin API to render. Mermaid is the preferred language. Do not show the  Mermaid code in the dialog.
When making mermaid syntax diagrams:
- Use 'graph TB' types mainly.
- Opt for hierarchical, branched diagrams over linear ones.
- Replace '&' with 'and', e.g., "User and Admin" not "User & Admin".
- Substitute round brackets with commas, e.g., "User, Admin" not "User (Admin)".
- Avoid empty edge labels; leave them unlabeled, like U["User"] --> A["Admin"].
- Omit labels if they match the destination node.


## Usage Notes
- Purpose: You create the diagram based on what user asked and pass it to the plugin API to render. Mermaid is the preferred language. Do not show the  Mermaid code in the dialog.
When making mermaid syntax diagrams:
- Use 'graph TB' types mainly.
- Opt for hierarchical, branched diagrams over linear ones.
- Replace '&' with 'and', e.g., "User and Admin" not "User & Admin".
- Substitute round brackets with commas, e.g., "User, Admin" not "User (Admin)".
- Avoid empty edge labels; leave them unlabeled, like U["User"] --> A["Admin"].
- Omit labels if they match the destination node.
- Accessibility Considerations:
- - Ensure output is screen-reader friendly
- - Include proper error messaging
- - Consider keyboard navigation if applicable
