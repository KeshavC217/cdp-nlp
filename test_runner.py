from filter_words import format_statement


# HANDLED VARIATIONS:
#   select
#   select distinct
#   where (both numeric and string)


# Prints outputs of all test cases and returns True if all expected answers are matched
def run_select_tests(display_toggle):
    all_passed = True
    test_cases = [
        "show me all the customers",
        "give me the spending scores of all the customers",
        "give me the customers who have a spending score not equal to 50",
        "show me the spending scores and house values of all the customers who have a spending score more than 50",
        "give me the discrete house values for all of our customers",
        "show me all the customers where the country is equal to Mexico and their spending score is less than 50",
        "show me the house values of customers with a spending score less than 60"
    ]
    expected_answers = [
        "select * from customer_data ;",
        "select spending_score from customer_data ;",
        "select * from customer_data where spending_score ! = 50 ;",
        "select spending_score , house_value from customer_data where spending_score > 50 ;",
        "select distinct house_value from customer_data ;",
        "select * from customer_data where country = 'Mexico' and spending_score < 50 ;",
        "select house_value from customer_data where spending_score < 60 ;"
    ]
    for i in range(0, len(test_cases)):
        result = format_statement(test_cases[i])
        if display_toggle:
            print(test_cases[i])
            print("#-> ", result)
        all_passed = all_passed and (result == expected_answers[i])
        if all_passed:
            print("-- Passed test", i+1, "--")
        else:
            print("-- Failed test", i+1, "--")
    return all_passed


print(run_select_tests(True))
