import argparse
import subprocess
from pathlib import Path
import os
import datetime
import git

class DependencyVisualizer:
    def __init__(self, repo_path: str, visualize_tool_path: str, result_file_path: str, cutoff_date: str):
        self.repo_path = repo_path
        self.visualize_tool_path = visualize_tool_path
        self.result_file_path = result_file_path
        self.cutoff_date = datetime.datetime.strptime(cutoff_date, '%Y-%m-%d')
        self.repo = git.Repo(self.repo_path)

    def get_commits_before_date(self):
        """
        Возвращает список коммитов, сделанных до заданной даты.
        """
        commits = []
        for commit in self.repo.iter_commits():
            commit_time = commit.committed_datetime.replace(tzinfo=None)  # Преобразуем в naive datetime
            if commit_time < self.cutoff_date:
                commits.append(commit)
        return commits

    def get_files_in_commit(self, commit):
        """
        Возвращает список файлов, измененных в коммите.
        """
        files = []
        for diff in commit.diff('HEAD~1', create_patch=True):
            if diff.a_path and diff.a_path not in files:
                files.append(diff.a_path)
            if diff.b_path and diff.b_path not in files:
                files.append(diff.b_path)
        return files

    def build_dependency_graph(self):
        """
        Строит граф зависимостей для коммитов и файлов.
        """
        commits = self.get_commits_before_date()
        graph_code = "digraph G {\n"

        for commit in commits:
            commit_files = self.get_files_in_commit(commit)
            commit_id = commit.hexsha[:7]
            graph_code += f'  "{commit_id}" [label="Commit: {commit_id}\\nFiles: {", ".join(commit_files)}"];\n'

            for parent in commit.parents:
                parent_id = parent.hexsha[:7]
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



