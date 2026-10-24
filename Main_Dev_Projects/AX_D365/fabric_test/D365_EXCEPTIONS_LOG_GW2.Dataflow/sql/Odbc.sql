-- Made by: Hazzard
-- D365 warehouse work exception log (Riverton C79), full staging row plus extraction stamp
SELECT
    'D365'                          AS DATA_BASE,
    'C79'                           AS ORG_CODE,
    'RIVERTON'                     AS ORG_NAME,
    'HVAC'                          AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy') AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')   AS EXECUTION_TIME,
    work_exception.*
FROM SIWHSWorkExceptionLogStaging work_exception;
