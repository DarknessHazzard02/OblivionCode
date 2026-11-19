// Made by: Hazzard
// Other Sources: TypeScript Data Transformer Utility

export function chunkArray<T>(items: T[], size: number): T[][] {
  const result: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    result.push(items.slice(i, i + size));
  }
  return result;
}

const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
console.log("Chunked (size 3):", chunkArray(numbers, 3));
