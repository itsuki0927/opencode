import argparse
import json
import os
import sys
import traceback

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.tools import ScmTools

def run_tool():
    parser = argparse.ArgumentParser(description="SCM MCP Tools CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_repo_args(p):
        p.add_argument("--repo_id", type=int, help="Repository ID")
        p.add_argument("--repo_name", type=str, help="Repository Name")

    def add_version_args(p):
        p.add_argument("--version_id", type=int, help="Version ID")
        p.add_argument("--version_number", type=str, help="Version Number")
        add_repo_args(p)

    # 1. get_repo
    p_get_repo = subparsers.add_parser("get_repo", help="Retrieve SCM repo details")
    add_repo_args(p_get_repo)

    # 2. get_version
    p_get_version = subparsers.add_parser("get_version", help="Retrieve SCM version details")
    add_version_args(p_get_version)

    # 3. get_version_status
    p_get_status = subparsers.add_parser("get_version_status", help="Retrieve SCM version status")
    add_version_args(p_get_status)

    # 4. get_version_dependencies
    p_get_deps = subparsers.add_parser("get_version_dependencies", help="Retrieve SCM version dependencies")
    add_version_args(p_get_deps)

    # 5. get_version_list
    p_get_list = subparsers.add_parser("get_version_list", help="Retrieve a list of SCM versions")
    add_repo_args(p_get_list)
    p_get_list.add_argument("--limit", type=int, default=10, help="Limit number of results")

    # 6. create_version
    p_create = subparsers.add_parser("create_version", help="Create a new SCM version")
    add_repo_args(p_create)
    p_create.add_argument("--type", dest="type_", default="online", choices=["online", "offline", "test"], help="Environment type")
    p_create.add_argument("--pub_base", default="branch_base", choices=["branch_base", "commit_base"], help="Publish base strategy")
    p_create.add_argument("--branch_name", help="Git branch name")
    p_create.add_argument("--commit_hash", help="Git commit hash")
    p_create.add_argument("--build_image", help="Custom build image")

    # 7. get_version_diff
    p_diff = subparsers.add_parser("get_version_diff", help="Compare two versions")
    add_repo_args(p_diff)
    p_diff.add_argument("--left_version_number", required=True, help="Left version number")
    p_diff.add_argument("--right_version_number", required=True, help="Right version number")

    # 8. get_build_log
    p_log = subparsers.add_parser("get_build_log", help="Retrieve build logs")
    add_repo_args(p_log)
    p_log.add_argument("--version_number", required=True, help="Version number")
    p_log.add_argument("--step_name", default="building", help="Build step name")
    p_log.add_argument("--arch", default="x86_64", help="Build architecture")

    args = parser.parse_args()
    tools = ScmTools()

    try:
        result = None
        if args.command == "get_repo":
            result = tools.get_repo(repo_id=args.repo_id, repo_name=args.repo_name)
        
        elif args.command == "get_version":
            result = tools.get_version(
                version_id=args.version_id, 
                version_number=args.version_number, 
                repo_id=args.repo_id, 
                repo_name=args.repo_name
            )
        
        elif args.command == "get_version_status":
            result = tools.get_version_status(
                version_id=args.version_id, 
                version_number=args.version_number, 
                repo_id=args.repo_id, 
                repo_name=args.repo_name
            )
            
        elif args.command == "get_version_dependencies":
            result = tools.get_version_dependencies(
                version_id=args.version_id, 
                version_number=args.version_number, 
                repo_id=args.repo_id, 
                repo_name=args.repo_name
            )
            
        elif args.command == "get_version_list":
            result = tools.get_version_list(
                repo_id=args.repo_id, 
                repo_name=args.repo_name, 
                limit=args.limit
            )
            
        elif args.command == "create_version":
            result = tools.create_version(
                repo_id=args.repo_id,
                repo_name=args.repo_name,
                type=args.type_,
                pub_base=args.pub_base,
                branch_name=args.branch_name,
                commit_hash=args.commit_hash,
                build_image=args.build_image
            )
            
        elif args.command == "get_version_diff":
            result = tools.get_version_diff(
                left_version_number=args.left_version_number,
                right_version_number=args.right_version_number,
                repo_id=args.repo_id,
                repo_name=args.repo_name
            )
            
        elif args.command == "get_build_log":
            result = tools.get_build_log(
                version_number=args.version_number,
                repo_id=args.repo_id,
                repo_name=args.repo_name,
                step_name=args.step_name,
                arch=args.arch
            )

        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_msg = {"error": str(e), "traceback": traceback.format_exc()}
        print(json.dumps(error_msg), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_tool()
