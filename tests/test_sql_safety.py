import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.services.sql_validator import validate_sql


class SQLValidatorTests(unittest.TestCase):
    def test_accepts_read_only_select_with_keyword_in_string(self):
        self.assertTrue(validate_sql("SELECT 'updated' AS status"))

    def test_rejects_mutation_and_select_into(self):
        for sql in (
            "UPDATE products SET price = 0",
            "SELECT id INTO backup FROM products",
            "SELECT 1; DROP TABLE products",
        ):
            with self.subTest(sql=sql):
                self.assertFalse(validate_sql(sql))

    def test_rejects_unterminated_comment_or_string(self):
        self.assertFalse(validate_sql("SELECT 1 /* unfinished"))
        self.assertFalse(validate_sql("SELECT 'unfinished"))


class SQLExecutorTests(unittest.TestCase):
    def test_sqlite_executor_rejects_writes_even_when_called_directly(self):
        try:
            from app.services.sql_executor import execute_sql
        except ModuleNotFoundError as error:
            if error.name == "sqlalchemy":
                self.skipTest("SQLAlchemy is unavailable in the current Python runtime")
            raise

        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "test.db"
            with sqlite3.connect(db_path) as connection:
                connection.execute("CREATE TABLE products (id INTEGER)")
                connection.execute("INSERT INTO products VALUES (1)")

            url = f"sqlite:///{db_path.as_posix()}"
            self.assertEqual(execute_sql("SELECT id FROM products", url), [{"id": 1}])
            with self.assertRaises(Exception):
                execute_sql("DELETE FROM products", url)

            with sqlite3.connect(db_path) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM products").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
