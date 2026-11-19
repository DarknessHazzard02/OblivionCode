// Made by: Hazzard
// FreeCodeCamp Certification Project - Cash Register
// Design a cash register drawer function checkCashRegister() that accepts purchase price as the first argument (price),
// payment as the second argument (cash), and cash-in-drawer (cid) as the third argument.

const DENOMINATIONS = [
  { name: "ONE HUNDRED", val: 100.00 },
  { name: "TWENTY",      val: 20.00 },
  { name: "TEN",         val: 10.00 },
  { name: "FIVE",        val: 5.00 },
  { name: "ONE",         val: 1.00 },
  { name: "QUARTER",     val: 0.25 },
  { name: "DIME",        val: 0.10 },
  { name: "NICKEL",      val: 0.05 },
  { name: "PENNY",       val: 0.01 }
];

function checkCashRegister(price, cash, cid) {
  let changeDue = Math.round((cash - price) * 100) / 100;
  
  // Calculate total cash in drawer
  let totalCID = cid.reduce((sum, curr) => sum + curr[1], 0);
  totalCID = Math.round(totalCID * 100) / 100;

  if (totalCID < changeDue) {
    return { status: "INSUFFICIENT_FUNDS", change: [] };
  }

  if (totalCID === changeDue) {
    return { status: "CLOSED", change: cid };
  }

  // Map cid to reverse order matching DENOMINATIONS
  const drawerMap = {};
  cid.forEach(([denom, amount]) => {
    drawerMap[denom] = Math.round(amount * 100) / 100;
  });

  const changeArray = [];

  for (const { name, val } of DENOMINATIONS) {
    let amountTaken = 0;
    while (changeDue >= val && drawerMap[name] > 0) {
      amountTaken = Math.round((amountTaken + val) * 100) / 100;
      drawerMap[name] = Math.round((drawerMap[name] - val) * 100) / 100;
      changeDue = Math.round((changeDue - val) * 100) / 100;
    }
    if (amountTaken > 0) {
      changeArray.push([name, amountTaken]);
    }
  }

  if (changeDue > 0) {
    return { status: "INSUFFICIENT_FUNDS", change: [] };
  }

  return { status: "OPEN", change: changeArray };
}

// Tests
console.log("=== Cash Register Tests ===");

console.log("\nTest 1 - Normal Change:");
console.log(checkCashRegister(19.5, 20, [
  ["PENNY", 1.01], ["NICKEL", 2.05], ["DIME", 3.1], ["QUARTER", 4.25],
  ["ONE", 90], ["FIVE", 55], ["TEN", 20], ["TWENTY", 60], ["ONE HUNDRED", 100]
]));

console.log("\nTest 2 - Exact Drawer Closed:");
console.log(checkCashRegister(19.5, 20, [
  ["PENNY", 0.5], ["NICKEL", 0], ["DIME", 0], ["QUARTER", 0],
  ["ONE", 0], ["FIVE", 0], ["TEN", 0], ["TWENTY", 0], ["ONE HUNDRED", 0]
]));

console.log("\nTest 3 - Insufficient Funds in specific coins:");
console.log(checkCashRegister(19.5, 20, [
  ["PENNY", 0.01], ["NICKEL", 0], ["DIME", 0], ["QUARTER", 0],
  ["ONE", 1], ["FIVE", 0], ["TEN", 0], ["TWENTY", 0], ["ONE HUNDRED", 0]
]));
