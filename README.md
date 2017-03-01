# HMM Part of Speech Tagger Implementing Viterbi Algorithm

## 1\.Usage

```
usage: $ ./Viterbi_tagger.py training_file_name input_file_name output_file_name

positional arguments:
  training_file_name	Two columns separated by a tab, 1st column: token, 2nd column: POS tag, blank lines separate sentences.
  input_file_name		One token per line, with blank lines between sentences.
  output_file_name		Same format as training file.

```
Alternatively, the job can run on an HPC cluster by submitting the slurm job script `runPOStagger.sh`.

## 2\.OOV Handling
Words occurring once in the training corpus are subcategorized to 
1. Words beginning with a capital letter
2. Words ending with an 's'
3. Words ending with 'ed'
4. **1** and **2**
5. **1** and **3**
6. Numerical words (e.g. 1,000,000.00) 
7. Other

When OOV occurs during the tagging process, its observation likelihood is determined by the subcategory defined above that the word falls into.

This OOV handling scheme replaces that of a baseline system where words occuring once in the training corpus are lumped together as **UNKNOWN_WORDS**.
The original OOV handling system yields 95.205917% accuracy on WSJ_24 Corpus, whereas the improved system yields a 95.686847% accuracy. The improvement is relatively small. To further improve the performance, manual rules may be applied to OOV words.