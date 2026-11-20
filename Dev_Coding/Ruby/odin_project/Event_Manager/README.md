# Event Manager

Reads `data/event_attendees.csv`, cleans ZIP codes and phone numbers, reports the peak registration hours and weekdays, and writes one thank-you letter per attendee to `output/` with an ERB template. The data is invented (see `data/CONTRATO.md`). The original exercise also looks up legislators through a Google API that needs a key; that step is left out.

Source: The Odin Project, Ruby path.

> **Not run yet.** Ruby is not installed on the machine where this was written, so the code was checked by reading only. Each file has a self-check; run it before trusting the code.

## How to run

```bash
ruby event_manager.rb
ruby event_manager.rb --check
```

---

*Made by: Hazzard*
