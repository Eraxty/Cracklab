# Cracklab

this is a tool for decrypting and analyzing ciphers

## Cracks
- Monoalphabetic substitution cipher cracking
- Caesar cipher
- Base64 decoding
- Base32 decoding
- Hex decoding
- Binary decoding
- Morse code decoding

---

## Features 
- Frequency analysis
- Index of coincidence
- Entropy analysis
- Bigram analysis
- Pattern and dictionary matching
- English text scoring
- Key-based encryption and decryption

## Usage

Run CrackLab:

```bash
python crack.py
```
### How to use 

Select option `1` and enter the ciphertext.
Example:-

```text
Enter ciphertext:
> SEVMTE8gV09STEQ=

Cipher: Base64 (99%)

Decoded:
HELLO WORLD
```


CrackLab will analyze the input, detect its likely type, and run the appropriate decoder or solver.


## Screenshots

![Cracklabcli](pics/image.png)

![cracklab](pics/image1.png)

### Encryption

Select option `2` and enter a message.

It generates an encrypted message with a key

### Decryption

Select option `3`, then enter the encrypted text with its key.


## Solver

The substitution solver does not simply replace letters based on frequency.

It combines several methods:

- Letter frequency analysis
- Repeated word patterns
- Dictionary candidate matching
- Partial plaintext matching
- N-gram scoring
- Common word scoring
- Mapping consistency
- Iterative candidate refinement

## Requirements

Install any project dependencies using:

```bash
pip install -r requirements.txt
```
## Use of ai
Ai was used in making iterative solver cuz i couldnt figure it out,even ai couldnt figure it out it took hours, Ai was also used in like small stuffs for making life easier like making dictionaries for words the the data and stuff like that 