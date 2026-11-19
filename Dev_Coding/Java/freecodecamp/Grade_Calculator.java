// FreeCodeCamp: Java Programming Course
// Project: Grade & Weighted Score Calculator

public class GradeCalculator {
    public static void main(String[] args) {
        int[] scores = { 85, 92, 78, 90, 88 };
        int sum = 0;

        for (int score : scores) {
            sum += score;
        }

        double average = (double) sum / scores.length;
        char letterGrade;

        if (average >= 90) letterGrade = 'A';
        else if (average >= 80) letterGrade = 'B';
        else if (average >= 70) letterGrade = 'C';
        else if (average >= 60) letterGrade = 'D';
        else letterGrade = 'F';

        System.out.println("=== Student Grade Report ===");
        System.out.println("Average Score: " + average);
        System.out.println("Final Letter Grade: " + letterGrade);
    }
}
