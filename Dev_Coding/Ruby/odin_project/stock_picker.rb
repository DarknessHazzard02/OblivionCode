# Made by: Hazzard
# The Odin Project - Ruby: Stock Picker. Best [buy_day, sell_day] in one pass (buy before sell).
# Run: ruby stock_picker.rb

def stock_picker(prices)
  raise ArgumentError, 'need at least two prices' if prices.length < 2

  best = [0, 1]
  best_profit = prices[1] - prices[0]
  low_day = 0
  prices.each_with_index do |price, day|
    next if day.zero?

    profit = price - prices[low_day]
    if profit > best_profit
      best_profit = profit
      best = [low_day, day]
    end
    low_day = day if price < prices[low_day]
  end
  best
end

if __FILE__ == $PROGRAM_NAME
  raise 'odin example failed' unless stock_picker([17, 3, 6, 9, 15, 8, 6, 1, 10]) == [1, 4]
  raise 'lowest last failed' unless stock_picker([5, 8, 1]) == [0, 1]
  raise 'falling prices failed' unless stock_picker([9, 7, 4, 1]) == [0, 1]
  puts stock_picker([17, 3, 6, 9, 15, 8, 6, 1, 10]).inspect
  puts 'Stock Picker: all checks passed.'
end
