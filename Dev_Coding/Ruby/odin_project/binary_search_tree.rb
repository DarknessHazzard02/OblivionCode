# Made by: Hazzard
# The Odin Project - Ruby (Computer Science): Binary Search Tree. Run: ruby binary_search_tree.rb

class TreeNode
  attr_accessor :data, :left, :right

  def initialize(data)
    @data = data
    @left = nil
    @right = nil
  end
end

class Tree
  attr_reader :root

  def initialize(array)
    @root = build_tree(array)
  end

  def build_tree(array)
    sorted = array.uniq.sort
    build = lambda do |first, last|
      return nil if first > last

      middle = (first + last) / 2
      node = TreeNode.new(sorted[middle])
      node.left = build.call(first, middle - 1)
      node.right = build.call(middle + 1, last)
      node
    end
    build.call(0, sorted.length - 1)
  end

  def insert(value, node = @root)
    return @root = TreeNode.new(value) if @root.nil?
    return if value == node.data

    if value < node.data
      if node.left.nil?
        node.left = TreeNode.new(value)
      else
        insert(value, node.left)
      end
    elsif node.right.nil?
      node.right = TreeNode.new(value)
    else
      insert(value, node.right)
    end
  end

  def delete(value)
    @root = delete_from(@root, value)
  end

  def find(value)
    node = @root
    node = value < node.data ? node.left : node.right while node && node.data != value
    node
  end

  def level_order
    result = []
    queue = @root ? [@root] : []
    until queue.empty?
      node = queue.shift
      block_given? ? yield(node) : result << node.data
      queue << node.left if node.left
      queue << node.right if node.right
    end
    result unless block_given?
  end

  def inorder(node = @root, result = [], &block)
    return result if node.nil?

    inorder(node.left, result, &block)
    block ? block.call(node) : result << node.data
    inorder(node.right, result, &block)
    result
  end

  def preorder(node = @root, result = [], &block)
    return result if node.nil?

    block ? block.call(node) : result << node.data
    preorder(node.left, result, &block)
    preorder(node.right, result, &block)
    result
  end

  def postorder(node = @root, result = [], &block)
    return result if node.nil?

    postorder(node.left, result, &block)
    postorder(node.right, result, &block)
    block ? block.call(node) : result << node.data
    result
  end

  def height(value)
    node = find(value)
    node && height_of(node)
  end

  def depth(value)
    node = @root
    edges = 0
    while node
      return edges if node.data == value

      node = value < node.data ? node.left : node.right
      edges += 1
    end
    nil
  end

  def balanced?
    !balanced_height(@root).nil?
  end

  def rebalance
    @root = build_tree(inorder)
  end

  private

  def height_of(node)
    return -1 if node.nil?

    1 + [height_of(node.left), height_of(node.right)].max
  end

  def balanced_height(node)
    return -1 if node.nil?

    left = balanced_height(node.left)
    right = balanced_height(node.right)
    return nil if left.nil? || right.nil? || (left - right).abs > 1

    1 + [left, right].max
  end

  def delete_from(node, value)
    return nil if node.nil?

    if value < node.data
      node.left = delete_from(node.left, value)
    elsif value > node.data
      node.right = delete_from(node.right, value)
    else
      return node.right if node.left.nil?
      return node.left if node.right.nil?

      successor = node.right
      successor = successor.left while successor.left
      node.data = successor.data
      node.right = delete_from(node.right, successor.data)
    end
    node
  end
end

if __FILE__ == $PROGRAM_NAME
  tree = Tree.new(Array.new(15) { rand(1..100) })
  raise 'not balanced at start' unless tree.balanced?
  [101, 150, 175, 200, 250].each { |value| tree.insert(value) }
  raise 'should be unbalanced' if tree.balanced?
  tree.rebalance
  raise 'rebalance failed' unless tree.balanced?

  fixed = Tree.new([1, 7, 4, 23, 8, 9, 4, 3, 5, 7, 9, 67, 6345, 324])
  raise 'inorder failed' unless fixed.inorder == [1, 3, 4, 5, 7, 8, 9, 23, 67, 324, 6345]
  raise 'root failed' unless fixed.root.data == 8
  raise 'height failed' unless fixed.height(8) == 3
  raise 'depth failed' unless fixed.depth(8).zero?
  fixed.delete(8)
  raise 'delete failed' unless fixed.find(8).nil?
  puts "level: #{tree.level_order.join(' ')}"
  puts 'Binary Search Tree: all checks passed.'
end
