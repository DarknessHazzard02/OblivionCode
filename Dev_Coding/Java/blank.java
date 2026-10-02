public class SalesCalculator {

    public static void main(String[] args) {

        double[] sales = {1500, 2100, 1850, 3200, 2750};

        double totalSales = 0;

        for (double sale : sales) {
            totalSales += sale;
        }

        double averageSales = totalSales / sales.length;

        System.out.println("Total Sales: $" + totalSales);
        System.out.println("Average Sales: $" + averageSales);
    }
}