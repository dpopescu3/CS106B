import subprocess
import tempfile
import os
import shutil
import re
import sys
import json
from collections import defaultdict

def run_git_command(args, cwd):
    result = subprocess.run(['git'] + args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(args)}\n{result.stderr}")
    return result.stdout.strip()

def get_all_commits(directory):
    return run_git_command(['log', '--pretty=format:%H'], directory).splitlines()

def extract_cpp_files_from_commit(repo_path, commit_hash, subdirectory):
    file_contents = {}
    files = run_git_command(['ls-tree', '-r', '--name-only', commit_hash, subdirectory], repo_path).splitlines()
    for file in files:
        if file.endswith('.cpp'):
            try:
                contents = run_git_command(['show', f'{commit_hash}:{file}'], repo_path)
                file_contents[file] = contents
            except Exception:
                pass  # skip if file not found in this commit
    return file_contents

def count_comments_and_code_from_text(text):
    comment_count = 0
    loc_count = 0
    in_block_comment = False

    for line in text.splitlines():
        stripped = line.strip()

        if in_block_comment:
            if '*/' in stripped:
                in_block_comment = False
            continue

        if '/*' in stripped:
            if '*/' not in stripped or stripped.index('/*') > stripped.index('*/'):
                in_block_comment = True
            comment_count += 1
            continue

        quote_free = re.sub(r'"[^"]*"', '', stripped)
        if '//' in quote_free:
            comment_count += 1
            continue

        if stripped:
            loc_count += 1

    return comment_count, loc_count

def count_new_comments_from_diff(diff_text):
    file_comments = defaultdict(int)
    current_file = None
    in_block_comment = False

    for line in diff_text.splitlines():
        if line.startswith('+++ b/'):
            current_file = line[6:]
        elif current_file and line.startswith('+') and not line.startswith('+++'):
            content = line[1:].strip()

            if in_block_comment:
                if '*/' in content:
                    in_block_comment = False
                continue

            if '/*' in content:
                if '*/' not in content or content.index('/*') > content.index('*/'):
                    in_block_comment = True
                file_comments[current_file] += 1
                continue

            if '//' in re.sub(r'"[^"]*"', '', content):
                file_comments[current_file] += 1

    return file_comments

def analyze_git_history_by_file(repo_path, subdirectory):
    commits = get_all_commits(repo_path)
    commit_data = defaultdict(dict)

    for i, commit in enumerate(commits):
        current_files = extract_cpp_files_from_commit(repo_path, commit, subdirectory)
        prev_files = extract_cpp_files_from_commit(repo_path, commits[i + 1], subdirectory) if i < len(commits) - 1 else {}

        for filename, content in current_files.items():
            comments, loc = count_comments_and_code_from_text(content)
            commit_data[commit][filename] = {
                'comments': comments,
                'loc': loc,
                'changed': 0,
                'new_comments': 0
            }

        # Compute diffs
        if i < len(commits) - 1:
            diff_output = run_git_command(['diff', f'{commits[i+1]}', f'{commit}', '--', subdirectory], repo_path)
            file_comment_diffs = count_new_comments_from_diff(diff_output)

            current_diff_file = None
            for line in diff_output.splitlines():
                if line.startswith('+++ b/'):
                    current_diff_file = line[6:]
                elif current_diff_file and line.startswith('+') and not line.startswith('+++'):
                    if current_diff_file in current_files:
                        commit_data[commit][current_diff_file]['changed'] += 1

            for file, new_comments in file_comment_diffs.items():
                if file in commit_data[commit]:
                    commit_data[commit][file]['new_comments'] = new_comments

    return commit_data

def print_detailed_report(commit_data):
    print(f"{'Commit':<10} {'File':<40} {'Comments':>8} {'LOC':>8} {'Changed':>10} {'New Comments':>14}")
    print("-" * 90)
    for commit, files in commit_data.items():
        for file, data in files.items():
            print(f"{commit[:7]:<10} {file:<40} {data['comments']:>8} {data['loc']:>8} {data['changed']:>10} {data['new_comments']:>14}")

def save_history_grouped_by_file(commit_data, filename="comment_file_history.json"):
    file_history = defaultdict(list)
    for commit_hash, files in commit_data.items():
        for file_path, stats in files.items():
            file_history[file_path].append({
                "commit": commit_hash,
                "comments": stats["comments"],
                "loc": stats["loc"],
                "changed": stats["changed"],
                "new_comments": stats["new_comments"]
            })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(file_history, f, indent=2)
    print(f"\n✅ JSON report saved to: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python git_comment_report_by_file.py <subdirectory>")
        sys.exit(1)

    repo_path = os.getcwd()
    subdirectory = sys.argv[1]

    if not os.path.isdir(os.path.join(repo_path, '.git')):
        print("Current directory is not a Git repository.")
        sys.exit(1)

    try:
        data = analyze_git_history_by_file(repo_path, subdirectory)
        print_detailed_report(data)
        save_history_grouped_by_file(data)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

