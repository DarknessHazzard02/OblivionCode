// Made by: Hazzard
// FreeCodeCamp & Microsoft C# Certification - Student Grading Calculator
// Teaches: Variables, Arrays, Foreach loops, Arithmetic operations, String formatting

using System;

class StudentGrading
{
    static void Main()
    {
        int currentAssignments = 5;

        int[] sophiaScores = new int[] { 90, 86, 87, 98, 100 };
        int[] andrewScores = new int[] { 92, 89, 81, 96, 90 };
        int[] emmaScores   = new int[] { 90, 85, 87, 98, 68 };
        int[] loganScores  = new int[] { 90, 95, 87, 88, 96 };

        string[] studentNames = new string[] { "Sophia", "Andrew", "Emma", "Logan" };
        int[] studentScores = new int[10];

        Console.WriteLine("Student\t\tGrade\n");

        foreach (string name in studentNames)
        {
            string currentStudent = name;

            if (currentStudent == "Sophia")
                studentScores = sophiaScores;
            else if (currentStudent == "Andrew")
                studentScores = andrewScores;
            else if (currentStudent == "Emma")
                studentScores = emmaScores;
            else if (currentStudent == "Logan")
                studentScores = loganScores;

            int sumAssignmentScores = 0;
            decimal currentStudentGrade = 0;

            foreach (int score in studentScores)
            {
                sumAssignmentScores += score;
            }

            currentStudentGrade = (decimal)sumAssignmentScores / currentAssignments;

            string currentStudentLetterGrade = "";

            if (currentStudentGrade >= 97)
                currentStudentLetterGrade = "A+";
            else if (currentStudentGrade >= 93)
                currentStudentLetterGrade = "A";
            else if (currentStudentGrade >= 90)
                currentStudentLetterGrade = "A-";
            else if (currentStudentGrade >= 87)
                currentStudentLetterGrade = "B+";
            else if (currentStudentGrade >= 83)
                currentStudentLetterGrade = "B";
            else if (currentStudentGrade >= 80)
                currentStudentLetterGrade = "B-";
            else if (currentStudentGrade >= 77)
                currentStudentLetterGrade = "C+";
            else if (currentStudentGrade >= 70)
                currentStudentLetterGrade = "C";
            else
                currentStudentLetterGrade = "F";

            Console.WriteLine($"{currentStudent}\t\t{currentStudentGrade}\t{currentStudentLetterGrade}");
        }
    }
}
