from flask import Flask, request, jsonify
from github import Github
from llama_index.readers.github import GithubRepositoryReader, GithubClient
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv
import nest_asyncio
import traceback
from typing import Dict, Optional
import threading

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Apply nest_asyncio for async operations
nest_asyncio.apply()

# Cache for storing repository indexes
repo_cache: Dict[str, VectorStoreIndex] = {}
cache_lock = threading.Lock()

def load_github_docs(repo_name: str, github_token: str = None, branch: str = "main") -> Optional[VectorStoreIndex]:
    """
    Load documentation from a GitHub repository and create an index.
    """
    try:
        # Get GitHub token from environment if not provided
        if github_token is None:
            github_token = os.getenv('GITHUB_TOKEN')
            if not github_token:
                raise ValueError("GitHub token not found")

        # Initialize Github client
        g = Github(github_token)
        
        # Split repo name into owner and repo
        owner = repo_name.split('/')[0]
        repo = repo_name.split('/')[1]
        
        # Get the repository and branch reference
        repository = g.get_repo(f"{owner}/{repo}")
        branch_ref = repository.get_branch(branch)
        
        # Initialize GitHub client and reader
        github_client = GithubClient(github_token)
        reader = GithubRepositoryReader(
            github_client=github_client,
            owner=owner,
            repo=repo,
            verbose=True
        )
        
        # Load documents
        documents = reader.load_data(
            commit_sha=branch_ref.commit.sha
        )
        
        if not documents:
            return None
        
        # Create and return the index
        return VectorStoreIndex.from_documents(
            documents,
            show_progress=True
        )
    
    except Exception as e:
        print(f"Error loading repository: {str(e)}")
        print(traceback.format_exc())
        return None
    finally:
        g.close()

def get_or_create_index(repo_name: str, branch: str = "main") -> Optional[VectorStoreIndex]:
    """
    Get index from cache or create new one.
    """
    cache_key = f"{repo_name}:{branch}"
    
    with cache_lock:
        if cache_key not in repo_cache:
            index = load_github_docs(repo_name, branch=branch)
            if index:
                repo_cache[cache_key] = index
        return repo_cache.get(cache_key)

@app.route('/query', methods=['POST'])
def query_docs():
    """
    Endpoint to query documentation.
    
    Expected JSON payload:
    {
        "repo": "owner/repo",
        "query": "your question here",
        "branch": "main"  # optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'repo' not in data or 'query' not in data:
            return jsonify({
                'error': 'Missing required parameters'
            }), 400
            
        repo = data['repo']
        query = data['query']
        branch = data.get('branch', 'main')
        
        # Get or create index
        index = get_or_create_index(repo, branch)
        if not index:
            return jsonify({
                'error': 'Failed to load repository'
            }), 500
            
        # Create query engine with OpenAI
        llm = OpenAI(model="gpt-3.5-turbo")
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            llm=llm
        )
        
        # Execute query
        response = query_engine.query(query)
        
        return jsonify({
            'response': str(response),
            'sources': [str(node.node.text) for node in response.source_nodes]
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Make sure environment variables are set
    required_vars = ['GITHUB_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
