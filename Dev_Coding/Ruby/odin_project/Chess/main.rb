# Made by: Hazzard
# The Odin Project - Ruby: Chess, terminal entry point.
# Run: ruby main.rb   |   self-check without RSpec: ruby main.rb --check

require 'stringio'
require_relative 'lib/game'

def start
  saves = Dir.exist?(Game::SAVE_DIR) ? Dir.children(Game::SAVE_DIR).grep(/\.json\z/).sort : []
  unless saves.empty?
    puts 'Saved games:'
    saves.each_with_index { |file, i| puts "  #{i + 1}. #{File.basename(file, '.json')}" }
    print 'Number to load, or Enter for a new game: '
    choice = $stdin.gets.to_s.strip
    unless choice.empty?
      file = saves[choice.to_i - 1]
      if file && choice.to_i.positive?
        begin
          return Game.from_json(File.read(File.join(Game::SAVE_DIR, file))).play
        rescue ArgumentError, KeyError, JSON::ParserError => e
          puts "Could not load that save (#{e.message}). Starting a new game."
        end
      else
        puts 'No save with that number. Starting a new game.'
      end
    end
  end
  Game.new.play
end

def play_moves(moves)
  game = Game.new(Board.standard, :white, input: StringIO.new, output: StringIO.new)
  moves.each { |move| raise "illegal in check: #{move}" unless game.try_move(move) }
  game
end

def self_check
  mate = play_moves(['f2 f3', 'e7 e5', 'g2 g4', 'd8 h4'])
  raise "fool's mate not detected" unless mate.board.checkmate?(:white)

  castle = play_moves(['e2 e4', 'e7 e5', 'g1 f3', 'b8 c6', 'f1 c4', 'g8 f6', 'e1 g1'])
  raise 'castling did not move the rook' unless castle.board.at(Board.square('f1'))&.type == :rook

  passant = play_moves(['e2 e4', 'a7 a6', 'e4 e5', 'd7 d5', 'e5 d6'])
  raise 'en passant did not capture' unless passant.board.at(Board.square('d5')).nil?

  # After Qh5 the f7 pawn is pinned on the h5-e8 diagonal: moving it would expose the king.
  pinned = play_moves(['e2 e4', 'e7 e5', 'd1 h5'])
  raise 'pinned pawn was allowed to move' if pinned.try_move('f7 f6')
  raise 'king moved two squares' if play_moves(['e2 e4', 'e7 e5']).try_move('e1 e3')

  restored = Game.from_json(castle.to_json)
  raise 'save/load lost the position' unless restored.board.to_h == castle.board.to_h && restored.turn == castle.turn

  puts 'Self-check passed: checkmate, castling, en passant, illegal moves, save/load.'
end

if __FILE__ == $PROGRAM_NAME
  ARGV.include?('--check') ? self_check : start
end
