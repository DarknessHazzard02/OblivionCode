// Made by: Hazzard
// Other Sources: String Reversal and Palindrome Checker in Java

public class StringManipulator {
    public static boolean isPalindrome(String input) {
        String clean = input.replaceAll("[^a-zA-Z0-9]", "").toLowerCase();
        int left = 0;
        int right = clean.length() - 1;

        while (left < right) {
            if (clean.charAt(left) != clean.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        String word = "Racecar";
        System.out.println("Is '" + word + "' a palindrome? " + isPalindrome(word));
    }
}
