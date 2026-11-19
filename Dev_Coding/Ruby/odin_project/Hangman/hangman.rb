# Made by: Hazzard
# The Odin Project - Ruby: Hangman. Picks a 5-12 letter word from words.txt, allows 7 misses,
# and can save the game to saves/<name>.json and load it back at the start.
# Run: ruby hangman.rb

require 'json'

class Hangman
  MAX_MISSES = 7
  WORDS_FILE = File.join(__dir__, 'words.txt')
  SAVE_DIR = File.join(__dir__, 'saves')

  attr_reader :word, :guesses, :misses

  def initialize(word: nil, guesses: [], misses: 0)
    @word = word || pick_word
    @guesses = guesses
    @misses = misses
  end

  def self.from_json(text)
    data = JSON.parse(text)
    unless data['word'].is_a?(String) && data['guesses'].is_a?(Array) && data['misses'].is_a?(Integer)
      raise ArgumentError, 'save file is missing word, guesses or misses'
    end

    new(word: data['word'], guesses: data['guesses'], misses: data['misses'])
  end

  def to_json(*_args)
    JSON.generate({ word: @word, guesses: @guesses, misses: @misses })
  end

  def masked
    @word.chars.map { |char| @guesses.include?(char) ? char : '_' }.join(' ')
  end

  # Returns :repeat, :hit or :miss.
  def guess(letter)
    return :repeat if @guesses.include?(letter)

    @guesses << letter
    return :hit if @word.include?(letter)

    @misses += 1
    :miss
  end

  def won?
    @word.chars.all? { |char| @guesses.include?(char) }
  end

  def lost?
    @misses >= MAX_MISSES
  end

  private

  def pick_word
    words = File.readlines(WORDS_FILE, chomp: true).map(&:strip).map(&:downcase)
    words.select! { |w| w.length.between?(5, 12) && w.match?(/\A[a-z]+\z/) }
    raise "No 5-12 letter words in #{WORDS_FILE}" if words.empty?

    words.sample
  end
end

def save_game(game)
  Dir.mkdir(Hangman::SAVE_DIR) unless Dir.exist?(Hangman::SAVE_DIR)
  print 'Save name (letters, digits, _ or -): '
  name = $stdin.gets.to_s.strip
  unless name.match?(/\A[\w-]{1,30}\z/)
    puts 'Invalid name. Game not saved.'
    return false
  end
  File.write(File.join(Hangman::SAVE_DIR, "#{name}.json"), game.to_json)
  puts "Saved as #{name}. Bye!"
  true
end

def load_game
  saves = Dir.exist?(Hangman::SAVE_DIR) ? Dir.children(Hangman::SAVE_DIR).grep(/\.json\z/).sort : []
  return Hangman.new if saves.empty?

  puts 'Saved games:'
  saves.each_with_index { |file, i| puts "  #{i + 1}. #{File.basename(file, '.json')}" }
  print 'Number to load, or Enter for a new game: '
  choice = $stdin.gets.to_s.strip
  return Hangman.new if choice.empty?

  file = saves[choice.to_i - 1]
  raise ArgumentError, 'no save with that number' if file.nil? || choice.to_i < 1

  Hangman.from_json(File.read(File.join(Hangman::SAVE_DIR, file)))
rescue ArgumentError, JSON::ParserError => e
  puts "Could not load that save (#{e.message}). Starting a new game."
  Hangman.new
end

def play
  game = load_game
  until game.won? || game.lost?
    puts "\n#{game.masked}   misses: #{game.misses}/#{Hangman::MAX_MISSES}   tried: #{game.guesses.join(' ')}"
    print "Guess a letter (or type 'save'): "
    input = $stdin.gets
    return puts("\nBye.") if input.nil?

    input = input.strip.downcase
    return if input == 'save' && save_game(game)
    next puts('Type a single letter a-z.') unless input.match?(/\A[a-z]\z/)

    puts 'You already tried that letter.' if game.guess(input) == :repeat
  end
  puts game.won? ? "\nYou win! The word was #{game.word}." : "\nYou lose. The word was #{game.word}."
end

def self_check
  game = Hangman.new(word: 'ruby')
  raise 'hit failed' unless game.guess('r') == :hit
  raise 'repeat failed' unless game.guess('r') == :repeat
  raise 'miss failed' unless game.guess('z') == :miss && game.misses == 1
  restored = Hangman.from_json(game.to_json)
  raise 'save round trip failed' unless restored.masked == 'r _ _ _' && restored.misses == 1
  %w[u b y].each { |l| restored.guess(l) }
  raise 'win failed' unless restored.won?
  puts 'Self-check passed.'
end

if __FILE__ == $PROGRAM_NAME
  ARGV.include?('--check') ? self_check : play
end
