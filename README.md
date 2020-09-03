# cdp-nlp

This project is an idea for an easier way to generate sql statments via code. 
The premise is that one can give a statement, for example:

"How many customers have a spending score greater than 50"

And have it converted to:

"select count(spending_score) from customer_data where spending_score>50"