# HMM Part of Speech Tagger Implementing Viterbi Algorithm

## 1\.Usage

```
usage: $ ./Viterbi_tagger.py training_file_name input_file_name output_file_name

positional arguments:
  training_file_name	Two columns separated by a tab, 1st column: token, 2nd column: POS tag, blank lines separate sentences.
  input_file_name		One token per line, with blank lines between sentences.
  output_file_name		Same format as training file.

```

## 2\.OOV Handling
Words occurring once in the training corpus are treated as UNKNOWN_WORD collectively.