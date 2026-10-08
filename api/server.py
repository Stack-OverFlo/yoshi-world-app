from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse

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
        body = json.dumps(data, default=str).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def send_empty(self, status=204):
        self.send_response(status)
        self.end_headers()

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            return json.loads(body)
        except (ValueError, json.JSONDecodeError):
            return None

    def get_yoshi_id(self):
        path = urlparse(self.path).path
        parts = path.rstrip("/").split("/")

        if len(parts) == 4 and parts[:3] == ["", "api", "yoshis"]:
            try:
                return int(parts[3])
            except ValueError:
                return None

        return None

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------

    def do_GET(self):

        path = urlparse(self.path).path

        # GET /api/yoshis
        if path == "/api/yoshis":
            try:
                with psycopg.connect(**DB_CONFIG) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT id, name, color, created_at
                            FROM yoshis
                            ORDER BY id;
                            """
                        )

                        yoshis = [
                            {
                                "id": row[0],
                                "name": row[1],
                                "color": row[2],
                                "created_at": row[3],
                            }
                            for row in cur.fetchall()
                        ]

                self.send_json(yoshis)

            except Exception:
                self.send_json(
                    {"error": "Database connection failed"},
                    status=500,
                )

            return

        # GET /api/yoshis/<id>
        yoshi_id = self.get_yoshi_id()

        if yoshi_id is not None:
            try:
                with psycopg.connect(**DB_CONFIG) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT id, name, color, created_at
                            FROM yoshis
                            WHERE id = %s;
                            """,
                            (yoshi_id,),
                        )

                        row = cur.fetchone()

                if row is None:
                    self.send_json(
                        {"error": "Yoshi not found"},
                        status=404,
                    )
                else:
                    self.send_json(
                        {
                            "id": row[0],
                            "name": row[1],
                            "color": row[2],
                            "created_at": row[3],
                        }
                    )

            except Exception:
                self.send_json(
                    {"error": "Database connection failed"},
                    status=500,
                )

            return

        # GET /
        if path == "/":
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

            except Exception:
                body = (
                    "Database connection failed\n"
                ).encode("utf-8")

                self.send_response(500)

            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.end_headers()
            self.wfile.write(body)

            return

        self.send_json(
            {"error": "Not found"},
            status=404,
        )

    # ---------------------------------------------------------
    # POST
    # ---------------------------------------------------------

    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/api/yoshis":
            self.send_json(
                {"error": "Not found"},
                status=404,
            )
            return

        data = self.read_json()

        if not isinstance(data, dict):
            self.send_json(
                {"error": "Invalid JSON"},
                status=400,
            )
            return

        name = data.get("name")
        color = data.get("color")

        if not isinstance(name, str) or not name.strip():
            self.send_json(
                {"error": "name is required"},
                status=400,
            )
            return

        if not isinstance(color, str) or not color.strip():
            self.send_json(
                {"error": "color is required"},
                status=400,
            )
            return

        try:
            with psycopg.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO yoshis (name, color)
                        VALUES (%s, %s)
                        RETURNING id, name, color, created_at;
                        """,
                        (name.strip(), color.strip()),
                    )

                    row = cur.fetchone()

                conn.commit()

            self.send_json(
                {
                    "id": row[0],
                    "name": row[1],
                    "color": row[2],
                    "created_at": row[3],
                },
                status=201,
            )

        except Exception:
            self.send_json(
                {"error": "Database connection failed"},
                status=500,
            )

    # ---------------------------------------------------------
    # PUT
    # ---------------------------------------------------------

    def do_PUT(self):

        yoshi_id = self.get_yoshi_id()

        if yoshi_id is None:
            self.send_json(
                {"error": "Not found"},
                status=404,
            )
            return

        data = self.read_json()

        if not isinstance(data, dict):
            self.send_json(
                {"error": "Invalid JSON"},
                status=400,
            )
            return

        name = data.get("name")
        color = data.get("color")

        if not isinstance(name, str) or not name.strip():
            self.send_json(
                {"error": "name is required"},
                status=400,
            )
            return

        if not isinstance(color, str) or not color.strip():
            self.send_json(
                {"error": "color is required"},
                status=400,
            )
            return

        try:
            with psycopg.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE yoshis
                        SET name = %s,
                            color = %s
                        WHERE id = %s
                        RETURNING id, name, color, created_at;
                        """,
                        (
                            name.strip(),
                            color.strip(),
                            yoshi_id,
                        ),
                    )

                    row = cur.fetchone()

                conn.commit()

            if row is None:
                self.send_json(
                    {"error": "Yoshi not found"},
                    status=404,
                )
                return

            self.send_json(
                {
                    "id": row[0],
                    "name": row[1],
                    "color": row[2],
                    "created_at": row[3],
                }
            )

        except Exception:
            self.send_json(
                {"error": "Database connection failed"},
                status=500,
            )

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def do_DELETE(self):

        yoshi_id = self.get_yoshi_id()

        if yoshi_id is None:
            self.send_json(
                {"error": "Not found"},
                status=404,
            )
            return

        try:
            with psycopg.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM yoshis
                        WHERE id = %s
                        RETURNING id;
                        """,
                        (yoshi_id,),
                    )

                    row = cur.fetchone()

                conn.commit()

            if row is None:
                self.send_json(
                    {"error": "Yoshi not found"},
                    status=404,
                )
                return

            self.send_empty(204)

        except Exception:
            self.send_json(
                {"error": "Database connection failed"},
                status=500,
            )


server = HTTPServer(("0.0.0.0", 8080), Handler)
server.serve_forever()
