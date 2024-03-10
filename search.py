import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

class Search:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.es = Elasticsearch('http://localhost:9200')
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        print(client_info.body)

    def create_index(self):
        self.es.indices.delete(index='my_documents', ignore_unavailable=True)
        self.es.indices.create(index='my_documents', body={
            'settings': {
                'analysis': {
                    # Any custom analysis settings
                },
                'similarity': {
                    'my_custom_similarity': {
                        'type': 'BM25',
                        'k1': 1.2, # high k1 means query freq in doc is more important, used defaults for testing
                        'b': 0.75 # high b means field length is more important, used defaults for testing
                    }
                }
            },
            'mappings': {
                'properties': {
                    'title': {
                        'type': 'text',
                        'similarity': 'my_custom_similarity'
                    },
                    'content': {
                        'type': 'text',
                    },
                    'summary': {
                        'type': 'text',
                    },
                    'tags': {
                        'type': 'text',
                    },
                    'embedding': {
                        'type': 'dense_vector',
                        'dims': 384
                    }
                }
            }
        })
        print('Index created with custom BM25 settings.')

    def get_embedding(self, document):
        # Combine title, content, and summary into a single text block
        combined_text = f"{document['title']} {document['content']} {document['summary']} {document['tags']}"
        # Generate embedding for the combined text
        return self.model.encode(combined_text)

    def insert_document(self, document):
        # Generate embedding for the combined text of title, content, and summary
        embedding = self.get_embedding(document)
        # Insert the document along with its embedding into Elasticsearch
        return self.es.index(index='my_documents', document={
            **document,
            'embedding': embedding,
        })

    def insert_documents(self, documents):
        operations = []
        for document in documents:
            # Generate embedding for the combined text of title, content, and summary, tags for each document
            embedding = self.get_embedding(document)
            operations.append({'index': {'_index': 'my_documents'}})
            operations.append({
                **document,
                'embedding': embedding,
            })
        # Execute bulk insertion in Elasticsearch
        return self.es.bulk(operations=operations)

    def reindex(self):
        self.create_index()
        with open('zurich_merged_data.json', 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents)

    def search(self, index='my_documents', **query_args):
        return self.es.search(index=index, **query_args)

    def retrieve_document(self, id):
        return self.es.get(index='my_documents', id=id)

    def get_query_embedding(self, query):
        return self.model.encode(query)

