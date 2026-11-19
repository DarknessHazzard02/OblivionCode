# Made by: Hazzard
# The Odin Project - Ruby: Caesar Cipher. Shifts letters, keeps case, leaves everything else.
# Run: ruby caesar_cipher.rb

def caesar_cipher(text, shift)
  text.chars.map do |char|
    if char.match?(/[a-z]/)
      (((char.ord - 'a'.ord + shift) % 26) + 'a'.ord).chr
    elsif char.match?(/[A-Z]/)
      (((char.ord - 'A'.ord + shift) % 26) + 'A'.ord).chr
    else
      char
    end
  end.join
end

if __FILE__ == $PROGRAM_NAME
  raise 'shift 5 failed' unless caesar_cipher('What a string!', 5) == 'Bmfy f xywnsl!'
  raise 'wrap failed' unless caesar_cipher('xyz', 3) == 'abc'
  raise 'negative shift failed' unless caesar_cipher('abc', -3) == 'xyz'
  raise 'round trip failed' unless caesar_cipher(caesar_cipher('Hello, World', 13), 13) == 'Hello, World'
  puts caesar_cipher('What a string!', 5)
  puts 'Caesar Cipher: all checks passed.'
end
