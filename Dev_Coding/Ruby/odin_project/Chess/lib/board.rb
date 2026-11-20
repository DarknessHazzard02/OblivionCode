# Made by: Hazzard
# The Odin Project - Ruby: Chess board and rules. Squares are [row, col] with row 0 = rank 8.
# Covers every piece move, check, checkmate, stalemate, castling, en passant and promotion
# (to a queen by default). The board can be saved to and loaded from a plain Hash (JSON).

PIECE_SYMBOLS = {
  white: { king: "♔", queen: "♕", rook: "♖", bishop: "♗", knight: "♘", pawn: "♙" },
  black: { king: "♚", queen: "♛", rook: "♜", bishop: "♝", knight: "♞", pawn: "♟" }
}.freeze

Piece = Struct.new(:color, :type, :moved) do
  def symbol
    PIECE_SYMBOLS[color][type]
  end
end

class Board
  BACK_RANK = %i[rook knight bishop queen king bishop knight rook].freeze
  KNIGHT_STEPS = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]].freeze
  KING_STEPS = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]].freeze
  SLIDES = {
    rook: [[1, 0], [-1, 0], [0, 1], [0, -1]],
    bishop: [[1, 1], [1, -1], [-1, 1], [-1, -1]],
    queen: [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
  }.freeze

  attr_reader :grid, :en_passant

  def self.standard
    board = new
    8.times do |col|
      board.place([0, col], Piece.new(:black, BACK_RANK[col], false))
      board.place([1, col], Piece.new(:black, :pawn, false))
      board.place([6, col], Piece.new(:white, :pawn, false))
      board.place([7, col], Piece.new(:white, BACK_RANK[col], false))
    end
    board
  end

  def initialize
    @grid = Array.new(8) { Array.new(8) }
    @en_passant = nil # square a pawn can capture into this turn
  end

  def self.square(text)
    return nil unless text.to_s.match?(/\A[a-h][1-8]\z/)

    [8 - text[1].to_i, text[0].ord - 'a'.ord]
  end

  def self.square_name(square)
    "#{('a'.ord + square[1]).chr}#{8 - square[0]}"
  end

  def place(square, piece)
    @grid[square[0]][square[1]] = piece
  end

  def at(square)
    @grid[square[0]][square[1]]
  end

  def inside?(square)
    square.all? { |n| n.between?(0, 7) }
  end

  # ==============================================================================
  # Moves
  # ==============================================================================
  def legal_moves(from)
    piece = at(from)
    return [] if piece.nil?

    pseudo_moves(from).reject { |to| leaves_king_in_check?(from, to, piece.color) }
  end

  def all_legal_moves(color)
    squares_of(color).flat_map { |from| legal_moves(from).map { |to| [from, to] } }
  end

  # Applies a legal move. Returns the captured piece (or nil). Raises on an illegal move.
  def move!(from, to, promotion: :queen)
    piece = at(from)
    raise ArgumentError, 'no piece on that square' if piece.nil?
    raise ArgumentError, 'illegal move' unless legal_moves(from).include?(to)

    perform(from, to, promotion)
  end

  def in_check?(color)
    king = squares_of(color).find { |sq| at(sq).type == :king }
    !king.nil? && attacked?(king, opponent(color))
  end

  def checkmate?(color)
    in_check?(color) && all_legal_moves(color).empty?
  end

  def stalemate?(color)
    !in_check?(color) && all_legal_moves(color).empty?
  end

  def attacked?(square, by_color)
    squares_of(by_color).any? { |from| attacks(from).include?(square) }
  end

  # ==============================================================================
  # Save / load
  # ==============================================================================
  def to_h
    pieces = []
    8.times do |row|
      8.times do |col|
        piece = @grid[row][col]
        pieces << { 'square' => Board.square_name([row, col]), 'color' => piece.color.to_s, 'type' => piece.type.to_s, 'moved' => piece.moved } if piece
      end
    end
    { 'pieces' => pieces, 'en_passant' => @en_passant && Board.square_name(@en_passant) }
  end

  def self.from_h(data)
    board = new
    data.fetch('pieces').each do |p|
      square = Board.square(p.fetch('square'))
      color = p.fetch('color').to_sym
      type = p.fetch('type').to_sym
      raise ArgumentError, "bad piece #{p.inspect}" unless square && %i[white black].include?(color) && SYMBOLS_OK.include?(type)

      board.place(square, Piece.new(color, type, p.fetch('moved') == true))
    end
    board.instance_variable_set(:@en_passant, data['en_passant'] && Board.square(data['en_passant']))
    board
  end

  SYMBOLS_OK = %i[king queen rook bishop knight pawn].freeze

  def to_s
    lines = @grid.each_with_index.map do |row, r|
      cells = row.map { |piece| piece ? piece.symbol : '.' }
      "#{8 - r} #{cells.join(' ')}"
    end
    (lines + ['  a b c d e f g h']).join("\n")
  end

  private

  def opponent(color)
    color == :white ? :black : :white
  end

  def squares_of(color)
    squares = []
    8.times { |r| 8.times { |c| squares << [r, c] if @grid[r][c]&.color == color } }
    squares
  end

  def forward(color)
    color == :white ? -1 : 1
  end

  # Squares a piece attacks (used for check detection). No castling, pawns only diagonally.
  def attacks(from)
    piece = at(from)
    case piece.type
    when :pawn
      dir = forward(piece.color)
      [[from[0] + dir, from[1] - 1], [from[0] + dir, from[1] + 1]].select { |sq| inside?(sq) }
    when :knight then steps(from, KNIGHT_STEPS, piece.color, include_own: true)
    when :king then steps(from, KING_STEPS, piece.color, include_own: true)
    else slides(from, SLIDES[piece.type], piece.color, include_own: true)
    end
  end

  def pseudo_moves(from)
    piece = at(from)
    case piece.type
    when :pawn then pawn_moves(from, piece)
    when :knight then steps(from, KNIGHT_STEPS, piece.color)
    when :king then steps(from, KING_STEPS, piece.color) + castling_moves(from, piece)
    else slides(from, SLIDES[piece.type], piece.color)
    end
  end

  def steps(from, deltas, color, include_own: false)
    deltas.map { |dr, dc| [from[0] + dr, from[1] + dc] }.select do |sq|
      inside?(sq) && (include_own || at(sq).nil? || at(sq).color != color)
    end
  end

  def slides(from, directions, color, include_own: false)
    moves = []
    directions.each do |dr, dc|
      sq = [from[0] + dr, from[1] + dc]
      while inside?(sq)
        if at(sq).nil?
          moves << sq
        else
          moves << sq if include_own || at(sq).color != color
          break
        end
        sq = [sq[0] + dr, sq[1] + dc]
      end
    end
    moves
  end

  def pawn_moves(from, piece)
    dir = forward(piece.color)
    moves = []
    one = [from[0] + dir, from[1]]
    if inside?(one) && at(one).nil?
      moves << one
      start_row = piece.color == :white ? 6 : 1
      two = [from[0] + (2 * dir), from[1]]
      moves << two if from[0] == start_row && at(two).nil?
    end
    [-1, 1].each do |dc|
      sq = [from[0] + dir, from[1] + dc]
      next unless inside?(sq)

      target = at(sq)
      moves << sq if (target && target.color != piece.color) || sq == @en_passant
    end
    moves
  end

  def castling_moves(from, king)
    return [] if king.moved || in_check?(king.color)

    row = from[0]
    moves = []
    { 7 => [5, 6], 0 => [3, 2] }.each do |rook_col, (pass_col, land_col)|
      rook = @grid[row][rook_col]
      next unless rook && rook.type == :rook && rook.color == king.color && !rook.moved

      between = rook_col == 7 ? [5, 6] : [1, 2, 3]
      next unless between.all? { |col| @grid[row][col].nil? }
      next if [pass_col, land_col].any? { |col| attacked?([row, col], opponent(king.color)) }

      moves << [row, land_col]
    end
    moves
  end

  def leaves_king_in_check?(from, to, color)
    copy = Marshal.load(Marshal.dump(self))
    copy.send(:perform, from, to, :queen)
    copy.in_check?(color)
  end

  def perform(from, to, promotion)
    piece = at(from)
    captured = at(to)
    # En passant: the captured pawn sits beside the moving pawn, not on the target square.
    if piece.type == :pawn && to == @en_passant && captured.nil?
      captured = @grid[from[0]][to[1]]
      @grid[from[0]][to[1]] = nil
    end
    # Castling: the king moves two files, so the rook jumps over it.
    if piece.type == :king && (to[1] - from[1]).abs == 2
      rook_from = to[1] == 6 ? 7 : 0
      rook_to = to[1] == 6 ? 5 : 3
      rook = @grid[from[0]][rook_from]
      @grid[from[0]][rook_from] = nil
      @grid[from[0]][rook_to] = rook
      rook.moved = true
    end
    @en_passant = piece.type == :pawn && (to[0] - from[0]).abs == 2 ? [(to[0] + from[0]) / 2, from[1]] : nil
    place(to, piece)
    place(from, nil)
    piece.moved = true
    piece.type = promotion if piece.type == :pawn && [0, 7].include?(to[0])
    captured
  end
end
