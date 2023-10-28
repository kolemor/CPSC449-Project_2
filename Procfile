enrollment: uvicorn enrollment.enrollment:app --host 0.0.0.0 --port $PORT --reload
litefs_primary: bin/litefs mount -config etc/primary.yml
litefs_secondary: bin/litefs mount -config etc/secondary.yml
litefs_ternary: bin/litefs mount -config etc/ternary.yml
krakend: echo ./etc/krakend.json | entr -nrz krakend run --config etc/krakend.json --port $PORT
