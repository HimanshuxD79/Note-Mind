# Memory Assistant

A intelligent assistant that can remember specific information provided by the user and use it to answer queries. It leverages a PostgreSQL database to store memories, Chroma for vector embeddings, and Ollama with the Llama3 model for natural language processing.

## Features

- Store specific memories using the `/memorize` command.
- Retrieve relevant memories when answering user queries.
- Classify memories to ensure only pertinent information is used.
- User-friendly interface powered by Streamlit.

## Technologies Used

- Python
- PostgreSQL
- Chroma
- Ollama (with Llama3 model)
- Streamlit

## Prerequisites

- PostgreSQL installed and running.
- Ollama installed with the Llama3 model available.
- Python 3.8 or higher.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/note_mind.git
   cd note_mind
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   - Create a database named `note_mind`.
   - Update the `DB_PARAMS` in `V3.py` with your database credentials.

5. Ensure Ollama is installed and the Llama3 model is available.

6. Set up Chroma:
   - The project uses a persistent Chroma client stored in `./chroma_data`.

## Usage

To run the application:

```
streamlit run V3.py
```

- Use the `/memorize <info>` command to store information (e.g., `/memorize My passport is in the drawer`).
- Ask questions like "Where is my passport?" to retrieve stored memories.

## Configuration

- Update the `DB_PARAMS` dictionary in `V3.py` with your PostgreSQL credentials.
- Ensure the Chroma data directory (`./chroma_data`) has write permissions.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
