# Made by: Hazzard
# The Odin Project - Ruby: Bubble Sort. Stops early when a pass makes no swaps.
# Run: ruby bubble_sort.rb

def bubble_sort(array)
  sorted = array.dup
  (sorted.length - 1).downto(1) do |last|
    swapped = false
    (0...last).each do |i|
      next unless sorted[i] > sorted[i + 1]

      sorted[i], sorted[i + 1] = sorted[i + 1], sorted[i]
      swapped = true
    end
    break unless swapped
  end
  sorted
end

if __FILE__ == $PROGRAM_NAME
  raise 'odin example failed' unless bubble_sort([4, 3, 78, 2, 0, 2]) == [0, 2, 2, 3, 4, 78]
  raise 'empty failed' unless bubble_sort([]) == []
  raise 'input mutated' unless bubble_sort([2, 1]) == [1, 2]
  puts bubble_sort([4, 3, 78, 2, 0, 2]).inspect
  puts 'Bubble Sort: all checks passed.'
end
