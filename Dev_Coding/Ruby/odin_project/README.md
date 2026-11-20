# The Odin Project - Ruby

Exercises and projects from The Odin Project Ruby path.

> **Not run yet.** Ruby is not installed on the machine where this was written, so the code was checked by reading only. Each file has a self-check; run it before trusting the code.

## Basics and Computer Science

Each file runs on its own and raises an error if any of its checks fails.

| File | Exercise |
|---|---|
| `caesar_cipher.rb` | Shift letters, keep case and punctuation |
| `sub_strings.rb` | Count dictionary words inside a text |
| `stock_picker.rb` | Best buy and sell day in one pass |
| `bubble_sort.rb` | Bubble sort that stops early |
| `recursion.rb` | `fibs`, `fibs_rec`, `merge_sort` |
| `linked_list.rb` | Singly linked list |
| `hash_map.rb` | Hash map with separate chaining and growth |
| `binary_search_tree.rb` | Balanced BST with traversals and rebalance |
| `knights_travails.rb` | Shortest knight path with breadth-first search |

```bash
ruby caesar_cipher.rb
```

## Projects

| Folder | Project | Self-check |
|---|---|---|
| `Mastermind/` | Codebreaker or codemaker against the computer | `ruby mastermind.rb --check` |
| `Hangman/` | Hangman with save and load to JSON | `ruby hangman.rb --check` |
| `Event_Manager/` | CSV cleaning, peak hours and ERB letters on invented data | `ruby event_manager.rb --check` |
| `Connect_Four/` | Connect Four built test-first | `rspec spec/connect_four_spec.rb` |
| `Chess/` | Two-player chess with every rule, save and load | `ruby main.rb --check`, `rspec spec/board_spec.rb` |

Run each check from inside its own folder. Connect Four and Chess both define a `Board` class, so loading both spec files in one `rspec` run would mix them up.

---

*Made by: Hazzard*
