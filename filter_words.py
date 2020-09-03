#############################################################
# Author: Keshav Chakrapani
# Email: kchakrapani@salesforce.com
# Role: Intern, CDP Fabric
#############################################################
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tag import pos_tag
from itertools import product
import re
import constants


# The way a statement is constructed is as follows:
#   Select
#   Column Name (if not here, use *)
#   --From-- (something the speaker shouldn't have to say, but implied)
#   Table Name
#   --Where-- (something that is again, implied if there is a condition)
#   Column Name
#   Condition
#   Value (can be directly taken from speaker, no conversion needed)
# Example:
#   Input: show me all the customers that have a spending score less than 30
#   After filtration: ['show', 'customers', 'spending', 'score', 'less', '30']
#   Conversion:
#       show -> select
#       customers -> customer_data
#       spending, score -> spending_score
#       less -> '<'
#       30 -> 30
#   Output: select * from customer_data where spending_score < 30;


# Generate a list of synonyms for a given word (string)
def syn_generator(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return list(set(synonyms))


# Remove all 'irrelevant' words from a sentence (list of words)
def filter_stopwords(sentence):
    tokens = nltk.word_tokenize(sentence)
    stop_words = set(stopwords.words('english'))
    for condition in constants.condition_names:
        syn_set = syn_generator(condition)
        for x in syn_set:
            if stop_words.__contains__(x):
                stop_words.remove(x)
    return [w for w in tokens if w not in stop_words]


# Returns similarity index of 2 words
def similarity(word1, word2):
    list1 = wordnet.synsets(word1)
    list2 = wordnet.synsets(word2)
    s = list1[0].wup_similarity(list2[0])
    return s


# Returns the maximum similarity for any two elements in two lists.
def max_similarity(list1, list2):
    syn1 = set(ss for word in list1 for ss in wordnet.synsets(word))
    syn2 = set(ss for word in list2 for ss in wordnet.synsets(word))
    best = max((wordnet.wup_similarity(s1, s2) or 0, s1, s2) for s1, s2 in product(syn1, syn2))
    return list(best)[0]


# Recursively find synonyms for words. This can implement the similarity functionality. (string, string, int, int, [])
def recurse_synonym(start_word, end_word, curr_depth, final_depth, used_words):
    if final_depth == curr_depth:
        return False
    temp = syn_generator(start_word)
    used_words.append(start_word)
    syn_list = [x for x in temp if x not in used_words]
    if end_word in syn_list:
        return True
    for syn_word in syn_list:
        rec_index_boolean = recurse_synonym(syn_word, end_word, curr_depth + 1, final_depth, used_words)
        if rec_index_boolean:
            return True
    return False


# Checks if any of the end words can by reached by a start word, with a precision of intended_depth. (list of
# strings, string, int)
def any_synonym(start_word, end_words, depth, accuracy):
    for end_word in end_words:
        x = similarity(start_word, end_word)
        if x is None:
            if recurse_synonym(start_word, end_word, 1, depth, []) is True:
                return end_word
            continue
        if x > accuracy:
            return end_word
    return None


# This function is designed to take in a word, and match it to the corresponding names table
def handle_names(word, names_list, depth):
    for data in names_list:
        breakdown_table = re.split(', |_|-|!', data)
        if any_synonym(word, breakdown_table, depth, 0.7) is not None:
            return data
    return None


def handle_conditions(word, names_list, depth):
    x = handle_names(word, names_list, depth)
    if x is None:
        return None
    elif x is 'less':
        return '<'
    elif x is 'more':
        return '>'
    elif x is 'equal':
        return '='
    elif x is 'not':
        return '!'
    else:
        return None


# Format: select [column_name] from table_name [where column_name condition value]
# This method takes a sentence and composes above functions, returning an array w/ relevant sql statement attributes
def process_select(sentence):
    filtered = filter_stopwords(sentence)
    result = []
    select_flag = False
    column_flag = False
    table_flag = False
    distinct_flag = False
    constant_flag = False
    for word in filtered:
        temp = any_synonym(word, constants.select_names, constants.DESIRED_DEPTH, constants.DESIRED_ACCURACY)
        if temp is not None and not select_flag:
            result.append(temp)
            select_flag = True
            continue
        temp = any_synonym(word, constants.distinct_names, constants.DESIRED_DEPTH, constants.DESIRED_ACCURACY)
        if temp is not None and not distinct_flag:
            result.append(temp)
            distinct_flag = True
            continue
        temp = handle_names(word, constants.column_names, constants.DESIRED_DEPTH)
        if temp is not None:
            if result[len(result) - 1] == temp:
                continue
            if table_flag and not constant_flag:
                result.append('where')
            if table_flag and constant_flag:
                result.append('and')  # change this to be or as well
            if column_flag and not table_flag:
                result.append(",")
            result.append(temp)
            column_flag = True
            continue
        temp = handle_names(word, constants.table_names, constants.DESIRED_DEPTH)
        if temp is not None and not table_flag:
            if not column_flag:
                result.append('*')
            result.append('from')
            result.append(temp)
            table_flag = True
            continue
        temp = handle_conditions(word, constants.condition_names, constants.DESIRED_DEPTH)
        if temp is not None:
            result.append(temp)
            continue
        if word.isnumeric():
            result.append(word)
            constant_flag = True
        _, tag = pos_tag([word])[0] if pos_tag([word])[0] is not None else (None, None)
        if tag is None:
            continue
        if tag == 'NNP':
            result.append("\'" + word + "\'")
            constant_flag = True
    result.append(';')
    return result


def format_statement(sentence):
    return ' '.join(process_select(sentence))
