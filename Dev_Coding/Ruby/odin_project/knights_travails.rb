# Made by: Hazzard
# The Odin Project - Ruby (Computer Science): Knights Travails with breadth-first search.
# Run: ruby knights_travails.rb

MOVES = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]].freeze

def on_board?(square)
  square.all? { |n| n.between?(0, 7) }
end

def knight_moves(start, finish)
  raise ArgumentError, 'squares must be [x, y] with 0..7' unless on_board?(start) && on_board?(finish)

  previous = { start => nil }
  queue = [start]
  until queue.empty?
    square = queue.shift
    break if square == finish

    MOVES.each do |dx, dy|
      step = [square[0] + dx, square[1] + dy]
      next if !on_board?(step) || previous.key?(step)

      previous[step] = square
      queue << step
    end
  end
  path = [finish]
  path.unshift(previous[path.first]) while previous[path.first]
  path
end

if __FILE__ == $PROGRAM_NAME
  raise 'one move failed' unless knight_moves([0, 0], [1, 2]) == [[0, 0], [1, 2]]
  raise 'two moves failed' unless knight_moves([0, 0], [3, 3]).length == 3
  raise 'corner failed' unless knight_moves([0, 0], [7, 7]).length == 7
  raise 'same square failed' unless knight_moves([4, 4], [4, 4]) == [[4, 4]]
  path = knight_moves([3, 3], [4, 3])
  puts "You made it in #{path.length - 1} moves! Here's your path:"
  path.each { |square| puts "  #{square.inspect}" }
  puts 'Knights Travails: all checks passed.'
end
