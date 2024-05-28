from flask import Flask, request, abort
import os
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Git sync command or script to pull the latest DAGs
        payload = request.get_json()
        if not payload:
            abort(400)
        update_dags()
        return 'success update dags', 200
    else:
        abort(400)
        return 'failed update dags', 400

def update_dags():
    dags_dir = '/airflow/dags'
    subprocess.run(['git', '-C', dags_dir, 'pull'], check=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)