// Made by: Hazzard
// FreeCodeCamp & Microsoft C# Certification - Fraudulent Order Detector
// Teaches: Arrays, Foreach iteration, String methods (StartsWith)

using System;

class FraudulentOrderDetector
{
    static void Main()
    {
        string[] orderIDs = { "B123", "C234", "A345", "C15", "B177", "G3003", "C235", "B179" };

        Console.WriteLine("=== Fraudulent Order Audit ===");
        Console.WriteLine("Scanning for flagged order IDs starting with 'B'...\n");

        int fraudCount = 0;

        foreach (string orderID in orderIDs)
        {
            if (orderID.StartsWith("B"))
            {
                Console.WriteLine($"[FLAGGED] Potential fraudulent order detected: {orderID}");
                fraudCount++;
            }
        }

        Console.WriteLine($"\nAudit Complete: {fraudCount} fraudulent orders identified.");
    }
}
