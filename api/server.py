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


def get_connection():
    return psycopg.connect(**DB_CONFIG)


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()

        self.wfile.write(body)

    def read_json(self):
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        if content_length == 0:
            return {}

        body = self.rfile.read(content_length)

        try:
            return json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Invalid JSON")

    def get_yoshi_id(self):
        path = urlparse(self.path).path
        parts = path.rstrip("/").split("/")

        if len(parts) == 4 and parts[:3] == [
            "",
            "api",
            "yoshis"
        ]:
            try:
                return int(parts[3])
            except ValueError:
                return None

        return None

    def validate_yoshi(self, data):
        name = data.get("name")
        color = data.get("color")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name is required")

        if not isinstance(color, str) or not color.strip():
            raise ValueError("Color is required")

        description = data.get("description")

        if description is not None and not isinstance(
            description,
            str
        ):
            raise ValueError(
                "Description must be a string"
            )

        image = data.get("image")

        if image is not None and not isinstance(
            image,
            str
        ):
            raise ValueError(
                "Image must be a string"
            )

        return (
            name.strip(),
            color.strip(),
            description.strip()
            if isinstance(description, str)
            else None,
            image.strip()
            if isinstance(image, str)
            else None,
        )

    def do_GET(self):

        path = urlparse(self.path).path

        # GET /api/yoshis
        if path == "/api/yoshis":

            with get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute("""
                        SELECT
                            id,
                            name,
                            color,
                            description,
                            image,
                            created_at
                        FROM yoshis
                        ORDER BY id
                    """)

                    rows = cur.fetchall()

            yoshis = [
                {
                    "id": row[0],
                    "name": row[1],
                    "color": row[2],
                    "description": row[3],
                    "image": row[4],
                    "created_at": row[5],
                }
                for row in rows
            ]

            self.send_json(yoshis)
            return

        # GET /api/yoshis/<id>
        yoshi_id = self.get_yoshi_id()

        if yoshi_id is not None:

            with get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute("""
                        SELECT
                            id,
                            name,
                            color,
                            description,
                            image,
                            created_at
                        FROM yoshis
                        WHERE id = %s
                    """, (yoshi_id,))

                    row = cur.fetchone()

            if row is None:
                self.send_json(
                    {"error": "Yoshi not found"},
                    404
                )
                return

            self.send_json({
                "id": row[0],
                "name": row[1],
                "color": row[2],
                "description": row[3],
                "image": row[4],
                "created_at": row[5],
            })

            return

        # GET /
        if path == "/":

            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]

            self.send_json({
                "status": "ok",
                "database": "PostgreSQL",
                "version": version,
            })

            return

        self.send_json(
            {"error": "Not found"},
            404
        )

    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/api/yoshis":
            self.send_json(
                {"error": "Not found"},
                404
            )
            return

        try:
            data = self.read_json()

            name, color, description, image = (
                self.validate_yoshi(data)
            )

        except ValueError as error:
            self.send_json(
                {"error": str(error)},
                400
            )
            return

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("""
                    INSERT INTO yoshis
                        (
                            name,
                            color,
                            description,
                            image
                        )
                    VALUES
                        (%s, %s, %s, %s)
                    RETURNING
                        id,
                        name,
                        color,
                        description,
                        image,
                        created_at
                """, (
                    name,
                    color,
                    description,
                    image,
                ))

                row = cur.fetchone()

            conn.commit()

        self.send_json({
            "id": row[0],
            "name": row[1],
            "color": row[2],
            "description": row[3],
            "image": row[4],
            "created_at": row[5],
        }, 201)

    def do_PUT(self):

        yoshi_id = self.get_yoshi_id()

        if yoshi_id is None:
            self.send_json(
                {"error": "Not found"},
                404
            )
            return

        try:
            data = self.read_json()

            name, color, description, image = (
                self.validate_yoshi(data)
            )

        except ValueError as error:
            self.send_json(
                {"error": str(error)},
                400
            )
            return

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("""
                    UPDATE yoshis
                    SET
                        name = %s,
                        color = %s,
                        description = %s,
                        image = %s
                    WHERE id = %s
                    RETURNING
                        id,
                        name,
                        color,
                        description,
                        image,
                        created_at
                """, (
                    name,
                    color,
                    description,
                    image,
                    yoshi_id,
                ))

                row = cur.fetchone()

            conn.commit()

        if row is None:
            self.send_json(
                {"error": "Yoshi not found"},
                404
            )
            return

        self.send_json({
            "id": row[0],
            "name": row[1],
            "color": row[2],
            "description": row[3],
            "image": row[4],
            "created_at": row[5],
        })

    def do_DELETE(self):

        yoshi_id = self.get_yoshi_id()

        if yoshi_id is None:
            self.send_json(
                {"error": "Not found"},
                404
            )
            return

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("""
                    DELETE FROM yoshis
                    WHERE id = %s
                    RETURNING id
                """, (yoshi_id,))

                row = cur.fetchone()

            conn.commit()

        if row is None:
            self.send_json(
                {"error": "Yoshi not found"},
                404
            )
            return

        self.send_response(204)
        self.end_headers()


server = HTTPServer(
    ("0.0.0.0", 8080),
    Handler
)

print("Yoshi API listening on port 8080")

server.serve_forever()
