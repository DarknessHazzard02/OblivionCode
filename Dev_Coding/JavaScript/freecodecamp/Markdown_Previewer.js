// Made by: Hazzard
// FreeCodeCamp Front End Development Libraries - Markdown Previewer (React + marked)
// The preview HTML is sanitized with DOMPurify before it is injected.
// Run it: open ../../HTML/freecodecamp/FCC_JS_Runner.html?app=Markdown_Previewer

const h = React.createElement;

// ==============================================================================
// Default text: covers every element the challenge asks for
// ==============================================================================
const DEFAULT_MARKDOWN = `# Markdown Previewer
## A sub-heading

Inline code: \`const answer = 42;\`

\`\`\`js
function greet(name) {
  return \`Hello, \${name}\`;
}
\`\`\`

- Lists
- with **bold** text

> A block quote.

[A link](https://www.freecodecamp.org)

![Placeholder image](data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='40'%3E%3Crect width='120' height='40' fill='%23e0262e'/%3E%3C/svg%3E)
`;

marked.setOptions({ breaks: true, gfm: true });

const render = (text) => DOMPurify.sanitize(marked.parse(text));

// ==============================================================================
// Component
// ==============================================================================
function Previewer() {
  const [text, setText] = React.useState(DEFAULT_MARKDOWN);

  return h("div", { className: "split" },
    h("section", { className: "card" },
      h("h2", null, "Editor"),
      h("textarea", {
        id: "editor",
        value: text,
        onChange: (e) => setText(e.target.value),
        spellCheck: false,
      })
    ),
    h("section", { className: "card" },
      h("h2", null, "Preview"),
      h("div", { id: "preview", className: "md", dangerouslySetInnerHTML: { __html: render(text) } })
    )
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(Previewer));
