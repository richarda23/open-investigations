This project is a series of Jupyter notebooks exploring function argument generation in OpenAI

Notebooks are derived from examples from the [OpenAI Cookbook](https://github.com/openai/openai-cookbook/blob/5783656852d507c335955d14875ebc9902f628ef/examples/How_to_call_functions_with_chat_models.ipynb)

and investigate how good chatgpt is in generating SQL queries for querying the Chinook music database.

`HowToCallFunctionsWithModelGeneratedArguments.ipynb` contains the queries and methods;
[ChinookDBInvestigation.ipynb](ChinookDBInvestigation.ipynb) summarises the results and provides some comments on how good are the queries.

The process is 

1. Tell ChatGPT to respond with SQL and provide a schema
2. Give it an input with a human-written SQL query and a function argument list
3. It responds with a function argument of an SQL query
4. We then query the database with the generated query and get results
5. The results are appended to the messages and sent to ChatGPT
6. ChatGPT provides an answer to the query in plain text


## Before starting

You'll need an OpenAI key exported  as an environment variable OPENAI_API_KEY

## To install

This project uses pipenv to manage dependencies

` pip3 install pipenv --user`

and add pipenv to your PATH if needed.


```
pipenv install 
pipenv run jupyter notebook
```

