// Made by: Hazzard
// Utility - Fibonacci Sequence Generator
// Demonstrates iterative calculation and array population in C#

using System;

class FibonacciGenerator
{
    static void Main()
    {
        int count = 15;
        long[] fibonacci = new long[count];

        fibonacci[0] = 0;
        fibonacci[1] = 1;

        for (int i = 2; i < count; i++)
        {
            fibonacci[i] = fibonacci[i - 1] + fibonacci[i - 2];
        }

        Console.WriteLine($"=== First {count} Fibonacci Numbers ===");
        for (int i = 0; i < count; i++)
        {
            Console.WriteLine($"F({i}) = {fibonacci[i]}");
        }
    }
}
