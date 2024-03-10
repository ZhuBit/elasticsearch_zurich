# Zurich City Guide App

## Overview

This application provides a searchable guide to Zurich's cultural history, landmarks, education, and more, utilizing Elasticsearch for efficient querying and OpenAI for dynamic answer generation. Designed with a Flask, Elasticsearch and simple HTML template, users can interact through a chat interface to find detailed information about Zurich.

## Features

- **Elasticsearch Integration**: Leverages Elasticsearch to index and search through Zurich's city data.
- **Sentence Transformers**: Utilizes `sentence-transformers` for generating document embeddings, enhancing search relevance.
- **OpenAI API**: Employs OpenAI's API for generating contextual answers to user queries.
- **Simple UI**: Offers a straightforward user interface for querying and receiving information.
- **Flask Application**: Built on Flask, facilitating easy web server setup and interaction.

## Data Variety Disclaimer

Please note that the data utilized in this application was sourced through web scraping from Zurich's official city site, focusing on cultural history, landmarks, education, and more. Therefore, simple searches related to broad categories like Landmarks, History, Politics, Travel, and Tourism are more likely to yield reliable results. Users seeking highly specific or nuanced information should verify the data through additional sources when necessary.


## Installation

1. Clone the repository:

```bash
git clone git@github.com:ZhuBit/elasticsearch_zurich.git
```

2. Creat .env file with:
```bash
OPENAI_API_KEY=<your_openai_api_key>
```
3. Install the required packages:

```bash
pip install -r requirements.txt
```
4. Creat docker container for elasticsearch:
```bash
docker run -p 9200:9200 -d --name elasticsearch_zurich \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "xpack.security.http.ssl.enabled=false" \
  -e "xpack.license.self_generated.type=trial" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
 ```
5. Start Docker container:
```bash
docker start <container_id>
```
6. Create index and index data:
```bash
flask reindex
```
7. Run the application:

```bash
flask run
```

## Requirements

- Python 3.8+
- Elasticsearch 7.x+
- An active OpenAI API key