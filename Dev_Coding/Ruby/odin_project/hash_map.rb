# Made by: Hazzard
# The Odin Project - Ruby (Computer Science): HashMap with separate chaining.
# Doubles capacity once the load factor is passed. Run: ruby hash_map.rb

class HashMap
  attr_reader :capacity

  def initialize(load_factor = 0.75, capacity = 16)
    @load_factor = load_factor
    @capacity = capacity
    @buckets = Array.new(capacity) { [] }
    @length = 0
  end

  def hash(key)
    raise TypeError, 'keys must be strings' unless key.is_a?(String)

    key.each_char.reduce(0) { |code, char| ((31 * code) + char.ord) % @capacity }
  end

  def set(key, value)
    bucket = bucket_for(key)
    entry = bucket.find { |pair| pair[0] == key }
    if entry
      entry[1] = value
      return
    end
    bucket << [key, value]
    @length += 1
    grow if @length > @capacity * @load_factor
  end

  def get(key)
    entry = bucket_for(key).find { |pair| pair[0] == key }
    entry&.last
  end

  def has?(key)
    bucket_for(key).any? { |pair| pair[0] == key }
  end

  def remove(key)
    bucket = bucket_for(key)
    index = bucket.index { |pair| pair[0] == key }
    return nil if index.nil?

    @length -= 1
    bucket.delete_at(index).last
  end

  def length
    @length
  end

  def clear
    @buckets = Array.new(@capacity) { [] }
    @length = 0
  end

  def keys
    entries.map(&:first)
  end

  def values
    entries.map(&:last)
  end

  def entries
    @buckets.flat_map { |bucket| bucket.map(&:dup) }
  end

  private

  def bucket_for(key)
    index = hash(key)
    raise IndexError, 'Trying to access index out of bounds' if index.negative? || index >= @buckets.length

    @buckets[index]
  end

  def grow
    old = entries
    @capacity *= 2
    @buckets = Array.new(@capacity) { [] }
    @length = 0
    old.each { |key, value| set(key, value) }
  end
end

if __FILE__ == $PROGRAM_NAME
  test = HashMap.new
  { 'apple' => 'red', 'banana' => 'yellow', 'carrot' => 'orange', 'dog' => 'brown', 'elephant' => 'gray',
    'frog' => 'green', 'grape' => 'purple', 'hat' => 'black', 'ice cream' => 'white', 'jacket' => 'blue',
    'kite' => 'pink', 'lion' => 'golden' }.each { |key, value| test.set(key, value) }
  raise 'length failed' unless test.length == 12
  test.set('apple', 'green')
  raise 'overwrite failed' unless test.length == 12 && test.get('apple') == 'green'
  test.set('moon', 'silver')
  raise 'grow failed' unless test.capacity == 32 && test.length == 13
  raise 'remove failed' unless test.remove('kite') == 'pink' && test.get('kite').nil?
  puts "capacity #{test.capacity}, length #{test.length}"
  puts 'HashMap: all checks passed.'
end
