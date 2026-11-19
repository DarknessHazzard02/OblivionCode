// Made by: Hazzard
// FreeCodeCamp - Role Playing Game (Dragon Repeller)
// Teaches: Objects, Arrays of Objects, Game Logic, State Management

let xp = 0;
let health = 100;
let gold = 50;
let currentWeapon = 0;
let inventory = ["stick"];

const weapons = [
  { name: "stick", power: 5 },
  { name: "dagger", power: 30 },
  { name: "claw hammer", power: 50 },
  { name: "sword", power: 100 }
];

const monsters = [
  { name: "Slime", level: 2, health: 15 },
  { name: "Fanged Beast", level: 8, health: 60 },
  { name: "Dragon", level: 20, health: 300 }
];

function buyHealth() {
  if (gold >= 10) {
    gold -= 10;
    health += 10;
    console.log(`Bought 10 health. Gold: ${gold}, Health: ${health}`);
  } else {
    console.log("You do not have enough gold to buy health.");
  }
}

function buyWeapon() {
  if (currentWeapon < weapons.length - 1) {
    if (gold >= 30) {
      gold -= 30;
      currentWeapon++;
      let newWeapon = weapons[currentWeapon].name;
      inventory.push(newWeapon);
      console.log(`Purchased ${newWeapon}. Gold: ${gold}. Inventory: ${inventory.join(", ")}`);
    } else {
      console.log("You do not have enough gold to buy a weapon.");
    }
  } else {
    console.log("You already have the most powerful weapon!");
  }
}

function fightMonster(monsterIndex) {
  let monster = { ...monsters[monsterIndex] };
  console.log(`\n--- Fighting ${monster.name} (HP: ${monster.health}) ---`);

  while (monster.health > 0 && health > 0) {
    // Player attacks
    const playerDamage = weapons[currentWeapon].power + Math.floor(Math.random() * xp) + 1;
    monster.health -= playerDamage;
    console.log(`You hit the ${monster.name} with your ${weapons[currentWeapon].name} for ${playerDamage} damage. (Monster HP: ${Math.max(0, monster.health)})`);

    if (monster.health <= 0) {
      gold += Math.floor(monster.level * 6.7);
      xp += monster.level;
      console.log(`You defeated the ${monster.name}! You earned ${monster.level} XP and gold.`);
      console.log(`Current Stats -> XP: ${xp}, Health: ${health}, Gold: ${gold}`);
      return;
    }

    // Monster attacks
    const monsterDamage = Math.max(1, (monster.level * 5) - Math.floor(Math.random() * xp));
    health -= monsterDamage;
    console.log(`The ${monster.name} attacks! You take ${monsterDamage} damage. (Player HP: ${Math.max(0, health)})`);
  }

  if (health <= 0) {
    console.log("You have died! Game Over.");
  }
}

// Gameplay Simulation
console.log("Initial State -> Health:", health, "Gold:", gold, "Weapon:", weapons[currentWeapon].name);
buyHealth();
buyWeapon();
fightMonster(0); // Fight Slime
fightMonster(1); // Fight Fanged Beast
