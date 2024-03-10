# Zurich City Guide App

## Overview

This application provides a searchable guide to Zurich's cultural history, landmarks, education, and more, utilizing Elasticsearch for efficient querying and OpenAI for dynamic answer generation. Designed with a Flask, Elasticsearch and simple HTML template, users can interact through a chat interface to find detailed information about Zurich.

## Features

- **Elasticsearch Integration**: Leverages Elasticsearch to index and search through Zurich's city data.
- **Sentence Transformers**: Utilizes `sentence-transformers` for generating document embeddings, enhancing search relevance.
- **OpenAI API**: Employs OpenAI's API for generating contextual answers to user queries.
- **Simple UI**: Offers a straightforward user interface for querying and receiving information.
- **Flask Application**: Built on Flask, facilitating easy web server setup and interaction.

## Requirements

- Python 3.8+
- Elasticsearch 7.x+
- An active OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
