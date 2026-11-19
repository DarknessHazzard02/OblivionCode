// Made by: Hazzard
// FreeCodeCamp & Microsoft C# Certification - Subscription Renewal Notice
// Teaches: Decision logic, nested conditionals, variable scoping

using System;

class SubscriptionNotice
{
    static void Main()
    {
        Random random = new Random();
        int daysUntilExpiration = random.Next(12);
        int discountPercentage = 0;

        Console.WriteLine($"Days until subscription expires: {daysUntilExpiration}");

        if (daysUntilExpiration == 0)
        {
            Console.WriteLine("Your subscription has expired.");
        }
        else if (daysUntilExpiration == 1)
        {
            Console.WriteLine("Your subscription expires within a day!");
            discountPercentage = 20;
        }
        else if (daysUntilExpiration <= 5)
        {
            Console.WriteLine($"Your subscription expires in {daysUntilExpiration} days.");
            discountPercentage = 10;
        }
        else if (daysUntilExpiration <= 10)
        {
            Console.WriteLine("Your subscription will expire soon. Renew now!");
        }

        if (discountPercentage > 0)
        {
            Console.WriteLine($"Renew now and save {discountPercentage}%!");
        }
    }
}
