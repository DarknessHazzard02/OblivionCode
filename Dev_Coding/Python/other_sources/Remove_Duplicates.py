def remove_duplicates(s):
    write = 0
    for read in range(1, len(s)):
        if s[read] != s[write]:
            write += 1
            s[write] = s[read]
    return write + 1