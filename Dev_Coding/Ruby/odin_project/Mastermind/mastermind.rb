# Made by: Hazzard
# The Odin Project - Ruby: Mastermind. Play as codebreaker or codemaker against the computer.
# The computer breaker keeps only the codes consistent with every answer so far.
# Run: ruby mastermind.rb

COLORS = %w[1 2 3 4 5 6].freeze
CODE_LENGTH = 4
MAX_TURNS = 12

# Returns [exact, color_only]: right color right place, and right color wrong place.
def score(guess, code)
  exact = guess.zip(code).count { |g, c| g == c }
  common = COLORS.sum { |color| [guess.count(color), code.count(color)].min }
  [exact, common - exact]
end

def all_codes
  COLORS.repeated_permutation(CODE_LENGTH).to_a
end

def read_code(prompt)
  loop do
    print prompt
    input = $stdin.gets
    raise Interrupt if input.nil?

    digits = input.strip.chars
    return digits if digits.length == CODE_LENGTH && digits.all? { |d| COLORS.include?(d) }

    puts "Enter #{CODE_LENGTH} digits from #{COLORS.first} to #{COLORS.last}, for example 1123."
  end
end

def play_breaker
  code = Array.new(CODE_LENGTH) { COLORS.sample }
  MAX_TURNS.times do |turn|
    guess = read_code("Turn #{turn + 1}/#{MAX_TURNS} - your guess: ")
    exact, near = score(guess, code)
    puts "  exact: #{exact}  right color, wrong place: #{near}"
    return puts('You cracked the code!') if exact == CODE_LENGTH
  end
  puts "Out of turns. The code was #{code.join}."
end

def play_maker
  code = read_code('Your secret code (the computer will not peek): ')
  candidates = all_codes
  guess = %w[1 1 2 2]
  MAX_TURNS.times do |turn|
    feedback = score(guess, code)
    puts "Computer turn #{turn + 1}: #{guess.join}  exact: #{feedback[0]}  near: #{feedback[1]}"
    return puts("The computer found your code in #{turn + 1} turns.") if feedback[0] == CODE_LENGTH

    candidates.select! { |candidate| score(guess, candidate) == feedback }
    guess = candidates.first
  end
  puts 'The computer ran out of turns. You win!'
end

def self_check
  raise 'score exact failed' unless score(%w[1 2 3 4], %w[1 2 3 4]) == [4, 0]
  raise 'score near failed' unless score(%w[1 1 2 2], %w[2 2 1 1]) == [0, 4]
  raise 'score duplicates failed' unless score(%w[1 1 1 1], %w[1 2 3 4]) == [1, 0]
  candidates = all_codes
  code = %w[6 5 4 3]
  guess = %w[1 1 2 2]
  turns = 1
  until guess == code
    feedback = score(guess, code)
    candidates.select! { |candidate| score(guess, candidate) == feedback }
    guess = candidates.first
    turns += 1
  end
  raise "breaker too slow: #{turns}" if turns > MAX_TURNS

  puts "Self-check passed (computer solved 6543 in #{turns} turns)."
end

if __FILE__ == $PROGRAM_NAME
  if ARGV.include?('--check')
    self_check
  else
    begin
      print 'Play as (1) codebreaker or (2) codemaker? '
      choice = $stdin.gets.to_s.strip
      choice == '2' ? play_maker : play_breaker
    rescue Interrupt
      puts "\nBye."
    end
  end
end
