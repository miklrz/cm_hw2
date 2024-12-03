import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from graphviz import Digraph


def get_git_commits(repo_path: Path, date: str):
    """
    Извлекает список коммитов до заданной даты вместе со списками измененных файлов.
    """
    command = [
        "git", "-C", str(repo_path),
        "log", "--pretty=format:%H %at", "--name-only", "--before", date
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    commits = []
    for block in result.stdout.strip().split("\n\n"):
        lines = block.strip().split("\n")
        commit_hash, timestamp = lines[0].split()[:2]
        files = lines[1:] if len(lines) > 1 else []
        commits.append({
            "hash": commit_hash,
            "timestamp": int(timestamp),
            "files": files
        })
    return commits


def build_dependency_graph(commits):
    """
    Строит граф зависимостей коммитов, основываясь на изменениях в файлах.
    """
    graph = Digraph()
    graph.attr(rankdir="LR")

    for commit in commits:
        node_label = f"{commit['hash'][:7]}\\n{datetime.utcfromtimestamp(commit['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}"
        if commit["files"]:
            node_label += "\\n" + "\\n".join(commit["files"])
        graph.node(commit["hash"], label=node_label, shape="box")

    for i in range(len(commits) - 1):
        graph.edge(commits[i + 1]["hash"], commits[i]["hash"])

    return graph


def save_graph_to_file(graph, output_path):
    """
    Сохраняет граф в текстовом виде в файл.
    """
    with open(output_path, "w") as file:
        file.write(graph.source)


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей коммитов Git.")
    parser.add_argument("--visualizer-path", type=Path, required=True, help="Путь к программе для визуализации графов.")
    parser.add_argument("--repo-path", type=Path, required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--output-path", type=Path, required=True, help="Путь к файлу-результату.")
    parser.add_argument("--date", type=str, required=True, help="Дата коммитов (формат YYYY-MM-DD).")

    args = parser.parse_args()

    commits = get_git_commits(args.repo_path, args.date)
    if not commits:
        print("Нет коммитов до заданной даты.")
        return

    graph = build_dependency_graph(commits)
    save_graph_to_file(graph, args.output_path)
    print(f"Граф успешно сохранен в файл: {args.output_path}")


if __name__ == "__main__":
    main()
