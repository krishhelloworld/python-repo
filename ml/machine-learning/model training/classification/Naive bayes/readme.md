# Naive Bayes-;

## DEFINITION-;
- it works for textual data .
- best examples are spam filters and sentimental analysis

> ![this is data of binary classification best bits for the naive bayes](assets/binary_classificationj.png){width=50}||image row will be -7||

> ![here we can see that the combination formula and the terms wise formula which works ](assets/example_solution.png){width=80}

## CODE EXAMPLE -;


- ![Type of probability distirubution](assets/Types_of_probab_dist.png){width=63}
- ![probability question on multinomial probability](assets/multinomial_question.png){width=65}

 
## DOING CODE-;

- FIRST CLEAN THE SENTENCE 
    - IF IT IS EXTRACTED FROM THE HTML,OR ANYTHING REMOVE THE < / > ,ETC
    - IF IT HAVE ALNUM() TEXT REMOVE IT (/,@!#),etc
    - remove the stopwords from the nltk.corpus.
    - lower the words in the sentence.
- THEN START TO MAKE THESE WORDS A COLUMN -> CountVectorizer(stop_words='english')

