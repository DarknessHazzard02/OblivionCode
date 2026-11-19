-- Other Sources: Advanced Sales Analytics Queries
-- Features: Window functions (ROW_NUMBER, DENSE_RANK, SUM OVER PARTITION), CTEs, and Running Totals

WITH MonthlySales AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS sales_month,
        department,
        SUM(amount) AS monthly_revenue
    FROM sales_orders
    GROUP BY DATE_TRUNC('month', order_date), department
),
RankedDepartments AS (
    SELECT 
        sales_month,
        department,
        monthly_revenue,
        DENSE_RANK() OVER (PARTITION BY sales_month ORDER BY monthly_revenue DESC) AS dept_rank,
        SUM(monthly_revenue) OVER (PARTITION BY department ORDER BY sales_month) AS cumulative_department_revenue
    FROM MonthlySales
)
SELECT 
    sales_month,
    department,
    monthly_revenue,
    dept_rank,
    cumulative_department_revenue
FROM RankedDepartments
WHERE dept_rank <= 3
ORDER BY sales_month DESC, dept_rank ASC;
