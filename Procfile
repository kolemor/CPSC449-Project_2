enrollment: uvicorn enrollment:app --host 0.0.0.0 --port $PORT --reload
users: uvicorn users:app --host 0.0.0.0 --port $PORT --reload
krakend: echo ./etc/krakend.json | entr -nrz krakend run --config etc/krakend.json --port $PORT