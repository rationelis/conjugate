with open('deck_export.txt', encoding="utf-8") as f:
    notes = f.readlines()

unique = 0
verbs = 0

remaining = []

print(str(len(notes)) + " cards in deck.")

for note in notes:
    front = note.split('	')[0]
    back = ','.join(note.split('	')[1:]).replace('\n', '').replace('\t', '')

    length = len(back.split(' '))
    if length == 1 or length == 2: # Unique words:
        unique += 1
    elif "Tense" in back: # Verbs
        verbs += 1
    else:
        remaining.append(back)

print("Unique words: " + str(unique))
print("Verbs: " + str(verbs / 10))
print("Remaining (grammar/context examples): " + str(len(remaining)))