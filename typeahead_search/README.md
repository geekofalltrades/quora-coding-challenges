#Typeahead Search

A pure Python implementation of the Typeahead Search challenge.

This implementation uses a Radix Trie to store words. Each node in the
Radix Trie maintains a complete set of the entries in the subtree rooted
at itself.

Current runtime for the largest possible datasets is about 16s, and memory
usage toes 512mb.
