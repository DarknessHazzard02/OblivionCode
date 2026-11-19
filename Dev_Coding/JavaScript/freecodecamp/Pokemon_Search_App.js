// FreeCodeCamp Certification Project - Pokémon Search App Logic
// Teaches: Object lookup, normalization, Data Extraction, Stat formatting

const pokemonDatabase = [
  {
    id: 1,
    name: "bulbasaur",
    weight: 69,
    height: 7,
    types: ["grass", "poison"],
    stats: { hp: 45, attack: 49, defense: 49, "special-attack": 65, "special-defense": 65, speed: 45 }
  },
  {
    id: 4,
    name: "charmander",
    weight: 85,
    height: 6,
    types: ["fire"],
    stats: { hp: 39, attack: 52, defense: 43, "special-attack": 60, "special-defense": 50, speed: 65 }
  },
  {
    id: 7,
    name: "squirtle",
    weight: 90,
    height: 5,
    types: ["water"],
    stats: { hp: 44, attack: 48, defense: 65, "special-attack": 50, "special-defense": 64, speed: 43 }
  },
  {
    id: 25,
    name: "pikachu",
    weight: 60,
    height: 4,
    types: ["electric"],
    stats: { hp: 35, attack: 55, defense: 40, "special-attack": 50, "special-defense": 50, speed: 90 }
  },
  {
    id: 94,
    name: "gengar",
    weight: 405,
    height: 15,
    types: ["ghost", "poison"],
    stats: { hp: 60, attack: 65, defense: 60, "special-attack": 130, "special-defense": 75, speed: 110 }
  }
];

function searchPokemon(query) {
  const normalizedQuery = String(query).trim().toLowerCase();
  
  const found = pokemonDatabase.find(
    (p) => String(p.id) === normalizedQuery || p.name === normalizedQuery
  );

  if (!found) {
    return { error: "Pokémon not found" };
  }

  return {
    name: found.name.toUpperCase(),
    id: `#${found.id}`,
    weight: `Weight: ${found.weight}`,
    height: `Height: ${found.height}`,
    types: found.types.map((t) => t.toUpperCase()),
    hp: found.stats.hp,
    attack: found.stats.attack,
    defense: found.stats.defense,
    specialAttack: found.stats["special-attack"],
    specialDefense: found.stats["special-defense"],
    speed: found.stats.speed
  };
}

// Tests
console.log("=== Pokémon Search Results ===");
["25", "Pikachu", "gengar", "1", "mewtwo"].forEach((query) => {
  console.log(`\nQuery: "${query}"`);
  console.log(searchPokemon(query));
});
