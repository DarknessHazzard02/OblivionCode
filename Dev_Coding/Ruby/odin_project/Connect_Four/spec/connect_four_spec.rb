# Made by: Hazzard
# The Odin Project - Ruby: Connect Four specs (TDD project). Run: rspec spec/connect_four_spec.rb

require 'stringio'
require_relative '../lib/connect_four'

describe Board do
  subject(:board) { described_class.new }

  describe '#drop' do
    it 'stacks tokens from the bottom' do
      expect(board.drop(0, 'X')).to eq(5)
      expect(board.drop(0, 'O')).to eq(4)
    end

    it 'rejects a full column' do
      6.times { board.drop(3, 'X') }
      expect(board.drop(3, 'O')).to be_nil
    end

    it 'rejects a column outside the board' do
      expect(board.drop(7, 'X')).to be_nil
      expect(board.drop(-1, 'X')).to be_nil
    end
  end

  describe '#winner' do
    it 'finds four in a row' do
      (0..3).each { |column| board.drop(column, 'X') }
      expect(board.winner).to eq('X')
    end

    it 'finds four in a column' do
      4.times { board.drop(2, 'O') }
      expect(board.winner).to eq('O')
    end

    it 'finds four on a diagonal' do
      [[0, %w[X]], [1, %w[O X]], [2, %w[O O X]], [3, %w[O O O X]]].each do |column, tokens|
        tokens.each { |token| board.drop(column, token) }
      end
      expect(board.winner).to eq('X')
    end

    it 'returns nil for three in a row' do
      (0..2).each { |column| board.drop(column, 'X') }
      expect(board.winner).to be_nil
    end
  end

  describe '#full?' do
    it 'is true once every column is full' do
      7.times { |column| 6.times { |i| board.drop(column, i.even? ? 'X' : 'O') } }
      expect(board).to be_full
    end
  end
end

describe ConnectFour do
  it 'ends when a player connects four' do
    input = StringIO.new("1\n2\n1\n2\n1\n2\n1\n")
    game = described_class.new(Board.new, input: input, output: StringIO.new)
    expect(game.play).to eq('X')
  end

  it 'asks again after an invalid column' do
    input = StringIO.new("9\nabc\n1\n2\n1\n2\n1\n2\n1\n")
    output = StringIO.new
    described_class.new(Board.new, input: input, output: output).play
    expect(output.string.scan('That column is not available.').size).to eq(2)
  end
end
