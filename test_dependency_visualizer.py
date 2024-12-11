import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from dependency_visualizer import DependencyVisualizer


class TestDependencyVisualizer(unittest.TestCase):

    def setUp(self):
        # Настройка объекта визуализатора с необходимыми аттрибутами
        self.visualizer = DependencyVisualizer(
            visualize_tool_path="C:\\Program Files\\Graphviz\\bin\\dot.exe",  # Путь к dot.exe
            repo_path="C:\\Users\\mmyty\\PycharmProjects\\cm_hw2",
            result_file_path="C:\\Users\\mmyty\\PycharmProjects\\cm_hw2\\output.dot",
            cutoff_date='2024-12-01' # Задание даты отсечения
        )

    @patch('git.Repo')  # Мокируем объект репозитория git
    def test_get_commits_before_date(self, MockRepo):
        # Мокируем репозиторий и его методы
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo

        # Создаем два фиктивных коммита
        commit1 = MagicMock()
        commit1.committed_datetime = '2024-12-30'
        commit1.hexsha = '0aeb162f9efb6a78fac7ac4ccfd25d2b7a835af2'  # Добавляем hexsha для сравнения

        commit2 = MagicMock()
        commit2.committed_datetime = '2024-12-02'
        commit2.hexsha = 'abcdef2'  # Добавляем hexsha для сравнения

        # Указываем, что репозиторий имеет эти два коммита
        mock_repo.iter_commits.return_value = [commit1, commit2]

        # Вызываем метод
        commits = self.visualizer.get_commits_before_date()

        # Проверяем, что commit2 исключен, потому что он позже cutoff_date
        commit1_hexsha = commit1.hexsha
        commit2_hexsha = commit2.hexsha

        self.assertIn(commit1_hexsha, [commit.hexsha for commit in commits])
        self.assertNotIn(commit2_hexsha, [commit.hexsha for commit in commits])

    @patch('git.Commit')  # Мокируем коммит
    def test_get_files_in_commit(self, MockCommit):
        # Мокируем данные коммита
        mock_commit = MagicMock()

        # Мокируем изменения в коммите
        diff = MagicMock()
        diff.a_path = 'file1.py'
        diff.b_path = 'file2.py'
        mock_commit.diff.return_value = [diff]

        # Вызываем метод
        files = self.visualizer.get_files_in_commit(mock_commit)

        # Проверяем, что список файлов не пуст и содержит нужные файлы
        self.assertEqual(files, ['file1.py', 'file2.py'])

    @patch('git.Repo')
    @patch('subprocess.run')
    def test_build_dependency_graph(self, mock_subprocess, MockRepo):
        # Мокаем коммит
        mock_commit = MagicMock()
        mock_commit.hexsha = 'abcdef1234567'

        # Мокаем дату как объект datetime, а не строку
        mock_commit.committed_datetime = datetime.strptime('2024-12-01', '%Y-%m-%d')

        mock_commit.parents = []  # Этот коммит не имеет родителей
        mock_commit.diff.return_value = []  # Мокаем отсутствие изменений в файлах

        # Мокаем репозиторий
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.iter_commits.return_value = [mock_commit]

        # Создаем экземпляр визуализатора
        visualizer = DependencyVisualizer(
            repo_path="test_repo",
            visualize_tool_path="graphviz_path",
            result_file_path="result.dot",
            cutoff_date="2024-12-02"
        )

        # Строим граф
        graph_code = visualizer.build_dependency_graph()

        # Проверяем, что граф начинается с 'digraph G {' и содержит хеш коммита
        self.assertIn('digraph G {', graph_code)
        self.assertIn('abcdef1', graph_code)  # Хеш коммита должен быть обрезан до первых 7 символов

    @patch('subprocess.run')  # Мокируем subprocess.run
    def test_visualize(self, mock_run):
        # Мокируем работу визуализатора
        self.visualizer.build_dependency_graph = MagicMock(
            return_value="digraph G {...}")  # Мокируем метод построения графа
        self.visualizer.save_graph_to_file = MagicMock()  # Мокируем сохранение в файл

        # Вызываем метод
        self.visualizer.visualize()

        # Проверяем, что subprocess.run был вызван (что означает, что визуализация была произведена)
        mock_run.assert_called_once_with([
            self.visualizer.visualize_tool_path, '-Tpng', self.visualizer.result_file_path, '-o', 'dependency_graph.png'
        ])


if __name__ == '__main__':
    unittest.main()
