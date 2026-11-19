# Made by: Hazzard
# The Odin Project - Ruby: Chess game loop for two players in the terminal.
# Moves are typed as "e2 e4". Other commands: save, quit. Saves go to saves/<name>.json.

require 'json'
require_relative 'board'

class Game
  SAVE_DIR = File.expand_path('../saves', __dir__)

  attr_reader :board, :turn

  def initialize(board = Board.standard, turn = :white, input: $stdin, output: $stdout)
    @board = board
    @turn = turn
    @input = input
    @output = output
  end

  def self.from_json(text, **io)
    data = JSON.parse(text)
    turn = data.fetch('turn').to_sym
    raise ArgumentError, 'turn must be white or black' unless %i[white black].include?(turn)

    new(Board.from_h(data.fetch('board')), turn, **io)
  end

  def to_json(*_args)
    JSON.generate({ 'turn' => @turn.to_s, 'board' => @board.to_h })
  end

  def play
    loop do
      @output.puts "\n#{@board}"
      return finish("Checkmate! #{other.capitalize} wins.") if @board.checkmate?(@turn)
      return finish('Stalemate. It is a draw.') if @board.stalemate?(@turn)

      @output.puts "#{@turn.capitalize} is in check!" if @board.in_check?(@turn)
      command = ask
      return finish('Bye.') if command.nil? || command == 'quit'
      next save if command == 'save'

      try_move(command)
    end
  end

  # Returns true when the move was made. Used by the loop and by the self-check.
  def try_move(command)
    from_text, to_text = command.split
    from = Board.square(from_text)
    to = Board.square(to_text)
    return complain('Type a move like "e2 e4", or save / quit.') unless from && to

    piece = @board.at(from)
    return complain("No #{@turn} piece on #{from_text}.") unless piece && piece.color == @turn
    return complain('That move is not legal.') unless @board.legal_moves(from).include?(to)

    @board.move!(from, to)
    @turn = other
    true
  end

  private

  def other
    @turn == :white ? :black : :white
  end

  def ask
    @output.print "#{@turn.capitalize} to move: "
    line = @input.gets
    line&.strip&.downcase
  end

  def complain(message)
    @output.puts message
    false
  end

  def finish(message)
    @output.puts message
    message
  end

  def save
    Dir.mkdir(SAVE_DIR) unless Dir.exist?(SAVE_DIR)
    @output.print 'Save name (letters, digits, _ or -): '
    name = @input.gets.to_s.strip
    return complain('Invalid name. Not saved.') unless name.match?(/\A[\w-]{1,30}\z/)

    File.write(File.join(SAVE_DIR, "#{name}.json"), to_json)
    @output.puts "Saved as #{name}."
  end
end
