import argparse
import subprocess
from pathlib import Path
import os
import datetime
import zlib

class DependencyVisualizer:
    def __init__(self, repo_path: str, visualize_tool_path: str, result_file_path: str, cutoff_date: str):
        self.visualize_tool_path = visualize_tool_path
        self.result_file_path = result_file_path
        self.cutoff_date = datetime.datetime.strptime(cutoff_date, '%Y-%m-%d')

        self.repo_path = Path(repo_path).resolve()
        if not (self.repo_path / ".git").exists():
            raise ValueError("Указанный путь не содержит Git-репозиторий.")

    def read_git_object(self, object_hash):
        """Читает объект из .git/objects по его хэшу."""
        object_dir = self.repo_path / ".git" / "objects" / object_hash[:2]
        object_file = object_dir / object_hash[2:]
        print(object_hash[2:])
        if not object_file.exists():
            raise FileNotFoundError(f"Объект {object_hash} не найден в репозитории.")

        with open(object_file, 'rb') as f:
            compressed_data = f.read()
            decompressed_data = zlib.decompress(compressed_data)

        return decompressed_data

    def parse_commit(self, commit_data):
        """Парсит объект коммита, извлекая его метаинформацию и сообщение."""
        header, _, body = commit_data.partition(b'\n\n')
        lines = header.split(b'\n')

        metadata = {}
        for line in lines:
            key, _, value = line.partition(b' ')
            metadata[key.decode()] = value.decode()

        metadata['message'] = body.decode().strip()
        return metadata

    def get_commits_before_date(self):
        """Возвращает список хэшей коммитов, сделанных до заданной даты."""
        head_file = self.repo_path / ".git" / "refs" / "heads" / "master"
        with open(head_file, 'r') as f:
            head_commit = f.read().strip()

        commits = []
        stack = [head_commit]

        while stack:
            current_hash = stack.pop()
            commit_data = self.read_git_object(current_hash)
            commit_info = self.parse_commit(commit_data)

            commit_time = datetime.datetime.fromtimestamp(int(commit_info['committer'].split(' ')[-2]))

            if commit_time < self.cutoff_date:
                commits.append((current_hash, commit_info))

            if 'parent' in commit_info:
                parent_hashes = commit_info['parent'].split()
                stack.extend(parent_hashes)

        return commits

    def build_dependency_graph(self):
        """
        Строит граф зависимостей для коммитов и файлов.
        """
        commits = self.get_commits_before_date()
        graph_code = "digraph G {\n"

        for commit_hash, commit_info in commits:
            commit_id = commit_hash[:7]
            graph_code += f'  "{commit_id}" [label="Commit: {commit_id}\n{commit_info["message"]}"]\n';

            if 'parent' in commit_info:
                for parent_hash in commit_info['parent'].split():
                    parent_id = parent_hash[:7]
                    graph_code += f'  "{parent_id}" -> "{commit_id}";\n'

        graph_code += "}\n"
        return graph_code

    def save_graph_to_file(self, graph_code):
        """
        Сохраняет код графа в файл.
        """
        with open(self.result_file_path, 'w') as result_file:
            result_file.write(graph_code)

    def visualize(self):
        """
        Генерирует визуализацию с помощью Graphviz.
        """
        graph_code = self.build_dependency_graph()
        self.save_graph_to_file(graph_code)

        # Выводим код графа на экран
        print(graph_code)

        # Проверяем, существует ли путь к Graphviz
        if self.visualize_tool_path and os.path.exists(self.visualize_tool_path):
            subprocess.run([self.visualize_tool_path, '-Tpng', self.result_file_path, '-o', 'dependency_graph.png'])
        else:
            print("Graphviz не найден. Пожалуйста, проверьте путь к инструменту визуализации.")

    def run(self):
        """
        Запускает процесс визуализации.
        """
        self.visualize()


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей коммитов Git.")
    parser.add_argument("--visualizer-path", type=Path, required=True, help="Путь к программе для визуализации графов.")
    parser.add_argument("--repo-path", type=Path, required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--output-path", type=Path, required=True, help="Путь к файлу-результату.")
    parser.add_argument("--date", type=str, required=True, help="Дата коммитов (формат YYYY-MM-DD).")

    args = parser.parse_args()

    repo_path = args.repo_path
    visualize_tool_path = args.visualizer_path  # Путь к инструменту Graphviz
    result_file_path = args.output_path
    cutoff_date = args.date

    visualizer = DependencyVisualizer(repo_path, visualize_tool_path, result_file_path, cutoff_date)
    visualizer.run()

if __name__ == "__main__":
    main()

# Пример использования класса
# if __name__ == '__main__':
#     repo_path = 'C:\\Users\\mmyty\\PycharmProjects\\cm_hw2'
#     visualize_tool_path = 'C:\\Program Files\\Graphviz\\bin\\dot.exe'  # Путь к инструменту Graphviz
#     result_file_path = 'C:\\Users\\mmyty\\PycharmProjects\\cm_hw2\\output.dot'
#     cutoff_date = '2025-01-01'
#
#     visualizer = DependencyVisualizer(repo_path, visualize_tool_path, result_file_path, cutoff_date)
#     visualizer.run()



