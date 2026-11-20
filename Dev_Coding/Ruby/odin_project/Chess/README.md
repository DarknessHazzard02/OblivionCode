# Chess

Two-player chess in the terminal with Unicode pieces. Moves are typed as `e2 e4`. It covers every piece, check, checkmate, stalemate, castling, en passant and promotion to a queen, and refuses moves that leave the king in check. Type `save` to store the game as JSON in `saves/`; the next start offers to load it.

Source: The Odin Project, Ruby path.

> **Not run yet.** Ruby is not installed on the machine where this was written, so the code was checked by reading only. Each file has a self-check; run it before trusting the code.

## How to run

```bash
ruby main.rb
ruby main.rb --check
rspec spec/board_spec.rb
```

---

*Made by: Hazzard*
