from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

import psycopg


DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        # GET /api/yoshis
        if self.path == "/api/yoshis":
            try:
                with psycopg.connect(**DB_CONFIG) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT id, name, color
                            FROM yoshis
                            ORDER BY id;
                            """
                        )

                        yoshis = [
                            {
                                "id": row[0],
                                "name": row[1],
                                "color": row[2],
                            }
                            for row in cur.fetchall()
                        ]

                self.send_json(yoshis)

            except Exception as e:
                self.send_json(
                    {"error": f"Database connection failed: {e}"},
                    status=500,
                )

            return

        # GET /
        try:
            with psycopg.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    version = cur.fetchone()[0]

            body = (
                "🥚 Welcome to Yoshi World!\n\n"
                "Database: PostgreSQL\n"
                "Status: Connected\n\n"
                f"{version}\n"
            ).encode("utf-8")

            self.send_response(200)

        except Exception as e:
            body = f"Database connection failed: {e}\n".encode("utf-8")
            self.send_response(500)

        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = HTTPServer(("0.0.0.0", 8080), Handler)
server.serve_forever()
