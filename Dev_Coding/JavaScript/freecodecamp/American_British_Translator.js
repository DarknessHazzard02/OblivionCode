// FreeCodeCamp Quality Assurance - American / British English Translator
// Translates dialect vocabulary, spelling conventions, titles, and time notation between American and British English

const americanToBritishSpelling = {
  "color": "colour",
  "favorite": "favourite",
  "flavor": "flavour",
  "honor": "honour",
  "center": "centre",
  "theater": "theatre",
  "meter": "metre",
  "organize": "organise",
  "realize": "realise",
  "apologize": "apologise"
};

const americanToBritishTitles = {
  "mr.": "Mr",
  "mrs.": "Mrs",
  "ms.": "Ms",
  "mx.": "Mx",
  "dr.": "Dr",
  "prof.": "Prof"
};

const americanOnly = {
  "trash can": "rubbish bin",
  "candy": "sweets",
  "cell phone": "mobile phone",
  "french fries": "chips",
  "sidewalk": "pavement",
  "apartment": "flat"
};

// Build reverse lookups
const britishToAmericanSpelling = Object.fromEntries(
  Object.entries(americanToBritishSpelling).map(([a, b]) => [b, a])
);

const britishToAmericanTitles = Object.fromEntries(
  Object.entries(americanToBritishTitles).map(([a, b]) => [b.toLowerCase(), a.charAt(0).toUpperCase() + a.slice(1)])
);

const britishOnly = Object.fromEntries(
  Object.entries(americanOnly).map(([a, b]) => [b, a])
);

function translate(text, locale) {
  if (!text || !locale) {
    return { error: "Required field(s) missing" };
  }
  if (locale !== "american-to-british" && locale !== "british-to-american") {
    return { error: "Invalid value for locale field" };
  }

  let translated = text;

  if (locale === "american-to-british") {
    // 1. Idioms
    for (const [am, br] of Object.entries(americanOnly)) {
      const regex = new RegExp(`\\b${am}\\b`, "gi");
      translated = translated.replace(regex, `<span class="highlight">${br}</span>`);
    }
    // 2. Titles
    for (const [am, br] of Object.entries(americanToBritishTitles)) {
      const regex = new RegExp(`\\b${am.replace(".", "\\.")}`, "gi");
      translated = translated.replace(regex, `<span class="highlight">${br}</span>`);
    }
    // 3. Spellings
    for (const [am, br] of Object.entries(americanToBritishSpelling)) {
      const regex = new RegExp(`\\b${am}\\b`, "gi");
      translated = translated.replace(regex, `<span class="highlight">${br}</span>`);
    }
    // 4. Time format: 10:30 -> 10.30
    translated = translated.replace(/(\b\d{1,2}):(\d{2}\b)/g, `<span class="highlight">$1.$2</span>`);
  } else {
    // British to American
    for (const [br, am] of Object.entries(britishOnly)) {
      const regex = new RegExp(`\\b${br}\\b`, "gi");
      translated = translated.replace(regex, `<span class="highlight">${am}</span>`);
    }
    for (const [br, am] of Object.entries(britishToAmericanTitles)) {
      const regex = new RegExp(`\\b${br}(?!\\.)\\b`, "gi");
      translated = translated.replace(regex, `<span class="highlight">${am}</span>`);
    }
    for (const [br, am] of Object.entries(britishToAmericanSpelling)) {
      const regex = new RegExp(`\\b${br}\\b`, "gi");
      translated = translated.replace(regex, `<span class="highlight">${am}</span>`);
    }
    // Time format: 10.30 -> 10:30
    translated = translated.replace(/(\b\d{1,2})\.(\d{2}\b)/g, `<span class="highlight">$1:$2</span>`);
  }

  if (translated === text) {
    return { text, translation: "Everything looks good to me!" };
  }

  return { text, translation: translated };
}

// Tests
console.log("=== American / British English Translator ===");
const ex1 = translate("Mangoes are my favorite fruit. Lunch is at 12:15 with Dr. Watson.", "american-to-british");
console.log("Original:   ", ex1.text);
console.log("Translation:", ex1.translation);

const ex2 = translate("We bought some sweets and ate them on the pavement.", "british-to-american");
console.log("\nOriginal:   ", ex2.text);
console.log("Translation:", ex2.translation);
