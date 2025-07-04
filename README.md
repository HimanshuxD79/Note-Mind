Memory Assistant
A intelligent assistant that can remember specific information provided by the user and use it to answer queries. It leverages a PostgreSQL database to store memories, Chroma for vector embeddings, and Ollama with the Llama3 model for natural language processing.
Features

Store specific memories using the /memorize command.
Retrieve relevant memories when answering user queries.
Classify memories to ensure only pertinent information is used.
User-friendly interface powered by Streamlit.

Technologies Used

Python
PostgreSQL
Chroma
Ollama (with Llama3 model)
Streamlit

Prerequisites

PostgreSQL installed and running.
Ollama installed with the Llama3 model available.
Python 3.8 or higher.

Installation

Clone the repository:
git clone https://github.com/HimanshuxD79/Note-Mind.git


Create a virtual environment and activate it:
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`


Install the required packages:
pip install -r requirements.txt


Set up the PostgreSQL database:

Create a database named note_mind.
Update the DB_PARAMS  with your database credentials.


Ensure Ollama is installed and the Llama3 model is available.

Set up Chroma:

The project uses a persistent Chroma client stored in ./chroma_data.



Usage
To run the application:
streamlit run V3.py


Use the /memorize <info> command to store information 

Configuration

Update the DB_PARAMS dictionary in V3.py with your PostgreSQL credentials.
Ensure the Chroma data directory (./chroma_data) has write permissions.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.
License
This project is licensed under the MIT License. See the LICENSE file for details.
