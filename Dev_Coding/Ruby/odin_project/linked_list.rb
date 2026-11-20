# Made by: Hazzard
# The Odin Project - Ruby (Computer Science): Linked List. Run: ruby linked_list.rb

class Node
  attr_accessor :value, :next_node

  def initialize(value = nil, next_node = nil)
    @value = value
    @next_node = next_node
  end
end

class LinkedList
  attr_reader :head, :size

  def initialize
    @head = nil
    @size = 0
  end

  def append(value)
    node = Node.new(value)
    if @head.nil?
      @head = node
    else
      tail.next_node = node
    end
    @size += 1
  end

  def prepend(value)
    @head = Node.new(value, @head)
    @size += 1
  end

  def tail
    node = @head
    node = node.next_node while node&.next_node
    node
  end

  def at(index)
    return nil if index.negative? || index >= @size

    node = @head
    index.times { node = node.next_node }
    node
  end

  def pop
    return nil if @head.nil?

    if @size == 1
      last = @head
      @head = nil
    else
      before = at(@size - 2)
      last = before.next_node
      before.next_node = nil
    end
    @size -= 1
    last
  end

  def contains?(value)
    !find(value).nil?
  end

  def find(value)
    node = @head
    index = 0
    while node
      return index if node.value == value

      node = node.next_node
      index += 1
    end
    nil
  end

  def to_s
    parts = []
    node = @head
    while node
      parts << "( #{node.value} )"
      node = node.next_node
    end
    (parts + ['nil']).join(' -> ')
  end

  def insert_at(value, index)
    raise IndexError, "index #{index} out of range 0..#{@size}" if index.negative? || index > @size
    return prepend(value) if index.zero?

    before = at(index - 1)
    before.next_node = Node.new(value, before.next_node)
    @size += 1
  end

  def remove_at(index)
    raise IndexError, "index #{index} out of range" if index.negative? || index >= @size

    if index.zero?
      removed = @head
      @head = removed.next_node
    else
      before = at(index - 1)
      removed = before.next_node
      before.next_node = removed.next_node
    end
    @size -= 1
    removed
  end
end

if __FILE__ == $PROGRAM_NAME
  list = LinkedList.new
  %w[dog cat parrot hamster snake turtle].each { |pet| list.append(pet) }
  expected = '( dog ) -> ( cat ) -> ( parrot ) -> ( hamster ) -> ( snake ) -> ( turtle ) -> nil'
  raise 'to_s failed' unless list.to_s == expected
  list.prepend('fish')
  raise 'size failed' unless list.size == 7
  raise 'pop failed' unless list.pop.value == 'turtle'
  raise 'find failed' unless list.find('hamster') == 4
  raise 'contains failed' if list.contains?('lion')
  list.insert_at('lion', 2)
  raise 'insert_at failed' unless list.at(2).value == 'lion'
  raise 'remove_at failed' unless list.remove_at(2).value == 'lion'
  puts list
  puts 'Linked List: all checks passed.'
end
