# Made by: Hazzard
# The Odin Project - Ruby: Chess specs. Run from the Chess folder: rspec spec/board_spec.rb

require 'stringio'
require_relative '../lib/game'

def game_after(moves)
  game = Game.new(Board.standard, :white, input: StringIO.new, output: StringIO.new)
  moves.each { |move| raise "illegal: #{move}" unless game.try_move(move) }
  game
end

describe Board do
  let(:sq) { ->(name) { Board.square(name) } }

  it 'gives every side 20 legal opening moves' do
    board = Board.standard
    expect(board.all_legal_moves(:white).size).to eq(20)
    expect(board.all_legal_moves(:black).size).to eq(20)
  end

  it "detects fool's mate" do
    expect(game_after(['f2 f3', 'e7 e5', 'g2 g4', 'd8 h4']).board.checkmate?(:white)).to be true
  end

  it 'castles king side and moves the rook' do
    board = game_after(['e2 e4', 'e7 e5', 'g1 f3', 'b8 c6', 'f1 c4', 'g8 f6', 'e1 g1']).board
    expect(board.at(sq.call('g1')).type).to eq(:king)
    expect(board.at(sq.call('f1')).type).to eq(:rook)
  end

  it 'captures en passant' do
    board = game_after(['e2 e4', 'a7 a6', 'e4 e5', 'd7 d5', 'e5 d6']).board
    expect(board.at(sq.call('d5'))).to be_nil
    expect(board.at(sq.call('d6')).color).to eq(:white)
  end

  it 'promotes a pawn to a queen' do
    board = Board.new
    board.place(sq.call('e1'), Piece.new(:white, :king, true))
    board.place(sq.call('h8'), Piece.new(:black, :king, true))
    board.place(sq.call('a7'), Piece.new(:white, :pawn, true))
    board.move!(sq.call('a7'), sq.call('a8'))
    expect(board.at(sq.call('a8')).type).to eq(:queen)
  end

  it 'detects stalemate' do
    board = Board.new
    board.place(sq.call('a8'), Piece.new(:black, :king, true))
    board.place(sq.call('b6'), Piece.new(:white, :queen, true))
    board.place(sq.call('c6'), Piece.new(:white, :king, true))
    expect(board.stalemate?(:black)).to be true
  end

  it 'rejects a move that leaves the king in check' do
    board = Board.new
    board.place(sq.call('e1'), Piece.new(:white, :king, true))
    board.place(sq.call('e2'), Piece.new(:white, :bishop, true))
    board.place(sq.call('e8'), Piece.new(:black, :rook, true))
    board.place(sq.call('a8'), Piece.new(:black, :king, true))
    expect(board.legal_moves(sq.call('e2'))).to be_empty
  end

  it 'round-trips through save and load' do
    game = game_after(['e2 e4', 'c7 c5'])
    restored = Game.from_json(game.to_json, input: StringIO.new, output: StringIO.new)
    expect(restored.board.to_h).to eq(game.board.to_h)
    expect(restored.turn).to eq(:white)
  end
end
