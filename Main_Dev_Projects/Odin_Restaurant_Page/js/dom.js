// Made by: Hazzard
// Odin Restaurant Page - tiny element builder shared by the tab modules (no innerHTML).

export function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  Object.entries(props).forEach(([key, value]) => {
    if (key === "class") node.className = value;
    else node.setAttribute(key, value);
  });
  node.append(...children);
  return node;
}

export function withAccent(before, accent, after = "") {
  return [before, el("span", {}, accent), after];
}
