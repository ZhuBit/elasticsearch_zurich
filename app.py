import re
from flask import Flask, render_template
from search import Search
from openai import OpenAI
import os
from flask import request, jsonify

app = Flask(__name__)
es = Search()


@app.get('/')
def index():
    return render_template('chat.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)

    # Generate query embedding using the updated method
    query_vector = es.get_query_embedding(parsed_query)

    # Define the search query with KNN and boosting tags field
    search_query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "title": parsed_query
                        }
                    },
                    {
                        "match": {
                            "content": parsed_query
                        }
                    },
                    {
                        "match": {
                            "summary": parsed_query
                        }
                    },
                    {
                        "match": {
                            "tags": {
                                "query": parsed_query,
                                "boost": 2.0  # boost the tags field used 2 for testing
                            }
                        }
                    },
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0", # Cosine similaraty for the query vector and the embedding( 1.0 is added to avoid negative score)
                                "params": {
                                    "query_vector": query_vector
                                }
                            }
                        }
                    }
                ]
            }
        },
        "size": 5,
        "from": from_,
        "_source": {"excludes": ["embedding"]}  # Exclude embedding from the source if not needed
    }

    results = es.search(body=search_query)
    if results['hits']['hits']:
        chat_results = []
        # Generate an answer based on the parsed query and the content of the first search result
        answer = generate_answer(parsed_query, results['hits']['hits'][0]['_source']['content'])
        chat_results = [answer]
    else:
        chat_results = []

    # Render the search results
    return render_template('chat.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], chat_results=chat_results)

@app.cli.command()
def reindex():
    # Create the index with custom BM25 settings
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')

@app.get('/document/<id>')
def get_document(id):
    # Retrieve the document from Elasticsearch
    document = es.retrieve_document(id)
    title = document['_source']['name']
    paragraphs = document['_source']['content'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)

def extract_filters(query): # Extract filters from the query, not used in the current implementation
    filters = []

    filter_regex = r'category:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'category.keyword': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    filter_regex = r'year:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'range': {
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query


@app.post('/documents')
def store_document():
    # Save doc from JSON request to Elasticsearch
    document_data = request.json

    # Process the document
    embedding = es.get_embedding(document_data)

    # Add embedding to document data
    document_data['embedding'] = embedding

    # Store the document in Elasticsearch
    result = es.insert_document(document_data)

    if not isinstance(result, dict):
        result = vars(result)

    # Return a success response
    return jsonify(result), 201


def generate_answer(question, context):
    # Call OpenAI API to generate an answer
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
    )
    # Prompt for the chat completion
    prompt = f'Question: {question}\n Answer: {context}\n Please answere the question based on context, Be short. \n I there is no context anser: "Sorry I coud not find the thing you where looking foor", '
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system",
                 "content": "You are a helpful  and cheerful assistant for Zurich City tourist that can answer questions in a given context."},
                {"role": "user", "content": prompt},
            ]
        )
        answer = response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error while calling OpenAI API: {e}")
        answer = "Sorry, I am not able to answer this question at the moment."
    return answer



