import requests


def start_http():
    from fastapi import FastAPI, Response
    import uvicorn

    app = FastAPI()
    mappings = {}

    @app.get("/")
    def test():
        return "ok"

    @app.get("/{file_name}")
    def read_file(file_name: str):
        if file_name in mappings:
            file_name = mappings[file_name]
        with open(f"./tests/test_feeds/{file_name}", "r", encoding="utf-8") as f:
            return Response(f.read(), media_type="application/xml")

    @app.post("/set_mapping")
    def add_mapping(name: str, location: str):
        mappings[name] = location
        return Response("success", status_code=201)

    @app.post("/reset_mappings")
    def reset_mappings():
        mappings.clear()
        return Response("success")

    uvicorn.run(app, host="127.0.0.1", port=8010)


def clear_mappings():
    requests.post("http://127.0.0.1:8010/reset_mappings")


def set_mapping(name, location):
    requests.post(f"http://127.0.0.1:8010/set_mapping?name={name}&location={location}")


def test_endpoint() -> bool:
    try:
        res = requests.get("http://127.0.0.1:8010/")
    except Exception:
        return False
    if not res.ok:
        return False
    return True
