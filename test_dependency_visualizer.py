import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import datetime
import zlib
from dependency_visualizer import DependencyVisualizer  # Импорт вашего класса

class TestDependencyVisualizer(unittest.TestCase):

    def setUp(self):
        # Настройки для тестов
        self.repo_path = "C:\\Users\\mmyty\\PycharmProjects\\PythonProject\\cm_hw2\\repository"
        self.visualize_tool_path = "C:/Program Files/Graphviz/bin/dot.exe"
        self.result_file_path = "C:\\Users\\mmyty\\PycharmProjects\\PythonProject\\cm_hw2\\test_output.dot"
        self.cutoff_date = "2025-01-01"
        self.visualizer = DependencyVisualizer(
            repo_path=self.repo_path,
            visualize_tool_path=self.visualize_tool_path,
            result_file_path=self.result_file_path,
            cutoff_date=self.cutoff_date,
        )

    @patch("pathlib.Path.exists")
    def test_repo_validation(self, mock_exists):
        # Тест валидации репозитория
        mock_exists.return_value = True
        visualizer = DependencyVisualizer(
            repo_path=self.repo_path,
            visualize_tool_path=self.visualize_tool_path,
            result_file_path=self.result_file_path,
            cutoff_date=self.cutoff_date,
        )
        self.assertTrue((Path(self.repo_path) / ".git").exists())

        mock_exists.return_value = False
        with self.assertRaises(ValueError):
            DependencyVisualizer(
                repo_path="invalid_path",
                visualize_tool_path=self.visualize_tool_path,
                result_file_path=self.result_file_path,
                cutoff_date=self.cutoff_date,
            )

    @patch("builtins.open", new_callable=mock_open, read_data=zlib.compress(b"commit data"))
    @patch("pathlib.Path.exists")
    def test_read_git_object(self, mock_exists, mock_open):
        # Настраиваем существование файла объекта
        mock_exists.return_value = True

        # Хэш объекта
        object_hash = "ad18c544e589f63fa8d21646844ff88a02aacf4c"

        # Читаем объект
        decompressed_data = self.visualizer.read_git_object(object_hash)

        # Проверяем, что объект был распакован правильно
        self.assertEqual(decompressed_data, b"commit data")

        # Проверяем правильность пути к объекту
        expected_path = Path(self.repo_path) / ".git" / "objects" / "ad" / "18c544e589f63fa8d21646844ff88a02aacf4c"
        mock_open.assert_called_once_with(expected_path, 'rb')

        # Проверяем, что Path.exists() был вызван корректно
        mock_exists.assert_called_once_with()

    def test_parse_commit(self):
        # Тест парсинга коммита
        commit_data = b"tree abcdef1234567890\nparent 1234567890abcdef\nauthor Test User <test@example.com> 1672531199 +0000\ncommitter Test User <test@example.com> 1672531199 +0000\n\nInitial commit"
        parsed_data = self.visualizer.parse_commit(commit_data)
        self.assertEqual(parsed_data['tree'], "abcdef1234567890")
        self.assertEqual(parsed_data['parent'], "1234567890abcdef")
        self.assertEqual(parsed_data['author'], "Test User <test@example.com> 1672531199 +0000")
        self.assertEqual(parsed_data['committer'], "Test User <test@example.com> 1672531199 +0000")
        self.assertEqual(parsed_data['message'], "Initial commit")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_graph_to_file(self, mock_open):
        # Тест сохранения графа в файл
        graph_code = "digraph G {\n}"
        self.visualizer.save_graph_to_file(graph_code)
        mock_open.assert_called_once_with(self.result_file_path, 'w')
        mock_open().write.assert_called_once_with(graph_code)

if __name__ == "__main__":
    unittest.main()
