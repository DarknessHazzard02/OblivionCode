const sales = [1500, 2100, 1850, 3200, 2750];

const totalSales = sales.reduce(
    (total, value) => total + value,
    0
);

const averageSales = totalSales / sales.length;

console.log(`Total Sales: $${totalSales}`);
console.log(`Average Sales: $${averageSales.toFixed(2)}`);