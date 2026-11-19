// FreeCodeCamp & Microsoft C# Certification - Contoso Pets Application
// Guided Project: Console application to manage animal pet shelter profiles

using System;

class ContosoPets
{
    static void Main()
    {
        int maxPets = 8;
        string[,] ourAnimals = new string[maxPets, 6];

        // Seed sample data
        ourAnimals[0, 0] = "ID #: d1";
        ourAnimals[0, 1] = "Species: dog";
        ourAnimals[0, 2] = "Age: 2";
        ourAnimals[0, 3] = "Nickname: lola";
        ourAnimals[0, 4] = "Physical description: medium sized cream colored female golden retriever";
        ourAnimals[0, 5] = "Personality: friendly, energetic, loves tennis balls";

        ourAnimals[1, 0] = "ID #: d2";
        ourAnimals[1, 1] = "Species: dog";
        ourAnimals[1, 2] = "Age: 9";
        ourAnimals[1, 3] = "Nickname: loki";
        ourAnimals[1, 4] = "Physical description: large reddish-brown male golden retriever";
        ourAnimals[1, 5] = "Personality: calm, loves belly rubs and gentle walks";

        ourAnimals[2, 0] = "ID #: c3";
        ourAnimals[2, 1] = "Species: cat";
        ourAnimals[2, 2] = "Age: 1";
        ourAnimals[2, 3] = "Nickname: paws";
        ourAnimals[2, 4] = "Physical description: small white female with black ears";
        ourAnimals[2, 5] = "Personality: playful, curious, climbs everything";

        Console.WriteLine("=================================================");
        Console.WriteLine(" Welcome to the Contoso Pet Friends App! ");
        Console.WriteLine("=================================================");
        Console.WriteLine("\nCurrent Pet Inventory:\n");

        for (int i = 0; i < maxPets; i++)
        {
            if (ourAnimals[i, 0] != null && ourAnimals[i, 0] != "ID #: ")
            {
                Console.WriteLine($"Pet #{i + 1}:");
                for (int j = 0; j < 6; j++)
                {
                    Console.WriteLine($"  {ourAnimals[i, j]}");
                }
                Console.WriteLine();
            }
        }
    }
}
