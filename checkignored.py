import os
import argparse
import sys


def parse_gitignore(gitignore_path):

    rules = []
    try:
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rules.append(line)
    except FileNotFoundError:
        print(f"Файл {gitignore_path} не найден.", file=sys.stderr)
        sys.exit(1)
    return rules


def file_is_ignored(rel_path, file_name, rules):

    for rule in rules:
        if rule.startswith("*"):
            pattern = rule[1:]
            if file_name.endswith(pattern):
                return True, rule
        else:
            if rel_path == rule:
                return True, rule
    return False, None


def main():
    parser = argparse.ArgumentParser(
        description="Проверка игнорируемых файлов в репозитории по правилам"
    )
    parser.add_argument(
        "--project_dir",
        required=True,
        help="Путь к каталогу репозитория, содержащего файл .gitignore"
    )
    args = parser.parse_args()

    project_dir = os.path.normpath(args.project_dir)
    gitignore_path = os.path.join(project_dir, ".gitignore")
    rules = parse_gitignore(gitignore_path)

    ignored_files = []

    for root, dirs, files in os.walk(project_dir):
        rel_dir = os.path.relpath(root, project_dir)
        for file in files:
            if file == ".gitignore":
                continue
            if rel_dir == ".":
                rel_path = file
            else:
                rel_path = os.path.join(rel_dir, file)

            ignored, rule = file_is_ignored(rel_path, file, rules)
            if ignored:
                if os.path.dirname(rel_path):
                    output_path = os.path.join(os.path.basename(project_dir), rel_path)
                else:
                    output_path = rel_path
                ignored_files.append((output_path, rule))

    print("Ignored files:")
    for filepath, rule in ignored_files:
        print(f"{filepath} ignored by expression {rule}")


main()
