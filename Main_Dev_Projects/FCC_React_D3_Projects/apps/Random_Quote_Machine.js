// Made by: Hazzard
// FreeCodeCamp Front End Development Libraries - Random Quote Machine (React)
// No build step: uses React.createElement instead of JSX.
// Run it: open ../FCC_JS_Runner.html?app=Random_Quote_Machine

const h = React.createElement;

// ==============================================================================
// Data: well-known short quotes
// ==============================================================================
const QUOTES = [
  { text: "Simplicity is prerequisite for reliability.", author: "Edsger W. Dijkstra" },
  { text: "Premature optimization is the root of all evil.", author: "Donald Knuth" },
  { text: "First, solve the problem. Then, write the code.", author: "John Johnson" },
  { text: "Talk is cheap. Show me the code.", author: "Linus Torvalds" },
  { text: "Programs must be written for people to read.", author: "Harold Abelson" },
  { text: "Make it work, make it right, make it fast.", author: "Kent Beck" },
  { text: "The best error message is the one that never shows up.", author: "Thomas Fuchs" },
  { text: "Without data, you're just another person with an opinion.", author: "W. Edwards Deming" },
];

const pickIndex = (exclude) => {
  let i;
  do {
    i = Math.floor(Math.random() * QUOTES.length);
  } while (i === exclude && QUOTES.length > 1);
  return i;
};

// ==============================================================================
// Component
// ==============================================================================
function QuoteBox() {
  const [index, setIndex] = React.useState(() => pickIndex(-1));
  const quote = QUOTES[index];
  const tweetUrl =
    "https://twitter.com/intent/tweet?text=" +
    encodeURIComponent(`"${quote.text}" - ${quote.author}`);

  return h("div", { id: "quote-box", className: "card" },
    h("p", { id: "text", className: "quote" }, `"${quote.text}"`),
    h("p", { id: "author", className: "muted" }, `- ${quote.author}`),
    h("div", { className: "row" },
      h("a", { id: "tweet-quote", href: tweetUrl, target: "_blank", rel: "noopener noreferrer", className: "btn ghost" }, "Tweet"),
      h("button", { id: "new-quote", className: "btn", onClick: () => setIndex(pickIndex(index)) }, "New quote")
    )
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(QuoteBox));
