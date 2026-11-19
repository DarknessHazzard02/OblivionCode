# Made by: Hazzard
# The Odin Project - Ruby: Sub Strings. Counts how many times each dictionary word appears
# inside the text, case-insensitive, including inside longer words. Run: ruby sub_strings.rb

def substrings(text, dictionary)
  lowered = text.downcase
  dictionary.each_with_object({}) do |word, counts|
    count = lowered.scan(word.downcase).length
    counts[word] = count if count.positive?
  end
end

if __FILE__ == $PROGRAM_NAME
  dictionary = %w[below down go going horn how howdy it i low own part partner sit]
  raise 'single word failed' unless substrings('below', dictionary) == { 'below' => 1, 'low' => 1 }
  expected = { 'down' => 1, 'go' => 1, 'going' => 1, 'how' => 2, 'howdy' => 1, 'it' => 2, 'i' => 3,
               'own' => 1, 'part' => 1, 'partner' => 1, 'sit' => 1 }
  result = substrings("Howdy partner, sit down! How's it going?", dictionary)
  raise "sentence failed: #{result}" unless result == expected
  puts result.inspect
  puts 'Sub Strings: all checks passed.'
end
