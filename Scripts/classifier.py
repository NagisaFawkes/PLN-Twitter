import pandas as pd
import numpy as np
import csv  
import sys

def binary_search(seq, t):
    min = 0
    max = len(seq) - 1
    while True:
        if max < min:
            return -1
        m = (min + max) // 2
        if seq[m] < t:
            min = m + 1
        elif seq[m] > t:
            max = m - 1
        else:
            return m

def classify(tweet_input_file, emotion_lex_file, output_file, check_context_option):
    negation_words = ["jamais", "nada", "nem", "nenhum", "ninguém", "nunca", "não", "tampouco"]
    amplifier_words = ["mais", "muito", "demais", "completamente", "absolutamente", "totalmente", \
                        "definitivamente", "extremamente", "frequentemente", "bastante"]
    downtoner_words = ["pouco", "quase", "menos", "apenas"]
    
    tweets = pd.read_csv(tweet_input_file, encoding="utf-8")
    
    lex = pd.read_csv(emotion_lex_file, encoding="utf-8")

    tweets['auto_score'] = 0
    positive = 0
    negative = 0
    undefined = 0
    sentiment_words = 0

    for i, row in tweets.iterrows():
        overall_sentiment = 0
        words = str(row["text_normalized"])
        print(words)
        # Removing irrelevant characters (punctuation, etc...)
        for ch in [',', '.', ';', '?', '!', '*', '(', ')', '%', '-', '"', '…', ':']:
            if ch in words:
                words = words.replace(ch, "")

        # Removing extra whitespace and splitting into a ndarray of strings
        words = np.asarray(words.strip().rstrip().split())
        no_sentiment_words = True

        for j, word in enumerate(words):
            # Find the index of the word in the lexicon
            index = binary_search(lex['word'], word.lower())

            amp_word_in_context = False
            if( word.upper() == word and word.lower() != word):
                amp_word_in_context = True

            words[j] = word.lower()
            
            # If not found, assign 0 to the polarity. Otherwise, assign the polarity found in the lexicon
            polarity = 0 if index < 0 else int(lex['class'][index])
            
            # If this word's polarity is 0, skip to the next word
            if (polarity == 0):
                continue

            no_sentiment_words = False
            sentiment_words += 1
            # Check the context if the argument was set to 1. Skip the check if it's the first word
            # The context window size was defined as 4
            if (check_context_option == 1 and j > 0):
                left_limit = 0 if j <= 4 else j - 4

                # The next three four loops check if there are any amplifier, downtoner or negation
                # words in the context
                for amplifier_word in amplifier_words:
                    if amplifier_word in words[left_limit : j]:
                        amp_word_in_context = True
                        break;
   

                down_word_in_context = False
                for downtoner_word in downtoner_words:
                    if downtoner_word in words[left_limit : j]:
                        down_word_in_context = True
                        break;

                neg_word_in_context = False
                for negation_word in negation_words:
                    if negation_word in words[left_limit : j]:
                        neg_word_in_context = True
                        break;


                # Tune the word's polarity according to its context
                if (amp_word_in_context):
                    if (neg_word_in_context):
                        polarity /= 3
                    else:
                        polarity *= 3
                elif (down_word_in_context):
                    if (neg_word_in_context):
                        polarity *= 3
                    else:
                        polarity /= 3
                elif (neg_word_in_context):
                    polarity *= -1

            overall_sentiment += polarity
            print(word, ": ", polarity)
        
        if overall_sentiment > 0 :
            tweets.loc[i, 'auto_score'] = 1
            positive +=1
        else:
            if overall_sentiment < 0:
                tweets.loc[i, 'auto_score'] = -1
                negative +=1

            else:
                tweets.loc[i, 'auto_score'] = -1
                negative +=1

        if no_sentiment_words:
            undefined +=1
        print("Resultado: ", overall_sentiment)
        #input()

    tweets.to_csv(output_file, index=False)
    
  
    fields=[emotion_lex_file,tweet_input_file,check_context_option, positive, negative, undefined, sentiment_words/412]
    with open('results.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fields)

if __name__ == "__main__":
    main()