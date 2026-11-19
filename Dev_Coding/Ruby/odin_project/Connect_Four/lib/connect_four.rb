# Made by: Hazzard
# The Odin Project - Ruby: Connect Four. Board rules are kept apart from the terminal game
# so the spec can test them without input.

class Board
  ROWS = 6
  COLUMNS = 7
  DIRECTIONS = [[0, 1], [1, 0], [1, 1], [1, -1]].freeze

  attr_reader :grid

  def initialize
    @grid = Array.new(ROWS) { Array.new(COLUMNS) }
  end

  def valid_column?(column)
    column.is_a?(Integer) && column.between?(0, COLUMNS - 1) && @grid[0][column].nil?
  end

  # Drops a token and returns the row it landed in, or nil when the column is full or invalid.
  def drop(column, token)
    return nil unless valid_column?(column)

    row = (ROWS - 1).downto(0).find { |r| @grid[r][column].nil? }
    @grid[row][column] = token
    row
  end

  def full?
    @grid[0].none?(&:nil?)
  end

  def winner
    ROWS.times do |row|
      COLUMNS.times do |column|
        token = @grid[row][column]
        next if token.nil?
        return token if DIRECTIONS.any? { |dr, dc| four_from?(row, column, dr, dc, token) }
      end
    end
    nil
  end

  def to_s
    rows = @grid.map { |row| "| #{row.map { |cell| cell || '.' }.join(' ')} |" }
    (rows + ["  #{(1..COLUMNS).to_a.join(' ')}"]).join("\n")
  end

  private

  def four_from?(row, column, d_row, d_column, token)
    (0...4).all? do |step|
      r = row + (d_row * step)
      c = column + (d_column * step)
      r.between?(0, ROWS - 1) && c.between?(0, COLUMNS - 1) && @grid[r][c] == token
    end
  end
end

class ConnectFour
  TOKENS = %w[X O].freeze

  def initialize(board = Board.new, input: $stdin, output: $stdout)
    @board = board
    @input = input
    @output = output
    @turn = 0
  end

  def play
    loop do
      @output.puts "\n#{@board}"
      token = TOKENS[@turn % 2]
      column = ask_column(token)
      return @output.puts("\nBye.") if column.nil?

      @board.drop(column, token)
      if @board.winner
        @output.puts "\n#{@board}\nPlayer #{token} wins!"
        return token
      end
      if @board.full?
        @output.puts "\n#{@board}\nIt's a draw."
        return nil
      end
      @turn += 1
    end
  end

  private

  def ask_column(token)
    loop do
      @output.print "Player #{token}, choose a column (1-#{Board::COLUMNS}): "
      line = @input.gets
      return nil if line.nil?

      column = line.strip.to_i - 1
      return column if line.strip.match?(/\A\d+\z/) && @board.valid_column?(column)

      @output.puts 'That column is not available.'
    end
  end
end
