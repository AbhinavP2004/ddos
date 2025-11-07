from flask import Flask, request, jsonify
import numpy as np 
import multiprocessing

app = Flask(__name__)

BIND_HOST="0.0.0.0"
BIND_PORT=5000

currect_connections = 0
connection_lock = threading.Lock()

def get_max_connections():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    if cpu_usage < 50 and memory_usage < 70:
        return 200
    elif cpu_usage < 70 and memory_usage < 85:
        return 150
    else:
        return 50
        
@app.before_request
def check_connections():
    global current_connections
    max_connections = get_max_connections()
    with connection_lock:
        if current_connections >= max_connections:
            abort(503, description="Server is at max connection limit.")
        current_connections += 1
        
@app.after_request
def track_connection_usage(response):
    global current_connections
    with connection_lock:
        current_connections -= 1
    return response
    
@app.route('/')
def index():
    return "Hello, Flask app with admission control!"

@app.route('/matmul')
def matmul():
	size = 200
	a = np.random.randint(500, 1001, (size,size))
	b = np.random.randint(500, 1001, (size,size))

	with multiprocessing.Pool() as pool:
		result = pool.apply(np.matmul, args=(a,b))

	return jsonify({'result': result.tolist()})

if __name__ == '__main__':
	app.run(host=BIND_HOST, port=BIND_PORT, debug=False)
