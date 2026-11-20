# Made by: Hazzard
# The Odin Project - Ruby (Computer Science): Recursion. fibs, fibs_rec and merge_sort.
# Run: ruby recursion.rb

def fibs(count)
  sequence = []
  count.times { |i| sequence << (i < 2 ? i : sequence[-1] + sequence[-2]) }
  sequence
end

def fibs_rec(count)
  return [] if count <= 0
  return [0] if count == 1
  return [0, 1] if count == 2

  previous = fibs_rec(count - 1)
  previous + [previous[-1] + previous[-2]]
end

def merge_sort(array)
  return array.dup if array.length <= 1

  middle = array.length / 2
  left = merge_sort(array[0...middle])
  right = merge_sort(array[middle..])
  merged = []
  merged << (left.first <= right.first ? left.shift : right.shift) until left.empty? || right.empty?
  merged + left + right
end

if __FILE__ == $PROGRAM_NAME
  raise 'fibs failed' unless fibs(8) == [0, 1, 1, 2, 3, 5, 8, 13]
  raise 'fibs_rec failed' unless fibs_rec(8) == fibs(8)
  raise 'merge_sort failed' unless merge_sort([3, 2, 1, 13, 8, 5, 0, 1]) == [0, 1, 1, 2, 3, 5, 8, 13]
  raise 'merge_sort empty failed' unless merge_sort([]) == []
  puts "fibs(8): #{fibs(8).inspect}"
  puts "merge_sort: #{merge_sort([105, 79, 100, 110]).inspect}"
  puts 'Recursion: all checks passed.'
end
