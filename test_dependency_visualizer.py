import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from dependency_visualizer import get_git_commits, build_dependency_graph

class TestDependencyVisualizer(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_git_commits(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=(
                "abc123 1690000000\nfile1.txt\nfile2.txt\n\n"
                "def456 1689990000\nfile3.txt\n"
            )
        )
        commits = get_git_commits(Path("/path/to/repo"), "2024-01-01")
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["hash"], "abc123")
        self.assertEqual(commits[0]["files"], ["file1.txt", "file2.txt"])

    def test_build_dependency_graph(self):
        commits = [
            {"hash": "abc123", "timestamp": 1690000000, "files": ["file1.txt"]},
            {"hash": "def456", "timestamp": 1689990000, "files": ["file2.txt"]},
        ]
        graph = build_dependency_graph(commits)
        self.assertIn("abc123", graph.source)
        self.assertIn("def456", graph.source)
        self.assertIn("abc123 -> def456", graph.source)

if __name__ == "__main__":
    unittest.main()
