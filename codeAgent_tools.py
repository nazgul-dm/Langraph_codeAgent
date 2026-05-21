import os
import requests
import docker
import uuid
import tempfile

from langchain.tools import tool

# Initialize Docker client once, outside the function
docker_client = docker.from_env()

@tool
def python_sandbox(code: str) -> str:
    """
    Executes Python code securely in a Docker sandbox.
    ALWAYS use this tool when the user asks to:
    - write, run, or execute Python code
    - calculate or compute something with code
    - solve a programming problem

    Available libraries: numpy, pandas, scipy, matplotlib, scikit-learn.
    Always use print() to return results.
    
    Example:
    import numpy as np
    result = np.mean([1, 2, 3])
    print(result)
    """
    
    # Step 1: Write code to temp file
    temp_dir = tempfile.gettempdir()
    
    unique_id = uuid.uuid4().hex
    code_path = os.path.join(temp_dir, f"code_{unique_id}.py")
    
    with open(code_path, "w") as f:
        f.write(f"""
try:
{chr(10).join(f"    {line}" for line in code.splitlines())}
except Exception as e:
    print(f"ERROR: {{str(e)}}")
""")

    # Step 2: Run container
    try:
        output = docker_client.containers.run(
            "my-secure-sandbox",
            command=["python", f"/tmp/code_{unique_id}.py"],
            volumes={temp_dir: {"bind": "/tmp", "mode": "rw"}},
            network_mode="none",
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
            remove=True,
            stdout=True,
            stderr=True,
        )
        return output.decode("utf-8").strip()
    
    except Exception as e:
        return f"Error: {str(e)}"