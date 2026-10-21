import requests

EXTENSIONS = {
    "audio": (".wav", ".mp3", ".ogg", ".flac", ".m4a", ".wem"),
    "object": (".obj", ".fbx", ".gltf", ".glb", ".dae"),
    "image": (".png", ".jpg", ".jpeg", ".tga", ".webp", ".bmp", ".gif")
}

repo = input("URL To Repo: ").strip()

if not repo:
    input("No repo entered.")
    raise SystemExit

token = input("Token (optional): ").strip()

if "github.com" in repo:
    repo = repo.split("github.com/")[-1]

parts = repo.strip("/").split("/")

if len(parts) < 2:
    input("Invalid repo.")
    raise SystemExit

owner = parts[0]
repo_name = parts[1]

selection = input("Categories (audio, object, image, all): ").lower().strip()

if not selection or selection == "all":
    wanted = list(EXTENSIONS)
else:
    wanted = []
    for item in selection.split(","):
        item = item.strip()
        if item in EXTENSIONS:
            wanted.append(item)

headers = {
    "Accept": "application/vnd.github+json"
}

if token:
    headers["Authorization"] = f"token {token}"

try:
    repo_info = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}",
        headers=headers
    )

    repo_info.raise_for_status()

    branch = repo_info.json().get("default_branch", "main")

    tree = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/{branch}?recursive=1",
        headers=headers
    )

    tree.raise_for_status()

    results = {
        "audio": [],
        "object": [],
        "image": []
    }

    for item in tree.json()["tree"]:
        if item["type"] != "blob":
            continue

        path = item["path"]
        lower = path.lower()

        for category, exts in EXTENSIONS.items():
            if lower.endswith(exts):
                results[category].append(
                    f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{path}"
                )
                break

    found = False

    for category in ("audio", "object", "image"):
        if category not in wanted:
            continue

        if not results[category]:
            continue

        found = True

        print(f"\n[{category}]")

        for url in results[category]:
            print(url)

    if not found:
        print("No matching files found.")

except Exception as e:
    print("\nERROR:")
    print(e)

input("\nPress Enter to close...")