SELECT
    Employee_ID,
    Employee_Name,
    Department,
    Salary,
    Salary * 12 AS Annual_Salary
FROM Employees
WHERE Salary >= 5000
ORDER BY Salary DESC;